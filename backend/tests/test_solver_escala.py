# Implementa: Fase 7 (RNF01) — valida zero-conflitos a uma escala maior que a Fase 3
# antes de escalar para o tamanho real do ISAF (100+ professores, 60+ turmas).
from collections import defaultdict

from app.solver.dto import (
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.solve import resolver_horario

MAX_TIME_TESTE = 10.0

N_DISCIPLINAS = 6
N_TURMAS = 12


def _construir_slots_reais() -> list[SlotDTO]:
    """45 slots reais do ISAF (9 tempos x 5 dias) — ver Settings em app/core/config.py."""
    slots = []
    slot_id = 1
    for dia in ["segunda", "terca", "quarta", "quinta", "sexta"]:
        for tempo in range(1, 10):
            slots.append(SlotDTO(id=slot_id, dia_semana=dia, tempo_ordem=tempo))
            slot_id += 1
    return slots


def _construir_cenario_em_escala() -> HorarioInput:
    """12 turmas x 2 disciplinas, 8 professores (6 especialistas + 2 flutuantes),
    5 salas, 45 slots reais — uma ordem de grandeza acima do cenário mínimo da Fase 3."""
    slots = _construir_slots_reais()

    turmas = [TurmaDTO(id=i, numero_alunos=30) for i in range(1, N_TURMAS + 1)]
    professores = [ProfessorDTO(id=p, classificacao=(p % 5) + 1, vinculo_casa=(p % 2 == 0)) for p in range(1, 9)]
    salas = [SalaDTO(id=s, capacidade=40) for s in range(1, 6)]

    # professores 1-6 são especialistas (1 disciplina cada); 7 e 8 são flutuantes,
    # qualificados para mais que uma disciplina — aumenta a concorrência sem tornar
    # o cenário artificialmente impossível.
    professor_disciplinas = [ProfessorDisciplinaDTO(professor_id=d, disciplina_id=d) for d in range(1, N_DISCIPLINAS + 1)]
    professor_disciplinas += [
        ProfessorDisciplinaDTO(professor_id=7, disciplina_id=1),
        ProfessorDisciplinaDTO(professor_id=7, disciplina_id=2),
        ProfessorDisciplinaDTO(professor_id=8, disciplina_id=3),
        ProfessorDisciplinaDTO(professor_id=8, disciplina_id=4),
    ]

    turma_disciplinas = []
    for i, turma in enumerate(turmas):
        disciplina_a = (i % N_DISCIPLINAS) + 1
        disciplina_b = ((i + 1) % N_DISCIPLINAS) + 1
        turma_disciplinas.append(TurmaDisciplinaDTO(turma_id=turma.id, disciplina_id=disciplina_a, carga_horaria_semanal=2))
        turma_disciplinas.append(TurmaDisciplinaDTO(turma_id=turma.id, disciplina_id=disciplina_b, carga_horaria_semanal=3))

    return HorarioInput(
        turmas=turmas,
        professores=professores,
        salas=salas,
        slots=slots,
        turma_disciplinas=turma_disciplinas,
        professor_disciplinas=professor_disciplinas,
        disponibilidades=[],  # RN07 — todos totalmente disponíveis
    )


def test_cenario_em_escala_permanece_sem_conflitos():
    dados = _construir_cenario_em_escala()
    resultado = resolver_horario(dados, max_time_in_seconds=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.diagnostico is None

    total_esperado = sum(td.carga_horaria_semanal for td in dados.turma_disciplinas)
    assert len(resultado.alocacoes) == total_esperado  # RN05

    contagem_professor_slot: dict[tuple[int, int], int] = defaultdict(int)
    contagem_turma_slot: dict[tuple[int, int], int] = defaultdict(int)
    contagem_sala_slot: dict[tuple[int, int], int] = defaultdict(int)
    for aloc in resultado.alocacoes:
        contagem_professor_slot[(aloc.professor_id, aloc.slot_id)] += 1
        contagem_turma_slot[(aloc.turma_id, aloc.slot_id)] += 1
        contagem_sala_slot[(aloc.sala_id, aloc.slot_id)] += 1

    # RN01, RN02, RN03 — nenhum conflito, mesmo à escala maior
    assert all(c <= 1 for c in contagem_professor_slot.values())
    assert all(c <= 1 for c in contagem_turma_slot.values())
    assert all(c <= 1 for c in contagem_sala_slot.values())


def test_tempo_insuficiente_nao_e_reportado_como_impossibilidade_estrutural():
    """UNKNOWN (tempo esgotado sem solução) != INFEASIBLE (impossibilidade provada) —
    ver correção em app/solver/solve.py encontrada ao escalar este teste."""
    dados = _construir_cenario_em_escala()
    resultado = resolver_horario(dados, max_time_in_seconds=0.01)

    assert resultado.status == "INFEASIBLE"
    assert "tempo" in resultado.diagnostico.lower()
    assert "revisão manual necessária" not in resultado.diagnostico.lower()
