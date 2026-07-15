# Implementa: RF11, RF12 (UC11, UC12) — traduz variáveis resolvidas do CP-SAT em Alocacao
from collections import defaultdict

from ortools.sat.python import cp_model

from app.solver.builder import VariaveisModelo
from app.solver.constraints_soft import penalizacao_rn04, penalizacao_rn08
from app.solver.dto import AlocacaoResult, HorarioInput


def mapear_resultado(
    solver: cp_model.CpSolver, variaveis: VariaveisModelo, dados: HorarioInput
) -> list[AlocacaoResult]:
    """Extrai as variáveis com valor 1 e devolve AlocacaoResult prontas para persistência.

    `penalizacao_aplicada` é recalculada aqui (mesma fórmula do objetivo) apenas para
    fins de auditoria (RN04/RN08) — quem persiste em `Alocacao` é a service layer.
    """
    slots_disponiveis: dict[int, set[int]] = defaultdict(set)
    for disp in dados.disponibilidades:
        slots_disponiveis[disp.professor_id].add(disp.slot_id)
    professores_com_registo = set(slots_disponiveis.keys())

    capacidade_sala = {sala.id: sala.capacidade for sala in dados.salas}
    alunos_turma = {turma.id: turma.numero_alunos for turma in dados.turmas}

    alocacoes = []
    for chave, var in variaveis.x.items():
        if solver.Value(var) != 1:
            continue

        turma_id, disciplina_id, professor_id, sala_id, slot_id = chave
        penalizacao = penalizacao_rn04(chave, slots_disponiveis, professores_com_registo) + penalizacao_rn08(
            chave, capacidade_sala, alunos_turma
        )
        alocacoes.append(
            AlocacaoResult(
                turma_id=turma_id,
                disciplina_id=disciplina_id,
                professor_id=professor_id,
                sala_id=sala_id,
                slot_id=slot_id,
                penalizacao_aplicada=float(penalizacao),
            )
        )

    return alocacoes
