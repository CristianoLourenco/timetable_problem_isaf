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

from app.core.config import settings
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


def build_variables(model: cp_model.CpModel, dados: HorarioInput) -> VariaveisModelo:
    """Gera x[turma, disciplina, professor, sala, dia, turno, periodo] só para combinações válidas.

    Filtragem em cascata (nunca modelagem densa turma x disciplina x professor x sala x tempo):
      1. TurmaDisciplina -> só pares (turma, disciplina) da grade curricular (conjunto E).
      2. ProfessorDisciplina -> só professores qualificados para a disciplina.
      3. Só tempos do turno da turma (uma turma nunca é alocada fora do seu turno).
      4. Sala com capacidade >= numero_alunos da turma, limitada às
         `settings.solver_max_salas_candidatas` salas com o excesso de capacidade mais
         baixo (necessidade física; a proximidade "ideal" de capacidade, RN08, é soft e
         tratada no objetivo — mas RN08 já define "capacidade mínima viável" como a
         alocação preferencial, logo as salas fora do top-K nunca seriam escolhidas numa
         solução ótima a não ser por conflito, e o top-K deixa folga suficiente para
         isso). Sem este limite, todas as salas com capacidade suficiente entram como
         candidatas — a maioria qualifica, criando simetria severa entre salas
         semelhantes e inflando o nº de BoolVar em ~5-10x sem ganho real (medido em
         benchmark à escala real do ISAF).

    Disponibilidade (RN04) não filtra aqui — é soft, ver nota de modelagem acima.
    """
    professores_por_disciplina: dict[int, list[int]] = defaultdict(list)
    for pd in dados.professor_disciplinas:
        professores_por_disciplina[pd.disciplina_id].append(pd.professor_id)

    salas_com_capacidade: dict[int, list[int]] = defaultdict(list)
    for turma in dados.turmas:
        # Desempate por hash(turma, sala) em vez de sala.id: turmas de tamanho
        # semelhante têm o mesmo grupo de salas empatadas em excesso de capacidade —
        # sem isto, um desempate fixo faria TODAS convergirem para as mesmas K salas
        # (contenção artificial de sala nunca implicada por RN08, que só pede
        # capacidade mínima viável, não uma sala específica).
        candidatas = sorted(
            (sala for sala in dados.salas if sala.capacidade >= turma.numero_alunos),
            key=lambda sala: (sala.capacidade - turma.numero_alunos, hash((turma.id, sala.id))),
        )
        salas_com_capacidade[turma.id] = [
            sala.id for sala in candidatas[: settings.solver_max_salas_candidatas]
        ]

    slots_por_turno: dict[str, list] = defaultdict(list)
    for slot in dados.slots:
        slots_por_turno[slot.turno].append(slot)

    turmas_por_id = {turma.id: turma for turma in dados.turmas}

    variaveis = VariaveisModelo(x={})

    for td in dados.turma_disciplinas:
        turma = turmas_por_id.get(td.turma_id)
        if turma is None:
            continue

        salas_validas = salas_com_capacidade.get(td.turma_id, [])
        if not salas_validas:
            continue  # nenhuma sala comporta a turma — surge no diagnóstico se INFEASIBLE

        professores_qualificados = professores_por_disciplina.get(td.disciplina_id, [])
        slots_do_turno = slots_por_turno.get(turma.turno, [])
        for professor_id in professores_qualificados:
            for slot in slots_do_turno:
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
