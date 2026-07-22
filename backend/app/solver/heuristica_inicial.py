# Implementa: warm-start para o CP-SAT (RF13/RNF01) — ver docs/relatorio/04_analise_desenvolvimento/
#
# Heurística construtiva gulosa "mais restrito primeiro" (padrão clássico de CSP):
# aloca primeiro os pares (turma, disciplina) com menos combinações válidas de
# professor×sala×tempo disponíveis, escolhendo greedily um professor+sala e
# preenchendo blocos contíguos de >=2 tempos (RN06) nos primeiros tempos livres.
#
# Múltiplas tentativas com ordens diferentes (dias embaralhados, professores
# ordenados por prioridade RN12 com desempate aleatório) — uma única passagem
# gulosa em ordem fixa tende a "gastar" cedo os tempos mais convenientes em
# pares fáceis, deixando pares difíceis sem hipótese mais tarde; repetir com
# ordens diferentes e ficar com a tentativa mais completa aproxima-se do padrão
# "construir uma solução completa, depois o CP-SAT só repara/otimiza localmente"
# usado por sistemas reais de timetabling (UniTime) em vez de "hint parcial +
# procura do zero".
#
# Isto NUNCA lança exceção nem garante uma solução completa — devolve o melhor
# hint conseguido (o CP-SAT aceita hints parciais via model.AddHint, ver
# solve.py). Pares que nenhuma tentativa consegue encaixar ficam sem hint —
# as variáveis correspondentes ficam livres para o CP-SAT decidir.
import random
from collections import defaultdict

from app.solver.builder import ChaveVar, VariaveisModelo
from app.solver.dto import HorarioInput

TempoChave = tuple[str, str, int]

_NUM_TENTATIVAS = 6
_SEMENTE_BASE = 42


def gerar_hint_inicial(
    dados: HorarioInput, variaveis: VariaveisModelo, prioridades: dict[int, float] | None = None
) -> dict[ChaveVar, int]:
    """Devolve {chave: 0|1} para um subconjunto das variáveis de `variaveis.x` —
    só as escolhidas ativamente pela heurística (1); as demais ficam sem entrada
    (nem 0 nem 1), deixando o CP-SAT livre para as decidir. Corre várias
    tentativas com ordens diferentes e devolve a mais completa (menos pares
    turma-disciplina por colocar).

    `prioridades` (RN12, ver prioridade_docente.py) influencia só a ordem em que os
    professores candidatos de um mesmo par (turma, disciplina) são tentados — nunca
    a ordem dos pares em si, que continua "mais restrito primeiro" (turma tem
    prioridade estrutural sobre professor, ver "Três Cenários Concorrentes")."""
    try:
        melhor_hint: dict[ChaveVar, int] = {}
        melhor_pares_cobertos = -1
        for tentativa in range(_NUM_TENTATIVAS):
            rng = random.Random(_SEMENTE_BASE + tentativa)
            hint, pares_cobertos = _construir(dados, variaveis, rng, prioridades or {})
            if pares_cobertos > melhor_pares_cobertos:
                melhor_hint = hint
                melhor_pares_cobertos = pares_cobertos
            if pares_cobertos == len(dados.turma_disciplinas):
                break  # já conseguiu colocar tudo, não vale a pena continuar a tentar
        return melhor_hint
    except Exception:
        # Bug na heurística não pode nunca impedir o solve real — sem hint,
        # o CP-SAT simplesmente procura do zero como fazia antes desta mudança.
        return {}


