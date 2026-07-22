# Implementa: Fase 7 (testes do solver) — ver docs/relatorio/04_analise_desenvolvimento/ secção 4.4.1
# Cenário pequeno e controlado (3 turmas) validando zero-conflitos antes de escalar (RNF01).
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
from app.solver.solve import resolver_horario

MAX_TIME_TESTE = 10.0
TURNO_TESTE = "manha"


def _construir_slots(dias: list[str], periodos_por_dia: int, turno: str = TURNO_TESTE) -> list[SlotDTO]:
    return [SlotDTO(dia_semana=dia, turno=turno, periodo=periodo) for dia in dias for periodo in range(1, periodos_por_dia + 1)]


def _cenario_viavel() -> HorarioInput:
    """3 turmas, 3 disciplinas, 2 professores, 3 salas — carga par (2) em cada
    disciplina. Uma sala por turma (ver builder.atribuir_salas_por_turma_turno,
    2026-07-19: cada turma fica presa a uma única sala pelo turno inteiro) —
    3 turmas no mesmo turno precisam de 3 salas distintas para não gerar
    pendência estrutural de escassez de sala."""
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
        salas=[SalaDTO(id=1, capacidade=30), SalaDTO(id=2, capacidade=30), SalaDTO(id=3, capacidade=30)],
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


def test_carga_impar_de_um_tempo_ja_nao_e_infeasible_fica_pendente():
    """RN06 continua a proibir tempo isolado, mas RN05 agora aceita défice — em vez
    de INFEASIBLE, a disciplina fica com 1 tempo em falta reportado como pendência."""
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

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.alocacoes == []
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].turma_id == 1
    assert resultado.pendencias[0].disciplina_id == 1
    assert resultado.pendencias[0].tempos_em_falta == 1


def test_rn12_prioridade_protege_professor_de_maior_prioridade_em_trade_off():
    """1 turma, 1 único bloco de tempo possível, 2 professores igualmente
    qualificados — ambos têm disponibilidade registada, mas nenhuma delas coincide
    com o único bloco disponível, logo qualquer que seja o professor escolhido vai
    violar RN04 (nada mais no cenário distingue os dois: mesma sala, mesma
    disciplina, mesmo custo de RN08/equidade). A solução ótima deve preferir violar
    a disponibilidade do professor de baixa prioridade, já que isso custa menos ao
    objetivo (peso_rn04 * (1 + prioridade))."""
    slots = _construir_slots(["segunda"], periodos_por_dia=2)  # único bloco possível (RN06: 2 tempos)

    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[
            ProfessorDTO(id=1, classificacao=5, vinculo_casa=True),  # alta prioridade
            ProfessorDTO(id=2, classificacao=1, vinculo_casa=False),  # baixa prioridade
        ],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=1),
        ],
        # Nenhum dos dois está registado disponível no único bloco real (segunda,
        # periodos 1-2) — ambos têm ALGUM registo (não caem no fallback RN07), mas
        # nenhum coincide, logo qualquer escolha viola RN04 exatamente uma vez.
        disponibilidades=[
            DisponibilidadeDTO(professor_id=1, dia_semana="terca", turno=TURNO_TESTE, periodo=1),
            DisponibilidadeDTO(professor_id=2, dia_semana="quarta", turno=TURNO_TESTE, periodo=1),
        ],
    )

    # relative_gap_limit=0.0 força prova de otimalidade exata — com o gap de produção
    # (10%, ver settings.solver_relative_gap_limit) a diferença de custo entre violar
    # o professor de alta e de baixa prioridade neste cenário minúsculo (~3.8%) cai
    # dentro da tolerância, e o warm-start (que tenta o professor de maior prioridade
    # primeiro, RN12) pode fazer o CP-SAT aceitar essa solução sub-ótima como "boa o
    # suficiente" e parar. Isto testa que o TERMO do objetivo está correto — a
    # interação com o gap de produção é uma limitação conhecida, não um bug aqui.
    resultado = resolver_horario(dados, max_time_in_seconds=MAX_TIME_TESTE, relative_gap_limit=0.0)
    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.alocacoes) == 2

    professor_escolhido = {a.professor_id for a in resultado.alocacoes}
    assert professor_escolhido == {2}, "o solver devia preferir violar RN04 do professor de baixa prioridade"
