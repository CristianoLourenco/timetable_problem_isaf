# Solver Nunca Devolve INFEASIBLE — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** RN05 (carga horária semanal cumprida) deixa de ser uma restrição exata do CP-SAT e passa a aceitar défice penalizado; `podar_dominio` deixa de bloquear upfront; o solver do ISAF passa a devolver sempre `OPTIMAL`/`FEASIBLE` (ou `UNKNOWN` só por tempo esgotado, nunca por escassez estrutural), acompanhado de uma lista de pendências com razão explicada, e o Gestor ganha um seletor de tempo de procura (1/5/10 min) por pedido de geração.

**Architecture:** Uma nova `IntVar` de défice por `(turma, disciplina)` substitui a igualdade exata em `add_carga_horaria_cumprida`; o objetivo penaliza fortemente essa variável. `podar_dominio` para de devolver "problemas" bloqueantes — os casos que detecta viram pendências de défice total desde logo. Depois do solve, uma nova função em `diagnostico.py` (reaproveitando a bisecção já existente) atribui uma razão textual a cada pendência. `orquestrador_turnos.py` agrega pendências das 3 fases. O tempo de procura passa a vir do `Job` (persistido, escolhido pelo Gestor), não de uma constante fixa.

**Tech Stack:** Python 3.12, OR-Tools CP-SAT, SQLModel, Pydantic v2 (via SQLModel), pytest.

## Global Constraints

- O solver (`app/solver/`) nunca importa nada de `api/`/routers — fluxo unidirecional `api → services → solver`.
- Nunca modelagem densa — `build_variables` continua a gerar `BoolVar` só para combinações válidas.
- `INFEASIBLE` nunca pode voltar a propagar como exceção — sempre um `SolverResult` estruturado.
- RN01 (professor sem dupla alocação), RN02 (turma sem dupla disciplina), RN03 (sala sem dupla turma), RN06 (blocos contíguos) continuam **hard**, sem alteração nesta plano.
- Testes existentes que hoje esperam `INFEASIBLE` por escassez combinatória (não por RN06/carga=1) devem passar a esperar `OPTIMAL`/`FEASIBLE` com pendências.
- Sem `.env`/segredos tocados; sem alterações a `docker-compose.yml`.
- Idioma: código/nomes em inglês onde já estão em inglês (manter convenção mista do repo: identificadores em português onde já é o padrão do domínio, ex. `carga_horaria_semanal`, `deficit`), comentários explicando o *porquê* em português (padrão já usado no repo), erros ao cliente em português.
- Cada ficheiro de código relevante mantém/adiciona o comentário de rastreabilidade `# Implementa: RFxx (UCyy)` no topo.

---

### Task 1: `PendenciaDTO` e `SolverResult.pendencias`

**Files:**
- Modify: `app/solver/dto.py`
- Test: `tests/test_solver.py` (verificação inline via import, sem teste dedicado — este DTO é testado através das tasks seguintes que o populam)

**Interfaces:**
- Produces: `PendenciaDTO(turma_id: int, disciplina_id: int, tempos_em_falta: int, razao: str, professores_conflitantes: tuple[int, ...] = (), turmas_conflitantes: tuple[int, ...] = ())`
- Produces: `SolverResult.pendencias: list[PendenciaDTO]` (novo campo, default `[]`)

- [ ] **Step 1: Adicionar `PendenciaDTO` e o campo `pendencias` em `SolverResult`**

Editar `app/solver/dto.py`, adicionando a classe logo antes de `SolverResult` e o novo campo em `SolverResult`:

```python
@dataclass(frozen=True)
class PendenciaDTO:
    """RF13/UC09 — um (turma, disciplina) que ficou com tempos por preencher depois
    do solve (RN05 relaxada para soft-com-défice, ver constraints_hard.py). `razao`
    é texto pronto para o Gestor, gerado por app/solver/diagnostico.py."""

    turma_id: int
    disciplina_id: int
    tempos_em_falta: int
    razao: str
    professores_conflitantes: tuple[int, ...] = ()
    turmas_conflitantes: tuple[int, ...] = ()


@dataclass(frozen=True)
class SolverResult:
    status: str  # "OPTIMAL" | "FEASIBLE" | "INFEASIBLE"
    alocacoes: list[AlocacaoResult] = field(default_factory=list)
    diagnostico: str | None = None  # RF13/UC09 — preenchido apenas quando INFEASIBLE (UNKNOWN por tempo)
    pendencias: list[PendenciaDTO] = field(default_factory=list)  # RF13 — défice de RN05 após o solve
```

- [ ] **Step 2: Verificar que nada quebrou**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/ -q 2>&1 | tail -20`
Expected: `91 passed` (mesmo número de antes — este DTO ainda não é usado em lado nenhum, é só a definição).

- [ ] **Step 3: Commit**

```bash
git add backend/app/solver/dto.py
git commit -m "feat(solver): adiciona PendenciaDTO e SolverResult.pendencias — RF13"
```

---

### Task 2: `add_carga_horaria_cumprida` aceita défice

**Files:**
- Modify: `app/solver/constraints_hard.py`
- Test: `tests/test_solver.py` (novo teste)

**Interfaces:**
- Consumes: `VariaveisModelo`, `HorarioInput` (sem mudança de tipo)
- Produces: `add_carga_horaria_cumprida(model, variaveis, dados) -> dict[tuple[int, int], cp_model.IntVar]` — chave `(turma_id, disciplina_id)`, valor a `IntVar` de défice (mudança de assinatura: antes devolvia `None` implicitamente)

- [ ] **Step 1: Escrever o teste que falha primeiro**

Adicionar a `tests/test_solver.py` (no fim do ficheiro):

```python
def test_carga_impar_de_um_tempo_ja_nao_e_infeasible_fica_pendente():
    """RN06 continua a proibir tempo isolado, mas RN05 agora aceita défice — em vez
    de INFEASIBLE, a disciplina fica com 1 tempo em falta reportado como pendência."""
    slots = _construir_slots(["segunda"], periodos_por_dia=4)

    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=1)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario(dados, max_time_in_seconds=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.alocacoes == []
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].turma_id == 1
    assert resultado.pendencias[0].disciplina_id == 1
    assert resultado.pendencias[0].tempos_em_falta == 1
```

Este teste **substitui** `test_carga_impar_de_um_tempo_e_infeasible_com_diagnostico` (que fica obsoleto pela mudança de comportamento). Remover o teste antigo do ficheiro nesta mesma edição.

- [ ] **Step 2: Rodar o teste para confirmar que falha**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_solver.py::test_carga_impar_de_um_tempo_ja_nao_e_infeasible_fica_pendente -v`
Expected: FAIL — `resultado.status == "INFEASIBLE"` ainda (comportamento antigo) ou `AttributeError: 'SolverResult' object has no attribute 'pendencias'` (já resolvido pela Task 1, mas o solve ainda não popula).

- [ ] **Step 3: Alterar `add_carga_horaria_cumprida` para aceitar défice**

Em `app/solver/constraints_hard.py`, substituir:

