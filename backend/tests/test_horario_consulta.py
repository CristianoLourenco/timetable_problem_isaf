# Implementa: Fase 5 (RF11, RF12) — consulta de horário estruturada por dia/tempo
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.models.turma_disciplina import TurmaDisciplina
from app.repositories.job_repository import JobRepository
from app.services.horario_service import HorarioService
from app.workers.job_runner import executar


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _semear_e_gerar(engine) -> tuple[int, int]:
    """Semeia um cenário viável e corre o job_runner — devolve (turma_id, professor_id)."""
    with Session(engine) as session:
        curso = Curso(codigo="INF", nome="Informática")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        turma = Turma(codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, curso_id=curso.id)
        professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disciplina = Disciplina(codigo="MAT", nome="Matemática")
        sala = Sala(codigo="S1", nome="Sala 1", capacidade=30)
        session.add_all([turma, professor, disciplina, sala])
        session.commit()
        session.refresh(turma)
        session.refresh(professor)
        session.refresh(disciplina)

        session.add(TurmaDisciplina(turma_id=turma.id, disciplina_id=disciplina.id, carga_horaria_semanal=2))
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()

        job_id = JobRepository(session).criar().id
        turma_id, professor_id = turma.id, professor.id

    executar(job_id, engine=engine)
    return turma_id, professor_id


def test_consultar_horario_por_turma_estruturado_por_dia_e_tempo():
    engine = _criar_engine_teste()
    turma_id, _ = _semear_e_gerar(engine)

    with Session(engine) as session:
        resposta = HorarioService(session).consultar_horario_turma(turma_id)

    assert [d.dia_semana for d in resposta.dias] == ["segunda", "terca", "quarta", "quinta", "sexta"]

    dias_com_aula = [d for d in resposta.dias if d.tempos]
    assert len(dias_com_aula) == 1  # bloco de 2 tempos cabe todo no mesmo dia (RN06)

    tempos = dias_com_aula[0].tempos
    assert len(tempos) == 2
    assert all(t.turno == "manha" for t in tempos)
    assert [t.periodo for t in tempos] == sorted(t.periodo for t in tempos)
    assert tempos[0].turma_nome == "Turma 1"
    assert tempos[0].disciplina_nome == "Matemática"
    assert tempos[0].professor_nome == "Prof A"
    assert tempos[0].sala_nome == "Sala 1"


def test_consultar_horario_por_professor_espelha_a_mesma_alocacao():
    engine = _criar_engine_teste()
    turma_id, professor_id = _semear_e_gerar(engine)

    with Session(engine) as session:
        horario_turma = HorarioService(session).consultar_horario_turma(turma_id)
        horario_professor = HorarioService(session).consultar_horario_professor(professor_id)

    def tempos_de(horario):
        return {(t.dia_semana, t.turno, t.periodo) for d in horario.dias for t in d.tempos}

    assert tempos_de(horario_turma) == tempos_de(horario_professor)


def test_turma_inexistente_levanta_erro_404():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        with pytest.raises(EntidadeNaoEncontradaError):
            HorarioService(session).consultar_horario_turma(999)


def test_sem_job_concluido_levanta_erro_404():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        curso = Curso(codigo="INF", nome="Informática")
        session.add(curso)
        session.commit()
        session.refresh(curso)
        turma = Turma(codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, curso_id=curso.id)
        session.add(turma)
        session.commit()
        session.refresh(turma)

        with pytest.raises(EntidadeNaoEncontradaError):
            HorarioService(session).consultar_horario_turma(turma.id)
