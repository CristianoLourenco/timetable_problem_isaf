# Solver nunca devolve INFEASIBLE — Design

Sub-projeto 1 de 3 (ver conversa de brainstorming de 2026-07-18). Os outros dois —
alocação manual (API + UI) e UI da Ficha do Docente / grade renovada — dependem
deste, porque só faz sentido mostrar/preencher pendências depois de o solver
deixar de bloquear com INFEASIBLE.

## Contexto e causa raiz confirmada

RN04 (disponibilidade do professor) já é modelada como soft — `builder.py` nunca
filtra variáveis por disponibilidade, só `constraints_soft.py` penaliza no
objetivo. Isto foi confirmado lendo o código antes de desenhar a solução: **o
INFEASIBLE real observado em produção (job `c5193bdb...`, ano 2026/semestre 1,
turno tarde) não vem de disponibilidade** — vem de RN05 (`add_carga_horaria_cumprida`,
hoje `sum(x) == carga_horaria_semanal`) se tornar impossível de cumprir
exatamente quando a escassez de professores qualificados (RN01 continua hard:
um professor não pode dar duas aulas em simultâneo) ou de tempos do turno
torna inatingível a carga completa de uma disciplina.

Casos adicionais que hoje bloqueiam **antes** de sequer montar o modelo
(`preprocessamento.podar_dominio`):
- turma_disciplina sem nenhum `ProfessorDisciplina` qualificado;
- turma com `numero_alunos` acima da capacidade máxima entre todas as salas.

Decisão do utilizador: nenhum destes casos deve impedir a geração do horário.
Todos devem virar **pendência** (défice de tempos por preencher), nunca um erro
que bloqueia o job inteiro. RN01 (professor sem dupla alocação), RN02 (turma sem
dupla disciplina), RN03 (sala sem dupla turma) e RN06 (blocos contíguos)
continuam hard — são fisicamente/logicamente absolutas, e folgam naturalmente
quando RN05 aceita défice em vez de exigir o valor exato.

## Mudança central: RN05 de hard-exato para soft-com-défice

`add_carga_horaria_cumprida` (`constraints_hard.py`) muda de:

```python
model.Add(sum(variaveis.x[c] for c in chaves) == td.carga_horaria_semanal)
```

para:

```python
deficit = model.NewIntVar(0, td.carga_horaria_semanal, f"deficit_t{td.turma_id}_d{td.disciplina_id}")
model.Add(sum(variaveis.x[c] for c in chaves) + deficit == td.carga_horaria_semanal)
```

Quando `chaves` está vazio (turma_disciplina sem nenhuma variável possível —
sem professor qualificado ou sem sala válida, ambos já detectados por
`podar_dominio`), `deficit` fica livre para ser fixado no valor máximo
(`carga_horaria_semanal`) sem qualquer termo de `x` — o CP-SAT resolve
trivialmente, sem custo de procura.

A função devolve (além de nada, hoje) o dicionário
`{(turma_id, disciplina_id): deficit_var}` para o objetivo e o result_mapper
usarem.

## Objetivo: penalizar défice fortemente

`build_objective` (`constraints_soft.py`) ganha um novo termo:

```python
settings.solver_peso_deficit_rn05 * sum(deficit_vars.values())
```

Peso proposto: `1000` (constante em `core/config.py`, ao lado de
`solver_peso_rn04_disponibilidade=10` e `solver_peso_rn08_capacidade=20`) —
suficientemente alto para que preencher a carga toda vença qualquer combinação
de penalizações RN04×prioridade + RN08 + equidade, mas ainda finito (o solver
continua a resolver corretamente quando cumprir tudo é possível).

## `podar_dominio` deixa de bloquear

`preprocessamento.py` para de devolver `problemas_estruturais` como motivo de
INFEASIBLE upfront. Em vez disso devolve uma lista de
`PendenciaEstruturalDTO(turma_id, disciplina_id, razao)` para os dois casos que já
detecta (sem professor qualificado / turma sem sala com capacidade). Essas
entradas nunca geram variáveis em `build_variables` (continuam corretamente
fora do modelo) e entram diretamente como défice total na lista final de
pendências.

`resolver_horario` deixa de ter o branch de retorno antecipado
`INFEASIBLE` a partir de `problemas_estruturais`.

## `solve.py` — status esperado

Com RN05 sempre satisfazível (via défice), o CP-SAT só pode devolver:
- `OPTIMAL` / `FEASIBLE` — caso normal, com ou sem pendências;
- `UNKNOWN` — tempo esgotado sem encontrar solução (cenário muito maior que o
  esperado); continua a ser reportado como está hoje
  (`_diagnosticar_tempo_esgotado`), nunca como impossibilidade estrutural.

