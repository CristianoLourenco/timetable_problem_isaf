# Implementa: RF13 (UC09) — testes de app/repositories/pendencia_repository.py
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.job import Job
from app.models.plano_curricular import PlanoCurricular
from app.models.turma import Turma
from app.repositories.pendencia_repository import PendenciaRepository


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _semear_job_turma_disciplina(session: Session):
    curso = Curso(codigo="INF", nome="Informática")
    session.add(curso)
    session.commit()
    session.refresh(curso)

    plano = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
    session.add(plano)
    session.commit()
    session.refresh(plano)

    turma = Turma(
        codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, plano_curricular_id=plano.id
    )
    disciplina = Disciplina(codigo="MAT", nome="Matemática")
    session.add_all([turma, disciplina])
    session.commit()
    session.refresh(turma)
    session.refresh(disciplina)

    job = Job(ano_letivo=2026, semestre="1")
    session.add(job)
    session.commit()
    session.refresh(job)

    return job, turma, disciplina


def test_criar_em_lote_e_listar_por_job():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, disciplina = _semear_job_turma_disciplina(session)
        repo = PendenciaRepository(session)

        repo.criar_em_lote(
            job.id,
            [
                {
                    "turma_id": turma.id,
                    "disciplina_id": disciplina.id,
                    "tempos_em_falta": 2,
                    "razao": "sem professor qualificado",
                    "professores_conflitantes": (),
                    "turmas_conflitantes": (),
                }
            ],
        )

        pendencias = repo.listar_por_job(job.id)
        assert len(pendencias) == 1
        assert pendencias[0].turma_id == turma.id
        assert pendencias[0].disciplina_id == disciplina.id
        assert pendencias[0].tempos_em_falta == 2
        assert pendencias[0].razao == "sem professor qualificado"


def test_listar_por_job_e_turma():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, disciplina = _semear_job_turma_disciplina(session)
        repo = PendenciaRepository(session)
        repo.criar_em_lote(
            job.id,
            [
                {
                    "turma_id": turma.id,
                    "disciplina_id": disciplina.id,
                    "tempos_em_falta": 1,
                    "razao": "razao qualquer",
                    "professores_conflitantes": (5, 6),
                    "turmas_conflitantes": (7,),
                }
            ],
        )

        pendencias = repo.listar_por_job_e_turma(job.id, turma.id)
        assert len(pendencias) == 1
        assert pendencias[0].professores_conflitantes == "5,6"
        assert pendencias[0].turmas_conflitantes == "7"

        assert repo.listar_por_job_e_turma(job.id, 999) == []


def test_remover_por_turma_disciplina():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, disciplina = _semear_job_turma_disciplina(session)
        repo = PendenciaRepository(session)
        repo.criar_em_lote(
            job.id,
            [
                {
                    "turma_id": turma.id,
                    "disciplina_id": disciplina.id,
                    "tempos_em_falta": 2,
                    "razao": "x",
                    "professores_conflitantes": (),
                    "turmas_conflitantes": (),
                }
            ],
        )

        repo.remover_por_turma_disciplina(job.id, turma.id, disciplina.id)

        assert repo.listar_por_job(job.id) == []
