# Implementa: Fase 7 — teste HTTP do auto-registo de Professor (RN10)
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.api.v1.deps import get_session
from app.core import security
from app.main import app as fastapi_app
from app.models.professor import Professor

CABECALHO_AUTH = {"Authorization": "Bearer qualquer"}


def _cliente_com_bd_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _sobrepor_sessao():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = _sobrepor_sessao
    return TestClient(fastapi_app), engine


def test_professor_com_email_correspondente_completa_registo(monkeypatch):
    client, engine = _cliente_com_bd_teste()
    try:
        with Session(engine) as session:
            professor = Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True)
            session.add(professor)
            session.commit()
            session.refresh(professor)
            professor_id_esperado = professor.id

        monkeypatch.setattr(security, "verificar_id_token", lambda token: "prof@isaf.co.ao")

        resposta = client.post(
            "/auth/registo-professor", json={"contacto_telefonico": "900000000"}, headers=CABECALHO_AUTH
        )

        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["perfil"] == "PROFESSOR"
        assert corpo["professor_id"] == professor_id_esperado
    finally:
        fastapi_app.dependency_overrides.clear()


def test_email_sem_correspondencia_de_professor_devolve_403(monkeypatch):
    client, _ = _cliente_com_bd_teste()
    try:
        monkeypatch.setattr(security, "verificar_id_token", lambda token: "desconhecido@isaf.co.ao")

        resposta = client.post(
            "/auth/registo-professor", json={"contacto_telefonico": "900000000"}, headers=CABECALHO_AUTH
        )

        assert resposta.status_code == 403
    finally:
        fastapi_app.dependency_overrides.clear()


def test_registo_duplicado_devolve_409(monkeypatch):
    client, engine = _cliente_com_bd_teste()
    try:
        with Session(engine) as session:
            session.add(Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True))
            session.commit()

        monkeypatch.setattr(security, "verificar_id_token", lambda token: "prof@isaf.co.ao")

        primeira = client.post(
            "/auth/registo-professor", json={"contacto_telefonico": "900000000"}, headers=CABECALHO_AUTH
        )
        assert primeira.status_code == 201

        segunda = client.post(
            "/auth/registo-professor", json={"contacto_telefonico": "900000001"}, headers=CABECALHO_AUTH
        )
        assert segunda.status_code == 409
    finally:
        fastapi_app.dependency_overrides.clear()