```python
def add_carga_horaria_cumprida(model: cp_model.CpModel, variaveis: VariaveisModelo, dados: HorarioInput) -> None:
    """RN05 — carga horária semanal da disciplina cumprida integralmente."""
    for td in dados.turma_disciplinas:
        chaves = variaveis.por_turma_disciplina.get((td.turma_id, td.disciplina_id), [])
        model.Add(sum(variaveis.x[c] for c in chaves) == td.carga_horaria_semanal)
```

por:

```python
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
```

- [ ] **Step 4: Rodar os testes de `constraints_hard`/`solve` para ver o novo erro esperado**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_solver.py -v 2>&1 | tail -30`
Expected: ainda FAIL (o `solve.py` não usa o retorno de défice nem popula `pendencias` — próxima task), mas sem `AttributeError` na chamada de `add_carga_horaria_cumprida` (ela já devolve o dict, só ainda não é usado).

- [ ] **Step 5: Commit**

```bash
git add backend/app/solver/constraints_hard.py backend/tests/test_solver.py
git commit -m "feat(solver): RN05 aceita défice via IntVar em vez de igualdade exata"
```

---

### Task 3: Penalizar défice no objetivo

**Files:**
- Modify: `app/core/config.py`
- Modify: `app/solver/constraints_soft.py`
- Test: nenhum teste dedicado nesta task (o efeito é observado end-to-end na Task 5); a integração é validada pelos testes já existentes de prioridade RN04 (não podem quebrar com o novo termo somado ao objetivo)

**Interfaces:**
- Consumes: `deficits: dict[tuple[int, int], cp_model.IntVar]` (produzido pela Task 2)
- Produces: `build_objective(model, variaveis, dados, deficits, prioridades=None, contagem_diaria_fixa=None)` — nova assinatura, com `deficits` como parâmetro posicional obrigatório logo após `dados`

- [ ] **Step 1: Adicionar o peso em `config.py`**

Em `app/core/config.py`, logo abaixo de `solver_peso_equidade_diaria: int = 1`:

```python
    # RF13 — défice de RN05 (carga horária não cumprida). Peso muito acima de
    # qualquer combinação plausível de RN04×prioridade (peso 10, multiplicador
    # até 2.0) + RN08 (peso 20) + equidade (peso 1) — o solver só aceita
    # défice quando preencher tudo é genuinamente impossível, nunca como troca
    # vantajosa face a uma otimização menor.
    solver_peso_deficit_rn05: int = 1000
```

- [ ] **Step 2: Atualizar `build_objective` para receber e penalizar `deficits`**

Em `app/solver/constraints_soft.py`, alterar a assinatura e o corpo de `build_objective`:

```python
def build_objective(
    model: cp_model.CpModel,
    variaveis: VariaveisModelo,
    dados: HorarioInput,
    deficits: dict[tuple[int, int], cp_model.IntVar],
    prioridades: dict[int, float] | None = None,
    contagem_diaria_fixa: dict[tuple[int, str], int] | None = None,
):
    """Monta o termo a minimizar: peso_deficit x RN05 + peso_RN04 x RN04 + peso_RN08 x RN08 + peso_equidade x amplitude diária.

    `deficits` (RF13) é o dicionário devolvido por
    constraints_hard.add_carga_horaria_cumprida — cada tempo em falta custa
    settings.solver_peso_deficit_rn05, muito acima de qualquer combinação das
    outras penalizações, para o solver preferir sempre cumprir a carga toda
    quando for fisicamente possível.

    RN12 (prioridade docente) entra aqui como um multiplicador por professor sobre a
    penalização de RN04 — violar a disponibilidade de um professor de alta prioridade
    custa mais do que violar a de um de baixa prioridade. `penalizacao_rn04` em si
    fica pura (0/1): result_mapper.py também a usa para auditoria e não devia herdar
    um significado dependente de prioridade.
    """
    prioridades = prioridades or {}
    tempos_disponiveis: dict[int, set[TempoChave]] = defaultdict(set)
    for disp in dados.disponibilidades:
        tempos_disponiveis[disp.professor_id].add((disp.dia_semana, disp.turno, disp.periodo))
    professores_com_registo = set(tempos_disponiveis.keys())

    capacidade_sala = {sala.id: sala.capacidade for sala in dados.salas}
    alunos_turma = {turma.id: turma.numero_alunos for turma in dados.turmas}

    termos_rn04 = []
    termos_rn08 = []
    for chave, var in variaveis.x.items():
        peso_rn04 = penalizacao_rn04(chave, tempos_disponiveis, professores_com_registo)
        if peso_rn04:
            professor_id = chave[2]
            multiplicador = 1.0 + prioridades.get(professor_id, 0.0)  # intervalo 1.0-2.0
            termos_rn04.append(peso_rn04 * multiplicador * var)

        peso_rn08 = penalizacao_rn08(chave, capacidade_sala, alunos_turma)
        if peso_rn08:
            termos_rn08.append(peso_rn08 * var)

    termo_equidade = _construir_termo_equidade(model, variaveis, dados, contagem_diaria_fixa or {})
    termo_deficit = sum(deficits.values())

    return (
        settings.solver_peso_deficit_rn05 * termo_deficit
        + settings.solver_peso_rn04_disponibilidade * sum(termos_rn04)
        + settings.solver_peso_rn08_capacidade * sum(termos_rn08)
        + settings.solver_peso_equidade_diaria * termo_equidade
    )
```

- [ ] **Step 3: Rodar os testes de prioridade para garantir que o novo termo não altera o resultado esperado**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_solver.py::test_rn12_prioridade_protege_professor_de_maior_prioridade_em_trade_off -v`
Expected: ainda FAIL nesta task (o `solve.py` ainda não repassa `deficits` para `build_objective` — próxima task conecta tudo). Confirmar que o erro agora é de assinatura (`missing required argument: 'deficits'`), não de lógica.

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/config.py backend/app/solver/constraints_soft.py
git commit -m "feat(solver): penaliza défice de RN05 no objetivo (peso 1000)"
```

---

### Task 4: Conectar défice em `solve.py` — o solver nunca mais retorna INFEASIBLE por escassez

**Files:**
- Modify: `app/solver/solve.py`
- Modify: `app/solver/preprocessamento.py`
- Test: `tests/test_solver.py`, `tests/test_preprocessamento.py`

**Interfaces:**
- Consumes: `add_carga_horaria_cumprida` (Task 2), `build_objective` com `deficits` (Task 3)
- Consumes: `podar_dominio(dados) -> tuple[HorarioInput, list[PendenciaDTO]]` (mudança de tipo — antes devolvia `list[str]`)
- Produces: `resolver_horario(...)` sempre popula `SolverResult.pendencias` a partir das `IntVar` de défice + das pendências estruturais de `podar_dominio`

- [ ] **Step 1: Escrever os testes que falham primeiro**

Em `tests/test_preprocessamento.py`, alterar `test_podar_dominio_detecta_disciplina_sem_professor_qualificado` e `test_podar_dominio_detecta_turma_sem_sala_com_capacidade` para o novo tipo de retorno, e alterar `test_resolver_horario_devolve_infeasible_instantaneo_sem_professor_qualificado` para o novo comportamento (não bloqueia mais):

```python
def test_podar_dominio_detecta_disciplina_sem_professor_qualificado():
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=99)],  # não é a disciplina 1
        disponibilidades=[],
    )

    _, pendencias = podar_dominio(dados)

    assert len(pendencias) == 1
    assert pendencias[0].turma_id == 1
    assert pendencias[0].disciplina_id == 1
    assert pendencias[0].tempos_em_falta == 2
    assert "nenhum professor qualificado" in pendencias[0].razao


