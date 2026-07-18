# Implementa: RF13 (UC09) — testes de app/services/alocacao_manual_service.py
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.core.exceptions import EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.job import Job
from app.models.plano_curricular import PlanoCurricular
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.pendencia_repository import PendenciaRepository
from app.services.alocacao_manual_service import AlocacaoManualService


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _semear_cenario(session: Session, *, qualificar_professor: bool = True):
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
    session.refresh(sala)

    if qualificar_professor:
        session.add(ProfessorDisciplina(professor_id=professor.id, disciplina_id=disciplina.id))
        session.commit()

    job = Job(ano_letivo=2026, semestre="1")
    session.add(job)
    session.commit()
    session.refresh(job)

    return job, turma, professor, disciplina, sala


def test_criar_alocacao_manual_bloco_valido():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)
        service = AlocacaoManualService(session)

        alocacoes = service.criar(
            job_id=job.id,
            turma_id=turma.id,
            disciplina_id=disciplina.id,
            professor_id=professor.id,
            sala_id=sala.id,
            dia_semana="segunda",
            turno="manha",
            periodos=[1, 2],
        )

        assert len(alocacoes) == 2
        assert {a.periodo for a in alocacoes} == {1, 2}
        assert all(a.professor_id == professor.id for a in alocacoes)

        persistidas = AlocacaoRepository(session).listar_por_job(job.id)
        assert len(persistidas) == 2


def test_criar_alocacao_manual_bloco_de_um_tempo_e_rejeitado():
    """RN06 — bloco tem de ter pelo menos 2 tempos contíguos."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)
        service = AlocacaoManualService(session)

        try:
            service.criar(
                job_id=job.id,
                turma_id=turma.id,
                disciplina_id=disciplina.id,
                professor_id=professor.id,
                sala_id=sala.id,
                dia_semana="segunda",
                turno="manha",
                periodos=[1],
            )
            assert False, "devia ter lançado IntegridadeVioladaError"
        except IntegridadeVioladaError as exc:
            assert "RN06" in str(exc) or "bloco" in str(exc).lower()


def test_criar_alocacao_manual_periodos_nao_contiguos_e_rejeitado():
    """RN06 — periodos têm de ser contíguos, não só >=2 no total."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)
        service = AlocacaoManualService(session)

        try:
            service.criar(
                job_id=job.id,
                turma_id=turma.id,
                disciplina_id=disciplina.id,
                professor_id=professor.id,
                sala_id=sala.id,
                dia_semana="segunda",
                turno="manha",
                periodos=[1, 3],
            )
            assert False, "devia ter lançado IntegridadeVioladaError"
        except IntegridadeVioladaError as exc:
            assert "contíguo" in str(exc).lower() or "contiguo" in str(exc).lower()


def test_criar_alocacao_manual_professor_nao_qualificado_e_rejeitado():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session, qualificar_professor=False)
        service = AlocacaoManualService(session)

        try:
            service.criar(
                job_id=job.id,
                turma_id=turma.id,
                disciplina_id=disciplina.id,
                professor_id=professor.id,
                sala_id=sala.id,
                dia_semana="segunda",
                turno="manha",
                periodos=[1, 2],
            )
            assert False, "devia ter lançado IntegridadeVioladaError"
        except IntegridadeVioladaError as exc:
            assert "qualificado" in str(exc).lower()


def test_criar_alocacao_manual_professor_ja_ocupado_e_rejeitado():
    """RN01 — professor sem dupla alocação no mesmo tempo."""
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)
        service = AlocacaoManualService(session)

        service.criar(
            job_id=job.id,
            turma_id=turma.id,
            disciplina_id=disciplina.id,
            professor_id=professor.id,
            sala_id=sala.id,
            dia_semana="segunda",
            turno="manha",
            periodos=[1, 2],
        )

        outra_turma = Turma(
            codigo="T2",
            nome="Turma 2",
            ano_letivo=2026,
            turno="manha",
            numero_alunos=20,
            plano_curricular_id=turma.plano_curricular_id,
        )
        session.add(outra_turma)
        session.commit()
        session.refresh(outra_turma)

        try:
            service.criar(
                job_id=job.id,
                turma_id=outra_turma.id,
                disciplina_id=disciplina.id,
                professor_id=professor.id,
                sala_id=sala.id,
                dia_semana="segunda",
                turno="manha",
                periodos=[2, 3],  # periodo 2 colide com a alocação anterior
            )
            assert False, "devia ter lançado IntegridadeVioladaError"
        except IntegridadeVioladaError as exc:
            assert "RN01" in str(exc) or "professor" in str(exc).lower()


def test_criar_alocacao_manual_reduz_pendencia_existente():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)
        PendenciaRepository(session).criar_em_lote(
            job.id,
            [
                {
                    "turma_id": turma.id,
                    "disciplina_id": disciplina.id,
                    "tempos_em_falta": 2,
                    "razao": "sem professor",
                    "professores_conflitantes": (),
                    "turmas_conflitantes": (),
                }
            ],
        )

        service = AlocacaoManualService(session)
        service.criar(
            job_id=job.id,
            turma_id=turma.id,
            disciplina_id=disciplina.id,
            professor_id=professor.id,
            sala_id=sala.id,
            dia_semana="segunda",
            turno="manha",
            periodos=[1, 2],
        )

        pendencias = PendenciaRepository(session).listar_por_job_e_turma(job.id, turma.id)
        assert pendencias == []


def test_criar_alocacao_manual_turma_inexistente_e_404():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)
        service = AlocacaoManualService(session)

        try:
            service.criar(
                job_id=job.id,
                turma_id=999,
                disciplina_id=disciplina.id,
                professor_id=professor.id,
                sala_id=sala.id,
                dia_semana="segunda",
                turno="manha",
                periodos=[1, 2],
            )
            assert False, "devia ter lançado EntidadeNaoEncontradaError"
        except EntidadeNaoEncontradaError:
            pass


def test_listar_professores_qualificados():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)

        outro_professor = Professor(nome="Prof B", email="profb@isaf.co.ao", classificacao=3, vinculo_casa=False)
        session.add(outro_professor)
        session.commit()
        session.refresh(outro_professor)
        # outro_professor não tem ProfessorDisciplina para esta disciplina

        service = AlocacaoManualService(session)
        qualificados = service.listar_professores_qualificados(disciplina.id)

        assert {p.id for p in qualificados} == {professor.id}


def test_listar_slots_vagos_exclui_periodos_ja_alocados_e_so_devolve_blocos_validos():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        job, turma, professor, disciplina, sala = _semear_cenario(session)

        service = AlocacaoManualService(session)
        service.criar(
            job_id=job.id,
            turma_id=turma.id,
            disciplina_id=disciplina.id,
            professor_id=professor.id,
            sala_id=sala.id,
            dia_semana="segunda",
            turno="manha",
            periodos=[1, 2],
        )

        # turno "manha" tem 6 periodos (ver settings.turno_periodos) — 1 e 2 já
        # ocupados nesta turma em "segunda"; sobra o bloco contíguo [3,4,5,6].
        blocos = service.listar_slots_vagos(turma.id, job.id)

        bloco_segunda = next(b for b in blocos if b["dia_semana"] == "segunda")
        assert bloco_segunda["periodos"] == [3, 4, 5, 6]

        # nenhum bloco de tamanho 1 é devolvido em nenhum dia
        assert all(len(b["periodos"]) >= 2 for b in blocos)
