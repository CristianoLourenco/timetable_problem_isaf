# Implementa: Fase 6 (RN09, RN10, RN11) — autenticação/autorização ponta-a-ponta via HTTP
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.api.v1.deps import get_session
from app.core import security
from app.core.config import settings
from app.main import app as fastapi_app


def _client_com_bd_teste():
    # StaticPool — FastAPI corre endpoints síncronos numa threadpool; sem isto, cada
    # thread veria uma BD SQLite em memória vazia e diferente (ligação não partilhada).
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _sobrepor_sessao():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = _sobrepor_sessao
    return TestClient(fastapi_app)


def test_sem_token_devolve_401():
    client = _client_com_bd_teste()
    try:
        resposta = client.get("/cursos")
        assert resposta.status_code == 401
    finally:
        fastapi_app.dependency_overrides.clear()


def test_token_valido_sem_perfil_devolve_403(monkeypatch):
    client = _client_com_bd_teste()
    monkeypatch.setattr(security, "verificar_id_token", lambda token: "desconhecido@isaf.co.ao")
    try:
        resposta = client.get("/cursos", headers={"Authorization": "Bearer qualquer"})
        assert resposta.status_code == 403
    finally:
        fastapi_app.dependency_overrides.clear()


def test_superadmin_bootstrap_acede_a_rota_de_gestor(monkeypatch):
    client = _client_com_bd_teste()
    monkeypatch.setattr(settings, "superadmin_emails", ["admin@isaf.co.ao"])
    monkeypatch.setattr(security, "verificar_id_token", lambda token: "admin@isaf.co.ao")
    try:
        resposta = client.get("/cursos", headers={"Authorization": "Bearer qualquer"})
        assert resposta.status_code == 200
        assert resposta.json() == []
    finally:
        fastapi_app.dependency_overrides.clear()


def test_apenas_superadmin_gere_utilizadores(monkeypatch):
    client = _client_com_bd_teste()
    monkeypatch.setattr(settings, "superadmin_emails", [])
    monkeypatch.setattr(security, "verificar_id_token", lambda token: "desconhecido@isaf.co.ao")
    try:
        resposta = client.get("/utilizadores", headers={"Authorization": "Bearer qualquer"})
        assert resposta.status_code == 403
    finally:
        fastapi_app.dependency_overrides.clear()