def test_podar_dominio_detecta_turma_sem_sala_com_capacidade():
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=50, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    _, pendencias = podar_dominio(dados)

    assert len(pendencias) == 1
    assert "50 alunos excede a capacidade" in pendencias[0].razao


def test_podar_dominio_cenario_valido_nao_bloqueia_resolucao():
    """Regressão: um cenário totalmente válido não deve ser sinalizado como
    pendência, e resolver_horario deve continuar a chegar ao CP-SAT."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    _, pendencias = podar_dominio(dados)
    assert pendencias == []

    resultado = resolver_horario(dados, max_time_in_seconds=5.0)
    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.pendencias == []


def test_resolver_horario_nunca_bloqueia_sem_professor_qualificado():
    """Antes: INFEASIBLE instantâneo. Agora: OPTIMAL/FEASIBLE com uma pendência de
    défice total, sem sequer acionar o CP-SAT para essa turma_disciplina."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=_slots(),
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=99)],
        disponibilidades=[],
    )

    resultado = resolver_horario(dados, max_time_in_seconds=10.0)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert resultado.alocacoes == []
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].tempos_em_falta == 2
    assert "nenhum professor qualificado" in resultado.pendencias[0].razao
```

Remover o teste antigo `test_resolver_horario_devolve_infeasible_instantaneo_sem_professor_qualificado` (substituído pelo de cima).

- [ ] **Step 2: Rodar os testes para confirmar que falham**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_preprocessamento.py -v`
Expected: FAIL em vários — `podar_dominio` ainda devolve `list[str]`, não `list[PendenciaDTO]`.

- [ ] **Step 3: Reescrever `podar_dominio` para devolver pendências em vez de bloquear**

Substituir todo o conteúdo de `app/solver/preprocessamento.py`:

```python
# Implementa: RN01-RN08, RF13 — poda de domínio antes da geração de variáveis
# ver docs/04_04_analise_desenvolvimento.md secção 4.3.3 e skill ortools-timetabling-solver.
#
# builder.py já garante que nenhum BoolVar é criado para uma combinação inválida
# (professor não qualificado, turno errado) — mas só filtra NO MOMENTO de criar as
# variáveis. Os dados brutos que chegam a resolver_horario() (professores,
# disponibilidades) não vêm pré-filtrados pelo âmbito, o que obriga RN01
# (constraints_hard.py), a fórmula de prioridade e o termo de equidade
# (constraints_soft.py) a iterar sobre professores estruturalmente irrelevantes
# a este (ano_letivo, semestre) — cada um deles nunca vai gerar nenhuma variável.
#
# Esta função poda esses dados ANTES de chegarem a build_variables, e aproveita a
# mesma passagem para detetar problemas estruturais óbvios (RN05 impossível de
# cumprir por falta de professor/sala). Desde RF13 (nunca bloquear com
# INFEASIBLE), estes problemas NUNCA impedem o solve — viram PendenciaDTO com
# défice total desde logo, para o Gestor resolver por alocação manual, sem
# sequer gastar tempo do CP-SAT numa turma_disciplina que já sabemos impossível
# de preencher automaticamente.
from collections import defaultdict

from app.solver.dto import HorarioInput, PendenciaDTO


def podar_dominio(dados: HorarioInput) -> tuple[HorarioInput, list[PendenciaDTO]]:
    """Remove professores/qualificações/disponibilidades irrelevantes ao âmbito de
    `dados` e devolve, no mesmo varrimento, as pendências estruturais óbvias
    (disciplina sem professor qualificado, turma sem sala com capacidade
    suficiente) — cada uma já com défice = carga_horaria_semanal inteira, pronta
    para entrar na lista final de SolverResult.pendencias sem acionar o CP-SAT."""
    disciplinas_em_uso = {td.disciplina_id for td in dados.turma_disciplinas}

    professores_por_disciplina: dict[int, list[int]] = defaultdict(list)
    for pd in dados.professor_disciplinas:
        if pd.disciplina_id in disciplinas_em_uso:
            professores_por_disciplina[pd.disciplina_id].append(pd.professor_id)

    professores_relevantes = {
        professor_id for professores in professores_por_disciplina.values() for professor_id in professores
    }

    turmas_por_id = {turma.id: turma for turma in dados.turmas}
    capacidade_maxima = max((sala.capacidade for sala in dados.salas), default=0)

    pendencias: list[PendenciaDTO] = []
    for td in dados.turma_disciplinas:
        if not professores_por_disciplina.get(td.disciplina_id):
            pendencias.append(
                PendenciaDTO(
                    turma_id=td.turma_id,
                    disciplina_id=td.disciplina_id,
                    tempos_em_falta=td.carga_horaria_semanal,
                    razao=(
                        f"Turma {td.turma_id} / disciplina {td.disciplina_id}: nenhum professor "
                        "qualificado registado em ProfessorDisciplina. Associe um professor a esta "
                        "disciplina, ou aloque manualmente escolhendo entre os professores já "
                        "qualificados para ela."
                    ),
                )
            )
            continue  # sem professor: turma sem sala não se aplica (já não há como alocar de todo)

        turma = turmas_por_id.get(td.turma_id)
        if turma is not None and turma.numero_alunos > capacidade_maxima:
            pendencias.append(
                PendenciaDTO(
                    turma_id=td.turma_id,
                    disciplina_id=td.disciplina_id,
                    tempos_em_falta=td.carga_horaria_semanal,
                    razao=(
                        f"Turma {td.turma_id}: {turma.numero_alunos} alunos excede a capacidade "
                        f"máxima disponível entre as salas ({capacidade_maxima}). Cadastre uma sala "
                        "com capacidade suficiente, ou aloque manualmente aceitando a lotação atual."
                    ),
                )
            )

    turma_disciplinas_bloqueadas = {(p.turma_id, p.disciplina_id) for p in pendencias}
    dados_podados = HorarioInput(
        turmas=dados.turmas,
        professores=[p for p in dados.professores if p.id in professores_relevantes],
        salas=dados.salas,
        slots=dados.slots,
        turma_disciplinas=[
            td for td in dados.turma_disciplinas if (td.turma_id, td.disciplina_id) not in turma_disciplinas_bloqueadas
        ],
        professor_disciplinas=[
            pd
            for pd in dados.professor_disciplinas
            if pd.disciplina_id in disciplinas_em_uso and pd.professor_id in professores_relevantes
        ],
        disponibilidades=[d for d in dados.disponibilidades if d.professor_id in professores_relevantes],
    )
    return dados_podados, pendencias
```

Nota de design: as `turma_disciplinas` já identificadas como pendência **saem** de `dados_podados.turma_disciplinas` — não chegam a `build_variables`/`add_carga_horaria_cumprida`, porque já sabemos que o défice será total; isto evita gerar uma `IntVar` de défice redundante para algo já resolvido sem o CP-SAT.

- [ ] **Step 4: Atualizar `resolver_horario` em `solve.py`**

Ler o ficheiro completo primeiro para ver o estado atual antes de editar:

