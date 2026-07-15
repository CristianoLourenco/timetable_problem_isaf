# Implementa: Fase 6 (RN10) — registo de Gestor (Superadmin) e auto-registo de Professor
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core.exceptions import AcessoNegadoError, IntegridadeVioladaError
from app.models.professor import Professor
from app.models.utilizador import PerfilUtilizador
from app.services.utilizador_service import UtilizadorService


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def test_criar_gestor():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        utilizador = UtilizadorService(session).criar_gestor("gestor@isaf.co.ao", "900000000")

    assert utilizador.perfil == PerfilUtilizador.GESTOR
    assert utilizador.professor_id is None


def test_criar_gestor_com_email_duplicado_levanta_integridade():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        service = UtilizadorService(session)
        service.criar_gestor("gestor@isaf.co.ao", "900000000")
        with pytest.raises(IntegridadeVioladaError):
            service.criar_gestor("gestor@isaf.co.ao", "900000001")


def test_registar_professor_com_email_correspondente_a_professor():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Prof A", email="prof@isaf.co.ao", classificacao=5, vinculo_casa=True)
        session.add(professor)
        session.commit()
        session.refresh(professor)
        professor_id_esperado = professor.id

        utilizador = UtilizadorService(session).registar_professor("prof@isaf.co.ao", "900000002")

    assert utilizador.perfil == PerfilUtilizador.PROFESSOR
    assert utilizador.professor_id == professor_id_esperado


def test_registar_professor_sem_correspondencia_levanta_acesso_negado():
    """RN10 — email não corresponde a nenhum Professor registado pelo Gestor."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        with pytest.raises(AcessoNegadoError):
            UtilizadorService(session).registar_professor("desconhecido@isaf.co.ao", "900000003")
