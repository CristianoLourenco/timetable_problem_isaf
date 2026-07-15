# Implementa: RN01-RN08 — geração esparsa de variáveis do modelo CP-SAT
# ver docs/06_arquitetura_backend.md secção "Fase 3" e skill ortools-timetabling-solver.
#
# Nota de modelagem (resolve uma ambiguidade entre a skill e a fonte de verdade):
# a disponibilidade do professor NÃO filtra variáveis aqui — RN04 está classificada
# como Soft em docs/analise_requisitos_v5.0.md secção 6, logo alocações fora da
# disponibilidade registada devem continuar possíveis (apenas penalizadas em
# constraints_soft.py). Só RN07 (sem registo = totalmente disponível) depende disto,
# e é aplicado no cálculo da penalização, não na geração de variáveis.
from collections import defaultdict
from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from app.solver.dto import HorarioInput

# chave esparsa: (turma_id, disciplina_id, professor_id, sala_id, slot_id)
ChaveVar = tuple[int, int, int, int, int]


@dataclass
class VariaveisModelo:
    x: dict[ChaveVar, cp_model.IntVar]
    por_professor_slot: dict[tuple[int, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_turma_slot: dict[tuple[int, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_sala_slot: dict[tuple[int, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_turma_disciplina: dict[tuple[int, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_turma_disciplina_professor_sala: dict[tuple[int, int, int, int], list[ChaveVar]] = field(
        default_factory=lambda: defaultdict(list)
    )


def build_variables(model: cp_model.CpModel, dados: HorarioInput) -> VariaveisModelo:
    """Gera x[turma, disciplina, professor, sala, slot] apenas para combinações válidas.

    Filtragem em cascata (nunca modelagem densa turma x disciplina x professor x sala x slot):
      1. TurmaDisciplina -> só pares (turma, disciplina) da grade curricular (conjunto E).
      2. ProfessorDisciplina -> só professores qualificados para a disciplina.
      3. Todos os slots (disponibilidade é soft — ver nota de modelagem acima).
      4. Sala com capacidade >= numero_alunos da turma (necessidade física; a
         proximidade "ideal" de capacidade, RN08, é soft e tratada no objetivo).
    """
    professores_por_disciplina: dict[int, list[int]] = defaultdict(list)
    for pd in dados.professor_disciplinas:
        professores_por_disciplina[pd.disciplina_id].append(pd.professor_id)

    salas_com_capacidade: dict[int, list[int]] = defaultdict(list)
    for turma in dados.turmas:
        for sala in dados.salas:
            if sala.capacidade >= turma.numero_alunos:
                salas_com_capacidade[turma.id].append(sala.id)

    variaveis = VariaveisModelo(x={})

    for td in dados.turma_disciplinas:
        salas_validas = salas_com_capacidade.get(td.turma_id, [])
        if not salas_validas:
            continue  # nenhuma sala comporta a turma — surge no diagnóstico se INFEASIBLE

        professores_qualificados = professores_por_disciplina.get(td.disciplina_id, [])
        for professor_id in professores_qualificados:
            for slot in dados.slots:
                for sala_id in salas_validas:
                    chave = (td.turma_id, td.disciplina_id, professor_id, sala_id, slot.id)
                    nome = f"x_t{td.turma_id}_d{td.disciplina_id}_p{professor_id}_s{sala_id}_sl{slot.id}"
                    var = model.NewBoolVar(nome)

                    variaveis.x[chave] = var
                    variaveis.por_professor_slot[(professor_id, slot.id)].append(chave)
                    variaveis.por_turma_slot[(td.turma_id, slot.id)].append(chave)
                    variaveis.por_sala_slot[(sala_id, slot.id)].append(chave)
                    variaveis.por_turma_disciplina[(td.turma_id, td.disciplina_id)].append(chave)
                    variaveis.por_turma_disciplina_professor_sala[
                        (td.turma_id, td.disciplina_id, professor_id, sala_id)
                    ].append(chave)

    return variaveis
