# Implementa: RN01, RN02, RN03, RN05, RN06 — ver docs/relatorio/04_analise_desenvolvimento/ secção 4.1.2
from collections import defaultdict

from ortools.sat.python import cp_model

from app.solver.builder import ChaveVar, VariaveisModelo
from app.solver.dto import HorarioInput


def add_professor_sem_dupla_alocacao(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN01 — professor sem dupla alocação no mesmo tempo."""
    for professor in dados.professores:
        for slot in dados.slots:
            chaves = variaveis.por_professor_tempo.get((professor.id, slot.dia_semana, slot.turno, slot.periodo), [])
            if chaves:
                model.Add(sum(variaveis.x[c] for c in chaves) <= 1)


def add_turma_sem_dupla_disciplina(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN02 — turma sem duas disciplinas no mesmo tempo."""
    for turma in dados.turmas:
        for slot in dados.slots:
            chaves = variaveis.por_turma_tempo.get((turma.id, slot.dia_semana, slot.turno, slot.periodo), [])
            if chaves:
                model.Add(sum(variaveis.x[c] for c in chaves) <= 1)


def add_sala_sem_dupla_turma(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN03 — sala sem duas turmas no mesmo tempo."""
    for sala in dados.salas:
        for slot in dados.slots:
            chaves = variaveis.por_sala_tempo.get((sala.id, slot.dia_semana, slot.turno, slot.periodo), [])
            if chaves:
                model.Add(sum(variaveis.x[c] for c in chaves) <= 1)


def add_carga_horaria_cumprida(
    model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput
) -> dict[tuple[int, int], cp_model.IntVar]:
    """RN05 — carga horária semanal da disciplina, soft-com-défice: o solver
    NUNCA mais fica INFEASIBLE por escassez de professor/tempo (RF13) — em vez
    disso, os tempos que não conseguir alocar ficam registados numa IntVar de
    défice por (turma, disciplina), fortemente penalizada no objetivo
    (constraints_soft.build_objective) para que o solver só aceite défice
    quando for genuinamente impossível preencher tudo. Quando `chaves` está
    vazio (sem professor qualificado / sem sala válida, já detectado por
    preprocessamento.podar_dominio), o défice fica automaticamente no valor
    máximo sem envolver nenhuma variável de alocação."""
    deficits: dict[tuple[int, int], cp_model.IntVar] = {}
    for td in dados.turma_disciplinas:
        chaves = variaveis.por_turma_disciplina.get((td.turma_id, td.disciplina_id), [])
        deficit = model.NewIntVar(
            0, td.carga_horaria_semanal, f"deficit_t{td.turma_id}_d{td.disciplina_id}"
        )
        model.Add(sum(variaveis.x[c] for c in chaves) + deficit == td.carga_horaria_semanal)
        deficits[(td.turma_id, td.disciplina_id)] = deficit
    return deficits


def add_agrupamento_em_blocos(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN06 — aulas agrupadas em blocos contíguos (>=2 tempos), sem tempos isolados.

    Aplicada à sequência x[turma, disciplina, professor, sala, *] de cada (dia, turno) —
    e não a um agregado por turma+disciplina — para que um bloco nunca troque de
    docente/sala a meio (decisão confirmada com o utilizador: bloco = mesmo professor e
    mesma sala do início ao fim). Agrupar por (dia, turno) e não só por dia evita que
    tempos de turnos diferentes (periodo reinicia em 1 a cada turno) sejam tratados como
    vizinhos. RN02 garante que a turma não tem duas disciplinas no mesmo tempo, logo não
    há ambiguidade entre blocos de disciplinas diferentes no mesmo (dia, turno).
    """
    slots_por_dia_turno: dict[tuple[str, str], list] = defaultdict(list)
    for slot in dados.slots:
        slots_por_dia_turno[(slot.dia_semana, slot.turno)].append(slot)
    for slots_do_grupo in slots_por_dia_turno.values():
        slots_do_grupo.sort(key=lambda s: s.periodo)

    for chaves in variaveis.por_turma_disciplina_professor_sala.values():
        tempo_para_chave: dict[tuple[str, str, int], ChaveVar] = {chave[4:7]: chave for chave in chaves}

        for slots_do_grupo in slots_por_dia_turno.values():
            sequencia = [
                tempo_para_chave.get((slot.dia_semana, slot.turno, slot.periodo)) for slot in slots_do_grupo
            ]
            _proibir_tempo_isolado(model, variaveis, sequencia)


def _proibir_tempo_isolado(
    model: cp_model.CpModel, variaveis: VariaveisModelo, sequencia: list[ChaveVar | None]
) -> None:
    """Janela deslizante sobre a sequência diária — proíbe o padrão 0,1,0 (tempo isolado).

    Nas fronteiras do dia (primeiro/último tempo), um tempo usado implica o vizinho
    imediato também usado; um tempo sem nenhum vizinho no dia nunca pode ser usado.
    """
    n = len(sequencia)
    for i, chave_atual in enumerate(sequencia):
        if chave_atual is None:
            continue
        var_atual = variaveis.x[chave_atual]
        chave_anterior = sequencia[i - 1] if i > 0 else None
        chave_seguinte = sequencia[i + 1] if i < n - 1 else None

        if chave_anterior is None and chave_seguinte is None:
            model.Add(var_atual == 0)
        elif chave_anterior is None:
            model.Add(var_atual <= variaveis.x[chave_seguinte])
        elif chave_seguinte is None:
            model.Add(var_atual <= variaveis.x[chave_anterior])
        else:
            model.AddBoolOr([variaveis.x[chave_anterior], var_atual.Not(), variaveis.x[chave_seguinte]])
