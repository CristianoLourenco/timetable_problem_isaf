# Implementa: RF09, RF10, RF13 (UC08, UC09, UC10) — ver docs/04_04_analise_desenvolvimento.md
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
from app.services.horario_service import extrair_dados
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

        dados = extrair_dados(session, job.ano_letivo, job.semestre)
        resultado = resolver_horario(
            dados,
            max_time_in_seconds=settings.solver_max_time_seconds,
            num_search_workers=settings.solver_num_search_workers,
        )

        if resultado.status == "INFEASIBLE":
            job_repo.atualizar_status(
                job,
                JobStatus.INFEASIBLE,
                diagnostico=resultado.diagnostico,
                concluido_em=datetime.utcnow(),
            )
            return

        # turno não é gravado em Alocacao — é sempre o da Turma alocada (3FN), o
        # solver ainda usa turno internamente (a.turno) para gerar/validar as
        # variáveis, só não persiste porque seria dependência transitiva.
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
        job_repo.atualizar_status(job, JobStatus.DONE, concluido_em=datetime.utcnow())
