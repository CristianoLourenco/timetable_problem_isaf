# Implementa: Fase 4 (RF09, RF10, RF13) — fluxo assíncrono ponta-a-ponta com BD em memória
from datetime import datetime

from sqlmodel import Session, SQLModel, create_engine, select

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.job import JobStatus
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.job_repository import JobRepository
from app.repositories.pendencia_repository import PendenciaRepository
from app.services.horario_service import extrair_dados
from app.workers.job_runner import executar


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _semear_plano_curricular(session: Session) -> PlanoCurricular:
    curso = Curso(codigo="INF", nome="Informática")
    session.add(curso)
    session.commit()
    session.refresh(curso)

    plano = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
    session.add(plano)
    session.commit()
    session.refresh(plano)
    return plano


def _semear_cenario_viavel(session: Session) -> None:
    plano = _semear_plano_curricular(session)

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
    session.refresh(sala)

    session.add(
        PlanoCurricularDisciplina(plano_curricular_id=plano.id, disciplina_id=disciplina.id, carga_horaria_semanal=2)
    )
    session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
    session.commit()


def test_job_runner_gera_alocacoes_para_cenario_viavel():
    engine = _criar_engine_teste()

    with Session(engine) as session:
        _semear_cenario_viavel(session)
        job_id = JobRepository(session).criar(ano_letivo=2026, semestre="1").id

    executar(job_id, engine=engine)

    with Session(engine) as session:
        job = JobRepository(session).obter(job_id)
        assert job.status == JobStatus.DONE
        assert job.diagnostico is None
        assert job.concluido_em is not None

        alocacoes = AlocacaoRepository(session).listar_por_job(job_id)
        assert len(alocacoes) == 2


def test_extrair_dados_ignora_turmas_de_outro_ano_letivo_ou_semestre():
    """Uma geração para (2026, "1") nunca deve puxar turmas de outro ano lectivo ou
    semestre — cada Job cobre sempre um único âmbito, gerado de uma só vez."""
    engine = _criar_engine_teste()

    with Session(engine) as session:
        curso = Curso(codigo="INF", nome="Informática")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        plano_alvo = PlanoCurricular(curso_id=curso.id, ano=1, semestre="1")
        plano_outro_semestre = PlanoCurricular(curso_id=curso.id, ano=1, semestre="2")
        plano_anual = PlanoCurricular(curso_id=curso.id, ano=2, semestre="Anual")
        session.add_all([plano_alvo, plano_outro_semestre, plano_anual])
        session.commit()
        for p in (plano_alvo, plano_outro_semestre, plano_anual):
            session.refresh(p)

        turma_alvo = Turma(
            codigo="ALVO", nome="Turma alvo", ano_letivo=2026, turno="manha",
            numero_alunos=20, plano_curricular_id=plano_alvo.id,
        )
        turma_ano_passado = Turma(
            codigo="PASSADO", nome="Turma do ano passado", ano_letivo=2025, turno="manha",
            numero_alunos=20, plano_curricular_id=plano_alvo.id,
        )
        turma_outro_semestre = Turma(
            codigo="OUTRO-SEM", nome="Turma de outro semestre", ano_letivo=2026, turno="manha",
            numero_alunos=20, plano_curricular_id=plano_outro_semestre.id,
        )
        turma_anual = Turma(
            codigo="ANUAL", nome="Turma anual", ano_letivo=2026, turno="manha",
            numero_alunos=20, plano_curricular_id=plano_anual.id,
        )
        session.add_all([turma_alvo, turma_ano_passado, turma_outro_semestre, turma_anual])
        session.commit()

        dados = extrair_dados(session, ano_letivo=2026, semestre="1")
        codigos = {t.id for t in dados.turmas}
        session.refresh(turma_alvo)
        session.refresh(turma_anual)
        session.refresh(turma_ano_passado)
        session.refresh(turma_outro_semestre)

        assert turma_alvo.id in codigos
        assert turma_anual.id in codigos  # "Anual" entra em ambos os semestres
        assert turma_ano_passado.id not in codigos
        assert turma_outro_semestre.id not in codigos


def test_consultar_horario_turma_usa_o_job_do_ano_letivo_da_propria_turma():
    """Gerar (2026, "2") depois de (2026, "1") não pode fazer uma turma de "1"
    passar a devolver (incorretamente) o horário mais recente de "2"."""
    engine = _criar_engine_teste()

    with Session(engine) as session:
        _semear_cenario_viavel(session)
        turma_id = session.exec(select(Turma)).first().id
        job_sem1_id = JobRepository(session).criar(ano_letivo=2026, semestre="1").id

    executar(job_sem1_id, engine=engine)

    with Session(engine) as session:
        # Uma segunda geração, para um semestre diferente, sem nenhuma turma —
        # simula "o Job mais recente" pertencer a outro âmbito.
        job_sem2 = JobRepository(session).criar(ano_letivo=2026, semestre="2")
        JobRepository(session).atualizar_status(job_sem2, JobStatus.DONE, concluido_em=datetime.utcnow())

    with Session(engine) as session:
        from app.services.horario_service import HorarioService

        resposta = HorarioService(session).consultar_horario_turma(turma_id)
        dias_com_aula = [d for d in resposta.dias if d.tempos]
        assert len(dias_com_aula) == 1
        assert resposta.job_id == job_sem1_id


def test_job_runner_respeita_tempo_maximo_escolhido_pelo_gestor():
    """RF09 — o Gestor escolhe 1/5/10 min por pedido; job_runner deve passar esse
    valor ao solver em vez do teto fixo de settings."""
    engine = _criar_engine_teste()

    with Session(engine) as session:
        _semear_cenario_viavel(session)
        job = JobRepository(session).criar(ano_letivo=2026, semestre="1", tempo_maximo_minutos=1)
        job_id = job.id
        assert job.tempo_maximo_minutos == 1

    executar(job_id, engine=engine)

    with Session(engine) as session:
        job = JobRepository(session).obter(job_id)
        assert job.status == JobStatus.DONE


def test_job_runner_conclui_com_pendencia_quando_rn06_e_impossivel():
    """RF13 — RN06 proíbe carga_horaria_semanal=1 (tempo isolado), mas RN05 agora
    aceita défice (ver app/solver/constraints_hard.py): o Job termina DONE, sem
    nenhuma alocação para esta disciplina, em vez de INFEASIBLE. A pendência fica
    persistida em Pendencia (RF13/sub-projeto alocação manual) para o Gestor
    resolver depois."""
    engine = _criar_engine_teste()

    with Session(engine) as session:
        plano = _semear_plano_curricular(session)

        turma = Turma(
            codigo="T1",
            nome="Turma 1",
            ano_letivo=2026,
            turno="manha",
            numero_alunos=20,
            plano_curricular_id=plano.id,
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
            PlanoCurricularDisciplina(
                plano_curricular_id=plano.id, disciplina_id=disciplina.id, carga_horaria_semanal=1
            )
        )
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()

        turma_id = turma.id
        disciplina_id = disciplina.id
        job_id = JobRepository(session).criar(ano_letivo=2026, semestre="1").id

    executar(job_id, engine=engine)

    with Session(engine) as session:
        job = JobRepository(session).obter(job_id)
        assert job.status == JobStatus.DONE
        assert job.diagnostico is None
        assert AlocacaoRepository(session).listar_por_job(job_id) == []

        pendencias = PendenciaRepository(session).listar_por_job(job_id)
        assert len(pendencias) == 1
        assert pendencias[0].turma_id == turma_id
        assert pendencias[0].disciplina_id == disciplina_id
        assert pendencias[0].tempos_em_falta == 1
