# Implementa: RF09, RF10, RF11, RF12 (UC08, UC10, UC11, UC12) — ver docs/analise_requisitos_v5.0.md
#
# Passo 1 (Extração) do fluxo descrito em docs/06_arquitetura_backend.md secção 1:
# lê as entidades da BD e traduz para as dataclasses simples que o solver aceita.
# O solver nunca vê a Session nem os models SQLModel diretamente.
from collections import defaultdict

from sqlmodel import Session, select

from app.core.config import settings
from app.core.exceptions import EntidadeNaoEncontradaError
from app.models.alocacao import Alocacao
from app.models.disponibilidade import Disponibilidade
from app.models.job import Job
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.slot import Slot
from app.models.turma import Turma
from app.models.turma_disciplina import TurmaDisciplina
from app.repositories.alocacao_repository import AlocacaoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.job_repository import JobRepository
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.sala_repository import SalaRepository
from app.repositories.slot_repository import SlotRepository
from app.repositories.turma_repository import TurmaRepository
from app.schemas.horario_schema import HorarioDiaSchema, HorarioItemSchema, HorarioResponseSchema
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
        self.alocacao_repo = AlocacaoRepository(session)
        self.turma_repo = TurmaRepository(session)
        self.professor_repo = ProfessorRepository(session)
        self.disciplina_repo = DisciplinaRepository(session)
        self.sala_repo = SalaRepository(session)
        self.slot_repo = SlotRepository(session)

    def disparar_geracao(self) -> Job:
        """RF09 — cria o Job em PENDING; o router dispara job_runner.executar em BackgroundTasks."""
        return self.job_repo.criar()

    def consultar_job(self, job_id: str) -> Job:
        """RF10 — consulta de estado de processamento."""
        job = self.job_repo.obter(job_id)
        if job is None:
            raise EntidadeNaoEncontradaError("Job não encontrado.")
        return job

    def consultar_horario_turma(self, turma_id: int) -> HorarioResponseSchema:
        """RF11 (UC11) — horário da turma, a partir do Job DONE mais recente."""
        if self.turma_repo.get(turma_id) is None:
            raise EntidadeNaoEncontradaError("Turma não encontrada.")

        job = self._obter_ultimo_job_concluido()
        alocacoes = self.alocacao_repo.listar_por_job_e_turma(job.id, turma_id)
        return self._montar_resposta(job.id, alocacoes)

    def consultar_horario_professor(self, professor_id: int) -> HorarioResponseSchema:
        """RF12 (UC12) — horário do professor, a partir do Job DONE mais recente."""
        if self.professor_repo.get(professor_id) is None:
            raise EntidadeNaoEncontradaError("Professor não encontrado.")

        job = self._obter_ultimo_job_concluido()
        alocacoes = self.alocacao_repo.listar_por_job_e_professor(job.id, professor_id)
        return self._montar_resposta(job.id, alocacoes)

    def _obter_ultimo_job_concluido(self) -> Job:
        job = self.job_repo.obter_ultimo_concluido()
        if job is None:
            raise EntidadeNaoEncontradaError("Ainda não existe nenhum horário gerado com sucesso.")
        return job

    def _montar_resposta(self, job_id: str, alocacoes: list[Alocacao]) -> HorarioResponseSchema:
        """Traduz linhas de Alocacao em JSON estruturado por dia/slot (nunca linhas soltas)."""
        turmas = {t.id: t for t in self.turma_repo.list()}
        professores = {p.id: p for p in self.professor_repo.list()}
        disciplinas = {d.id: d for d in self.disciplina_repo.list()}
        salas = {s.id: s for s in self.sala_repo.list()}
        slots = {sl.id: sl for sl in self.slot_repo.list()}

        itens_por_dia: dict[str, list[HorarioItemSchema]] = defaultdict(list)
        for aloc in alocacoes:
            slot = slots[aloc.slot_id]
            itens_por_dia[slot.dia_semana].append(
                HorarioItemSchema(
                    slot_id=slot.id,
                    dia_semana=slot.dia_semana,
                    tempo_ordem=slot.tempo_ordem,
                    hora_inicio=slot.hora_inicio,
                    hora_fim=slot.hora_fim,
                    turma_id=aloc.turma_id,
                    turma_nome=turmas[aloc.turma_id].nome,
                    disciplina_id=aloc.disciplina_id,
                    disciplina_nome=disciplinas[aloc.disciplina_id].nome,
                    professor_id=aloc.professor_id,
                    professor_nome=professores[aloc.professor_id].nome,
                    sala_id=aloc.sala_id,
                    sala_nome=salas[aloc.sala_id].nome,
                )
            )

        dias = [
            HorarioDiaSchema(
                dia_semana=dia,
                tempos=sorted(itens_por_dia.get(dia, []), key=lambda item: item.tempo_ordem),
            )
            for dia in settings.slot_dias_semana
        ]
        return HorarioResponseSchema(job_id=job_id, dias=dias)
