# Implementa: RF13 (UC09) — resolução do modelo CP-SAT e tratamento estruturado de INFEASIBLE (RNF03)
from collections import defaultdict

from ortools.sat.python import cp_model

from app.solver.builder import build_variables
from app.solver.constraints_hard import (
    add_agrupamento_em_blocos,
    add_carga_horaria_cumprida,
    add_professor_sem_dupla_alocacao,
    add_sala_sem_dupla_turma,
    add_turma_sem_dupla_disciplina,
)
from app.solver.constraints_soft import build_objective
from app.solver.dto import HorarioInput, SolverResult
from app.solver.result_mapper import mapear_resultado

_STATUS_VIAVEL = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE"}


def resolver_horario(dados: HorarioInput, max_time_in_seconds: float) -> SolverResult:
    """Monta o modelo completo, resolve com limite de tempo e nunca deixa INFEASIBLE
    propagar como exceção — devolve sempre um SolverResult estruturado (RNF03)."""
    model = cp_model.CpModel()
    variaveis = build_variables(model, dados)

    add_professor_sem_dupla_alocacao(model, variaveis, dados)
    add_turma_sem_dupla_disciplina(model, variaveis, dados)
    add_sala_sem_dupla_turma(model, variaveis, dados)
    add_carga_horaria_cumprida(model, variaveis, dados)
    add_agrupamento_em_blocos(model, variaveis, dados)

    model.Minimize(build_objective(model, variaveis, dados))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_in_seconds
    status = solver.Solve(model)

    status_nome = _STATUS_VIAVEL.get(status)
    if status_nome is None:
        return SolverResult(status="INFEASIBLE", alocacoes=[], diagnostico=_diagnosticar_infeasible(dados))

    alocacoes = mapear_resultado(solver, variaveis, dados)
    return SolverResult(status=status_nome, alocacoes=alocacoes, diagnostico=None)


def _diagnosticar_infeasible(dados: HorarioInput) -> str:
    """Diagnóstico estrutural leve (RF13/UC09) — verificações baratas, sem re-otimizar.

    Não usa `SufficientAssumptionsForInfeasibility`/`AssumeConstraint` do CP-SAT (que
    exigiria remodelar as constraints como assumptions) — fica como melhoria futura se
    este diagnóstico mínimo não for suficiente na prática.
    """
    problemas: list[str] = []

    professores_por_disciplina: dict[int, list[int]] = defaultdict(list)
    for pd in dados.professor_disciplinas:
        professores_por_disciplina[pd.disciplina_id].append(pd.professor_id)

    turmas_por_id = {turma.id: turma for turma in dados.turmas}
    capacidade_maxima = max((sala.capacidade for sala in dados.salas), default=0)
    total_slots_semana = len(dados.slots)

    for td in dados.turma_disciplinas:
        if not professores_por_disciplina.get(td.disciplina_id):
            problemas.append(
                f"Turma {td.turma_id} / disciplina {td.disciplina_id}: nenhum professor "
                "qualificado registado em ProfessorDisciplina."
            )

        turma = turmas_por_id.get(td.turma_id)
        if turma and turma.numero_alunos > capacidade_maxima:
            problemas.append(
                f"Turma {td.turma_id}: {turma.numero_alunos} alunos excede a capacidade "
                f"máxima disponível entre as salas ({capacidade_maxima})."
            )

        if td.carga_horaria_semanal == 1:
            problemas.append(
                f"Turma {td.turma_id} / disciplina {td.disciplina_id}: carga_horaria_semanal=1 "
                "é incompatível com RN06 (bloco mínimo de 2 tempos contíguos)."
            )

        if td.carga_horaria_semanal > total_slots_semana:
            problemas.append(
                f"Turma {td.turma_id} / disciplina {td.disciplina_id}: carga_horaria_semanal "
                f"({td.carga_horaria_semanal}) excede o total de slots da semana ({total_slots_semana})."
            )

    if not problemas:
        return (
            "INFEASIBLE sem causa estrutural identificada nas verificações automáticas — "
            "possível conflito combinatório entre RN01-RN06 (ex: disponibilidade insuficiente "
            "de professores/salas para a carga total exigida). Revisão manual necessária."
        )
    return "; ".join(problemas)
