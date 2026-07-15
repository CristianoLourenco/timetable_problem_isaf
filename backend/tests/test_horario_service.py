# Implementa: Fase 4 (RF09, RF10, RF13) — fluxo assíncrono ponta-a-ponta com BD em memória
from datetime import time

from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.job import JobStatus
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.slot import Slot
from app.models.turma import Turma
from app.models.turma_disciplina import TurmaDisciplina
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.job_repository import JobRepository
from app.workers.job_runner import executar


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _semear_slots(session: Session) -> None:
    for dia in ["segunda", "terca"]:
        for tempo in range(1, 5):
            session.add(Slot(dia_semana=dia, tempo_ordem=tempo, hora_inicio=time(7, 30), hora_fim=time(8, 15)))
    session.commit()


def _semear_cenario_viavel(session: Session) -> None:
    curso = Curso(codigo="INF", nome="Informática")
    session.add(curso)
    session.commit()
    session.refresh(curso)

    turma = Turma(codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, curso_id=curso.id)
    professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
    disciplina = Disciplina(codigo="MAT", nome="Matemática")
    sala = Sala(codigo="S1", nome="Sala 1", capacidade=30)
    session.add_all([turma, professor, disciplina, sala])
    session.commit()
    session.refresh(turma)
    session.refresh(professor)
    session.refresh(disciplina)
    session.refresh(sala)

    _semear_slots(session)

    session.add(TurmaDisciplina(turma_id=turma.id, disciplina_id=disciplina.id, carga_horaria_semanal=2))
    session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
    session.commit()


def test_job_runner_gera_alocacoes_para_cenario_viavel():
    engine = _criar_engine_teste()

    with Session(engine) as session:
        _semear_cenario_viavel(session)
        job_id = JobRepository(session).criar().id

    executar(job_id, engine=engine)

    with Session(engine) as session:
        job = JobRepository(session).obter(job_id)
        assert job.status == JobStatus.DONE
        assert job.diagnostico is None
        assert job.concluido_em is not None

        alocacoes = AlocacaoRepository(session).listar_por_job(job_id)
        assert len(alocacoes) == 2


def test_job_runner_marca_infeasible_com_diagnostico():
    """RN06 proíbe carga_horaria_semanal=1 (tempo isolado) — deve terminar em INFEASIBLE, nunca em exceção."""
    engine = _criar_engine_teste()

    with Session(engine) as session:
        curso = Curso(codigo="INF", nome="Informática")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        turma = Turma(codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, curso_id=curso.id)
        professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disciplina = Disciplina(codigo="MAT", nome="Matemática")
        sala = Sala(codigo="S1", nome="Sala 1", capacidade=30)
        session.add_all([turma, professor, disciplina, sala])
        session.commit()
        session.refresh(turma)
        session.refresh(professor)
        session.refresh(disciplina)

        _semear_slots(session)

        session.add(TurmaDisciplina(turma_id=turma.id, disciplina_id=disciplina.id, carga_horaria_semanal=1))
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()

        job_id = JobRepository(session).criar().id

    executar(job_id, engine=engine)

    with Session(engine) as session:
        job = JobRepository(session).obter(job_id)
        assert job.status == JobStatus.INFEASIBLE
        assert "carga_horaria_semanal=1" in job.diagnostico
        assert AlocacaoRepository(session).listar_por_job(job_id) == []
