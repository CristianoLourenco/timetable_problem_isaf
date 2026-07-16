# Implementa: RN01-RN08 (UC08) — estruturas de entrada/saída do solver
# ver docs/04_04_analise_desenvolvimento.md secção 4.3.3 e docs/04_04_analise_desenvolvimento.md secção 4.1.2 (RNs).
#
# Puras dataclasses — nunca SQLModel/Pydantic aqui. A service layer (fora de app/solver/)
# é responsável por ler a BD e traduzir as entidades para estas estruturas simples.
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SlotDTO:
    """Um tempo letivo (dia_semana + turno + periodo) — sem hora, o solver não precisa
    de horas reais, só de distinguir combinações. periodo reinicia em 1 a cada turno."""

    dia_semana: str
    turno: str
    periodo: int


@dataclass(frozen=True)
class TurmaDTO:
    id: int
    numero_alunos: int
    turno: str  # a turma só pode ser alocada em tempos do seu próprio turno


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
    dia_semana: str
    turno: str
    periodo: int


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
    dia_semana: str
    turno: str
    periodo: int
    penalizacao_aplicada: float = 0.0


@dataclass(frozen=True)
class SolverResult:
    status: str  # "OPTIMAL" | "FEASIBLE" | "INFEASIBLE"
    alocacoes: list[AlocacaoResult] = field(default_factory=list)
    diagnostico: str | None = None  # RF13/UC09 — preenchido apenas quando INFEASIBLE
