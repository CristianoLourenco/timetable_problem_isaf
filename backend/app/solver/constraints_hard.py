# Implementa: RN01, RN02, RN03, RN05, RN06 — ver docs/analise_requisitos_v5.0.md secção 6
from collections import defaultdict

from ortools.sat.python import cp_model

from app.solver.builder import ChaveVar, VariaveisModelo
from app.solver.dto import HorarioInput


def add_professor_sem_dupla_alocacao(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN01 — professor sem dupla alocação no mesmo slot."""
    for professor in dados.professores:
        for slot in dados.slots:
            chaves = variaveis.por_professor_slot.get((professor.id, slot.id), [])
            if chaves:
                model.Add(sum(variaveis.x[c] for c in chaves) <= 1)


def add_turma_sem_dupla_disciplina(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN02 — turma sem duas disciplinas no mesmo slot."""
    for turma in dados.turmas:
        for slot in dados.slots:
            chaves = variaveis.por_turma_slot.get((turma.id, slot.id), [])
            if chaves:
                model.Add(sum(variaveis.x[c] for c in chaves) <= 1)


def add_sala_sem_dupla_turma(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN03 — sala sem duas turmas no mesmo slot."""
    for sala in dados.salas:
        for slot in dados.slots:
            chaves = variaveis.por_sala_slot.get((sala.id, slot.id), [])
            if chaves:
                model.Add(sum(variaveis.x[c] for c in chaves) <= 1)


def add_carga_horaria_cumprida(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN05 — carga horária semanal da disciplina cumprida integralmente."""
    for td in dados.turma_disciplinas:
        chaves = variaveis.por_turma_disciplina.get((td.turma_id, td.disciplina_id), [])
        model.Add(sum(variaveis.x[c] for c in chaves) == td.carga_horaria_semanal)


def add_agrupamento_em_blocos(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN06 — aulas agrupadas em blocos contíguos (>=2 tempos), sem tempos isolados.

    Aplicada à sequência x[turma, disciplina, professor, sala, *] de cada dia — e não
    a um agregado por turma+disciplina — para que um bloco nunca troque de docente/sala
    a meio (decisão confirmada com o utilizador: bloco = mesmo professor e mesma sala
    do início ao fim). RN02 garante que a turma não tem duas disciplinas no mesmo slot,
    logo não há ambiguidade entre blocos de disciplinas diferentes no mesmo dia.
    """
    slots_por_dia: dict[str, list] = defaultdict(list)
    for slot in dados.slots:
        slots_por_dia[slot.dia_semana].append(slot)
    for slots_do_dia in slots_por_dia.values():
        slots_do_dia.sort(key=lambda s: s.tempo_ordem)

    for chaves in variaveis.por_turma_disciplina_professor_sala.values():
        slot_para_chave: dict[int, ChaveVar] = {chave[4]: chave for chave in chaves}

        for slots_do_dia in slots_por_dia.values():
            sequencia = [slot_para_chave.get(slot.id) for slot in slots_do_dia]
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
