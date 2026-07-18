# Implementa: RF09/RF13 — testes da decomposição por turno, ver app/solver/orquestrador_turnos.py
from collections import defaultdict

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
from app.solver.orquestrador_turnos import resolver_horario_por_turnos

MAX_TIME_TESTE = 5.0


def _slots(turno: str, dias: list[str], periodos_por_dia: int) -> list[SlotDTO]:
    return [SlotDTO(dia_semana=dia, turno=turno, periodo=p) for dia in dias for p in range(1, periodos_por_dia + 1)]


def _cenario_dois_turnos() -> HorarioInput:
    """2 turmas manhã + 2 turmas tarde, professores partilhados entre turnos —
    valida que a decomposição resolve ambas as fases sem conflitos e sem
    duplicar/perder alocações."""
    slots = _slots("manha", ["segunda", "terca"], 4) + _slots("tarde", ["segunda", "terca"], 4)

    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="manha"),
            TurmaDTO(id=3, numero_alunos=20, turno="tarde"),
            TurmaDTO(id=4, numero_alunos=20, turno="tarde"),
        ],
        professores=[
            ProfessorDTO(id=1, classificacao=5, vinculo_casa=True),
            ProfessorDTO(id=2, classificacao=3, vinculo_casa=False),
        ],
        salas=[SalaDTO(id=1, capacidade=30), SalaDTO(id=2, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=2, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=3, disciplina_id=3, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=4, disciplina_id=4, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[
            # professor 1 dá manhã e tarde (partilhado entre fases)
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=3),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=2),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=4),
        ],
        disponibilidades=[],  # RN07 — todos totalmente disponíveis
    )


def test_decomposicao_resolve_ambas_as_fases_sem_conflitos():
    dados = _cenario_dois_turnos()
    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_por_turno=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.diagnostico is None
    assert len(resultado.alocacoes) == 8  # soma das cargas: 2+2+2+2

    def tempo_de(aloc):
        return (aloc.dia_semana, aloc.turno, aloc.periodo)

    contagem_professor_tempo: dict[tuple, int] = defaultdict(int)
    contagem_turma_tempo: dict[tuple, int] = defaultdict(int)
    contagem_sala_tempo: dict[tuple, int] = defaultdict(int)
    for aloc in resultado.alocacoes:
        contagem_professor_tempo[(aloc.professor_id, *tempo_de(aloc))] += 1
        contagem_turma_tempo[(aloc.turma_id, *tempo_de(aloc))] += 1
        contagem_sala_tempo[(aloc.sala_id, *tempo_de(aloc))] += 1

    assert all(c <= 1 for c in contagem_professor_tempo.values())
    assert all(c <= 1 for c in contagem_turma_tempo.values())
    assert all(c <= 1 for c in contagem_sala_tempo.values())

    turmas_manha = {1, 2}
    turmas_tarde = {3, 4}
    for aloc in resultado.alocacoes:
        if aloc.turma_id in turmas_manha:
            assert aloc.turno == "manha"
        else:
            assert aloc.turma_id in turmas_tarde
            assert aloc.turno == "tarde"


def test_turma_sem_professor_qualificado_vira_pendencia_no_turno_certo():
    """Turma da tarde sem nenhum professor qualificado — a fase da manhã resolve
    normalmente; a turma da tarde fica como pendência (não bloqueia mais nada)."""
    slots = _slots("manha", ["segunda"], 4) + _slots("tarde", ["segunda"], 4)

    dados = HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="tarde"),
        ],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=99, carga_horaria_semanal=2),  # sem professor qualificado
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_por_turno=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.alocacoes) == 2  # só a turma 1 (manhã) foi alocada
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].turma_id == 2
    assert resultado.pendencias[0].disciplina_id == 99


def test_fase_sem_turmas_e_ignorada():
    """Âmbito só com turmas da manhã — a fase da tarde/noite deve ser saltada sem
    erro (nenhuma turma para resolver)."""
    slots = _slots("manha", ["segunda"], 4)
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno="manha")],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_por_turno=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.alocacoes) == 2
    assert all(a.turno == "manha" for a in resultado.alocacoes)
