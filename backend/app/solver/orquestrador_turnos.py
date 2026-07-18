# Implementa: RF09/RF13 — decomposição por turno (Manhã → Tarde → Noite)
# ver docs/04_04_analise_desenvolvimento.md secção 4.3.3.
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
    max_time_in_seconds_por_turno: float,
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

    `prioridades` (RN12) é calculada uma única vez sobre `dados` completo (semana
    toda, não filtrado por turno) — a escassez de disponibilidade tem de refletir
    a semana inteira, não uma fatia."""
    prioridades = calcular_prioridades(dados.professores, dados.disponibilidades)

    chaves_ocupadas: set[tuple[int, str, str, int]] = set()
    contagem_diaria: dict[tuple[int, str], int] = {}
    todas_alocacoes: list[AlocacaoResult] = []
    todas_pendencias: list = []
    alguma_fase_feasible = False

    for turno in ordem_turnos:
        sub_dados = _filtrar_por_turno(dados, turno)
        if not sub_dados.turmas:
            continue  # nenhuma turma deste turno neste âmbito — nada a resolver

        resultado = resolver_horario(
            sub_dados,
            max_time_in_seconds=max_time_in_seconds_por_turno,
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
