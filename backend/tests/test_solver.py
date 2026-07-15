# Implementa: Fase 7 (testes do solver) — ver docs/06_arquitetura_backend.md secção 5
# Cenário pequeno e controlado (3 turmas) validando zero-conflitos antes de escalar (RNF01).
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


def _construir_slots(dias: list[str], tempos_por_dia: int) -> list[SlotDTO]:
    slots = []
    slot_id = 1
    for dia in dias:
        for tempo in range(1, tempos_por_dia + 1):
            slots.append(SlotDTO(id=slot_id, dia_semana=dia, tempo_ordem=tempo))
            slot_id += 1
    return slots


def _cenario_viavel() -> HorarioInput:
    """3 turmas, 3 disciplinas, 2 professores, 1 sala — carga par (2) em cada disciplina."""
    slots = _construir_slots(["segunda", "terca"], tempos_por_dia=4)

    return HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20), TurmaDTO(id=2, numero_alunos=20), TurmaDTO(id=3, numero_alunos=20)],
        professores=[
            ProfessorDTO(id=1, classificacao=5, vinculo_casa=True),
            ProfessorDTO(id=2, classificacao=3, vinculo_casa=False),
        ],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=2, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=3, disciplina_id=3, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=2),
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=3),
        ],
        disponibilidades=[],  # RN07 — sem registo, ambos totalmente disponíveis
    )


def test_cenario_pequeno_e_viavel_sem_conflitos():
    dados = _cenario_viavel()
    resultado = resolver_horario(dados, max_time_in_seconds=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.diagnostico is None
    assert len(resultado.alocacoes) == 6  # soma das cargas: 2 + 2 + 2

    slots_por_id = {slot.id: slot for slot in dados.slots}

    contagem_professor_slot: dict[tuple[int, int], int] = defaultdict(int)
    contagem_turma_slot: dict[tuple[int, int], int] = defaultdict(int)
    contagem_sala_slot: dict[tuple[int, int], int] = defaultdict(int)
    por_turma_disciplina: dict[tuple[int, int], list] = defaultdict(list)

    for aloc in resultado.alocacoes:
        contagem_professor_slot[(aloc.professor_id, aloc.slot_id)] += 1
        contagem_turma_slot[(aloc.turma_id, aloc.slot_id)] += 1
        contagem_sala_slot[(aloc.sala_id, aloc.slot_id)] += 1
        por_turma_disciplina[(aloc.turma_id, aloc.disciplina_id)].append(aloc)

    # RN01, RN02, RN03 — nunca duas alocações no mesmo (professor|turma|sala, slot)
    assert all(c <= 1 for c in contagem_professor_slot.values())
    assert all(c <= 1 for c in contagem_turma_slot.values())
    assert all(c <= 1 for c in contagem_sala_slot.values())

    # RN05 — carga cumprida integralmente; RN06 — bloco contíguo de 2, mesmo professor/sala
    for chave, alocacoes_da_disciplina in por_turma_disciplina.items():
        assert len(alocacoes_da_disciplina) == 2, chave
        professores = {a.professor_id for a in alocacoes_da_disciplina}
        salas = {a.sala_id for a in alocacoes_da_disciplina}
        assert len(professores) == 1
        assert len(salas) == 1

        slots_da_disciplina = sorted(
            (slots_por_id[a.slot_id] for a in alocacoes_da_disciplina), key=lambda s: s.tempo_ordem
        )
        primeiro, segundo = slots_da_disciplina
        assert primeiro.dia_semana == segundo.dia_semana
        assert segundo.tempo_ordem - primeiro.tempo_ordem == 1


def test_carga_impar_de_um_tempo_e_infeasible_com_diagnostico():
    """RN06 proíbe tempo isolado — carga_horaria_semanal=1 nunca pode formar bloco >=2."""
    slots = _construir_slots(["segunda"], tempos_por_dia=4)

    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20)],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=1)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario(dados, max_time_in_seconds=MAX_TIME_TESTE)

    assert resultado.status == "INFEASIBLE"
    assert resultado.alocacoes == []
    assert "carga_horaria_semanal=1" in resultado.diagnostico
