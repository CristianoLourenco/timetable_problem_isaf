# Implementa: Fase 7 (testes do solver) — ver docs/04_04_analise_desenvolvimento.md secção 4.4.1
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
TURNO_TESTE = "manha"


def _construir_slots(dias: list[str], periodos_por_dia: int, turno: str = TURNO_TESTE) -> list[SlotDTO]:
    return [SlotDTO(dia_semana=dia, turno=turno, periodo=periodo) for dia in dias for periodo in range(1, periodos_por_dia + 1)]


def _cenario_viavel() -> HorarioInput:
    """3 turmas, 3 disciplinas, 2 professores, 1 sala — carga par (2) em cada disciplina."""
    slots = _construir_slots(["segunda", "terca"], periodos_por_dia=4)

    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE),
            TurmaDTO(id=2, numero_alunos=20, turno=TURNO_TESTE),
            TurmaDTO(id=3, numero_alunos=20, turno=TURNO_TESTE),
        ],
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

    def tempo_de(aloc):
        return (aloc.dia_semana, aloc.turno, aloc.periodo)

    contagem_professor_tempo: dict[tuple, int] = defaultdict(int)
    contagem_turma_tempo: dict[tuple, int] = defaultdict(int)
    contagem_sala_tempo: dict[tuple, int] = defaultdict(int)
    por_turma_disciplina: dict[tuple[int, int], list] = defaultdict(list)

    for aloc in resultado.alocacoes:
        contagem_professor_tempo[(aloc.professor_id, *tempo_de(aloc))] += 1
        contagem_turma_tempo[(aloc.turma_id, *tempo_de(aloc))] += 1
        contagem_sala_tempo[(aloc.sala_id, *tempo_de(aloc))] += 1
        por_turma_disciplina[(aloc.turma_id, aloc.disciplina_id)].append(aloc)

    # RN01, RN02, RN03 — nunca duas alocações no mesmo (professor|turma|sala, tempo)
    assert all(c <= 1 for c in contagem_professor_tempo.values())
    assert all(c <= 1 for c in contagem_turma_tempo.values())
    assert all(c <= 1 for c in contagem_sala_tempo.values())

    # RN05 — carga cumprida integralmente; RN06 — bloco contíguo de 2, mesmo professor/sala
    for chave, alocacoes_da_disciplina in por_turma_disciplina.items():
        assert len(alocacoes_da_disciplina) == 2, chave
        professores = {a.professor_id for a in alocacoes_da_disciplina}
        salas = {a.sala_id for a in alocacoes_da_disciplina}
        assert len(professores) == 1
        assert len(salas) == 1

        primeiro, segundo = sorted(alocacoes_da_disciplina, key=lambda a: a.periodo)
        assert primeiro.dia_semana == segundo.dia_semana
        assert primeiro.turno == segundo.turno
        assert segundo.periodo - primeiro.periodo == 1


def test_carga_impar_de_um_tempo_e_infeasible_com_diagnostico():
    """RN06 proíbe tempo isolado — carga_horaria_semanal=1 nunca pode formar bloco >=2."""
    slots = _construir_slots(["segunda"], periodos_por_dia=4)

    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
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
