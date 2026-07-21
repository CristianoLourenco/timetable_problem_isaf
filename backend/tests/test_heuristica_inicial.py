# Implementa: warm-start do CP-SAT (RF13/RNF01) — ver app/solver/heuristica_inicial.py
from ortools.sat.python import cp_model

from app.solver.builder import build_variables
from app.solver.dto import (
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.heuristica_inicial import gerar_hint_inicial
from tests.test_solver import _cenario_viavel
from tests.test_solver_escala import _construir_cenario_em_escala


def _hint_nao_torna_infeasible(dados) -> None:
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)
    hint = gerar_hint_inicial(dados, variaveis)

    assert all(chave in variaveis.x for chave in hint), "hint só pode referenciar chaves reais de variaveis.x"

    # fix_variables_to_their_hinted_value força o CP-SAT a respeitar o hint —
    # se isso tornar o modelo INFEASIBLE, a heurística tem um bug (produziu uma
    # atribuição que colide com uma constraint hard), não um problema do solve real.
    from app.solver.constraints_hard import (
        add_agrupamento_em_blocos,
        add_carga_horaria_cumprida,
        add_professor_sem_dupla_alocacao,
        add_sala_sem_dupla_turma,
        add_turma_sem_dupla_disciplina,
    )

    add_professor_sem_dupla_alocacao(model, variaveis, dados)
    add_turma_sem_dupla_disciplina(model, variaveis, dados)
    add_sala_sem_dupla_turma(model, variaveis, dados)
    add_carga_horaria_cumprida(model, variaveis, dados)
    add_agrupamento_em_blocos(model, variaveis, dados)

    for chave, valor in hint.items():
        model.AddHint(variaveis.x[chave], valor)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.fix_variables_to_their_hinted_value = True
    status = solver.Solve(model)

    assert status != cp_model.INFEASIBLE, "hint da heurística colide com uma constraint hard"


def test_heuristica_nunca_lanca_excecao_em_cenario_pequeno():
    dados = _cenario_viavel()
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)
    gerar_hint_inicial(dados, variaveis)  # não deve lançar


def test_heuristica_nunca_lanca_excecao_em_cenario_em_escala():
    dados = _construir_cenario_em_escala()
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)
    gerar_hint_inicial(dados, variaveis)  # não deve lançar


def test_hint_em_cenario_pequeno_nao_colide_com_constraints_hard():
    _hint_nao_torna_infeasible(_cenario_viavel())


def test_hint_em_cenario_em_escala_nao_colide_com_constraints_hard():
    _hint_nao_torna_infeasible(_construir_cenario_em_escala())


def test_hint_prefere_professor_de_maior_prioridade_rn12():
    """1 turma/1 disciplina, 2 professores igualmente qualificados/disponíveis —
    o hint deve escolher sistematicamente o de maior prioridade (RN12), já que
    combos são ordenados por -prioridade antes do desempate aleatório."""
    slots = [SlotDTO(dia_semana=dia, turno="manha", periodo=p) for dia in ["segunda", "terca"] for p in range(1, 5)]
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno="manha")],
        professores=[
            ProfessorDTO(id=1, classificacao=3, vinculo_casa=False),
            ProfessorDTO(id=2, classificacao=3, vinculo_casa=False),
        ],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[
            ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1),
            ProfessorDisciplinaDTO(professor_id=2, disciplina_id=1),
        ],
        disponibilidades=[],
    )
    prioridades = {1: 0.1, 2: 0.9}  # professor 2 é claramente mais prioritário

    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)
    hint = gerar_hint_inicial(dados, variaveis, prioridades)

    professores_no_hint = {chave[2] for chave, valor in hint.items() if valor == 1}
    assert professores_no_hint == {2}