`INFEASIBLE` deixa de ser um status que `resolver_horario` produz em uso
normal. Mantém-se apenas como valor teoricamente possível do enum de status —
não é removido do tipo, só nunca mais é o caminho esperado.

## Diagnóstico de pendências — reaproveita `diagnostico.py`

Em vez de descartar `_diagnosticar_infeasible`/`isolar_nucleo_infeasible`
(ficariam órfãs, já que nunca mais há um INFEASIBLE genuíno por escassez para
diagnosticar), a lógica muda de propósito: **gerar a razão de cada pendência
individual**, para o Gestor perceber porquê e como resolver.

Depois do solve, para cada `(turma_id, disciplina_id)` com `deficit > 0`,
construir uma `PendenciaDTO` com uma razão textual, verificada em ordem
barata → cara (reaproveitando o que `_diagnosticar_infeasible` já sabia
verificar, adaptado a per-pendência em vez de per-cenário):

| # | Causa verificada | Barato/caro | Campos extra na pendência |
|---|---|---|---|
| 1 | Sem `ProfessorDisciplina` (upfront, de `podar_dominio`) | Barato | — |
| 2 | Turma sem sala com capacidade suficiente (upfront) | Barato | — |
| 3 | `carga_horaria_semanal` da disciplina sozinha excede os tempos do turno | Barato | — |
| 4 | Soma da carga de todas as disciplinas da turma excede os tempos do turno | Barato | `turmas_conflitantes` (a própria) |
| 5 | Professor(es) qualificados todos ocupados nos mesmos tempos por outra turma | Médio (cruzar `por_professor_tempo` do resultado) | `professores_conflitantes`, `turmas_conflitantes` |
| 6 | Fallback: `isolar_nucleo_infeasible` adaptado — tenta isolar, com o mesmo orçamento de tempo já existente (`solver_diagnostico_orcamento_total`), um subconjunto de turmas cujo défice persiste mesmo sem as outras | Caro | `turmas_conflitantes` (núcleo encontrado) |
| 7 | Fallback final: nenhuma causa automática identificada | — | — |

Cada `PendenciaDTO` (novo em `dto.py`):

```python
@dataclass(frozen=True)
class PendenciaDTO:
    turma_id: int
    disciplina_id: int
    tempos_em_falta: int
    razao: str
    professores_conflitantes: tuple[int, ...] = ()
    turmas_conflitantes: tuple[int, ...] = ()
```

`SolverResult` ganha `pendencias: list[PendenciaDTO] = field(default_factory=list)`.

## Ficheiros afetados

- `app/solver/dto.py` — `PendenciaDTO`, `SolverResult.pendencias`.
- `app/solver/constraints_hard.py` — `add_carga_horaria_cumprida` devolve dict de défice.
- `app/solver/constraints_soft.py` — novo termo no objetivo.
- `app/solver/preprocessamento.py` — não bloqueia; devolve pendências estruturais.
- `app/solver/solve.py` — remove branch de INFEASIBLE upfront; monta `pendencias` no fim.
- `app/solver/diagnostico.py` — funções adaptadas para gerar razão por pendência em vez de provar impossibilidade total.
- `app/solver/result_mapper.py` — sem mudança de contrato (continua só a mapear `x`); pendências vêm de função nova em `solve.py`/`diagnostico.py`.
- `app/core/config.py` — `solver_peso_deficit_rn05: int = 1000`.
- `app/solver/orquestrador_turnos.py` — precisa de agregar `pendencias` de cada fase (Manhã/Tarde/Noite) no resultado final.
- Testes: `test_solver.py`, `test_diagnostico.py`, `test_preprocessamento.py`, `test_orquestrador_turnos.py`, `test_heuristica_inicial.py` (hints não podem colidir com a nova variável de défice).

## Fora de âmbito (fica para os sub-projetos 2 e 3)

- Persistir pendências em BD / expor via API (`Job`/`Alocacao`) — sub-projeto 2.
- Endpoints e UI de alocação manual — sub-projeto 2.
- UI da Ficha do Docente e grade renovada, incluindo a secção de "professores/turmas por distribuir" no ecrã de horário — sub-projeto 3.

## Testes

- Cenário com 2 turmas partilhando o único professor qualificado no mesmo
  turno (o caso real que já existe em `test_diagnostico.py`) — antes dava
  INFEASIBLE, agora deve dar `OPTIMAL`/`FEASIBLE` com pendências não-vazias e
  razão mencionando o professor partilhado.
- Cenário com turma_disciplina sem nenhum `ProfessorDisciplina` — pendência com
  défice = carga total, razão "sem professor qualificado".
- Cenário viável sem escassez (os já existentes) — continuam a dar zero
  pendências, comportamento idêntico ao atual.
- Reprodução em escala real (seed real via Docker/Postgres, ano 2026 semestre 1)
  — job deve terminar com status ≠ INFEASIBLE e uma lista de pendências
  reportável.
