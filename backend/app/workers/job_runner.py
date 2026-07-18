# Implementa: RF09, RF10, RF13 (UC08, UC09, UC10) — ver docs/04_04_analise_desenvolvimento.md
#
# Corre fora do ciclo do pedido HTTP (FastAPI BackgroundTasks, sem Celery/Redis no MVP —
# ver backend/CLAUDE.md "Proibições absolutas"). Abre a sua própria Session porque o
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
        tempo_total_segundos = job.tempo_maximo_minutos * 60
        if settings.solver_usar_decomposicao_turno:
            resultado = resolver_horario_por_turnos(
                dados,
                # 3 fases (Manhã/Tarde/Noite) dividem o orçamento total escolhido pelo
                # Gestor — mantém a mesma proporção que settings.solver_max_time_seconds_por_turno
                # já usava (100s de 300s totais = 1/3 por fase).
                max_time_in_seconds_por_turno=tempo_total_segundos / 3,
                num_search_workers=settings.solver_num_search_workers,
            )
        else:
            resultado = resolver_horario(
                dados,
                max_time_in_seconds=tempo_total_segundos,
                num_search_workers=settings.solver_num_search_workers,
            )

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
