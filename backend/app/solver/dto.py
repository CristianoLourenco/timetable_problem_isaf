# Implementa: RN01-RN08 (UC08) — estruturas de entrada/saída do solver
# ver docs/relatorio/04_analise_desenvolvimento/ secção 4.3.3 e docs/relatorio/04_analise_desenvolvimento/ secção 4.1.2 (RNs).
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
class PendenciaDTO:
    """RF13/UC09 — um (turma, disciplina) que ficou com tempos por preencher depois
    do solve (RN05 relaxada para soft-com-défice, ver constraints_hard.py). `razao`
    é texto pronto para o Gestor, gerado por app/solver/diagnostico.py."""

    turma_id: int
    disciplina_id: int
    tempos_em_falta: int
    razao: str
    professores_conflitantes: tuple[int, ...] = ()
    turmas_conflitantes: tuple[int, ...] = ()


@dataclass(frozen=True)
class SolverResult:
    status: str  # "OPTIMAL" | "FEASIBLE" | "INFEASIBLE"
    alocacoes: list[AlocacaoResult] = field(default_factory=list)
    diagnostico: str | None = None  # RF13/UC09 — preenchido apenas quando INFEASIBLE (UNKNOWN por tempo)
    pendencias: list[PendenciaDTO] = field(default_factory=list)  # RF13 — défice de RN05 após o solve