Substituir a função `resolver_horario` inteira (do `def resolver_horario` até ao `return SolverResult(status=status_nome, alocacoes=alocacoes, diagnostico=None)`) por:

```python
def resolver_horario(
    dados: HorarioInput,
    max_time_in_seconds: float,
    num_search_workers: int = 8,
    relative_gap_limit: float | None = None,
    prioridades: dict[int, float] | None = None,
    chaves_professor_ocupadas: frozenset[tuple[int, str, str, int]] = frozenset(),
    contagem_diaria_fixa: dict[tuple[int, str], int] | None = None,
) -> SolverResult:
    """Monta o modelo completo, resolve com limite de tempo e nunca deixa INFEASIBLE
    propagar como exceção nem como status por escassez estrutural (RF13) — RN05 é
    soft-com-défice (constraints_hard.add_carga_horaria_cumprida), logo o único
    status não-viável possível é UNKNOWN (tempo esgotado, RNF03), nunca
    impossibilidade combinatória provada.

    `prioridades` (RN12) é opcional — se omitido, é calculado aqui a partir de
    `dados.professores`/`dados.disponibilidades` já podados. `chaves_professor_ocupadas`
    e `contagem_diaria_fixa` só são usados por uma decomposição por turno (ver
    app/solver/orquestrador_turnos.py) para propagar fixações de fases anteriores —
    um chamador direto nunca precisa de os passar.
    """
    dados, pendencias_estruturais = podar_dominio(dados)

    if prioridades is None:
        prioridades = calcular_prioridades(dados.professores, dados.disponibilidades)

    model = cp_model.CpModel()
    variaveis = build_variables(model, dados, chaves_professor_ocupadas)

    add_professor_sem_dupla_alocacao(model, variaveis, dados)
    add_turma_sem_dupla_disciplina(model, variaveis, dados)
    add_sala_sem_dupla_turma(model, variaveis, dados)
    deficits = add_carga_horaria_cumprida(model, variaveis, dados)
    add_agrupamento_em_blocos(model, variaveis, dados)

    model.Minimize(
        build_objective(
            model, variaveis, dados, deficits, prioridades=prioridades, contagem_diaria_fixa=contagem_diaria_fixa
        )
    )

    # Warm-start: uma atribuição gulosa rápida ("mais restrito primeiro", professores
    # candidatos ordenados por RN12) dá ao CP-SAT um ponto de partida perto de uma
    # solução válida e prioridade-consciente em vez de procurar do zero — hints
    # parciais são aceites pelo CP-SAT, por isso um resultado incompleto da
    # heurística (nunca lança exceção) ainda ajuda. Ver app/solver/heuristica_inicial.py
    # para a estratégia e o porquê.
    hint = gerar_hint_inicial(dados, variaveis, prioridades)
    for chave, valor in hint.items():
        # Defesa extra (a heurística já só produz chaves reais de variaveis.x,
        # por construção — ver heuristica_inicial.py) — um hint nunca deve poder
        # rebentar o solve real por si só.
        var = variaveis.x.get(chave)
        if var is not None:
            model.AddHint(var, valor)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_in_seconds
    # Sem isto, o CP-SAT satura todos os cores da máquina (ver core/config.py) —
    # limitar aqui é o que torna a geração viável em paralelo com o resto do
    # sistema, já que corre numa thread à parte (BackgroundTasks) mas continua a
    # competir por CPU com o event loop e com o utilizador. O portfolio de
    # sub-solvers focados em encontrar a primeira solução só ativa a partir de
    # 5 workers — ver comentário em core/config.py.
    solver.parameters.num_search_workers = num_search_workers
    # Aceitar uma solução dentro do gap (não exigir otimalidade provada) — a
    # função objetivo é uma soma de penalizações soft, "boa e rápida" vale mais
    # do que "marginalmente melhor e lenta" em produção. Ver core/config.py.
    solver.parameters.relative_gap_limit = (
        relative_gap_limit if relative_gap_limit is not None else settings.solver_relative_gap_limit
    )
    status = solver.Solve(model)

    status_nome = _STATUS_VIAVEL.get(status)
    if status_nome is None:
        # UNKNOWN (tempo esgotado sem encontrar nenhuma solução) é o ÚNICO caso não
        # otimizado/viável possível agora que RN05 nunca torna o modelo genuinamente
        # INFEASIBLE (RF13) — reportar como tal evita dizer ao Gestor que o cenário é
        # impossível quando na verdade só precisava de mais tempo (RNF03).
        return SolverResult(
            status="INFEASIBLE", alocacoes=[], diagnostico=_diagnosticar_tempo_esgotado(max_time_in_seconds)
        )

    alocacoes = mapear_resultado(solver, variaveis, dados)
    pendencias = pendencias_estruturais + _extrair_pendencias_deficit(solver, deficits, dados)
    return SolverResult(status=status_nome, alocacoes=alocacoes, diagnostico=None, pendencias=pendencias)
```

- [ ] **Step 5: Adicionar `_extrair_pendencias_deficit` e importar `PendenciaDTO` / `gerar_razao_pendencia`**

No topo de `solve.py`, atualizar os imports:

```python
from app.solver.diagnostico import gerar_razao_pendencia
from app.solver.dto import HorarioInput, PendenciaDTO, SolverResult
```

(remove os imports antigos de `formatar_diagnostico_nucleo, isolar_nucleo_infeasible` do topo — passam a ser usados só dentro de `diagnostico.py`, chamados via `gerar_razao_pendencia`, que é criada na Task 6).

Adicionar, depois de `resolver_horario` (antes de `_diagnosticar_tempo_esgotado`):

```python
def _extrair_pendencias_deficit(
    solver: cp_model.CpSolver, deficits: dict[tuple[int, int], cp_model.IntVar], dados: HorarioInput
) -> list[PendenciaDTO]:
    """Lê o valor resolvido de cada IntVar de défice (RN05 soft) e gera a
    PendenciaDTO correspondente para as que ficaram > 0, com a razão explicada
    por app/solver/diagnostico.py (RF13)."""
    pendencias = []
    for (turma_id, disciplina_id), var in deficits.items():
        tempos_em_falta = solver.Value(var)
        if tempos_em_falta > 0:
            pendencias.append(gerar_razao_pendencia(turma_id, disciplina_id, tempos_em_falta, dados))
    return pendencias
```

- [ ] **Step 6: Remover o branch de `problemas_estruturais` (já não existe mais — substituído por `pendencias_estruturais` no Step 4) e a função `_diagnosticar_infeasible`**

Remover completamente a função `_diagnosticar_infeasible` de `solve.py` (do `def _diagnosticar_infeasible` até ao fim do ficheiro) — a sua lógica de causas baratas migra para `diagnostico.py` na Task 6, adaptada para gerar razão por pendência individual em vez de diagnóstico de cenário inteiro.

`Counter` e `defaultdict` (import do topo, `from collections import Counter, defaultdict`) eram usados só dentro de `_diagnosticar_infeasible` — depois de a remover, trocar essa linha de import por nada (sem `collections` neste ficheiro; confirmar com `grep -n "Counter\|defaultdict" app/solver/solve.py` que não sobra nenhuma referência antes de apagar o import).

- [ ] **Step 7: Este passo vai falhar até a Task 6 existir — não rodar testes ainda**

