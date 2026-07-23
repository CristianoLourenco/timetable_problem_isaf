# Implementa: Fase 5 (RF11, RF12) — consulta de horário estruturada por dia/tempo
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
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

        plano = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
        session.add(plano)
        session.commit()
        session.refresh(plano)

        turma = Turma(
            codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, plano_curricular_id=plano.id
        )
        professor = Professor(nome="Prof A", email="profa@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disciplina = Disciplina(codigo="MAT", nome="Matemática")
        sala = Sala(codigo="S1", nome="Sala 1", capacidade=30)
        session.add_all([turma, professor, disciplina, sala])
        session.commit()
        session.refresh(turma)
        session.refresh(professor)
        session.refresh(disciplina)

        session.add(
            PlanoCurricularDisciplina(plano_curricular_id=plano.id, disciplina_id=disciplina.id, carga_horaria_semanal=2)
        )
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()

        job_id = JobRepository(session).criar(ano_letivo=2026, semestre="1").id
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
    # RF13 — a UI precisa do id da Alocacao para poder mover/remover a partir da grade.
    assert all(isinstance(t.alocacao_id, int) for t in tempos)
    assert len({t.alocacao_id for t in tempos}) == len(tempos)  # um id distinto por tempo


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


def test_horario_professor_escopado_nao_ignora_job_mais_recente_de_outro_semestre():
    """Bug real (2026-07-24): consultar_horario_professor usava sempre o Job DONE
    mais recente entre TODOS os âmbitos. Um professor que só lecione no 1º
    semestre passava a ter horário vazio assim que o 2º semestre fosse gerado
    depois — mesmo com alocações reais na BD para o 1º semestre. Passando
    (ano_letivo, semestre) explícitos (filtro de âmbito da UI), a busca deve
    escopar ao Job DONE desse âmbito exato, igual ao já feito para turma."""
    engine = _criar_engine_teste()
    turma_id, professor_id = _semear_e_gerar(engine)  # gera o Job do 1º semestre

    with Session(engine) as session:
        curso2 = Curso(codigo="CF", nome="Contabilidade")
        session.add(curso2)
        session.commit()
        session.refresh(curso2)
        plano2 = PlanoCurricular(curso_id=curso2.id, ano=1, semestre="2")
        session.add(plano2)
        session.commit()
        session.refresh(plano2)
        turma2 = Turma(
            codigo="T2", nome="Turma 2", ano_letivo=2026, turno="manha", numero_alunos=20, plano_curricular_id=plano2.id
        )
        professor2 = Professor(nome="Prof B", email="profb@isaf.co.ao", classificacao=5, vinculo_casa=True)
        disciplina2 = Disciplina(codigo="CTB", nome="Contabilidade")
        sala2 = Sala(codigo="S2", nome="Sala 2", capacidade=30)
        session.add_all([turma2, professor2, disciplina2, sala2])
        session.commit()
        session.refresh(turma2)
        session.refresh(professor2)
        session.refresh(disciplina2)
        session.add(
            PlanoCurricularDisciplina(
                plano_curricular_id=plano2.id, disciplina_id=disciplina2.id, carga_horaria_semanal=2
            )
        )
        session.add(ProfessorDisciplina(professor_id=professor2.id, disciplina_id=disciplina2.id))
        session.commit()
        job2_id = JobRepository(session).criar(ano_letivo=2026, semestre="2").id

    executar(job2_id, engine=engine)  # Job DONE mais recente agora é o do 2º semestre

    with Session(engine) as session:
        sem_escopo = HorarioService(session).consultar_horario_professor(professor_id)
        com_escopo = HorarioService(session).consultar_horario_professor(professor_id, ano_letivo=2026, semestre="1")

    assert not any(t for d in sem_escopo.dias for t in d.tempos)  # bug: vazio sem o escopo
    assert any(t for d in com_escopo.dias for t in d.tempos)  # corrigido: encontra o horário do 1º semestre


def test_sem_job_concluido_devolve_none_em_vez_de_erro():
    """"Ainda não gerado" é um estado normal da UI (ex: filtro de ano/semestre
    sem horário), não um erro — turma existente sem Job DONE devolve None (200
    na API), nunca EntidadeNaoEncontradaError (404). Turma inexistente continua
    a levantar erro (ver test_turma_inexistente_levanta_erro_404)."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        curso = Curso(codigo="INF", nome="Informática")
        session.add(curso)
        session.commit()
        session.refresh(curso)
        plano = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
        session.add(plano)
        session.commit()
        session.refresh(plano)
        turma = Turma(
            codigo="T1", nome="Turma 1", ano_letivo=2026, turno="manha", numero_alunos=20, plano_curricular_id=plano.id
        )
        session.add(turma)
        session.commit()
        session.refresh(turma)

        assert HorarioService(session).consultar_horario_turma(turma.id) is None
