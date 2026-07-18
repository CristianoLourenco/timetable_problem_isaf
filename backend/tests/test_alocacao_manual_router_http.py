# Implementa: RF13 (UC09) — endpoints de alocação manual via HTTP real, autenticado
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.api.v1.deps import get_session
from app.core import security
from app.core.config import settings
from app.main import app as fastapi_app
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.job import Job
from app.models.plano_curricular import PlanoCurricular
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.repositories.pendencia_repository import PendenciaRepository

EMAIL_GESTOR = "gestor.teste@isaf.co.ao"
CABECALHO_AUTH = {"Authorization": "Bearer qualquer"}


def _cliente_autenticado_como_gestor(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _sobrepor_sessao():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = _sobrepor_sessao
    monkeypatch.setattr(settings, "superadmin_emails", [EMAIL_GESTOR])
    monkeypatch.setattr(security, "verificar_id_token", lambda token: EMAIL_GESTOR)

    return TestClient(fastapi_app), engine


def _semear_cenario(engine):
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
            codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20,
            plano_curricular_id=plano.id,
        )
        professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disciplina = Disciplina(codigo="MAT", nome="Matemática")
        sala = Sala(codigo="S1", nome="Sala 1", capacidade=30)
        session.add_all([turma, professor, disciplina, sala])
        session.commit()
        session.refresh(turma)
        session.refresh(professor)
        session.refresh(disciplina)
        session.refresh(sala)

        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))

        job = Job(ano_letivo=2026, semestre="1")
        session.add(job)
        session.commit()
        session.refresh(job)

        return {
            "turma_id": turma.id,
            "professor_id": professor.id,
            "disciplina_id": disciplina.id,
            "sala_id": sala.id,
            "job_id": job.id,
        }


def test_criar_alocacao_manual_sucesso(monkeypatch):
    client, engine = _cliente_autenticado_como_gestor(monkeypatch)
    try:
        ids = _semear_cenario(engine)

        resposta = client.post(
            "/alocacoes",
            json={
                "job_id": ids["job_id"],
                "turma_id": ids["turma_id"],
                "disciplina_id": ids["disciplina_id"],
                "professor_id": ids["professor_id"],
                "sala_id": ids["sala_id"],
                "dia_semana": "segunda",
                "turno": "manha",
                "periodos": [1, 2],
            },
            headers=CABECALHO_AUTH,
        )
        assert resposta.status_code == 201, resposta.text
        alocacoes = resposta.json()
        assert len(alocacoes) == 2
    finally:
        fastapi_app.dependency_overrides.clear()


def test_criar_alocacao_manual_professor_nao_qualificado_e_409(monkeypatch):
    client, engine = _cliente_autenticado_como_gestor(monkeypatch)
    try:
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
                codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20,
                plano_curricular_id=plano.id,
            )
            professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
            disciplina = Disciplina(codigo="MAT", nome="Matemática")
            sala = Sala(codigo="S1", nome="Sala 1", capacidade=30)
            session.add_all([turma, professor, disciplina, sala])
            session.commit()
            session.refresh(turma)
            session.refresh(professor)
            session.refresh(disciplina)
            session.refresh(sala)
            job = Job(ano_letivo=2026, semestre="1")
            session.add(job)
            session.commit()
            session.refresh(job)
            ids = {
                "turma_id": turma.id,
                "professor_id": professor.id,
                "disciplina_id": disciplina.id,
                "sala_id": sala.id,
                "job_id": job.id,
            }
            # nunca adicionado ProfessorDisciplina — professor não qualificado

        resposta = client.post(
            "/alocacoes",
            json={
                "job_id": ids["job_id"],
                "turma_id": ids["turma_id"],
                "disciplina_id": ids["disciplina_id"],
                "professor_id": ids["professor_id"],
                "sala_id": ids["sala_id"],
                "dia_semana": "segunda",
                "turno": "manha",
                "periodos": [1, 2],
            },
            headers=CABECALHO_AUTH,
        )
        assert resposta.status_code == 409, resposta.text
        assert "qualificado" in resposta.json()["detail"].lower()
    finally:
        fastapi_app.dependency_overrides.clear()


def test_listar_pendencias_e_professores_qualificados_e_slots_vagos(monkeypatch):
    client, engine = _cliente_autenticado_como_gestor(monkeypatch)
    try:
        ids = _semear_cenario(engine)
        with Session(engine) as session:
            PendenciaRepository(session).criar_em_lote(
                ids["job_id"],
                [
                    {
                        "turma_id": ids["turma_id"],
                        "disciplina_id": ids["disciplina_id"],
                        "tempos_em_falta": 2,
                        "razao": "sem professor",
                        "professores_conflitantes": (),
                        "turmas_conflitantes": (),
                    }
                ],
            )

        pendencias = client.get(f"/jobs/{ids['job_id']}/pendencias", headers=CABECALHO_AUTH)
        assert pendencias.status_code == 200
        assert len(pendencias.json()) == 1
        assert pendencias.json()[0]["turma_id"] == ids["turma_id"]

        professores = client.get(
            f"/turmas/{ids['turma_id']}/professores-qualificados",
            params={"disciplina_id": ids["disciplina_id"]},
            headers=CABECALHO_AUTH,
        )
        assert professores.status_code == 200
        assert len(professores.json()) == 1
        assert professores.json()[0]["id"] == ids["professor_id"]

        slots = client.get(
            f"/turmas/{ids['turma_id']}/slots-vagos",
            params={"job_id": ids["job_id"]},
            headers=CABECALHO_AUTH,
        )
        assert slots.status_code == 200
        assert len(slots.json()) > 0
        assert all(len(b["periodos"]) >= 2 for b in slots.json())
    finally:
        fastapi_app.dependency_overrides.clear()


def test_mover_e_remover_alocacao(monkeypatch):
    client, engine = _cliente_autenticado_como_gestor(monkeypatch)
    try:
        ids = _semear_cenario(engine)

        criada = client.post(
            "/alocacoes",
            json={
                "job_id": ids["job_id"],
                "turma_id": ids["turma_id"],
                "disciplina_id": ids["disciplina_id"],
                "professor_id": ids["professor_id"],
                "sala_id": ids["sala_id"],
                "dia_semana": "segunda",
                "turno": "manha",
                "periodos": [1, 2],
            },
            headers=CABECALHO_AUTH,
        )
        alocacao_id = criada.json()[0]["id"]

        movida = client.patch(
            f"/alocacoes/{alocacao_id}",
            json={"dia_semana": "terca", "periodo": 1},
            headers=CABECALHO_AUTH,
        )
        assert movida.status_code == 200, movida.text
        assert movida.json()["dia_semana"] == "terca"

        removida = client.delete(f"/alocacoes/{alocacao_id}", headers=CABECALHO_AUTH)
        assert removida.status_code == 204

        removida_de_novo = client.delete(f"/alocacoes/{alocacao_id}", headers=CABECALHO_AUTH)
        assert removida_de_novo.status_code == 404
    finally:
        fastapi_app.dependency_overrides.clear()


def test_endpoints_exigem_autenticacao_de_gestor():
    client = TestClient(fastapi_app)
    resposta = client.get("/jobs/qualquer/pendencias")
    assert resposta.status_code == 401
