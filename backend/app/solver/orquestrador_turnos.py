# Implementa: RF09/RF13 — decomposição por turno (Manhã → Tarde → Noite)
# ver docs/relatorio/04_analise_desenvolvimento/ secção 4.3.3.
#
# Com a configuração atual de turno_hora_inicio/turno_periodos (core/config.py) os
# três turnos nunca se sobrepõem em hora real, e RN01 já chaveia por turno — logo
# decompor em 3 sub-modelos independentes não corrige nenhum conflito duro genuíno,
# é sobretudo uma redução do tamanho de cada modelo CP-SAT individual, tornando
# viável encontrar uma solução completa dentro do orçamento de tempo à escala real
# do ISAF (RNF01). `chaves_professor_ocupadas` (builder.py) e `contagem_diaria_fixa`
# (constraints_soft.py) propagam o que cada fase já decidiu para a fase seguinte —
# sem eles a fase da Tarde trataria cada professor como se começasse o dia do zero.
from app.solver.dto import AlocacaoResult, HorarioInput, SolverResult
from app.solver.prioridade_docente import calcular_prioridades
from app.solver.solve import resolver_horario

_ORDEM_TURNOS_PADRAO = ("manha", "tarde", "noite")

# Fração mínima do orçamento total garantida a cada turno ativo, mesmo que a
# estimativa de tamanho lhe atribua uma fatia proporcional menor — nunca deixar
# um turno pequeno com um tempo tão curto que nem o warm-start/construção do
# modelo (~2-3s medido à escala real do ISAF) tenha margem para correr.
_FRACAO_MINIMA_POR_TURNO = 0.15


def _estimar_tamanho_turno(dados: HorarioInput) -> int:
    """Proxy barata do nº de variáveis que build_variables() geraria para este
    sub-problema, sem construir nenhuma BoolVar — soma, por (turma, disciplina),
    o nº de professores qualificados vezes o nº de slots do turno da turma
    (o nº de salas candidatas é o mesmo teto para todas as turmas, por isso não
    muda a proporção RELATIVA entre turnos e pode ser omitido do produto).
    Calibrado contra medições reais à escala do ISAF em 2026-07-19: Manhã
    (35250 vars reais) convergiu em 75s, Tarde (48625 vars reais) não convergiu
    em 100s — confirma que mais variáveis correlaciona com mais dificuldade,
    justificando distribuir o orçamento proporcionalmente a esta estimativa."""
    professores_por_disciplina: dict[int, int] = {}
    for pd in dados.professor_disciplinas:
        professores_por_disciplina[pd.disciplina_id] = professores_por_disciplina.get(pd.disciplina_id, 0) + 1

    slots_por_turno: dict[str, int] = {}
    for slot in dados.slots:
        slots_por_turno[slot.turno] = slots_por_turno.get(slot.turno, 0) + 1

    turmas_por_id = {turma.id: turma for turma in dados.turmas}

    total = 0
    for td in dados.turma_disciplinas:
        turma = turmas_por_id.get(td.turma_id)
        if turma is None:
            continue
        n_professores = professores_por_disciplina.get(td.disciplina_id, 0)
        n_slots = slots_por_turno.get(turma.turno, 0)
        total += n_professores * n_slots
    return total


def _distribuir_orcamento(
    dados_por_turno: dict[str, HorarioInput], orcamento_total: float
) -> dict[str, float]:
    """Divide `orcamento_total` entre os turnos ativos proporcionalmente ao
    tamanho estimado de cada um (ver `_estimar_tamanho_turno`), com um piso de
    `_FRACAO_MINIMA_POR_TURNO` do valor que cada turno receberia numa divisão
    igual — evita que um turno pequeno fique com tempo insuficiente mesmo para
    a construção do modelo, sem deixar de dar mais tempo ao turno maior."""
    tamanhos = {turno: _estimar_tamanho_turno(sub_dados) for turno, sub_dados in dados_por_turno.items()}
    total_tamanho = sum(tamanhos.values())
    n_turnos = len(dados_por_turno)

    if total_tamanho == 0 or n_turnos == 0:
        # Sem sinal para distribuir de forma proporcional — divide em partes iguais.
        return {turno: orcamento_total / n_turnos for turno in dados_por_turno} if n_turnos else {}

    piso = _FRACAO_MINIMA_POR_TURNO * (orcamento_total / n_turnos)
    brutos = {turno: (tamanhos[turno] / total_tamanho) * orcamento_total for turno in dados_por_turno}
    com_piso = {turno: max(valor, piso) for turno, valor in brutos.items()}

    # Reescalar para a soma continuar a ser exatamente orcamento_total, já que
    # aplicar o piso pode ter feito a soma ultrapassar o total pedido.
    soma_com_piso = sum(com_piso.values())
    fator = orcamento_total / soma_com_piso if soma_com_piso > 0 else 1.0
    return {turno: valor * fator for turno, valor in com_piso.items()}


