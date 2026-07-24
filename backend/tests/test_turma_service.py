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


def test_listar_turmas_detalhadas_filtra_por_ano_letivo_e_semestre():
    """RF09 — o ecrã de Horário não deve receber turmas de um âmbito diferente
    do selecionado (bug real: turmas de ambos os semestres apareciam juntas no
    mesmo seletor, fazendo parecer que turmas "ficavam sem horário" quando na
    verdade pertenciam a um âmbito para o qual nenhum Job tinha sido gerado)."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        curso = Curso(codigo="IGF", nome="Informática de Gestão Financeira")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        plano_sem1 = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
        plano_sem2 = PlanoCurricular(curso_id=curso.id, ano=1, semestre="2")
        plano_anual = PlanoCurricular(curso_id=curso.id, ano=2, semestre="Anual")
        session.add_all([plano_sem1, plano_sem2, plano_anual])
        session.commit()
        session.refresh(plano_sem1)
        session.refresh(plano_sem2)
        session.refresh(plano_anual)

        session.add_all([
            Turma(codigo="T-SEM1", nome="T Sem1", ano_letivo=2026, turno="tarde", numero_alunos=20, plano_curricular_id=plano_sem1.id),
            Turma(codigo="T-SEM2", nome="T Sem2", ano_letivo=2026, turno="tarde", numero_alunos=20, plano_curricular_id=plano_sem2.id),
            Turma(codigo="T-ANUAL", nome="T Anual", ano_letivo=2026, turno="tarde", numero_alunos=20, plano_curricular_id=plano_anual.id),
            Turma(codigo="T-OUTRO-ANO", nome="T Outro Ano", ano_letivo=2025, turno="tarde", numero_alunos=20, plano_curricular_id=plano_sem1.id),
        ])
        session.commit()

    with Session(engine) as session:
        resultado = listar_turmas_detalhadas(session, ano_letivo=2026, semestre="1")

    codigos = sorted(t.codigo for t in resultado)
    assert codigos == ["T-ANUAL", "T-SEM1"]


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
