# Implementa: RF13 (UC09) — diagnóstico aprofundado de INFEASIBLE por bisecção
# ver docs/04_04_analise_desenvolvimento.md secção 4.3.3.
#
# As verificações baratas em solve.py (_diagnosticar_infeasible) apanham causas
# estruturais óbvias (professor não qualificado, carga incompatível com o turno),
# mas deixam passar conflitos genuinamente combinatórios — ex: duas turmas
# partilharem o único professor qualificado para uma disciplina, tornando
# impossível encaixar as duas agendas mesmo com RN01-RN06 corretos e sem
# nenhum erro de modelagem. Isto aconteceu de facto à escala real do ISAF
# (currículo real extraído dos PDFs, ver seed_dados_teste.py) e a mensagem
# genérica "revisão manual necessária" não ajuda o Gestor a saber o quê corrigir.
#
# Técnica: bisecção gulosa sobre o conjunto de turmas, reaproveitando as mesmas
# funções de constraints_hard.py — nunca duplica a modelagem. Só corre quando o
# CP-SAT já provou INFEASIBLE no solve principal (nunca para decidir UNKNOWN vs
# INFEASIBLE, isso já está resolvido em solve.py); tempo limitado por chamada e
# no total para nunca transformar um diagnóstico em nova fonte de lentidão —
# se não conseguir confirmar nada dentro do orçamento, devolve None e quem
# chama mantém a mensagem genérica em vez de arriscar um falso positivo.
import time
from collections import defaultdict

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
from app.solver.dto import HorarioInput


def isolar_nucleo_infeasible(
    dados: HorarioInput,
    *,
    timeout_por_tentativa: float | None = None,
    orcamento_total: float | None = None,
    num_search_workers: int | None = None,
    tamanho_maximo_util: int | None = None,
) -> list[int] | None:
    """Bisecção gulosa: tenta remover turmas uma a uma do conjunto INFEASIBLE
    conhecido, mantendo a remoção sempre que o subconjunto restante continuar
    provadamente INFEASIBLE. Devolve a lista de turma_id do núcleo encontrado
    (não necessariamente o mínimo absoluto — a primeira redução estável que o
    orçamento de tempo permitir), ou None se não conseguir confirmar nada útil.

    Cada tentativa reconstrói o modelo do zero (build_variables + constraints) —
    a essa escala isso sozinho já pode demorar vários segundos, ANTES de
    `timeout_por_tentativa` sequer começar a contar (só limita o solver.Solve,
    não a construção). A `orcamento_total` pode por isso esgotar-se a meio de
    uma ronda de remoção, devolvendo um núcleo grande e pouco útil (perto do
    conjunto original) em vez de um núcleo pequeno e acionável — nesse caso é
    preferível admitir que não convergiu (None, mantém a mensagem genérica) do
    que despejar uma lista enorme de turmas/professores no Gestor."""
    timeout_por_tentativa = timeout_por_tentativa or settings.solver_diagnostico_timeout_por_tentativa
    orcamento_total = orcamento_total or settings.solver_diagnostico_orcamento_total
    num_search_workers = num_search_workers or settings.solver_num_search_workers
    tamanho_maximo_util = tamanho_maximo_util or settings.solver_diagnostico_tamanho_maximo_util

    inicio = time.perf_counter()
    todas_ids = {turma.id for turma in dados.turmas}

    if _provado_infeasible(dados, todas_ids, timeout_por_tentativa, num_search_workers) is not True:
        return None  # nem o conjunto completo confirma depressa — não arriscar um falso positivo

    atual = set(todas_ids)
    mudou = True
    while mudou:
        mudou = False
        for turma_id in sorted(atual):
            if time.perf_counter() - inicio > orcamento_total:
                return sorted(atual) if len(atual) <= tamanho_maximo_util else None
            candidato = atual - {turma_id}
            if _provado_infeasible(dados, candidato, timeout_por_tentativa, num_search_workers) is True:
                atual = candidato
                mudou = True
    return sorted(atual) if len(atual) <= tamanho_maximo_util else None


def formatar_diagnostico_nucleo(nucleo: list[int], dados: HorarioInput) -> str:
    """Traduz o núcleo de turma_id encontrado numa mensagem acionável, incluindo
    que professores ficam sobrecarregados entre as turmas do núcleo (a causa
    mais comum — ver nota de topo)."""
    disciplinas_por_turma: dict[int, set[int]] = defaultdict(set)
    for td in dados.turma_disciplinas:
        if td.turma_id in nucleo:
            disciplinas_por_turma[td.turma_id].add(td.disciplina_id)

    professores_por_disciplina: dict[int, set[int]] = defaultdict(set)
    for pd in dados.professor_disciplinas:
        professores_por_disciplina[pd.disciplina_id].add(pd.professor_id)

    professores_por_turma: dict[int, set[int]] = {
        turma_id: {p for d in disciplinas for p in professores_por_disciplina.get(d, set())}
        for turma_id, disciplinas in disciplinas_por_turma.items()
    }

    nucleo_ordenado = sorted(nucleo)
    partilhas = []
    for i, turma_a in enumerate(nucleo_ordenado):
        for turma_b in nucleo_ordenado[i + 1 :]:
            comuns = professores_por_turma.get(turma_a, set()) & professores_por_turma.get(turma_b, set())
            if comuns:
                lista_profs = ", ".join(str(p) for p in sorted(comuns))
                partilhas.append(f"turmas {turma_a} e {turma_b} partilham professor(es) {lista_profs}")

    turmas_str = ", ".join(str(t) for t in nucleo_ordenado)
    detalhe = "; ".join(partilhas) if partilhas else "sem professor explicitamente partilhado identificado"
    return (
        f"INFEASIBLE — conflito estrutural isolado nas turmas [{turmas_str}]: nenhuma "
        f"combinação de horário satisfaz RN01-RN06 para este subconjunto em simultâneo "
        f"({detalhe}). Reveja a qualificação de professores (ProfessorDisciplina) para as "
        f"disciplinas destas turmas — provavelmente falta um professor alternativo — ou "
        f"gere estas turmas em fases separadas."
    )


def _provado_infeasible(
    dados: HorarioInput, turma_ids: set[int], timeout: float, num_search_workers: int
) -> bool | None:
    """True só se o CP-SAT PROVAR infeasible (status cru, nunca a string colapsada
    de resolver_horario) dentro do timeout; None se inconclusivo (UNKNOWN) — nunca
    tratar inconclusivo como feasible nem como infeasible."""
    if not turma_ids:
        return False
    sub_dados = _filtrar_por_turmas(dados, turma_ids)
    model = cp_model.CpModel()
    variaveis = build_variables(model, sub_dados)
    add_professor_sem_dupla_alocacao(model, variaveis, sub_dados)
    add_turma_sem_dupla_disciplina(model, variaveis, sub_dados)
    add_sala_sem_dupla_turma(model, variaveis, sub_dados)
    add_carga_horaria_cumprida(model, variaveis, sub_dados)
    add_agrupamento_em_blocos(model, variaveis, sub_dados)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = num_search_workers
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        return True
    if status == cp_model.UNKNOWN:
        return None
    return False


def _filtrar_por_turmas(dados: HorarioInput, turma_ids: set[int]) -> HorarioInput:
    return HorarioInput(
        turmas=[t for t in dados.turmas if t.id in turma_ids],
        professores=dados.professores,
        salas=dados.salas,
        slots=dados.slots,
        turma_disciplinas=[td for td in dados.turma_disciplinas if td.turma_id in turma_ids],
        professor_disciplinas=dados.professor_disciplinas,
        disponibilidades=dados.disponibilidades,
    )
