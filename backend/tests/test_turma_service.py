# Implementa: RF02 (UC02) — Turma enriquecida com curso + ano curricular (ver app/services/turma_service.py)
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.models.curso import Curso
from app.models.plano_curricular import PlanoCurricular
from app.models.turma import Turma
from app.services.turma_service import listar_turmas_detalhadas


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def test_listar_turmas_detalhadas_resolve_curso_e_ano_curricular():
    """Bug real reportado: o frontend confundia ano_letivo (ano civil, ex: 2026)
    com o ano curricular (1..4, PlanoCurricular.ano). Este endpoint devolve os
    dois campos já resolvidos e distintos, para o frontend nunca ter de escolher
    o errado nem fazer a junção Turma -> PlanoCurricular -> Curso por conta própria."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        curso = Curso(codigo="IGF", nome="Informática de Gestão Financeira")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        plano = PlanoCurricular(curso_id=curso.id, ano=3, semestre="1")
        session.add(plano)
        session.commit()
        session.refresh(plano)

        turma = Turma(
            codigo="IGF3S1-T1",
            nome="IGF 3º Ano T1",
            ano_letivo=2026,
            turno="tarde",
            numero_alunos=30,
            plano_curricular_id=plano.id,
        )
        session.add(turma)
        session.commit()

    with Session(engine) as session:
        resultado = listar_turmas_detalhadas(session)

    assert len(resultado) == 1
    detalhe = resultado[0]
    assert detalhe.curso_codigo == "IGF"
    assert detalhe.curso_nome == "Informática de Gestão Financeira"
    assert detalhe.ano_curricular == 3
    assert detalhe.ano_letivo == 2026
    assert detalhe.ano_curricular != detalhe.ano_letivo


def test_listar_turmas_detalhadas_com_plano_ou_curso_em_falta_nao_rebenta():
    """Defesa contra dados inconsistentes (ex: plano_curricular_id órfão) — nunca
    deixar a listagem inteira falhar por uma turma com referência quebrada."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        turma = Turma(
            codigo="ORFA",
            nome="Turma órfã",
            ano_letivo=2026,
            turno="noite",
            numero_alunos=20,
            plano_curricular_id=999,
        )
        session.add(turma)
        session.commit()

    with Session(engine) as session:
        resultado = listar_turmas_detalhadas(session)

    assert len(resultado) == 1
    assert resultado[0].curso_codigo == "?"
    assert resultado[0].ano_curricular == 0
