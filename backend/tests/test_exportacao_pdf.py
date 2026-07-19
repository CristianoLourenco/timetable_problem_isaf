# Implementa: RF11, RF12 — testes de exportação do horário em PDF/zip,
# ver app/services/exportacao_pdf_service.py.
import zipfile
from io import BytesIO

import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.job import Job, JobStatus
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.repositories.job_repository import JobRepository
from app.services.exportacao_pdf_service import gerar_pdf_turma, gerar_zip_por_job
from app.workers.job_runner import executar


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _semear_e_gerar(engine, n_turmas: int = 2) -> tuple[str, list[int]]:
    """Semeia n_turmas viáveis (mesma disciplina/professor, uma sala por turma)
    e corre o job_runner — devolve (job_id, [turma_ids]). Uma sala por turma:
    cada turma fica presa a uma única sala pelo turno inteiro (ver
    builder.atribuir_salas_por_turma_turno, 2026-07-19) — n_turmas turmas do
    mesmo turno precisam de n_turmas salas para não gerar défice estrutural
    por escassez de sala."""
    with Session(engine) as session:
        curso = Curso(codigo="INF", nome="Informática")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        plano = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
        session.add(plano)
        session.commit()
        session.refresh(plano)

        professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disciplina = Disciplina(codigo="MAT", nome="Matemática")
        salas = [Sala(codigo=f"S{i + 1}", nome=f"Sala {i + 1}", capacidade=30) for i in range(n_turmas)]
        session.add_all([professor, disciplina, *salas])
        session.commit()
        session.refresh(professor)
        session.refresh(disciplina)
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        # Grade curricular é partilhada por todas as turmas do mesmo plano — um só
        # registo, não um por turma (ver docs/04_04_analise_desenvolvimento.md secção 4.2.3).
        session.add(
            PlanoCurricularDisciplina(plano_curricular_id=plano.id, disciplina_id=disciplina.id, carga_horaria_semanal=2)
        )
        session.commit()

        turma_ids = []
        for i in range(n_turmas):
            turma = Turma(
                codigo=f"T{i + 1}",
                nome=f"Turma {i + 1}",
                ano_letivo=2026,
                turno="manha",
                numero_alunos=20,
                plano_curricular_id=plano.id,
            )
            session.add(turma)
            session.commit()
            session.refresh(turma)
            turma_ids.append(turma.id)

        job_id = JobRepository(session).criar(ano_letivo=2026, semestre="1").id

    executar(job_id, engine=engine)
    return job_id, turma_ids


def test_gerar_pdf_turma_produz_documento_valido():
    engine = _criar_engine_teste()
    _, turma_ids = _semear_e_gerar(engine, n_turmas=1)

    with Session(engine) as session:
        pdf_bytes = gerar_pdf_turma(session, turma_ids[0])

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_gerar_pdf_turma_inexistente_levanta_erro():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        with pytest.raises(EntidadeNaoEncontradaError):
            gerar_pdf_turma(session, 999)


def test_gerar_pdf_turma_sem_horario_gerado_levanta_erro():
    """Diferente da consulta JSON (RF11, que devolve None/200 — "ainda não
    gerado" é normal na UI interativa), exportar um PDF é uma ação explícita do
    Gestor: sem nenhum horário gerado para o âmbito da turma, continua 404."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
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
        session.add(turma)
        session.commit()
        session.refresh(turma)
        turma_id = turma.id

    with Session(engine) as session:
        with pytest.raises(EntidadeNaoEncontradaError):
            gerar_pdf_turma(session, turma_id)


def test_gerar_zip_por_job_contem_um_pdf_por_turma():
    engine = _criar_engine_teste()
    job_id, turma_ids = _semear_e_gerar(engine, n_turmas=3)

    with Session(engine) as session:
        zip_bytes = gerar_zip_por_job(session, job_id)

    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        nomes = sorted(zf.namelist())
        assert nomes == ["T1.pdf", "T2.pdf", "T3.pdf"]
        for nome in nomes:
            conteudo = zf.read(nome)
            assert conteudo.startswith(b"%PDF")


def test_gerar_zip_job_inexistente_levanta_erro():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        with pytest.raises(EntidadeNaoEncontradaError):
            gerar_zip_por_job(session, "job-inexistente")


def test_gerar_zip_por_job_nao_repete_query_de_listagem_por_turma():
    """Bug de performance real (2026-07-19): montar_resposta recarregava
    turma/professor/disciplina/sala inteiros (SELECT * sem WHERE) a cada
    chamada — gerar_zip_por_job chama-o uma vez por turma, então 86 turmas
    reais do ISAF mediam 86x a mesma query completa. Corrigido com cache por
    instância de HorarioService (_carregar_referencias) — aqui confirma-se
    que N turmas custam O(1) SELECTs de listagem, não O(N)."""
    from sqlalchemy import event

    engine = _criar_engine_teste()
    job_id, turma_ids = _semear_e_gerar(engine, n_turmas=5)

    queries_sem_where: list[str] = []

    def _contar(conn, cursor, statement, parameters, context, executemany):
        sql = statement.strip().upper()
        if sql.startswith("SELECT") and "WHERE" not in sql and "FROM TURMA" in sql:
            queries_sem_where.append(statement)

    with Session(engine) as session:
        event.listen(engine, "before_cursor_execute", _contar)
        try:
            gerar_zip_por_job(session, job_id)
        finally:
            event.remove(engine, "before_cursor_execute", _contar)

    assert len(queries_sem_where) <= 1, (
        f"esperava no máximo 1 SELECT completo de turma (cacheado), encontrou {len(queries_sem_where)}"
    )


def test_gerar_zip_job_nao_concluido_levanta_erro():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job = Job(status=JobStatus.RUNNING, ano_letivo=2026, semestre="1")
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id

    with Session(engine) as session:
        with pytest.raises(ValueError):
            gerar_zip_por_job(session, job_id)