def _filtrar_por_turno(dados: HorarioInput, turno: str) -> HorarioInput:
    """Restringe turmas/turma_disciplinas/slots ao turno; professores/salas/
    professor_disciplinas/disponibilidades ficam completos (não são turno-específicos
    a priori) — a poda ao que é realmente relevante nesta fase (ver
    app/solver/preprocessamento.py) acontece automaticamente dentro de
    resolver_horario(), que já chama podar_dominio() como primeiro passo."""
    turma_ids = {turma.id for turma in dados.turmas if turma.turno == turno}
    return HorarioInput(
        turmas=[t for t in dados.turmas if t.id in turma_ids],
        professores=dados.professores,
        salas=dados.salas,
        slots=[s for s in dados.slots if s.turno == turno],
        turma_disciplinas=[td for td in dados.turma_disciplinas if td.turma_id in turma_ids],
        professor_disciplinas=dados.professor_disciplinas,
        disponibilidades=dados.disponibilidades,
    )


def resolver_horario_por_turnos(
    dados: HorarioInput,
    max_time_in_seconds_total: float,
    num_search_workers: int = 8,
    relative_gap_limit: float | None = None,
    ordem_turnos: tuple[str, ...] = _ORDEM_TURNOS_PADRAO,
) -> SolverResult:
    """Resolve cada turno em sequência, com as alocações de professores de fases
    anteriores fixadas (nunca reatribuídas) na fase seguinte. Se uma fase posterior
    der INFEASIBLE (UNKNOWN por tempo esgotado — ver nota abaixo), o `SolverResult`
    devolvido preserva as alocações/pendências já resolvidas das fases anteriores
    em vez de as descartar, para o Gestor não perder o trabalho já feito só porque
    uma fase seguinte precisou de mais tempo do que o orçamento permitia — mesmo
    assim `status="INFEASIBLE"` sinaliza que o resultado está incompleto (Job tem
    um único par status/diagnostico, sem um estado "parcialmente pronto" dedicado).

    `max_time_in_seconds_total` é o orçamento AGREGADO das 3 fases, não um valor
    fixo por turno — distribuído proporcionalmente ao tamanho estimado de cada
    turno ativo (ver `_distribuir_orcamento`/`_estimar_tamanho_turno`). Achado
    real medido à escala do ISAF (2026-07-19): um valor fixo igual para todos os
    turnos desperdiça tempo no turno pequeno (converge bem antes do teto) e falta
    tempo ao turno grande (não converge nem no dobro do tempo do pequeno).

    `prioridades` (RN12) é calculada uma única vez sobre `dados` completo (semana
    toda, não filtrado por turno) — a escassez de disponibilidade tem de refletir
    a semana inteira, não uma fatia."""
    prioridades = calcular_prioridades(dados.professores, dados.disponibilidades)

    dados_por_turno = {
        turno: sub_dados
        for turno in ordem_turnos
        if (sub_dados := _filtrar_por_turno(dados, turno)).turmas
    }
    tempo_por_turno = _distribuir_orcamento(dados_por_turno, max_time_in_seconds_total)

    chaves_ocupadas: set[tuple[int, str, str, int]] = set()
    contagem_diaria: dict[tuple[int, str], int] = {}
    todas_alocacoes: list[AlocacaoResult] = []
    todas_pendencias: list = []
    alguma_fase_feasible = False

    for turno, sub_dados in dados_por_turno.items():
        resultado = resolver_horario(
            sub_dados,
            max_time_in_seconds=tempo_por_turno[turno],
            num_search_workers=num_search_workers,
            relative_gap_limit=relative_gap_limit,
            prioridades=prioridades,
            chaves_professor_ocupadas=frozenset(chaves_ocupadas),
            contagem_diaria_fixa=dict(contagem_diaria),
        )

        if resultado.status == "INFEASIBLE":
            # Só resta UNKNOWN por tempo esgotado (RF13 — RN05 nunca mais bloqueia
            # por escassez) — identifica a fase que não teve tempo, cumpre RNF03.
            # Preserva alocações/pendências já resolvidas de fases anteriores em vez
            # de as descartar: o Gestor não perde o trabalho já feito só porque uma
            # fase seguinte precisou de mais tempo do que o orçamento permitia.
            return SolverResult(
                status="INFEASIBLE",
                alocacoes=todas_alocacoes,
                diagnostico=f"[Turno {turno}] {resultado.diagnostico}",
                pendencias=todas_pendencias,
            )

        if resultado.status == "FEASIBLE":
            alguma_fase_feasible = True

        for aloc in resultado.alocacoes:
            chaves_ocupadas.add((aloc.professor_id, aloc.dia_semana, aloc.turno, aloc.periodo))
            chave_dia = (aloc.professor_id, aloc.dia_semana)
            contagem_diaria[chave_dia] = contagem_diaria.get(chave_dia, 0) + 1
        todas_alocacoes.extend(resultado.alocacoes)
        todas_pendencias.extend(resultado.pendencias)

    status_final = "FEASIBLE" if alguma_fase_feasible else "OPTIMAL"
    return SolverResult(status=status_final, alocacoes=todas_alocacoes, diagnostico=None, pendencias=todas_pendencias)