`gerar_razao_pendencia` ainda não existe (Task 6 cria). Prosseguir para a Task 5 (ajuste do `orquestrador_turnos.py`) antes de rodar qualquer teste, para não perder tempo com um estado intermediário conhecido como incompleto.

- [ ] **Step 8: Commit (estado intermediário, testes ainda vermelhos — documentado)**

```bash
git add backend/app/solver/solve.py backend/app/solver/preprocessamento.py backend/tests/test_preprocessamento.py backend/tests/test_solver.py
git commit -m "feat(solver): resolver_horario nunca bloqueia por escassez — usa défice de RN05 (WIP: diagnostico.py na próxima task)"
```

---

### Task 5: `orquestrador_turnos.py` agrega pendências das 3 fases

**Files:**
- Modify: `app/solver/orquestrador_turnos.py`
- Test: `tests/test_orquestrador_turnos.py`

**Interfaces:**
- Consumes: `SolverResult.pendencias` (Task 1/4)
- Produces: `resolver_horario_por_turnos(...)` continua com a mesma assinatura, `SolverResult.pendencias` agora é a concatenação das pendências de todas as fases resolvidas

- [ ] **Step 1: Escrever o teste que falha primeiro**

Adicionar a `tests/test_orquestrador_turnos.py`, substituindo `test_diagnostico_infeasible_identifica_o_turno` (o cenário de "turma da tarde sem professor qualificado" já não bloqueia — passa a ser pendência):

```python
def test_turma_sem_professor_qualificado_vira_pendencia_no_turno_certo():
    """Turma da tarde sem nenhum professor qualificado — a fase da manhã resolve
    normalmente; a turma da tarde fica como pendência (não bloqueia mais nada)."""
    slots = _slots("manha", ["segunda"], 4) + _slots("tarde", ["segunda"], 4)

    dados = HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno="manha"),
            TurmaDTO(id=2, numero_alunos=20, turno="tarde"),
        ],
        professores=[ProfessorDTO(id=1, classificacao=3, vinculo_casa=False)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=99, carga_horaria_semanal=2),  # sem professor qualificado
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_por_turno=MAX_TIME_TESTE)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.alocacoes) == 2  # só a turma 1 (manhã) foi alocada
    assert len(resultado.pendencias) == 1
    assert resultado.pendencias[0].turma_id == 2
    assert resultado.pendencias[0].disciplina_id == 99
```

Remover `test_diagnostico_infeasible_identifica_o_turno` do ficheiro.

- [ ] **Step 2: Rodar para confirmar que falha**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_orquestrador_turnos.py -v`
Expected: FAIL — `resolver_horario_por_turnos` hoje devolve `INFEASIBLE` cedo assim que uma fase falha, sem agregar pendências.

- [ ] **Step 3: Atualizar `resolver_horario_por_turnos`**

Em `app/solver/orquestrador_turnos.py`, substituir a linha de inicialização:

```python
    todas_alocacoes: list[AlocacaoResult] = []
```

por (adiciona `todas_pendencias` ao lado):

```python
    todas_alocacoes: list[AlocacaoResult] = []
    todas_pendencias: list = []
```

E substituir o corpo do `for turno in ordem_turnos:` e o `return` final:

```python
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
            return SolverResult(status="INFEASIBLE", alocacoes=[], diagnostico=f"[Turno {turno}] {resultado.diagnostico}")

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
```

- [ ] **Step 4: Rodar os testes do orquestrador**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_orquestrador_turnos.py -v`
Expected: ainda FAIL na parte que depende de `gerar_razao_pendencia` (Task 6) — confirmar que o erro agora vem de `diagnostico.py`, não da agregação em si.

- [ ] **Step 5: Commit**

```bash
git add backend/app/solver/orquestrador_turnos.py backend/tests/test_orquestrador_turnos.py
git commit -m "feat(solver): orquestrador_turnos agrega pendências das 3 fases (WIP)"
```

---

### Task 6: `diagnostico.py` gera a razão de cada pendência

**Files:**
- Modify: `app/solver/diagnostico.py`
- Test: `tests/test_diagnostico.py`

**Interfaces:**
- Produces: `gerar_razao_pendencia(turma_id: int, disciplina_id: int, tempos_em_falta: int, dados: HorarioInput) -> PendenciaDTO`
- Consumes internamente: `isolar_nucleo_infeasible` (mantido, mesma assinatura) como último recurso

- [ ] **Step 1: Escrever os testes que falham primeiro**

Substituir `tests/test_diagnostico.py` inteiro (o cenário de teste principal é reaproveitado, só a asserção final muda de "prova INFEASIBLE" para "gera razão de pendência"):

```python
# Implementa: RF13 (UC09) — geração de razão por pendência (app/solver/diagnostico.py)
from app.solver.diagnostico import formatar_diagnostico_nucleo, gerar_razao_pendencia, isolar_nucleo_infeasible
from app.solver.dto import (
    HorarioInput,
    ProfessorDisciplinaDTO,
    ProfessorDTO,
    SalaDTO,
    SlotDTO,
    TurmaDisciplinaDTO,
    TurmaDTO,
)
from app.solver.solve import resolver_horario

TURNO_TESTE = "manha"


def _cenario_com_professor_sobrecarregado() -> HorarioInput:
    """2 turmas partilham o ÚNICO professor qualificado para a sua disciplina, mas
    o turno só tem 3 tempos no total — o professor precisaria de 4 (2+2) usos
    distintos, impossível por pigeonhole independentemente de blocos/salas.
    Réplica minimalista do caso real encontrado à escala do ISAF (GBS 4º ano)."""
    slots = [SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 4)]
    return HorarioInput(
        turmas=[
            TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE),
            TurmaDTO(id=2, numero_alunos=20, turno=TURNO_TESTE),
        ],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[
            TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2),
            TurmaDisciplinaDTO(turma_id=2, disciplina_id=1, carga_horaria_semanal=2),
        ],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )


def test_isolar_nucleo_encontra_as_duas_turmas_em_conflito():
    dados = _cenario_com_professor_sobrecarregado()
    nucleo = isolar_nucleo_infeasible(dados, timeout_por_tentativa=5.0, orcamento_total=20.0)

    assert nucleo == [1, 2]


def test_formatar_diagnostico_menciona_o_professor_partilhado():
    dados = _cenario_com_professor_sobrecarregado()
    mensagem = formatar_diagnostico_nucleo([1, 2], dados)

    assert "turmas 1 e 2" in mensagem
    assert "professor(es) 1" in mensagem


def test_isolar_nucleo_devolve_none_para_cenario_viavel():
    """Não deve nunca reportar um núcleo para um cenário que é, na verdade, viável."""
    slots = [SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 5)]
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=slots,
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=2)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )
    nucleo = isolar_nucleo_infeasible(dados, timeout_por_tentativa=5.0, orcamento_total=10.0)

    assert nucleo is None


def test_resolver_horario_reporta_pendencia_com_professor_partilhado_de_ponta_a_ponta():
    """Antes: INFEASIBLE com o núcleo isolado no campo `diagnostico`. Agora (RF13):
    OPTIMAL/FEASIBLE com uma pendência por turma, cada uma explicando o professor
    partilhado na razão."""
    dados = _cenario_com_professor_sobrecarregado()
    resultado = resolver_horario(dados, max_time_in_seconds=20.0, num_search_workers=4)

    assert resultado.status in ("OPTIMAL", "FEASIBLE")
    assert len(resultado.pendencias) >= 1
    turmas_pendentes = {p.turma_id for p in resultado.pendencias}
    assert turmas_pendentes & {1, 2}
    assert any("professor" in p.razao.lower() for p in resultado.pendencias)


def test_gerar_razao_pendencia_disciplina_excede_tempos_do_turno():
    """Causa barata #3: a própria carga da disciplina excede o total de tempos do
    turno da turma — deve ser identificada sem precisar da bisecção cara."""
    dados = HorarioInput(
        turmas=[TurmaDTO(id=1, numero_alunos=20, turno=TURNO_TESTE)],
        professores=[ProfessorDTO(id=1, classificacao=5, vinculo_casa=True)],
        salas=[SalaDTO(id=1, capacidade=30)],
        slots=[SlotDTO(dia_semana="segunda", turno=TURNO_TESTE, periodo=p) for p in range(1, 3)],  # só 2 tempos
        turma_disciplinas=[TurmaDisciplinaDTO(turma_id=1, disciplina_id=1, carga_horaria_semanal=6)],
        professor_disciplinas=[ProfessorDisciplinaDTO(professor_id=1, disciplina_id=1)],
        disponibilidades=[],
    )

    pendencia = gerar_razao_pendencia(1, 1, tempos_em_falta=4, dados=dados)

    assert pendencia.turma_id == 1
    assert pendencia.disciplina_id == 1
    assert pendencia.tempos_em_falta == 4
    assert "excede o total de tempos semanais do turno" in pendencia.razao
```

