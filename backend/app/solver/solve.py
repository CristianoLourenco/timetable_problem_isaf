# Implementa: RF13 (UC09) — resolução do modelo CP-SAT e tratamento estruturado de INFEASIBLE (RNF03)
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
from app.solver.diagnostico import gerar_razao_pendencia
from app.solver.dto import HorarioInput, PendenciaDTO, SolverResult
from app.solver.heuristica_inicial import gerar_hint_inicial
from app.solver.preprocessamento import podar_dominio
from app.solver.prioridade_docente import calcular_prioridades
from app.solver.result_mapper import mapear_resultado

_STATUS_VIAVEL = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE"}


def resolver_horario(
    dados: HorarioInput,
    max_time_in_seconds: float,
    num_search_workers: int = 8,
    relative_gap_limit: float | None = None,
    prioridades: dict[int, float] | None = None,
    chaves_professor_ocupadas: frozenset[tuple[int, str, str, int]] = frozenset(),
    contagem_diaria_fixa: dict[tuple[int, str], int] | None = None,
) -> SolverResult:
    """Monta o modelo completo, resolve com limite de tempo e nunca deixa INFEASIBLE
    propagar como exceção nem como status por escassez estrutural (RF13) — RN05 é
    soft-com-défice (constraints_hard.add_carga_horaria_cumprida), logo o único
    status não-viável possível é UNKNOWN (tempo esgotado, RNF03), nunca
    impossibilidade combinatória provada.

    `prioridades` (RN12) é opcional — se omitido, é calculado aqui a partir de
    `dados.professores`/`dados.disponibilidades` já podados. `chaves_professor_ocupadas`
    e `contagem_diaria_fixa` só são usados por uma decomposição por turno (ver
    app/solver/orquestrador_turnos.py) para propagar fixações de fases anteriores —
    um chamador direto nunca precisa de os passar.
    """
    dados, pendencias_estruturais = podar_dominio(dados)

    if prioridades is None:
        prioridades = calcular_prioridades(dados.professores, dados.disponibilidades)

    model = cp_model.CpModel()
    variaveis = build_variables(model, dados, chaves_professor_ocupadas)

    add_professor_sem_dupla_alocacao(model, variaveis, dados)
    add_turma_sem_dupla_disciplina(model, variaveis, dados)
    add_sala_sem_dupla_turma(model, variaveis, dados)
    deficits = add_carga_horaria_cumprida(model, variaveis, dados)
    add_agrupamento_em_blocos(model, variaveis, dados)

    model.Minimize(
        build_objective(
            model, variaveis, dados, deficits, prioridades=prioridades, contagem_diaria_fixa=contagem_diaria_fixa
        )
    )

    # Warm-start: uma atribuição gulosa rápida ("mais restrito primeiro", professores
    # candidatos ordenados por RN12) dá ao CP-SAT um ponto de partida perto de uma
    # solução válida e prioridade-consciente em vez de procurar do zero — hints
    # parciais são aceites pelo CP-SAT, por isso um resultado incompleto da
    # heurística (nunca lança exceção) ainda ajuda. Ver app/solver/heuristica_inicial.py
    # para a estratégia e o porquê.
    hint = gerar_hint_inicial(dados, variaveis, prioridades)
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
        # UNKNOWN (tempo esgotado sem encontrar nenhuma solução) é o ÚNICO caso não
        # otimizado/viável possível agora que RN05 nunca torna o modelo genuinamente
        # INFEASIBLE (RF13) — reportar como tal evita dizer ao Gestor que o cenário é
        # impossível quando na verdade só precisava de mais tempo (RNF03).
        return SolverResult(
            status="INFEASIBLE", alocacoes=[], diagnostico=_diagnosticar_tempo_esgotado(max_time_in_seconds)
        )

    alocacoes = mapear_resultado(solver, variaveis, dados)
    pendencias = pendencias_estruturais + _extrair_pendencias_deficit(solver, deficits, dados)
    return SolverResult(status=status_nome, alocacoes=alocacoes, diagnostico=None, pendencias=pendencias)


def _extrair_pendencias_deficit(
    solver: cp_model.CpSolver, deficits: dict[tuple[int, int], cp_model.IntVar], dados: HorarioInput
) -> list[PendenciaDTO]:
    """Lê o valor resolvido de cada IntVar de défice (RN05 soft) e gera a
    PendenciaDTO correspondente para as que ficaram > 0, com a razão explicada
    por app/solver/diagnostico.py (RF13)."""
    pendencias = []
    for (turma_id, disciplina_id), var in deficits.items():
        tempos_em_falta = solver.Value(var)
        if tempos_em_falta > 0:
            pendencias.append(gerar_razao_pendencia(turma_id, disciplina_id, tempos_em_falta, dados))
    return pendencias


def _diagnosticar_tempo_esgotado(max_time_in_seconds: float) -> str:
    """UNKNOWN — o solver esgotou o tempo sem encontrar nenhuma solução (viável ou não).

    Não confundir com impossibilidade estrutural (RF13 — RN05 é soft-com-défice,
    nunca mais é essa a causa): isto só prova que o espaço de procura não foi
    explorado o suficiente no tempo dado (RNF01/RNF03)."""
    return (
        f"O solver não encontrou nenhuma solução dentro do limite de tempo "
        f"({max_time_in_seconds:.0f}s) — isto não significa que o cenário seja "
        "impossível, apenas que precisa de mais tempo de procura. Tente novamente "
        "escolhendo um tempo máximo maior (1, 5 ou 10 min)."
    )
