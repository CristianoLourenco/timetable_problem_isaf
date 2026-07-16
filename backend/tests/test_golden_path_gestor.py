# Implementa: Fase 7 — teste de integração ponta-a-ponta do fluxo do Gestor
# (RF01-RF04, RF06/RF07 grade curricular, RF09-RF12), via HTTP real com autenticação,
# não apenas chamadas diretas à service layer (essas já estão cobertas nas Fases 3-6).
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.api.v1.routers.horario as horario_router
import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.api.v1.deps import get_session
from app.core import security
from app.core.config import settings
from app.main import app as fastapi_app
from app.workers import job_runner

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

    # BackgroundTasks corre fora do ciclo de dependências do FastAPI (get_session
    # não se aplica) — sem isto, job_runner.executar tentaria ligar-se ao Postgres
    # de produção (indisponível neste sandbox) em vez da BD de teste.
    monkeypatch.setattr(horario_router, "executar", lambda job_id: job_runner.executar(job_id, engine=engine))

    return TestClient(fastapi_app)


def test_fluxo_completo_gestor_cria_dados_gera_e_consulta_horario(monkeypatch):
    client = _cliente_autenticado_como_gestor(monkeypatch)
    try:
        curso = client.post("/cursos", json={"codigo": "INF", "nome": "Informática"}, headers=CABECALHO_AUTH)
        assert curso.status_code == 201, curso.text
        curso_id = curso.json()["id"]

        professor = client.post(
            "/professores",
            json={"nome": "Prof A", "email": "profa@isaf.co.ao", "classificacao": 5, "vinculo_casa": True},
            headers=CABECALHO_AUTH,
        )
        assert professor.status_code == 201, professor.text
        professor_id = professor.json()["id"]

        plano = client.post(
            "/planos-curriculares",
            json={"curso_id": curso_id, "ano": 1, "semestre": "1"},
            headers=CABECALHO_AUTH,
        )
        assert plano.status_code == 201, plano.text
        plano_id = plano.json()["id"]

        turma = client.post(
            "/turmas",
            json={
                "codigo": "T1",
                "nome": "Turma 1",
                "ano_letivo": 2026,
                "turno": "manha",
                "numero_alunos": 25,
                "plano_curricular_id": plano_id,
            },
            headers=CABECALHO_AUTH,
        )
        assert turma.status_code == 201, turma.text
        turma_id = turma.json()["id"]

        disciplina = client.post("/disciplinas", json={"codigo": "MAT", "nome": "Matemática"}, headers=CABECALHO_AUTH)
        assert disciplina.status_code == 201, disciplina.text
        disciplina_id = disciplina.json()["id"]

        sala = client.post("/salas", json={"codigo": "S1", "nome": "Sala 1", "capacidade": 30}, headers=CABECALHO_AUTH)
        assert sala.status_code == 201, sala.text

        grade = client.post(
            f"/planos-curriculares/{plano_id}/disciplinas",
            json={"itens": [{"disciplina_id": disciplina_id, "carga_horaria_semanal": 2}]},
            headers=CABECALHO_AUTH,
        )
        assert grade.status_code == 200, grade.text

        qualificacao = client.post(
            f"/professores/{professor_id}/disciplinas",
            json={"disciplina_ids": [disciplina_id]},
            headers=CABECALHO_AUTH,
        )
        assert qualificacao.status_code == 200, qualificacao.text

        # BackgroundTasks corre de forma síncrona dentro do próprio ciclo do TestClient —
        # ao devolver a resposta, o job_runner já terminou.
        disparo = client.post("/gerar-horario", headers=CABECALHO_AUTH)
        assert disparo.status_code == 202, disparo.text
        job_id = disparo.json()["job_id"]

        job = client.get(f"/jobs/{job_id}", headers=CABECALHO_AUTH)
        assert job.status_code == 200
        assert job.json()["status"] == "DONE", job.json()

        horario_turma = client.get(f"/horarios/turma/{turma_id}", headers=CABECALHO_AUTH)
        assert horario_turma.status_code == 200
        tempos_turma = [t for dia in horario_turma.json()["dias"] for t in dia["tempos"]]
        assert len(tempos_turma) == 2
        assert tempos_turma[0]["disciplina_nome"] == "Matemática"
        assert tempos_turma[0]["professor_nome"] == "Prof A"

        horario_professor = client.get(f"/horarios/professor/{professor_id}", headers=CABECALHO_AUTH)
        assert horario_professor.status_code == 200
        tempos_professor = [t for dia in horario_professor.json()["dias"] for t in dia["tempos"]]

        def chave(t):
            return (t["dia_semana"], t["turno"], t["periodo"])

        assert {chave(t) for t in tempos_professor} == {chave(t) for t in tempos_turma}
    finally:
        fastapi_app.dependency_overrides.clear()