- [ ] **Step 2: Rodar para confirmar que falha**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_diagnostico.py -v`
Expected: FAIL — `gerar_razao_pendencia` ainda não existe (`ImportError`).

- [ ] **Step 3: Adicionar `gerar_razao_pendencia` a `diagnostico.py`**

Adicionar ao topo de `app/solver/diagnostico.py`, no bloco de imports:

```python
from app.solver.dto import HorarioInput, PendenciaDTO
```

Adicionar a função (antes de `_provado_infeasible`, depois de `formatar_diagnostico_nucleo`):

```python
def gerar_razao_pendencia(
    turma_id: int, disciplina_id: int, tempos_em_falta: int, dados: HorarioInput
) -> PendenciaDTO:
    """RF13 — traduz uma pendência de défice (turma, disciplina) numa razão
    acionável para o Gestor, verificando causas prováveis em ordem barata -> cara:

      1. carga da disciplina sozinha excede os tempos do turno da turma;
      2. soma da carga de TODAS as disciplinas da turma excede os tempos do turno;
      3. professor(es) qualificados desta disciplina todos ocupados nos mesmos
         tempos por outra turma (via bisecção, app/solver/isolar_nucleo_infeasible,
         mesmo orçamento de tempo já existente);
      4. fallback — nenhuma causa automática identificada.

    Nunca lança exceção: se a bisecção (causa 3) não convergir dentro do
    orçamento, cai no fallback genérico em vez de travar o relatório final."""
    turmas_por_id = {turma.id: turma for turma in dados.turmas}
    turma = turmas_por_id.get(turma_id)
    slots_por_turno: dict[str, int] = defaultdict(int)
    for slot in dados.slots:
        slots_por_turno[slot.turno] += 1
    total_tempos_turno = slots_por_turno.get(turma.turno if turma else None, 0)

    carga_disciplina = next(
        (td.carga_horaria_semanal for td in dados.turma_disciplinas if td.turma_id == turma_id and td.disciplina_id == disciplina_id),
        tempos_em_falta,
    )
    if carga_disciplina > total_tempos_turno:
        return PendenciaDTO(
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tempos_em_falta=tempos_em_falta,
            razao=(
                f"Turma {turma_id} / disciplina {disciplina_id}: carga_horaria_semanal "
                f"({carga_disciplina}) excede o total de tempos semanais do turno "
                f"'{turma.turno if turma else '?'}' ({total_tempos_turno}). Reduza a carga ou "
                "distribua a disciplina por mais de uma turma paralela."
            ),
        )

    carga_total_turma = sum(td.carga_horaria_semanal for td in dados.turma_disciplinas if td.turma_id == turma_id)
    if carga_total_turma > total_tempos_turno:
        return PendenciaDTO(
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tempos_em_falta=tempos_em_falta,
            razao=(
                f"Turma {turma_id}: a soma da carga_horaria_semanal de todas as disciplinas "
                f"({carga_total_turma}) excede o total de tempos semanais do turno "
                f"'{turma.turno if turma else '?'}' ({total_tempos_turno}). Aloque manualmente "
                "escolhendo quais disciplinas priorizar, ou revise a grade curricular desta turma."
            ),
            turmas_conflitantes=(turma_id,),
        )

    nucleo = isolar_nucleo_infeasible(dados)
    if nucleo and turma_id in nucleo:
        disciplinas_por_turma: dict[int, set[int]] = defaultdict(set)
        for td in dados.turma_disciplinas:
            if td.turma_id in nucleo:
                disciplinas_por_turma[td.turma_id].add(td.disciplina_id)
        professores_por_disciplina: dict[int, set[int]] = defaultdict(set)
        for pd in dados.professor_disciplinas:
            professores_por_disciplina[pd.disciplina_id].add(pd.professor_id)
        professores_desta_turma = {
            p for d in disciplinas_por_turma.get(turma_id, set()) for p in professores_por_disciplina.get(d, set())
        }
        outras_turmas = tuple(t for t in nucleo if t != turma_id)
        return PendenciaDTO(
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tempos_em_falta=tempos_em_falta,
            razao=(
                f"Turma {turma_id} / disciplina {disciplina_id}: professor(es) qualificados "
                f"partilhados com outra(s) turma(s) do mesmo turno ({', '.join(str(t) for t in outras_turmas)}) "
                "não têm tempos suficientes para atender todas em simultâneo. Aloque manualmente "
                "escolhendo outro professor qualificado (se existir) ou outro horário."
            ),
            professores_conflitantes=tuple(sorted(professores_desta_turma)),
            turmas_conflitantes=outras_turmas,
        )

    return PendenciaDTO(
        turma_id=turma_id,
        disciplina_id=disciplina_id,
        tempos_em_falta=tempos_em_falta,
        razao=(
            f"Turma {turma_id} / disciplina {disciplina_id}: {tempos_em_falta} tempo(s) não "
            "foram alocados automaticamente — conflito combinatório não identificado pelas "
            "verificações automáticas (ex: disponibilidade insuficiente de professores/salas "
            "face à carga total exigida). Aloque manualmente ou revise a grade desta turma."
        ),
    )
```

- [ ] **Step 4: Rodar os testes de diagnóstico**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_diagnostico.py -v`
Expected: `6 passed`.

