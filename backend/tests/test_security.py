# Implementa: Fase 6 (RN09, RN10, RN11) — resolução de papel e verificação de token
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core import security
from app.core.config import settings
from app.core.exceptions import AcessoNegadoError, TokenInvalidoError
from app.models.utilizador import PerfilUtilizador, Utilizador


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def test_superadmin_bootstrap_nao_precisa_de_registo(monkeypatch):
    monkeypatch.setattr(settings, "superadmin_emails", ["admin@isaf.co.ao"])
    engine = _criar_engine_teste()
    with Session(engine) as session:
        user = security.get_current_user(session=session, email="admin@isaf.co.ao")

    assert user.papel == security.Papel.SUPERADMIN
    assert user.professor_id is None


def test_gestor_registado_resolve_papel_gestor(monkeypatch):
    monkeypatch.setattr(settings, "superadmin_emails", [])
    engine = _criar_engine_teste()
    with Session(engine) as session:
        session.add(Utilizador(email="gestor@isaf.co.ao", contacto_telefonico="900000000", perfil=PerfilUtilizador.GESTOR))
        session.commit()

        user = security.get_current_user(session=session, email="gestor@isaf.co.ao")

    assert user.papel == security.Papel.GESTOR


def test_professor_registado_resolve_papel_professor_com_id(monkeypatch):
    monkeypatch.setattr(settings, "superadmin_emails", [])
    engine = _criar_engine_teste()
    with Session(engine) as session:
        session.add(
            Utilizador(
                email="prof@isaf.co.ao", contacto_telefonico="900000001", perfil=PerfilUtilizador.PROFESSOR, professor_id=7
            )
        )
        session.commit()

        user = security.get_current_user(session=session, email="prof@isaf.co.ao")

    assert user.papel == security.Papel.PROFESSOR
    assert user.professor_id == 7


def test_email_sem_registo_levanta_acesso_negado(monkeypatch):
    monkeypatch.setattr(settings, "superadmin_emails", [])
    engine = _criar_engine_teste()
    with Session(engine) as session:
        with pytest.raises(AcessoNegadoError):
            security.get_current_user(session=session, email="desconhecido@isaf.co.ao")


def test_require_gestor_bloqueia_professor():
    professor = security.UtilizadorAutenticado(email="prof@isaf.co.ao", papel=security.Papel.PROFESSOR, professor_id=1)
    with pytest.raises(AcessoNegadoError):
        security.require_gestor(professor)


def test_require_gestor_permite_superadmin_e_gestor():
    superadmin = security.UtilizadorAutenticado(email="admin@isaf.co.ao", papel=security.Papel.SUPERADMIN)
    gestor = security.UtilizadorAutenticado(email="gestor@isaf.co.ao", papel=security.Papel.GESTOR)
    assert security.require_gestor(superadmin) is superadmin
    assert security.require_gestor(gestor) is gestor


def test_professor_so_acede_aos_seus_proprios_dados():
    professor = security.UtilizadorAutenticado(email="prof@isaf.co.ao", papel=security.Papel.PROFESSOR, professor_id=1)
    security.verificar_acesso_professor_proprio(professor, 1)  # não levanta

    with pytest.raises(AcessoNegadoError):
        security.verificar_acesso_professor_proprio(professor, 2)


def test_gestor_acede_a_qualquer_professor():
    gestor = security.UtilizadorAutenticado(email="gestor@isaf.co.ao", papel=security.Papel.GESTOR)
    security.verificar_acesso_professor_proprio(gestor, 999)  # não levanta


def test_verificar_id_token_invalido_levanta_token_invalido(monkeypatch):
    def _falha(*args, **kwargs):
        raise ValueError("assinatura inválida")

    monkeypatch.setattr(security.id_token, "verify_firebase_token", _falha)
    with pytest.raises(TokenInvalidoError):
        security.verificar_id_token("token-qualquer")


def test_verificar_id_token_valido_devolve_email(monkeypatch):
    monkeypatch.setattr(
        security.id_token, "verify_firebase_token", lambda *args, **kwargs: {"email": "user@isaf.co.ao"}
    )
    assert security.verificar_id_token("token-qualquer") == "user@isaf.co.ao"
