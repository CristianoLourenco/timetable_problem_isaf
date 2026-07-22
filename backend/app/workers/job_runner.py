# Implementa: RF09, RF10, RF13 (UC08, UC09, UC10) — ver docs/relatorio/04_analise_desenvolvimento/
#
# Corre fora do ciclo do pedido HTTP (FastAPI BackgroundTasks, sem Celery/Redis no MVP —
# ver backend/docs/CONVENCOES.md "Proibições absolutas"). Abre a sua própria Session porque o
# pedido original já terminou quando esta função executa.
from datetime import datetime

from sqlmodel import Session

from app.core.config import settings
from app.core.database import engine as _engine_producao
from app.models.alocacao import Alocacao
from app.models.job import JobStatus
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.job_repository import JobRepository
from app.repositories.pendencia_repository import PendenciaDict, PendenciaRepository
from app.services.disponibilidade_geracao_service import gerar_disponibilidade_sintetica
from app.services.horario_service import extrair_dados
from app.solver.orquestrador_turnos import resolver_horario_por_turnos
from app.solver.solve import resolver_horario

# RF13 — nunca pedir ao Gestor para escolher tempo de procura: cada Job começa
# sempre pelo valor mais baixo e só escala para o seguinte se o solver devolver
# UNKNOWN por tempo esgotado (nunca por impossibilidade — RN05 é soft-com-défice,
# ver sub-projeto "solver nunca INFEASIBLE"). Mantém a maioria dos horários
# rápidos (a maior parte resolve em 2 min) sem pagar sempre o custo de 10 min.
ESCALONAMENTO_TEMPO_MINUTOS = (2, 5, 10)


def executar(job_id: str, *, engine=_engine_producao) -> None:
    """RF09/RF10 — atualiza o Job para RUNNING, resolve, grava DONE/INFEASIBLE (RNF03).

    `engine` é injetável para permitir testar com uma BD SQLite em memória sem tocar
    na ligação de produção.
    """
    with Session(engine) as session:
        job_repo = JobRepository(session)
        job = job_repo.obter(job_id)
        if job is None:
            return  # job removido entretanto — nada a fazer

        job_repo.atualizar_status(job, JobStatus.RUNNING)

        # RF05/RN07 — quando o Job corre, turmas+grade+qualificações já têm de
        # existir (não há como gerar horário sem elas), logo é o primeiro ponto do
        # pipeline com sinal completo para fundamentar disponibilidade sintética em
        # professores reais importados via Excel (RF06/RF07 não tem caminho de
        # importação para Disponibilidade — ver app/services/disponibilidade_geracao_service.py).
        # Nunca sobrescreve um registo já existente (RF05 real ou geração anterior).
        gerar_disponibilidade_sintetica(session)

        dados = extrair_dados(session, job.ano_letivo, job.semestre)

        # RF13 — escalonamento automático: tenta 2 min, se UNKNOWN-por-tempo tenta
        # 5, depois 10. RN05 é soft-com-défice (sub-projeto "solver nunca
        # INFEASIBLE"), logo o único status não-viável possível é UNKNOWN por tempo
        # esgotado — nunca impossibilidade estrutural — por isso é sempre seguro
        # tentar de novo com mais tempo em vez de desistir.
        for tempo_minutos in ESCALONAMENTO_TEMPO_MINUTOS:
            job.tempo_maximo_minutos = tempo_minutos
            tempo_total_segundos = tempo_minutos * 60
            if settings.solver_usar_decomposicao_turno:
                resultado = resolver_horario_por_turnos(
                    dados,
                    # Orçamento agregado desta tentativa — resolver_horario_por_turnos
                    # distribui-o entre as fases (Manhã/Tarde/Noite) proporcionalmente
                    # ao tamanho estimado de cada uma, não em partes iguais (achado
                    # real: um turno maior precisa de bem mais tempo do que um
                    # pequeno para convergir — ver _distribuir_orcamento).
                    max_time_in_seconds_total=tempo_total_segundos,
                    num_search_workers=settings.solver_num_search_workers,
                )
            else:
                resultado = resolver_horario(
                    dados,
                    max_time_in_seconds=tempo_total_segundos,
                    num_search_workers=settings.solver_num_search_workers,
                )

            if resultado.status != "INFEASIBLE":
                break  # OPTIMAL/FEASIBLE — não precisa de mais tempo
            if tempo_minutos == ESCALONAMENTO_TEMPO_MINUTOS[-1]:
                break  # já tentou o teto (10 min) — reporta o UNKNOWN final

        # turno não é gravado em Alocacao — é sempre o da Turma alocada (3FN), o
        # solver ainda usa turno internamente (a.turno) para gerar/validar as
        # variáveis, só não persiste porque seria dependência transitiva.
        #
        # Persistido em AMBOS os ramos (DONE e INFEASIBLE-por-timeout): desde o
        # sub-projeto "solver nunca INFEASIBLE", um timeout parcial na decomposição
        # por turno preserva as alocações/pendências de fases já resolvidas (ver
        # app/solver/orquestrador_turnos.py) — nunca descartar esse trabalho já
        # feito só porque uma fase seguinte precisou de mais tempo.
        alocacoes = [
            Alocacao(
                job_id=job_id,
                turma_id=a.turma_id,
                disciplina_id=a.disciplina_id,
                professor_id=a.professor_id,
                sala_id=a.sala_id,
                dia_semana=a.dia_semana,
                periodo=a.periodo,
                penalizacao_aplicada=a.penalizacao_aplicada,
            )
            for a in resultado.alocacoes
        ]
        AlocacaoRepository(session).criar_em_lote(alocacoes)

        pendencias: list[PendenciaDict] = [
            {
                "turma_id": p.turma_id,
                "disciplina_id": p.disciplina_id,
                "tempos_em_falta": p.tempos_em_falta,
                "razao": p.razao,
                "professores_conflitantes": p.professores_conflitantes,
                "turmas_conflitantes": p.turmas_conflitantes,
            }
            for p in resultado.pendencias
        ]
        PendenciaRepository(session).criar_em_lote(job_id, pendencias)

        if resultado.status == "INFEASIBLE":
            job_repo.atualizar_status(
                job,
                JobStatus.INFEASIBLE,
                diagnostico=resultado.diagnostico,
                concluido_em=datetime.utcnow(),
            )
            return

        job_repo.atualizar_status(job, JobStatus.DONE, concluido_em=datetime.utcnow())
