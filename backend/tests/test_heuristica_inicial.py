# Implementa: warm-start do CP-SAT (RF13/RNF01) — ver app/solver/heuristica_inicial.py
from ortools.sat.python import cp_model

from app.solver.builder import build_variables
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
