# Implementa: RF13 (UC09) — diagnóstico aprofundado de INFEASIBLE por bisecção
# ver docs/relatorio/04_analise_desenvolvimento/ secção 4.3.3.
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
from app.solver.dto import HorarioInput, PendenciaDTO

# Sentinela distinta de `None` para `gerar_razao_pendencia(nucleo_compartilhado=...)` —
# `None` é um valor LEGÍTIMO de retorno de isolar_nucleo_infeasible (bisecção não
# convergiu, ver docstring), por isso não pode também significar "não fornecido pelo
# chamador". Bug real medido à escala do ISAF (2026-07-19, 86 turmas): quando o
# cenário tem défice mas não é genuinamente INFEASIBLE (comum agora que RN05 é
# soft-com-défice), a chamada única em _extrair_pendencias_deficit devolve None —
# e `nucleo_compartilhado if nucleo_compartilhado is not None else isolar_nucleo_infeasible(dados)`
# tratava esse None como "não fornecido", recalculando a bisecção (5-9s) para CADA
# uma das pendências do cenário — 56 pendências mediram 419s só nisto, 73% do
# tempo total do teste ponta-a-ponta (572s).
_NAO_FORNECIDO = object()


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


def gerar_razao_pendencia(
    turma_id: int,
    disciplina_id: int,
    tempos_em_falta: int,
    dados: HorarioInput,
    nucleo_compartilhado: list[int] | None = _NAO_FORNECIDO,
) -> PendenciaDTO:
    """RF13 — traduz uma pendência de défice (turma, disciplina) numa razão
    acionável para o Gestor, verificando causas prováveis em ordem barata -> cara:

      1. carga da disciplina sozinha excede os tempos do turno da turma;
      2. soma da carga de TODAS as disciplinas da turma excede os tempos do turno;
      3. professor(es) qualificados desta disciplina todos ocupados nos mesmos
         tempos por outra turma (via bisecção, app/solver/isolar_nucleo_infeasible,
         mesmo orçamento de tempo já existente);
      4. fallback — nenhuma causa automática identificada.

    `nucleo_compartilhado`: quando o chamador (`_extrair_pendencias_deficit` em
    solve.py) já tem várias pendências no mesmo cenário, a bisecção da causa #3
    seria idêntica para todas — calcular uma vez por chamada e passar aqui em vez
    de repetir isolar_nucleo_infeasible(dados) por pendência evita um custo de até
    N × orçamento_total (confirmado >15min de CPU num cenário real do ISAF com 86
    turmas). Se omitido (sentinela `_NAO_FORNECIDO`), mantém o comportamento antigo
    — chama isolar_nucleo_infeasible(dados) aqui mesmo, para retrocompatibilidade de
    quem invoca esta função diretamente (ex: testes). Passar `None` explicitamente
    (o valor real de "bisecção não convergiu") NUNCA deve disparar o recálculo —
    ver `_NAO_FORNECIDO` no topo do módulo para o bug real que isto corrige.

    Nunca lança exceção: se a bisecção (causa 3) não convergir dentro do
    orçamento, cai no fallback genérico em vez de travar o relatório final."""
    turmas_por_id = {turma.id: turma for turma in dados.turmas}
    turma = turmas_por_id.get(turma_id)
    slots_por_turno: dict[str, int] = defaultdict(int)
    for slot in dados.slots:
        slots_por_turno[slot.turno] += 1
    total_tempos_turno = slots_por_turno.get(turma.turno if turma else None, 0)

    carga_disciplina = next(
        (td.carga_horaria_semanal for td in dados.turma_disciplinas if td.turma_id == turma_id and td.disciplina_id == disciplina_id),
        tempos_em_falta,
    )
    if carga_disciplina > total_tempos_turno:
        return PendenciaDTO(
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tempos_em_falta=tempos_em_falta,
            razao=(
                f"Turma {turma_id} / disciplina {disciplina_id}: carga_horaria_semanal "
                f"({carga_disciplina}) excede o total de tempos semanais do turno "
                f"'{turma.turno if turma else '?'}' ({total_tempos_turno}). Reduza a carga ou "
                "distribua a disciplina por mais de uma turma paralela."
            ),
        )

    carga_total_turma = sum(td.carga_horaria_semanal for td in dados.turma_disciplinas if td.turma_id == turma_id)
    if carga_total_turma > total_tempos_turno:
        return PendenciaDTO(
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tempos_em_falta=tempos_em_falta,
            razao=(
                f"Turma {turma_id}: a soma da carga_horaria_semanal de todas as disciplinas "
                f"({carga_total_turma}) excede o total de tempos semanais do turno "
                f"'{turma.turno if turma else '?'}' ({total_tempos_turno}). Aloque manualmente "
                "escolhendo quais disciplinas priorizar, ou revise a grade curricular desta turma."
            ),
            turmas_conflitantes=(turma_id,),
        )

    nucleo = isolar_nucleo_infeasible(dados) if nucleo_compartilhado is _NAO_FORNECIDO else nucleo_compartilhado
    if nucleo and turma_id in nucleo:
        disciplinas_por_turma: dict[int, set[int]] = defaultdict(set)
        for td in dados.turma_disciplinas:
            if td.turma_id in nucleo:
                disciplinas_por_turma[td.turma_id].add(td.disciplina_id)
        professores_por_disciplina: dict[int, set[int]] = defaultdict(set)
        for pd in dados.professor_disciplinas:
            professores_por_disciplina[pd.disciplina_id].add(pd.professor_id)
        professores_desta_turma = {
            p for d in disciplinas_por_turma.get(turma_id, set()) for p in professores_por_disciplina.get(d, set())
        }
        outras_turmas = tuple(t for t in nucleo if t != turma_id)
        return PendenciaDTO(
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tempos_em_falta=tempos_em_falta,
            razao=(
                f"Turma {turma_id} / disciplina {disciplina_id}: professor(es) qualificados "
                f"partilhados com outra(s) turma(s) do mesmo turno ({', '.join(str(t) for t in outras_turmas)}) "
                "não têm tempos suficientes para atender todas em simultâneo. Aloque manualmente "
                "escolhendo outro professor qualificado (se existir) ou outro horário."
            ),
            professores_conflitantes=tuple(sorted(professores_desta_turma)),
            turmas_conflitantes=outras_turmas,
        )

    return PendenciaDTO(
        turma_id=turma_id,
        disciplina_id=disciplina_id,
        tempos_em_falta=tempos_em_falta,
        razao=(
            f"Turma {turma_id} / disciplina {disciplina_id}: {tempos_em_falta} tempo(s) não "
            "foram alocados automaticamente — conflito combinatório não identificado pelas "
            "verificações automáticas (ex: disponibilidade insuficiente de professores/salas "
            "face à carga total exigida). Aloque manualmente ou revise a grade desta turma."
        ),
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
    deficits = add_carga_horaria_cumprida(model, variaveis, sub_dados)
    add_agrupamento_em_blocos(model, variaveis, sub_dados)
    # add_carga_horaria_cumprida agora é soft-com-défice (RN05 relaxada, RF13) — mas
    # este diagnóstico existe precisamente para provar INFEASIBLE genuíno, então aqui
    # (e só aqui) travamos o défice a zero para recuperar a semântica hard original.
    for deficit_var in deficits.values():
        model.Add(deficit_var == 0)

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
