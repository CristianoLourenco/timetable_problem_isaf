# Implementa: Fase 7 (RNF01) — valida zero-conflitos a uma escala maior que a Fase 3
# antes de escalar para o tamanho real do ISAF (100+ professores, 60+ turmas).
from collections import defaultdict

from app.core.calendario import gerar_grelha_tempos
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
TURNO_TESTE = "manha"  # concentra as 12 turmas num único turno — maior contenção que espalhar por 3


def _construir_slots_reais() -> list[SlotDTO]:
    """Grelha real do ISAF (turno x período, ver app/core/config.py), um único turno."""
    return [SlotDTO(dia_semana=g.dia_semana, turno=g.turno, periodo=g.periodo) for g in gerar_grelha_tempos() if g.turno == TURNO_TESTE]


def _construir_cenario_em_escala() -> HorarioInput:
    """12 turmas x 2 disciplinas, 8 professores (6 especialistas + 2 flutuantes),
    12 salas (1 por turma — ver builder.atribuir_salas_por_turma_turno, 2026-07-19:
    cada turma fica presa a uma única sala pelo turno inteiro, logo N turmas no
    mesmo turno exigem N salas para não gerar défice estrutural por escassez de
    sala, distinto do défice de RN05/gap que este teste efetivamente mede),
    grelha real de um turno — uma ordem de grandeza acima do cenário mínimo da Fase 3."""
    slots = _construir_slots_reais()

    turmas = [TurmaDTO(id=i, numero_alunos=30, turno=TURNO_TESTE) for i in range(1, N_TURMAS + 1)]
    professores = [ProfessorDTO(id=p, classificacao=(p % 5) + 1, vinculo_casa=(p % 2 == 0)) for p in range(1, 9)]
    salas = [SalaDTO(id=s, capacidade=40) for s in range(1, N_TURMAS + 1)]

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
    """RN01-RN03 continuam corretas à escala. RN05 (défice) — com
    relative_gap_limit=0.30 (ver core/config.py), o CP-SAT pode provar OPTIMAL
    aceitando um pequeno défice residual como "suficientemente bom" antes de
    esgotar o tempo, mesmo quando o cenário tem solução completa alcançável —
    trade-off aceite conscientemente para reduzir o tempo de geração à escala
    real do ISAF (ver docs/superpowers/specs/2026-07-19-... para a ideia de
    refinamento em background que mitigaria isto no futuro). Por isso só
    validamos aqui que o défice, se existir, é pequeno — não que é sempre zero."""
    dados = _construir_cenario_em_escala()
    resultado = resolver_horario(dados, max_time_in_seconds=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.diagnostico is None

    total_esperado = sum(td.carga_horaria_semanal for td in dados.turma_disciplinas)
    total_deficit = total_esperado - len(resultado.alocacoes)
    assert total_deficit >= 0
    assert total_deficit <= 3, f"défice residual maior do que o esperado: {total_deficit}"

    def tempo_de(aloc):
        return (aloc.dia_semana, aloc.turno, aloc.periodo)

    contagem_professor_tempo: dict[tuple, int] = defaultdict(int)
    contagem_turma_tempo: dict[tuple, int] = defaultdict(int)
    contagem_sala_tempo: dict[tuple, int] = defaultdict(int)
    for aloc in resultado.alocacoes:
        contagem_professor_tempo[(aloc.professor_id, *tempo_de(aloc))] += 1
        contagem_turma_tempo[(aloc.turma_id, *tempo_de(aloc))] += 1
        contagem_sala_tempo[(aloc.sala_id, *tempo_de(aloc))] += 1

    # RN01, RN02, RN03 — nenhum conflito, mesmo à escala maior
    assert all(c <= 1 for c in contagem_professor_tempo.values())
    assert all(c <= 1 for c in contagem_turma_tempo.values())
    assert all(c <= 1 for c in contagem_sala_tempo.values())


def test_tempo_insuficiente_nao_e_reportado_como_impossibilidade_estrutural():
    """UNKNOWN (tempo esgotado sem solução) != INFEASIBLE (impossibilidade provada) —
    ver correção em app/solver/solve.py encontrada ao escalar este teste."""
    dados = _construir_cenario_em_escala()
    resultado = resolver_horario(dados, max_time_in_seconds=0.01)

    assert resultado.status == "INFEASIBLE"
    assert "tempo" in resultado.diagnostico.lower()
    assert "revisão manual necessária" not in resultado.diagnostico.lower()
