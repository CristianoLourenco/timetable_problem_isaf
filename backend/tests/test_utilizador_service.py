# Implementa: Fase 6 (RN10) — registo de Gestor (Superadmin) e auto-registo de Professor
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core import firebase_rest
from app.core.exceptions import AcessoNegadoError, IntegridadeVioladaError
from app.models.professor import Professor
from app.models.utilizador import PerfilUtilizador
from app.services.utilizador_service import UtilizadorService

SESSAO_FIREBASE_FAKE = {"idToken": "tok", "refreshToken": "refresh", "expiresIn": "3600"}


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _mockar_criacao_de_conta_firebase(monkeypatch):
    monkeypatch.setattr(
        firebase_rest, "criar_conta_com_password", lambda email, password: SESSAO_FIREBASE_FAKE
    )


def test_criar_gestor(monkeypatch):
    _mockar_criacao_de_conta_firebase(monkeypatch)
    engine = _criar_engine_teste()
    with Session(engine) as session:
        sessao = UtilizadorService(session).criar_gestor("gestor@isaf.co.ao", "palavra-passe", "900000000")

    assert sessao.utilizador.perfil == PerfilUtilizador.GESTOR
    assert sessao.utilizador.professor_id is None
    assert sessao.id_token == "tok"
    assert sessao.refresh_token == "refresh"


def test_criar_gestor_com_email_duplicado_levanta_integridade(monkeypatch):
    _mockar_criacao_de_conta_firebase(monkeypatch)
    engine = _criar_engine_teste()
    with Session(engine) as session:
        service = UtilizadorService(session)
        service.criar_gestor("gestor@isaf.co.ao", "palavra-passe", "900000000")
        with pytest.raises(IntegridadeVioladaError):
            service.criar_gestor("gestor@isaf.co.ao", "outra-palavra-passe", "900000001")


def test_registar_professor_com_email_correspondente_a_professor(monkeypatch):
    _mockar_criacao_de_conta_firebase(monkeypatch)
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True)
        session.add(professor)
        session.commit()
        session.refresh(professor)
        professor_id_esperado = professor.id

        sessao = UtilizadorService(session).registar_professor("prof@isaf.co.ao", "palavra-passe", "900000002")

    assert sessao.utilizador.perfil == PerfilUtilizador.PROFESSOR
    assert sessao.utilizador.professor_id == professor_id_esperado
    assert sessao.id_token == "tok"


def test_registar_professor_sem_correspondencia_levanta_acesso_negado(monkeypatch):
    """RN10 — email não corresponde a nenhum Professor registado pelo Gestor.

    Não deve sequer tentar criar a conta Firebase — validação acontece antes.
    """
    chamou_firebase = []
    monkeypatch.setattr(
        firebase_rest,
        "criar_conta_com_password",
        lambda email, password: chamou_firebase.append(email) or SESSAO_FIREBASE_FAKE,
    )
    engine = _criar_engine_teste()
    with Session(engine) as session:
        with pytest.raises(AcessoNegadoError):
            UtilizadorService(session).registar_professor("desconhecido@isaf.co.ao", "palavra-passe", "900000003")

    assert chamou_firebase == []
