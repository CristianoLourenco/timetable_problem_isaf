# Implementa: RF05/RN07 — testes de geração de disponibilidade sintética,
# ver app/services/disponibilidade_geracao_service.py.
from sqlmodel import Session, SQLModel, create_engine, select

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.disponibilidade import Disponibilidade
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.turma import Turma
from app.services.disponibilidade_geracao_service import gerar_disponibilidade_sintetica


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _turma_para_disciplina(session: Session, disciplina: Disciplina, turno: str, codigo: str) -> None:
    """Cria curso+plano+turma+grade curricular mínimos para que `disciplina`
    "decorra" no `turno` dado — sinal real que a geração sintética consulta."""
    curso = Curso(codigo=f"C{codigo}", nome=f"Curso {codigo}")
    session.add(curso)
    session.commit()
    session.refresh(curso)

    plano = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
    session.add(plano)
    session.commit()
    session.refresh(plano)

    session.add(PlanoCurricularDisciplina(plano_curricular_id=plano.id, disciplina_id=disciplina.id, carga_horaria_semanal=2))
    session.add(Turma(codigo=codigo, nome=f"Turma {codigo}", ano_letivo=2026, turno=turno, numero_alunos=25, plano_curricular_id=plano.id))
    session.commit()


def test_gera_disponibilidade_so_no_turno_das_disciplinas_qualificadas_visitante():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Bruno Silva", email="bruno@isaf.co.ao", classificacao=3, vinculo_casa=False)
        disciplina = Disciplina(codigo="ALG", nome="Algoritmos")
        session.add(professor)
        session.add(disciplina)
        session.commit()
        session.refresh(professor)
        session.refresh(disciplina)

        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()
        _turma_para_disciplina(session, disciplina, "tarde", "T1")

        semeados = gerar_disponibilidade_sintetica(session)

        assert semeados == 1
        linhas = list(session.exec(select(Disponibilidade).where(Disponibilidade.professor_id == professor.id)))
        assert len(linhas) > 0
        assert all(linha.turno == "tarde" for linha in linhas)
        assert all(linha.gerada_automaticamente is True for linha in linhas)
        assert len({linha.dia_semana for linha in linhas}) == 2


def test_gera_disponibilidade_em_todos_os_turnos_para_professor_de_casa():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Ana Costa", email="ana@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disc_manha = Disciplina(codigo="POO", nome="Programação Orientada a Objectos")
        disc_noite = Disciplina(codigo="BD", nome="Bases de Dados")
        session.add(professor)
        session.add(disc_manha)
        session.add(disc_noite)
        session.commit()
        session.refresh(professor)
        session.refresh(disc_manha)
        session.refresh(disc_noite)

        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disc_manha.id))
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disc_noite.id))
        session.commit()
        _turma_para_disciplina(session, disc_manha, "manha", "T1")
        _turma_para_disciplina(session, disc_noite, "noite", "T2")

        semeados = gerar_disponibilidade_sintetica(session)

        assert semeados == 1
        linhas = list(session.exec(select(Disponibilidade).where(Disponibilidade.professor_id == professor.id)))
        turnos_cobertos = {linha.turno for linha in linhas}
        assert turnos_cobertos == {"manha", "noite"}
        assert len({linha.dia_semana for linha in linhas}) == 4


def test_professor_sem_qualificacoes_nao_gera_nenhuma_linha():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Carlos Neto", email="carlos@isaf.co.ao", classificacao=3, vinculo_casa=False)
        session.add(professor)
        session.commit()

        semeados = gerar_disponibilidade_sintetica(session)

        assert semeados == 0
        linhas = list(session.exec(select(Disponibilidade)))
        assert linhas == []


def test_idempotente_segunda_chamada_nao_gera_linhas_extra():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Bruno Silva", email="bruno@isaf.co.ao", classificacao=3, vinculo_casa=False)
        disciplina = Disciplina(codigo="ALG", nome="Algoritmos")
        session.add(professor)
        session.add(disciplina)
        session.commit()
        session.refresh(professor)
        session.refresh(disciplina)
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()
        _turma_para_disciplina(session, disciplina, "tarde", "T1")

        primeira = gerar_disponibilidade_sintetica(session)
        linhas_apos_primeira = list(session.exec(select(Disponibilidade)))

        segunda = gerar_disponibilidade_sintetica(session)
        linhas_apos_segunda = list(session.exec(select(Disponibilidade)))

        assert primeira == 1
        assert segunda == 0
        assert len(linhas_apos_primeira) == len(linhas_apos_segunda)


def test_nunca_sobrescreve_disponibilidade_real_ja_registada():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        professor = Professor(nome="Bruno Silva", email="bruno@isaf.co.ao", classificacao=3, vinculo_casa=False)
        disciplina = Disciplina(codigo="ALG", nome="Algoritmos")
        session.add(professor)
        session.add(disciplina)
        session.commit()
        session.refresh(professor)
        session.refresh(disciplina)
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()
        _turma_para_disciplina(session, disciplina, "tarde", "T1")

        # Disponibilidade real (RF05), não gerada automaticamente
        session.add(
            Disponibilidade(
                professor_id=professor.id,
                dia_semana="segunda",
                turno="manha",
                periodo=1,
                gerada_automaticamente=False,
            )
        )
        session.commit()

        semeados = gerar_disponibilidade_sintetica(session)

        assert semeados == 0
        linhas = list(session.exec(select(Disponibilidade).where(Disponibilidade.professor_id == professor.id)))
        assert len(linhas) == 1
        assert linhas[0].gerada_automaticamente is False
        assert linhas[0].turno == "manha"  # não foi tocada/substituída
