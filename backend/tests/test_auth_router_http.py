# Implementa: RF15, RF16 (UC13, UC14), RN10 — endpoints de autenticação via HTTP,
# sem contactar o Firebase real (tudo mockado ao nível do módulo importado pelo router).
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.api.v1.routers.auth as auth_router
import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.api.v1.deps import get_session
from app.core import firebase_rest, security
from app.core.firebase_rest import FirebaseAuthError
from app.main import app as fastapi_app
from app.models.professor import Professor

SESSAO_FIREBASE_FAKE = {"idToken": "tok", "refreshToken": "refresh", "expiresIn": "3600"}


def _cliente_com_bd_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _sobrepor_sessao():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = _sobrepor_sessao
    return TestClient(fastapi_app), engine


def test_login_sucesso(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        monkeypatch.setattr(auth_router, "login_com_password", lambda email, password: SESSAO_FIREBASE_FAKE)
        resposta = client.post("/auth/login", json={"email": "prof@isaf.co.ao", "password": "palavra-passe"})
        assert resposta.status_code == 200
        assert resposta.json() == {"id_token": "tok", "refresh_token": "refresh", "expires_in": 3600}
    finally:
        fastapi_app.dependency_overrides.clear()


def test_login_credenciais_invalidas(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        def _falhar(email, password):
            raise FirebaseAuthError("INVALID_LOGIN_CREDENTIALS")

        monkeypatch.setattr(auth_router, "login_com_password", _falhar)
        resposta = client.post("/auth/login", json={"email": "prof@isaf.co.ao", "password": "errada"})
        assert resposta.status_code == 401
    finally:
        fastapi_app.dependency_overrides.clear()


def test_refresh_sucesso(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        monkeypatch.setattr(auth_router, "renovar_token", lambda refresh_token: SESSAO_FIREBASE_FAKE)
        resposta = client.post("/auth/refresh", json={"refresh_token": "refresh-antigo"})
        assert resposta.status_code == 200
        assert resposta.json()["id_token"] == "tok"
    finally:
        fastapi_app.dependency_overrides.clear()


def test_login_google_sucesso(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        monkeypatch.setattr(auth_router, "login_com_google", lambda google_id_token: SESSAO_FIREBASE_FAKE)
        resposta = client.post("/auth/login-google", json={"google_id_token": "google-tok"})
        assert resposta.status_code == 200
        assert resposta.json()["id_token"] == "tok"
    finally:
        fastapi_app.dependency_overrides.clear()


def test_recuperar_password_sucesso(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        monkeypatch.setattr(auth_router, "enviar_email_recuperacao_password", lambda email: None)
        resposta = client.post("/auth/recuperar-password", json={"email": "prof@isaf.co.ao"})
        assert resposta.status_code == 204
    finally:
        fastapi_app.dependency_overrides.clear()


def test_recuperar_password_email_inexistente_nao_revela_isso(monkeypatch):
    """Evita enumeration — 204 mesmo quando o email não existe."""
    client, _ = _cliente_com_bd_teste()
    try:
        def _falhar(email):
            raise FirebaseAuthError("EMAIL_NOT_FOUND")

        monkeypatch.setattr(auth_router, "enviar_email_recuperacao_password", _falhar)
        resposta = client.post("/auth/recuperar-password", json={"email": "desconhecido@isaf.co.ao"})
        assert resposta.status_code == 204
    finally:
        fastapi_app.dependency_overrides.clear()


def test_registo_professor_com_email_correspondente(monkeypatch):
    client, engine = _cliente_com_bd_teste()
    try:
        with Session(engine) as session:
            professor = Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True)
            session.add(professor)
            session.commit()
            session.refresh(professor)
            professor_id_esperado = professor.id

        monkeypatch.setattr(firebase_rest, "criar_conta_com_password", lambda email, password: SESSAO_FIREBASE_FAKE)

        resposta = client.post(
            "/auth/registo-professor",
            json={"email": "prof@isaf.co.ao", "password": "palavra-passe", "contacto_telefonico": "900000000"},
        )

        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["id_token"] == "tok"
        assert corpo["utilizador"]["perfil"] == "PROFESSOR"
        assert corpo["utilizador"]["professor_id"] == professor_id_esperado
    finally:
        fastapi_app.dependency_overrides.clear()


def test_registo_professor_sem_correspondencia_devolve_403(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        monkeypatch.setattr(firebase_rest, "criar_conta_com_password", lambda email, password: SESSAO_FIREBASE_FAKE)

        resposta = client.post(
            "/auth/registo-professor",
            json={"email": "desconhecido@isaf.co.ao", "password": "palavra-passe", "contacto_telefonico": "900000000"},
        )
        assert resposta.status_code == 403
    finally:
        fastapi_app.dependency_overrides.clear()


def test_me_devolve_papel_e_professor_id(monkeypatch):
    client, engine = _cliente_com_bd_teste()
    try:
        with Session(engine) as session:
            professor = Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True)
            session.add(professor)
            session.commit()
            session.refresh(professor)
            professor_id_esperado = professor.id

        monkeypatch.setattr(firebase_rest, "criar_conta_com_password", lambda email, password: SESSAO_FIREBASE_FAKE)
        client.post(
            "/auth/registo-professor",
            json={"email": "prof@isaf.co.ao", "password": "palavra-passe", "contacto_telefonico": "900000000"},
        )

        monkeypatch.setattr(security, "verificar_id_token", lambda token: "prof@isaf.co.ao")
        resposta = client.get("/auth/me", headers={"Authorization": "Bearer qualquer"})

        assert resposta.status_code == 200
        assert resposta.json() == {"email": "prof@isaf.co.ao", "papel": "PROFESSOR", "professor_id": professor_id_esperado}
    finally:
        fastapi_app.dependency_overrides.clear()


def test_me_sem_token_devolve_401(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        resposta = client.get("/auth/me")
        assert resposta.status_code == 401
    finally:
        fastapi_app.dependency_overrides.clear()


def test_registo_professor_duplicado_devolve_409(monkeypatch):
    client, engine = _cliente_com_bd_teste()
    try:
        with Session(engine) as session:
            session.add(Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True))
            session.commit()

        monkeypatch.setattr(firebase_rest, "criar_conta_com_password", lambda email, password: SESSAO_FIREBASE_FAKE)

        payload = {"email": "prof@isaf.co.ao", "password": "palavra-passe", "contacto_telefonico": "900000000"}
        primeira = client.post("/auth/registo-professor", json=payload)
        assert primeira.status_code == 201

        segunda = client.post("/auth/registo-professor", json=payload)
        assert segunda.status_code == 409
    finally:
        fastapi_app.dependency_overrides.clear()
