# Implementa: RN04, RN08 + função objetivo (equidade, secção 5-C) — docs/analise_requisitos_v5.0.md secção 6
from collections import defaultdict

from ortools.sat.python import cp_model

from app.core.config import settings
from app.solver.builder import ChaveVar, VariaveisModelo
from app.solver.dto import HorarioInput


def penalizacao_rn04(
    chave: ChaveVar, slots_disponiveis: dict[int, set[int]], professores_com_registo: set[int]
) -> int:
    """RN04 — penaliza alocação fora da disponibilidade registada do professor.

    RN07: professor sem nenhum registo de disponibilidade = totalmente disponível,
    logo nunca é penalizado.
    """
    _, _, professor_id, _, slot_id = chave
    if professor_id not in professores_com_registo:
        return 0
    return 0 if slot_id in slots_disponiveis[professor_id] else 1


def penalizacao_rn08(chave: ChaveVar, capacidade_sala: dict[int, int], alunos_turma: dict[int, int]) -> int:
    """RN08 — penaliza capacidade de sala excedente face ao número de alunos da turma."""
    turma_id, _, _, sala_id, _ = chave
    return capacidade_sala[sala_id] - alunos_turma[turma_id]


def build_objective(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput):
    """Monta o termo a minimizar: peso_RN04 x RN04 + peso_RN08 x RN08 + peso_equidade x amplitude diária."""
    slots_disponiveis: dict[int, set[int]] = defaultdict(set)
    for disp in dados.disponibilidades:
        slots_disponiveis[disp.professor_id].add(disp.slot_id)
    professores_com_registo = set(slots_disponiveis.keys())

    capacidade_sala = {sala.id: sala.capacidade for sala in dados.salas}
    alunos_turma = {turma.id: turma.numero_alunos for turma in dados.turmas}

    termos_rn04 = []
    termos_rn08 = []
    for chave, var in variaveis.x.items():
        peso_rn04 = penalizacao_rn04(chave, slots_disponiveis, professores_com_registo)
        if peso_rn04:
            termos_rn04.append(peso_rn04 * var)

        peso_rn08 = penalizacao_rn08(chave, capacidade_sala, alunos_turma)
        if peso_rn08:
            termos_rn08.append(peso_rn08 * var)

    termo_equidade = _construir_termo_equidade(model, variaveis, dados)

    return (
        settings.solver_peso_rn04_disponibilidade * sum(termos_rn04)
        + settings.solver_peso_rn08_capacidade * sum(termos_rn08)
        + settings.solver_peso_equidade_diaria * termo_equidade
    )


def _construir_termo_equidade(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput):
    """Equidade — minimiza a amplitude (máximo - mínimo) de aulas por dia, por professor.

    Proxy linear da "variância de distribuição diária" (docs/analise_requisitos_v5.0.md
    secção 6): CP-SAT não modela variância diretamente em termos lineares, e reduzir a
    amplitude entre o dia mais cheio e o mais vazio de cada professor tem o mesmo efeito
    prático de equilibrar a carga ao longo da semana.
    """
    dias = sorted({slot.dia_semana for slot in dados.slots})
    slots_por_dia: dict[str, list[int]] = defaultdict(list)
    for slot in dados.slots:
        slots_por_dia[slot.dia_semana].append(slot.id)

    termos_amplitude = []
    for professor in dados.professores:
        contagens_diarias = []
        total_chaves_professor = 0
        for dia in dias:
            chaves_do_dia = [
                chave
                for slot_id in slots_por_dia[dia]
                for chave in variaveis.por_professor_slot.get((professor.id, slot_id), [])
            ]
            total_chaves_professor += len(chaves_do_dia)
            if not chaves_do_dia:
                continue
            contagem = model.NewIntVar(0, len(chaves_do_dia), f"contagem_p{professor.id}_{dia}")
            model.Add(contagem == sum(variaveis.x[c] for c in chaves_do_dia))
            contagens_diarias.append(contagem)

        if len(contagens_diarias) < 2:
            continue  # sem variação possível entre dias

        maximo = model.NewIntVar(0, total_chaves_professor, f"max_p{professor.id}")
        minimo = model.NewIntVar(0, total_chaves_professor, f"min_p{professor.id}")
        model.AddMaxEquality(maximo, contagens_diarias)
        model.AddMinEquality(minimo, contagens_diarias)
        termos_amplitude.append(maximo - minimo)

    return sum(termos_amplitude)