- [ ] **Step 5: Rodar toda a suite do solver**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_solver.py tests/test_preprocessamento.py tests/test_orquestrador_turnos.py tests/test_diagnostico.py tests/test_heuristica_inicial.py -v 2>&1 | tail -60`
Expected: todos passam. Se `test_heuristica_inicial.py` falhar por assinatura de `build_objective`/`add_carga_horaria_cumprida`, ver Task 7 (hints não podem colidir com a variável de défice — mas hints só tocam `variaveis.x`, nunca `deficit`, então não deveria haver colisão; se houver falha, é provavelmente só um teste que chama `build_variables`+constraints diretamente sem passar por `resolver_horario` — verificar e ajustar a chamada de teste para capturar o novo retorno de `add_carga_horaria_cumprida`).

- [ ] **Step 6: Commit**

```bash
git add backend/app/solver/diagnostico.py backend/tests/test_diagnostico.py
git commit -m "feat(solver): diagnostico.py gera razão explicável por pendência (RF13)"
```

---

### Task 7: Suite completa + reprodução em escala real via Docker

**Files:**
- Test: suite completa + script de reprodução ad-hoc (não persistido no repo)

- [ ] **Step 1: Rodar a suite completa do backend**

Run: `cd backend && source .venv/bin/activate && python -m pytest -q 2>&1 | tail -30`
Expected: todos os testes passam (mesmo número de testes de antes, com os substituídos desta plano).

- [ ] **Step 2: Reproduzir com dados reais via Docker (BD já seedada — 86 turmas, 62 professores)**

```bash
newgrp docker <<'EOF'
cd /home/cristiano/src/timetable_problem_isaf/backend && source .venv/bin/activate && python -c "
from sqlmodel import Session
from app.core.database import engine
from app.services.horario_service import extrair_dados
from app.solver.orquestrador_turnos import resolver_horario_por_turnos

with Session(engine) as s:
    dados = extrair_dados(s, 2026, '1')

resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_por_turno=100.0, num_search_workers=8)
print('STATUS:', resultado.status)
print('Alocacoes:', len(resultado.alocacoes))
print('Pendencias:', len(resultado.pendencias))
for p in resultado.pendencias[:10]:
    print(' -', p.turma_id, p.disciplina_id, p.tempos_em_falta, '|', p.razao[:120])
"
EOF
```

Expected: `STATUS: OPTIMAL` ou `FEASIBLE` (nunca `INFEASIBLE` a menos que o tempo tenha mesmo esgotado sem nenhuma solução — se isso acontecer, é `UNKNOWN`/tempo, não escassez; confirmar lendo a mensagem de diagnóstico impressa, que deve mencionar "não encontrou nenhuma solução dentro do limite de tempo", nunca "conflito estrutural" ou "sem causa identificada").

- [ ] **Step 3: Se o passo 2 der `INFEASIBLE` por tempo esgotado, repetir com mais tempo antes de reportar como falha**

```bash
newgrp docker <<'EOF'
cd /home/cristiano/src/timetable_problem_isaf/backend && source .venv/bin/activate && python -c "
from sqlmodel import Session
from app.core.database import engine
from app.services.horario_service import extrair_dados
from app.solver.orquestrador_turnos import resolver_horario_por_turnos

with Session(engine) as s:
    dados = extrair_dados(s, 2026, '1')

resultado = resolver_horario_por_turnos(dados, max_time_in_seconds_por_turno=300.0, num_search_workers=8)
print('STATUS:', resultado.status)
print('Alocacoes:', len(resultado.alocacoes))
print('Pendencias:', len(resultado.pendencias))
"
EOF
```

- [ ] **Step 4: Commit final da task (se houve algum ajuste extra descoberto na reprodução real)**

```bash
git status
# só commitar se houve mudança de código; a reprodução em si não gera ficheiro persistido
```

---

### Task 8: Tempo de procura configurável (1/5/10 min) — schema, model, service, worker

**Files:**
- Modify: `app/schemas/job_schema.py`
- Modify: `app/models/job.py`
- Modify: `app/services/horario_service.py`
- Modify: `app/workers/job_runner.py`
- Modify: `app/solver/solve.py` (mensagem de `_diagnosticar_tempo_esgotado`)
- Test: `tests/test_horario_service.py`

**Interfaces:**
- Produces: `GerarHorarioRequest.tempo_maximo_minutos: Literal[1, 5, 10] = 5`
- Produces: `Job.tempo_maximo_minutos: int` (nova coluna)
- Produces: `HorarioService.disparar_geracao(ano_letivo, semestre, tempo_maximo_minutos=5) -> Job`
- Consumes em `job_runner.executar`: `job.tempo_maximo_minutos` em vez de `settings.solver_max_time_seconds*`

- [ ] **Step 1: Escrever o teste que falha primeiro**

Adicionar a `tests/test_horario_service.py` (usa o mesmo padrão de `_semear_cenario_viavel` já existente no ficheiro):

```python
def test_job_runner_respeita_tempo_maximo_escolhido_pelo_gestor():
    """RF09 — o Gestor escolhe 1/5/10 min por pedido; job_runner deve passar esse
    valor ao solver em vez do teto fixo de settings."""
    engine = _criar_engine_teste()

    with Session(engine) as session:
        _semear_cenario_viavel(session)
        job = JobRepository(session).criar(ano_letivo=2026, semestre="1", tempo_maximo_minutos=1)
        job_id = job.id
        assert job.tempo_maximo_minutos == 1

    executar(job_id, engine=engine)

    with Session(engine) as session:
        job = JobRepository(session).obter(job_id)
        assert job.status == JobStatus.DONE
```

- [ ] **Step 2: Rodar para confirmar que falha**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_horario_service.py::test_job_runner_respeita_tempo_maximo_escolhido_pelo_gestor -v`
Expected: FAIL — `JobRepository.criar` não aceita `tempo_maximo_minutos`.

- [ ] **Step 3: Adicionar a coluna ao model `Job`**

Em `app/models/job.py`, adicionar o campo depois de `semestre`:

```python
    semestre: str  # "1" | "2"
    # RF09 — tempo máximo de procura do CP-SAT escolhido pelo Gestor por pedido
    # (1, 5 ou 10 min; ver GerarHorarioRequest). UNKNOWN por tempo esgotado nunca
    # mais significa "impossível" (RF13 — RN05 é soft-com-défice), só "precisa de
    # mais tempo" — este campo dá ao Gestor a ação concreta de tentar de novo com
    # um valor maior.
    tempo_maximo_minutos: int = Field(default=5)
```

- [ ] **Step 4: Atualizar `GerarHorarioRequest`**

Em `app/schemas/job_schema.py`:

```python
class GerarHorarioRequest(SQLModel):
    """RF09 — âmbito da geração: um Job gera sempre o horário completo de todas as
    turmas de um único (ano_letivo, semestre) de uma só vez."""

    ano_letivo: int
    semestre: Literal["1", "2"]
    # RF13 — UNKNOWN por tempo esgotado é sempre "precisa de mais tempo", nunca
    # impossibilidade estrutural; o Gestor escolhe entre 3 opções, nunca um valor
    # livre (evita tempos de procura fora do que foi testado/documentado).
    tempo_maximo_minutos: Literal[1, 5, 10] = 5
```

E em `JobRead`, adicionar o campo para o Gestor ver o valor usado num Job já criado:

```python
class JobRead(SQLModel):
    id: str
    status: JobStatus
    criado_em: datetime
    concluido_em: datetime | None
    diagnostico: str | None
    ano_letivo: int
    semestre: str
    tempo_maximo_minutos: int
```

