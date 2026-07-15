# Implementa: RF09, RF10 (UC08, UC10) — ver docs/analise_requisitos_v5.0.md
#
# Passo 1 (Extração) do fluxo descrito em docs/06_arquitetura_backend.md secção 1:
# lê as entidades da BD e traduz para as dataclasses simples que o solver aceita.
# O solver nunca vê a Session nem os models SQLModel diretamente.
from sqlmodel import Session, select

from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.disponibilidade import Disponibilidade
from app.models.job import Job
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.slot import Slot
from app.models.turma import Turma
from app.models.turma_disciplina import TurmaDisciplina
from app.repositories.job_repository import JobRepository
from app.solver.dto import (
    DisponibilidadeDTO,
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)


def extrair_dados(session: Session) -> HorarioInput:
    """Lê todas as entidades relevantes da BD e monta o HorarioInput do solver."""
    turmas = session.exec(select(Turma)).all()
    professores = session.exec(select(Professor)).all()
    salas = session.exec(select(Sala)).all()
    slots = session.exec(select(Slot)).all()
    turma_disciplinas = session.exec(select(TurmaDisciplina)).all()
    professor_disciplinas = session.exec(select(ProfessorDisciplina)).all()
    disponibilidades = session.exec(select(Disponibilidade)).all()

    return HorarioInput(
        turmas=[TurmaDTO(id=t.id, numero_alunos=t.numero_alunos) for t in turmas],
        professores=[
            ProfessorDTO(id=p.id, classificacao=p.classificacao, vinculo_casa=p.vinculo_casa) for p in professores
        ],
        salas=[SalaDTO(id=s.id, capacidade=s.capacidade) for s in salas],
        slots=[SlotDTO(id=sl.id, dia_semana=sl.dia_semana, tempo_ordem=sl.tempo_ordem) for sl in slots],
        turma_disciplinas=[
            TurmaDisciplinaDTO(
                turma_id=td.turma_id,
                disciplina_id=td.disciplina_id,
                carga_horaria_semanal=td.carga_horaria_semanal,
            )
            for td in turma_disciplinas
        ],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=pd.professor_id, disciplina_id=pd.disciplina_id)
            for pd in professor_disciplinas
        ],
        disponibilidades=[
            DisponibilidadeDTO(professor_id=d.professor_id, slot_id=d.slot_id) for d in disponibilidades
        ],
    )


class HorarioService:
    """Orquestra o ciclo de vida do Job — quem executa o solver é workers/job_runner.py."""

    def __init__(self, session: Session):
        self.job_repo = JobRepository(session)

    def disparar_geracao(self) -> Job:
        """RF09 — cria o Job em PENDING; o router dispara job_runner.executar em BackgroundTasks."""
        return self.job_repo.criar()

    def consultar_job(self, job_id: str) -> Job:
        """RF10 — consulta de estado de processamento."""
        job = self.job_repo.obter(job_id)
        if job is None:
            raise EntidadeNaoEncontradaError("Job não encontrado.")
        return job
