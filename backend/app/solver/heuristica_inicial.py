# Implementa: warm-start para o CP-SAT (RF13/RNF01) — ver docs/04_04_analise_desenvolvimento.md
#
# Heurística construtiva gulosa "mais restrito primeiro" (padrão clássico de CSP):
# aloca primeiro os pares (turma, disciplina) com menos combinações válidas de
# professor×sala×tempo disponíveis, escolhendo greedily um professor+sala e
# preenchendo blocos contíguos de >=2 tempos (RN06) nos primeiros tempos livres.
#
# Isto NUNCA lança exceção nem garante uma solução completa — devolve um hint
# PARCIAL (o CP-SAT aceita hints parciais via model.AddHint, ver solve.py) que
# serve só para arrancar a procura perto de uma atribuição plausível em vez de
# vazia. Se a heurística ficar bloqueada a meio (ex: não sobra nenhum tempo
# livre para um par difícil), simplesmente salta esse par — as variáveis
# correspondentes ficam sem hint e o CP-SAT decide-as livremente.
from collections import defaultdict

from app.solver.builder import ChaveVar, VariaveisModelo
from app.solver.dto import HorarioInput

TempoChave = tuple[str, str, int]


def gerar_hint_inicial(dados: HorarioInput, variaveis: VariaveisModelo) -> dict[ChaveVar, int]:
    """Devolve {chave: 0|1} para um subconjunto das variáveis de `variaveis.x` —
    só as escolhidas ativamente pela heurística (1); as demais ficam sem entrada
    (nem 0 nem 1), deixando o CP-SAT livre para as decidir."""
    try:
        return _construir(dados, variaveis)
    except Exception:
        # Bug na heurística não pode nunca impedir o solve real — sem hint,
        # o CP-SAT simplesmente procura do zero como fazia antes desta mudança.
        return {}


def _construir(dados: HorarioInput, variaveis: VariaveisModelo) -> dict[ChaveVar, int]:
    turmas_por_id = {turma.id: turma for turma in dados.turmas}

    slots_por_turno_dia: dict[tuple[str, str], list[int]] = defaultdict(list)
    for slot in dados.slots:
        slots_por_turno_dia[(slot.turno, slot.dia_semana)].append(slot.periodo)
    for periodos in slots_por_turno_dia.values():
        periodos.sort()
    dias_ordenados = sorted({slot.dia_semana for slot in dados.slots})

    # Mais restrito primeiro: menos combinações (professor,sala,tempo) disponíveis = mais prioritário.
    pares_ordenados = sorted(
        dados.turma_disciplinas,
        key=lambda td: len(variaveis.por_turma_disciplina.get((td.turma_id, td.disciplina_id), [])),
    )

    ocupado_professor: set[tuple[int, str, str, int]] = set()
    ocupado_sala: set[tuple[int, str, str, int]] = set()
    ocupado_turma: set[tuple[int, str, str, int]] = set()
    hint: dict[ChaveVar, int] = {}

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

        for professor_id, sala_id in combos:
            chaves_do_par = _tentar_alocar_par(
                turma_id=td.turma_id,
                disciplina_id=td.disciplina_id,
                turno=turma.turno,
                professor_id=professor_id,
                sala_id=sala_id,
                blocos=blocos,
                dias_ordenados=dias_ordenados,
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
                break  # este par de (turma,disciplina) já está resolvido, passa ao próximo

    return hint


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
