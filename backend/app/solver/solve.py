# Implementa: RF13 (UC09) — resolução do modelo CP-SAT e tratamento estruturado de INFEASIBLE (RNF03)
from collections import Counter, defaultdict

from ortools.sat.python import cp_model

from app.core.config import settings
from app.solver.builder import build_variables
from app.solver.constraints_hard import (
    add_agrupamento_em_blocos,
    add_carga_horaria_cumprida,
    add_professor_sem_dupla_alocacao,
    add_sala_sem_dupla_turma,
    add_turma_sem_dupla_disciplina,
)
from app.solver.constraints_soft import build_objective
from app.solver.diagnostico import formatar_diagnostico_nucleo, isolar_nucleo_infeasible
from app.solver.dto import HorarioInput, SolverResult
from app.solver.heuristica_inicial import gerar_hint_inicial
from app.solver.result_mapper import mapear_resultado

_STATUS_VIAVEL = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE"}


def resolver_horario(
    dados: HorarioInput,
    max_time_in_seconds: float,
    num_search_workers: int = 8,
    relative_gap_limit: float | None = None,
) -> SolverResult:
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

    # Warm-start: uma atribuição gulosa rápida ("mais restrito primeiro") dá ao
    # CP-SAT um ponto de partida perto de uma solução válida em vez de procurar
    # do zero — hints parciais são aceites pelo CP-SAT, por isso um resultado
    # incompleto da heurística (nunca lança exceção) ainda ajuda. Ver
    # app/solver/heuristica_inicial.py para a estratégia e o porquê.
    hint = gerar_hint_inicial(dados, variaveis)
    for chave, valor in hint.items():
        # Defesa extra (a heurística já só produz chaves reais de variaveis.x,
        # por construção — ver heuristica_inicial.py) — um hint nunca deve poder
        # rebentar o solve real por si só.
        var = variaveis.x.get(chave)
        if var is not None:
            model.AddHint(var, valor)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_in_seconds
    # Sem isto, o CP-SAT satura todos os cores da máquina (ver core/config.py) —
    # limitar aqui é o que torna a geração viável em paralelo com o resto do
    # sistema, já que corre numa thread à parte (BackgroundTasks) mas continua a
    # competir por CPU com o event loop e com o utilizador. O portfolio de
    # sub-solvers focados em encontrar a primeira solução só ativa a partir de
    # 5 workers — ver comentário em core/config.py.
    solver.parameters.num_search_workers = num_search_workers
    # Aceitar uma solução dentro do gap (não exigir otimalidade provada) — a
    # função objetivo é uma soma de penalizações soft, "boa e rápida" vale mais
    # do que "marginalmente melhor e lenta" em produção. Ver core/config.py.
    solver.parameters.relative_gap_limit = (
        relative_gap_limit if relative_gap_limit is not None else settings.solver_relative_gap_limit
    )
    status = solver.Solve(model)

    status_nome = _STATUS_VIAVEL.get(status)
    if status_nome is None:
        # UNKNOWN (tempo esgotado sem encontrar nenhuma solução) não é o mesmo que
        # INFEASIBLE (impossibilidade estrutural provada) — reportar cada um com o
        # diagnóstico correto evita dizer ao Gestor que o cenário é impossível quando
        # na verdade só precisava de mais tempo (RNF03).
        diagnostico = (
            _diagnosticar_tempo_esgotado(max_time_in_seconds)
            if status == cp_model.UNKNOWN
            else _diagnosticar_infeasible(dados)
        )
        return SolverResult(status="INFEASIBLE", alocacoes=[], diagnostico=diagnostico)

    alocacoes = mapear_resultado(solver, variaveis, dados)
    return SolverResult(status=status_nome, alocacoes=alocacoes, diagnostico=None)


def _diagnosticar_tempo_esgotado(max_time_in_seconds: float) -> str:
    """UNKNOWN — o solver esgotou o tempo sem encontrar nenhuma solução (viável ou não).

    Não confundir com INFEASIBLE: isto não prova impossibilidade estrutural, só que o
    espaço de procura não foi explorado o suficiente no tempo dado (RNF01/RNF03).
    """
    return (
        f"O solver não encontrou nenhuma solução dentro do limite de tempo "
        f"({max_time_in_seconds:.0f}s) — isto não prova que o cenário seja "
        "estruturalmente impossível, apenas que o espaço de procura é grande "
        "demais para o tempo disponível. Aumente solver_max_time_seconds ou "
        "reduza o âmbito do pedido."
    )


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
    slots_por_turno = Counter(slot.turno for slot in dados.slots)

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

        total_tempos_turno = slots_por_turno.get(turma.turno if turma else None, 0)
        if td.carga_horaria_semanal > total_tempos_turno:
            problemas.append(
                f"Turma {td.turma_id} / disciplina {td.disciplina_id}: carga_horaria_semanal "
                f"({td.carga_horaria_semanal}) excede o total de tempos semanais do turno "
                f"'{turma.turno if turma else '?'}' ({total_tempos_turno})."
            )

    # Verificação agregada — a de cima só compara UMA disciplina contra o turno; uma turma
    # com várias disciplinas de carga individualmente válida pode ainda assim exigir, no
    # total, mais tempos do que o turno tem disponíveis (ex: 5 disciplinas somando 26h
    # numa turma de turno noite com só 25 tempos/semana) — impossível independentemente de
    # professores/salas, e sem isto cai silenciosamente na mensagem genérica de baixo.
    carga_total_por_turma: dict[int, int] = defaultdict(int)
    for td in dados.turma_disciplinas:
        carga_total_por_turma[td.turma_id] += td.carga_horaria_semanal
    for turma_id, carga_total in carga_total_por_turma.items():
        turma = turmas_por_id.get(turma_id)
        total_tempos_turno = slots_por_turno.get(turma.turno if turma else None, 0)
        if carga_total > total_tempos_turno:
            problemas.append(
                f"Turma {turma_id}: soma da carga_horaria_semanal de todas as disciplinas "
                f"({carga_total}) excede o total de tempos semanais do turno "
                f"'{turma.turno if turma else '?'}' ({total_tempos_turno})."
            )

    if not problemas:
        # Nenhuma causa óbvia e barata — tenta isolar um núcleo combinatório concreto
        # por bisecção (ver app/solver/diagnostico.py) antes de desistir. Isto é o
        # caso que apanha, por exemplo, duas turmas a partilhar o único professor
        # qualificado para uma disciplina — confirmado real à escala do ISAF.
        nucleo = isolar_nucleo_infeasible(dados)
        if nucleo:
            return formatar_diagnostico_nucleo(nucleo, dados)
        return (
            "INFEASIBLE sem causa estrutural identificada nas verificações automáticas — "
            "possível conflito combinatório entre RN01-RN06 (ex: disponibilidade insuficiente "
            "de professores/salas para a carga total exigida). Revisão manual necessária."
        )
    return "; ".join(problemas)