def _construir(
    dados: HorarioInput, variaveis: VariaveisModelo, rng: random.Random, prioridades: dict[int, float]
) -> tuple[dict[ChaveVar, int], int]:
    turmas_por_id = {turma.id: turma for turma in dados.turmas}

    slots_por_turno_dia: dict[tuple[str, str], list[int]] = defaultdict(list)
    for slot in dados.slots:
        slots_por_turno_dia[(slot.turno, slot.dia_semana)].append(slot.periodo)
    for periodos in slots_por_turno_dia.values():
        periodos.sort()
    dias_base = sorted({slot.dia_semana for slot in dados.slots})

    # Mais restrito primeiro (chave primária) — desempate aleatório por tentativa,
    # para que tentativas diferentes explorem ordens de colocação diferentes em
    # vez de repetirem sempre o mesmo caminho guloso.
    pares_ordenados = sorted(
        dados.turma_disciplinas,
        key=lambda td: (
            len(variaveis.por_turma_disciplina.get((td.turma_id, td.disciplina_id), [])),
            rng.random(),
        ),
    )

    ocupado_professor: set[tuple[int, str, str, int]] = set()
    ocupado_sala: set[tuple[int, str, str, int]] = set()
    ocupado_turma: set[tuple[int, str, str, int]] = set()
    hint: dict[ChaveVar, int] = {}
    pares_cobertos = 0

    for td in pares_ordenados:
        turma = turmas_por_id.get(td.turma_id)
        if turma is None:
            continue
        blocos = _decompor_em_blocos(td.carga_horaria_semanal)
        if not blocos:
            continue  # carga incompatível com RN06 (ex: 1) — o diagnóstico de INFEASIBLE trata disto

        combos = _combos_professor_sala(variaveis, td.turma_id, td.disciplina_id)
        if not combos:
            continue
        # RN12 — professor de maior prioridade tentado primeiro (chave primária);
        # desempate aleatório por tentativa preserva a diversidade das _NUM_TENTATIVAS
        # entre professores de prioridade semelhante/igual.
        combos.sort(key=lambda combo: (-prioridades.get(combo[0], 0.0), rng.random()))

        dias_tentativa = list(dias_base)
        rng.shuffle(dias_tentativa)

        for professor_id, sala_id in combos:
            chaves_do_par = _tentar_alocar_par(
                turma_id=td.turma_id,
                disciplina_id=td.disciplina_id,
                turno=turma.turno,
                professor_id=professor_id,
                sala_id=sala_id,
                blocos=blocos,
                dias_ordenados=dias_tentativa,
                slots_por_turno_dia=slots_por_turno_dia,
                ocupado_professor=ocupado_professor,
                ocupado_sala=ocupado_sala,
                ocupado_turma=ocupado_turma,
            )
            if chaves_do_par is not None:
                for chave in chaves_do_par:
                    hint[chave] = 1
                    ocupado_professor.add((chave[2], chave[4], chave[5], chave[6]))
                    ocupado_sala.add((chave[3], chave[4], chave[5], chave[6]))
                    ocupado_turma.add((chave[0], chave[4], chave[5], chave[6]))
                pares_cobertos += 1
                break  # este par de (turma,disciplina) já está resolvido, passa ao próximo

    return hint, pares_cobertos


def _decompor_em_blocos(carga: int) -> list[int]:
    """RN06: blocos contíguos >=2, sem tempo isolado. Carga par -> blocos de 2;
    carga ímpar -> um bloco de 3 + resto em blocos de 2. Carga < 2 é incompatível
    com RN06 (devolve [] — o par fica sem hint, mesmo tratamento que "sem combo")."""
    if carga < 2:
        return []
    if carga % 2 == 0:
        return [2] * (carga // 2)
    return [3] + [2] * ((carga - 3) // 2)


def _combos_professor_sala(
    variaveis: VariaveisModelo, turma_id: int, disciplina_id: int
) -> list[tuple[int, int]]:
    combos: set[tuple[int, int]] = set()
    for chave in variaveis.por_turma_disciplina.get((turma_id, disciplina_id), []):
        combos.add((chave[2], chave[3]))  # (professor_id, sala_id)
    return sorted(combos)


def _tentar_alocar_par(
    *,
    turma_id: int,
    disciplina_id: int,
    turno: str,
    professor_id: int,
    sala_id: int,
    blocos: list[int],
    dias_ordenados: list[str],
    slots_por_turno_dia: dict[tuple[str, str], list[int]],
    ocupado_professor: set[tuple[int, str, str, int]],
    ocupado_sala: set[tuple[int, str, str, int]],
    ocupado_turma: set[tuple[int, str, str, int]],
) -> list[ChaveVar] | None:
    """Tenta encaixar TODOS os blocos deste (turma,disciplina,professor,sala) em
    dias distintos (um bloco por dia, política simples que favorece distribuição
    semanal). Devolve None se não conseguir encaixar algum bloco — sem alterar
    os conjuntos de ocupação partilhados (falha atómica por combo)."""
    chaves: list[ChaveVar] = []
    dias_usados: set[str] = set()

    for tamanho in blocos:
        colocado = False
        for dia in dias_ordenados:
            if dia in dias_usados:
                continue
            periodos = slots_por_turno_dia.get((turno, dia), [])
            inicio = _procurar_janela_livre(
                periodos, tamanho, turma_id, turno, dia, professor_id, sala_id,
                ocupado_professor, ocupado_sala, ocupado_turma,
            )
            if inicio is None:
                continue
            for periodo in periodos[inicio : inicio + tamanho]:
                chave: ChaveVar = (turma_id, disciplina_id, professor_id, sala_id, dia, turno, periodo)
                chaves.append(chave)
            dias_usados.add(dia)
            colocado = True
            break
        if not colocado:
            return None

    return chaves


def _procurar_janela_livre(
    periodos: list[int],
    tamanho: int,
    turma_id: int,
    turno: str,
    dia: str,
    professor_id: int,
    sala_id: int,
    ocupado_professor: set[tuple[int, str, str, int]],
    ocupado_sala: set[tuple[int, str, str, int]],
    ocupado_turma: set[tuple[int, str, str, int]],
) -> int | None:
    n = len(periodos)
    for inicio in range(n - tamanho + 1):
        janela = periodos[inicio : inicio + tamanho]
        if all(
            (professor_id, dia, turno, p) not in ocupado_professor
            and (sala_id, dia, turno, p) not in ocupado_sala
            and (turma_id, dia, turno, p) not in ocupado_turma
            for p in janela
        ):
            return inicio
    return None