- [ ] **Step 5: Atualizar `JobRepository.criar`**

Em `app/repositories/job_repository.py`:

```python
    def criar(self, ano_letivo: int, semestre: str, tempo_maximo_minutos: int = 5) -> Job:
        job = Job(ano_letivo=ano_letivo, semestre=semestre, tempo_maximo_minutos=tempo_maximo_minutos)
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
```

- [ ] **Step 6: Atualizar `HorarioService.disparar_geracao`**

Em `app/services/horario_service.py`, localizar `disparar_geracao` e alterar:

```python
    def disparar_geracao(self, ano_letivo: int, semestre: str, tempo_maximo_minutos: int = 5) -> Job:
        """RF09 — cria o Job em PENDING para o âmbito (ano_letivo, semestre); o router
        dispara a execução em BackgroundTasks logo a seguir. `tempo_maximo_minutos`
        (RF13) é escolhido pelo Gestor por pedido — ver GerarHorarioRequest."""
        return self.job_repo.criar(ano_letivo=ano_letivo, semestre=semestre, tempo_maximo_minutos=tempo_maximo_minutos)
```

- [ ] **Step 7: Atualizar o router `POST /gerar-horario`**

Em `app/api/v1/routers/horario.py`, alterar a chamada:

```python
    job = service.disparar_geracao(payload.ano_letivo, payload.semestre, payload.tempo_maximo_minutos)
```

- [ ] **Step 8: Atualizar `job_runner.executar` para usar `job.tempo_maximo_minutos`**

Em `app/workers/job_runner.py`, substituir o bloco:

```python
        dados = extrair_dados(session, job.ano_letivo, job.semestre)
        if settings.solver_usar_decomposicao_turno:
            resultado = resolver_horario_por_turnos(
                dados,
                max_time_in_seconds_por_turno=settings.solver_max_time_seconds_por_turno,
                num_search_workers=settings.solver_num_search_workers,
            )
        else:
            resultado = resolver_horario(
                dados,
                max_time_in_seconds=settings.solver_max_time_seconds,
                num_search_workers=settings.solver_num_search_workers,
            )
```

por:

```python
        dados = extrair_dados(session, job.ano_letivo, job.semestre)
        tempo_total_segundos = job.tempo_maximo_minutos * 60
        if settings.solver_usar_decomposicao_turno:
            resultado = resolver_horario_por_turnos(
                dados,
                # 3 fases (Manhã/Tarde/Noite) dividem o orçamento total escolhido pelo
                # Gestor — mantém a mesma proporção que settings.solver_max_time_seconds_por_turno
                # já usava (100s de 300s totais = 1/3 por fase).
                max_time_in_seconds_por_turno=tempo_total_segundos / 3,
                num_search_workers=settings.solver_num_search_workers,
            )
        else:
            resultado = resolver_horario(
                dados,
                max_time_in_seconds=tempo_total_segundos,
                num_search_workers=settings.solver_num_search_workers,
            )
```

- [ ] **Step 9: Atualizar a mensagem de tempo esgotado em `solve.py`**

Em `app/solver/solve.py`, substituir `_diagnosticar_tempo_esgotado`:

```python
def _diagnosticar_tempo_esgotado(max_time_in_seconds: float) -> str:
    """UNKNOWN — o solver esgotou o tempo sem encontrar nenhuma solução (viável ou não).

    Não confundir com impossibilidade estrutural (RF13 — RN05 é soft-com-défice,
    nunca mais é essa a causa): isto só prova que o espaço de procura não foi
    explorado o suficiente no tempo dado (RNF01/RNF03)."""
    return (
        f"O solver não encontrou nenhuma solução dentro do limite de tempo "
        f"({max_time_in_seconds:.0f}s) — isto não significa que o cenário seja "
        "impossível, apenas que precisa de mais tempo de procura. Tente novamente "
        "escolhendo um tempo máximo maior (1, 5 ou 10 min)."
    )
```

- [ ] **Step 10: Rodar o teste da Task 8 e a suite completa**

Run: `cd backend && source .venv/bin/activate && python -m pytest tests/test_horario_service.py -v`
Expected: PASS.

Run: `cd backend && source .venv/bin/activate && python -m pytest -q 2>&1 | tail -20`
Expected: todos os testes passam.

- [ ] **Step 11: Migrar a coluna na BD real (Docker/Postgres já seedada)**

O projeto usa `init_db.py`/SQLModel `create_all` sem Alembic (confirmar lendo `app/core/database.py` antes deste passo — se não houver Alembic configurado, a tabela `job` já existente no Postgres real precisa da coluna nova via `ALTER TABLE`, já que `create_all` não altera tabelas existentes):

```bash
newgrp docker <<'EOF'
cd /home/cristiano/src/timetable_problem_isaf/backend && source .venv/bin/activate && python -c "
from sqlmodel import Session, text
from app.core.database import engine
with Session(engine) as s:
    s.exec(text('ALTER TABLE job ADD COLUMN IF NOT EXISTS tempo_maximo_minutos INTEGER NOT NULL DEFAULT 5'))
    s.commit()
print('coluna adicionada/confirmada')
"
EOF
```

- [ ] **Step 12: Commit**

```bash
git add backend/app/models/job.py backend/app/schemas/job_schema.py backend/app/repositories/job_repository.py backend/app/services/horario_service.py backend/app/api/v1/routers/horario.py backend/app/workers/job_runner.py backend/app/solver/solve.py backend/tests/test_horario_service.py
git commit -m "feat(backend): RF09 — Gestor escolhe tempo máximo de procura (1/5/10 min)"
```

---

### Task 9: Verificação final ponta-a-ponta

**Files:** nenhum (só verificação)

- [ ] **Step 1: Suite completa**

Run: `cd backend && source .venv/bin/activate && python -m pytest -q 2>&1 | tail -10`
Expected: todos os testes passam, nenhum warning novo de erro.

- [ ] **Step 2: Reprodução real via API (servidor local + Docker já rodando)**

```bash
newgrp docker <<'EOF'
cd /home/cristiano/src/timetable_problem_isaf/backend && source .venv/bin/activate
uvicorn app.main:app --port 8000 &
sleep 3
curl -s -X POST http://localhost:8000/gerar-horario \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat /tmp/isaf_test_token 2>/dev/null || echo dummy)" \
  -d '{"ano_letivo": 2026, "semestre": "1", "tempo_maximo_minutos": 5}'
EOF
```

Nota: se não houver um token de teste válido à mão (`require_gestor` exige autenticação Firebase), este passo pode ser pulado — a Task 7 (reprodução direta via `extrair_dados`+`resolver_horario_por_turnos`) já valida o comportamento do solver sem precisar do endpoint HTTP. Usar este passo só se um token de Gestor de teste já estiver disponível na sessão.

- [ ] **Step 3: Confirmar no output do passo 2 (ou da Task 7) que nunca aparece "conflito combinatório" nem "sem causa estrutural identificada" como motivo de bloqueio total — só pendências individuais ou (se tempo insuficiente) a mensagem de "tente novamente com mais tempo"**

- [ ] **Step 4: Parar o servidor de teste, se foi iniciado**

```bash
kill %1 2>/dev/null || true
```
