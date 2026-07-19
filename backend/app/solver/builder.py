# Implementa: RN01-RN08 — geração esparsa de variáveis do modelo CP-SAT
# ver docs/04_04_analise_desenvolvimento.md secção 4.3.3 e skill ortools-timetabling-solver.
#
# Nota de modelagem (resolve uma ambiguidade entre a skill e a fonte de verdade):
# a disponibilidade do professor NÃO filtra variáveis aqui — RN04 está classificada
# como Soft em docs/04_04_analise_desenvolvimento.md secção 4.1.2, logo alocações fora da
# disponibilidade registada devem continuar possíveis (apenas penalizadas em
# constraints_soft.py). Só RN07 (sem registo = totalmente disponível) depende disto,
# e é aplicado no cálculo da penalização, não na geração de variáveis.
from collections import defaultdict
from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from app.solver.dto import HorarioInput

# chave esparsa: (turma_id, disciplina_id, professor_id, sala_id, dia_semana, turno, periodo)
# — não existe slot_id/tabela Slot (ver app/core/calendario.py); periodo reinicia em 1
# a cada turno, por isso turno faz sempre parte da chave.
ChaveVar = tuple[int, int, int, int, str, str, int]


@dataclass
class VariaveisModelo:
    x: dict[ChaveVar, cp_model.IntVar]
    por_professor_tempo: dict[tuple[int, str, str, int], list[ChaveVar]] = field(
        default_factory=lambda: defaultdict(list)
    )
    por_turma_tempo: dict[tuple[int, str, str, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_sala_tempo: dict[tuple[int, str, str, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_turma_disciplina: dict[tuple[int, int], list[ChaveVar]] = field(default_factory=lambda: defaultdict(list))
    por_turma_disciplina_professor_sala: dict[tuple[int, int, int, int], list[ChaveVar]] = field(
        default_factory=lambda: defaultdict(list)
    )


def atribuir_salas_por_turma_turno(dados: HorarioInput) -> dict[tuple[int, str], int]:
    """Decide, de forma determinística e FORA do CP-SAT, uma única sala por
    (turma_id, turno) — a turma usa essa mesma sala do início ao fim do turno,
    mesmo trocando de disciplina (decisão confirmada com o utilizador,
    2026-07-19: "uma vez encontrada [a sala] naquele turno, [a turma] deve ter
    o seu horário gerado naquela sala por completo naquele período").

    Isto substitui a escolha de sala como parte da otimização do CP-SAT — RN08
    (capacidade mais próxima) já é satisfeita aqui pelo mesmo critério de
    desempate usado antes (menor excesso de capacidade, hash(turma,sala) para
    quebrar empates sem convergir turmas parecidas para as mesmas salas).
    Reduz drasticamente o nº de BoolVar (de até `solver_max_salas_candidatas`
    salas candidatas por tempo para 1 sala fixa por turma+turno) e elimina por
    construção qualquer troca de sala dentro do mesmo turno — nunca precisa de
    uma restrição hard extra no modelo para impedir isso.

    Duas turmas do MESMO turno nunca recebem a mesma sala (glutão por ordem de
    `numero_alunos` decrescente — turmas maiores, com menos salas candidatas,
    escolhem primeiro); turmas de turnos DIFERENTES podem repetir a mesma sala
    livremente (nunca estão simultaneamente em uso)."""
    turmas_por_turno: dict[str, list] = defaultdict(list)
    for turma in dados.turmas:
        turmas_por_turno[turma.turno].append(turma)

    atribuicao: dict[tuple[int, str], int] = {}
    for turno, turmas_do_turno in turmas_por_turno.items():
        salas_ocupadas_no_turno: set[int] = set()
        # Turmas maiores primeiro — têm menos salas candidatas (capacidade
        # mínima mais alta), logo devem escolher antes que as menores
        # esgotem as salas pequenas que também lhes serviriam.
        for turma in sorted(turmas_do_turno, key=lambda t: -t.numero_alunos):
            candidatas = sorted(
                (
                    sala
                    for sala in dados.salas
                    if sala.capacidade >= turma.numero_alunos and sala.id not in salas_ocupadas_no_turno
                ),
                key=lambda sala: (sala.capacidade - turma.numero_alunos, hash((turma.id, sala.id))),
            )
            if not candidatas:
                continue  # sem sala livre e com capacidade suficiente — surge no diagnóstico se INFEASIBLE
            sala_escolhida = candidatas[0]
            atribuicao[(turma.id, turno)] = sala_escolhida.id
            salas_ocupadas_no_turno.add(sala_escolhida.id)
    return atribuicao


def build_variables(
    model: cp_model.CpModel,
    dados: HorarioInput,
    chaves_professor_ocupadas: frozenset[tuple[int, str, str, int]] = frozenset(),
) -> VariaveisModelo:
    """Gera x[turma, disciplina, professor, sala, dia, turno, periodo] só para combinações válidas.

    Filtragem em cascata (nunca modelagem densa turma x disciplina x professor x sala x tempo):
      1. TurmaDisciplina -> só pares (turma, disciplina) da grade curricular (conjunto E).
      2. ProfessorDisciplina -> só professores qualificados para a disciplina.
      3. Só tempos do turno da turma (uma turma nunca é alocada fora do seu turno).
      3.5. `chaves_professor_ocupadas` -> exclui (professor, dia, turno, periodo) já
         fixados por uma fase anterior de uma decomposição por turno (ver
         app/solver/orquestrador_turnos.py). Com a configuração atual de
         `turno_hora_inicio`/`turno_periodos` (core/config.py) os turnos nunca se
         sobrepõem em hora real e RN01 já chaveia por turno, logo isto é um no-op
         hoje — fica como proteção defensiva única (nunca duplicada) caso essa
         configuração mude para turnos sobrepostos no futuro.
      4. Sala: UMA única sala por (turma, turno) — ver atribuir_salas_por_turma_turno.
         Não é mais uma escolha do CP-SAT entre top-K candidatas: a turma usa a
         mesma sala do início ao fim do turno, decidido fora do modelo.

    Disponibilidade (RN04) não filtra aqui — é soft, ver nota de modelagem acima.
    """
    professores_por_disciplina: dict[int, list[int]] = defaultdict(list)
    for pd in dados.professor_disciplinas:
        professores_por_disciplina[pd.disciplina_id].append(pd.professor_id)

    sala_por_turma_turno = atribuir_salas_por_turma_turno(dados)

    slots_por_turno: dict[str, list] = defaultdict(list)
    for slot in dados.slots:
        slots_por_turno[slot.turno].append(slot)

    turmas_por_id = {turma.id: turma for turma in dados.turmas}

    variaveis = VariaveisModelo(x={})

    for td in dados.turma_disciplinas:
        turma = turmas_por_id.get(td.turma_id)
        if turma is None:
            continue

        sala_id = sala_por_turma_turno.get((td.turma_id, turma.turno))
        if sala_id is None:
            continue  # nenhuma sala comporta a turma — surge no diagnóstico se INFEASIBLE
        salas_validas = [sala_id]

        professores_qualificados = professores_por_disciplina.get(td.disciplina_id, [])
        slots_do_turno = slots_por_turno.get(turma.turno, [])
        for professor_id in professores_qualificados:
            for slot in slots_do_turno:
                if (professor_id, slot.dia_semana, slot.turno, slot.periodo) in chaves_professor_ocupadas:
                    continue
                for sala_id in salas_validas:
                    chave = (
                        td.turma_id,
                        td.disciplina_id,
                        professor_id,
                        sala_id,
                        slot.dia_semana,
                        slot.turno,
                        slot.periodo,
                    )
                    nome = (
                        f"x_t{td.turma_id}_d{td.disciplina_id}_p{professor_id}_s{sala_id}"
                        f"_{slot.dia_semana}_{slot.turno}_{slot.periodo}"
                    )
                    var = model.NewBoolVar(nome)

                    tempo_chave = (slot.dia_semana, slot.turno, slot.periodo)
                    variaveis.x[chave] = var
                    variaveis.por_professor_tempo[(professor_id, *tempo_chave)].append(chave)
                    variaveis.por_turma_tempo[(td.turma_id, *tempo_chave)].append(chave)
                    variaveis.por_sala_tempo[(sala_id, *tempo_chave)].append(chave)
                    variaveis.por_turma_disciplina[(td.turma_id, td.disciplina_id)].append(chave)
                    variaveis.por_turma_disciplina_professor_sala[
                        (td.turma_id, td.disciplina_id, professor_id, sala_id)
                    ].append(chave)

    return variaveis
