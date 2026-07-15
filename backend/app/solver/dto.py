# Implementa: RN01-RN08 (UC08) — estruturas de entrada/saída do solver
# ver docs/06_arquitetura_backend.md secção "Fase 3" e docs/analise_requisitos_v5.0.md secção 6.
#
# Puras dataclasses — nunca SQLModel/Pydantic aqui. A service layer (fora de app/solver/)
# é responsável por ler a BD e traduzir as entidades para estas estruturas simples.
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SlotDTO:
    id: int
    dia_semana: str
    tempo_ordem: int


@dataclass(frozen=True)
class TurmaDTO:
    id: int
    numero_alunos: int


@dataclass(frozen=True)
class ProfessorDTO:
    id: int
    classificacao: int
    vinculo_casa: bool


@dataclass(frozen=True)
class SalaDTO:
    id: int
    capacidade: int


@dataclass(frozen=True)
class TurmaDisciplinaDTO:
    turma_id: int
    disciplina_id: int
    carga_horaria_semanal: int


@dataclass(frozen=True)
class ProfessorDisciplinaDTO:
    professor_id: int
    disciplina_id: int


@dataclass(frozen=True)
class DisponibilidadeDTO:
    professor_id: int
    slot_id: int


@dataclass(frozen=True)
class HorarioInput:
    turmas: list[TurmaDTO]
    professores: list[ProfessorDTO]
    salas: list[SalaDTO]
    slots: list[SlotDTO]
    turma_disciplinas: list[TurmaDisciplinaDTO]
    professor_disciplinas: list[ProfessorDisciplinaDTO]
    disponibilidades: list[DisponibilidadeDTO]


@dataclass(frozen=True)
class AlocacaoResult:
    turma_id: int
    disciplina_id: int
    professor_id: int
    sala_id: int
    slot_id: int
    penalizacao_aplicada: float = 0.0


@dataclass(frozen=True)
class SolverResult:
    status: str  # "OPTIMAL" | "FEASIBLE" | "INFEASIBLE"
    alocacoes: list[AlocacaoResult] = field(default_factory=list)
    diagnostico: str | None = None  # RF13/UC09 — preenchido apenas quando INFEASIBLE
