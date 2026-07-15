---
name: ortools-timetabling-solver
description: Use ao escrever ou alterar qualquer código dentro de backend/app/solver/ (builder.py, constraints_hard.py, constraints_soft.py, solve.py, result_mapper.py), ou ao discutir modelagem CP-SAT, variáveis esparsas, hard/soft constraints, função objetivo, tratamento de INFEASIBLE, ou o problema UCTP (University Course Timetabling Problem) do ISAF. Também usar ao decidir estrutura de dados que alimenta o solver.
---

# Motor de otimização — Google OR-Tools CP-SAT (ISAF)

## Regra de isolamento (inegociável)

`backend/app/solver/` nunca importa nada de `api/` ou de sessões SQLModel/FastAPI. Recebe apenas listas/objetos Python simples já filtrados pelos services. Devolve estruturas Python simples — quem persiste em `Alocacao` é o `result_mapper.py` chamado pelo service, nunca o solver a escrever na BD diretamente.

## Passo 1 — Extração (fora do solver, na service layer)

`horario_service.py` lê da BD e monta em memória: lista de `Turma`, `Disciplina`, `Professor`, `Sala`, `Slot` (45 = 9 tempos × 5 dias), `TurmaDisciplina`, `ProfessorDisciplina`, `Disponibilidade`.

## Passo 2 — Geração esparsa de variáveis (`builder.py`)

**Nunca** criar `model.NewBoolVar()` para todas as combinações turma × disciplina × professor × sala × slot (explosão combinatória). Filtrar em cascata, na ordem:

1. `TurmaDisciplina` → só pares (turma, disciplina) que existem na grade curricular (conjunto `E` da definição formal UCTP).
2. `ProfessorDisciplina` → só professores qualificados para aquela disciplina.
3. `Disponibilidade` do professor **OU** RN07 (sem registo = totalmente disponível) → só slots válidos por professor.
4. `Sala` com `capacidade >= turma.numero_alunos` — RN08 é soft (não elimina a variável, apenas penaliza depois; não filtrar aqui, só ordenar por preferência).

Cada `BoolVar` só existe se sobreviveu a todos os filtros acima. Nomear as variáveis de forma rastreável, ex: `x[turma_id, disciplina_id, professor_id, sala_id, slot_id]`, guardadas num dict esparso — não uma matriz N-dimensional densa.

## Passo 3 — Hard constraints (`constraints_hard.py`)

| ID | Regra | Como modelar |
|---|---|---|
| RN01 | Professor sem dupla alocação no mesmo slot | `sum(x[..., professor_id=p, slot_id=s] para todo turma/disciplina/sala) <= 1`, para cada (p, s) |
| RN02 | Turma sem duas disciplinas no mesmo slot | idem, fixando turma_id e slot_id |
| RN03 | Sala sem duas turmas no mesmo slot | idem, fixando sala_id e slot_id |
| RN05 | Carga horária semanal da disciplina cumprida integralmente | `sum(x[turma, disciplina, ...]) == TurmaDisciplina.carga_horaria_semanal` |
| RN06 | Aulas agrupadas em blocos, sem tempos isolados | usar variáveis auxiliares de "início de bloco" + restrições de adjacência no mesmo dia; proibir bloco de tamanho 1; sem limite máximo; carga ímpar → decompor em blocos par+ímpar (ex: 5 = 2+3) |

## Passo 4 — Soft constraints e função objetivo (`constraints_soft.py`)

```
minimizar: (peso_A × penalização_disponibilidade_RN04) + (peso_B × variância_distribuição_diária)
```

- **RN04** (peso alto) — penalizar alocações fora dos slots de disponibilidade registada pelo professor.
- **RN08** (peso muito alto, mas soft) — penalizar alocação em sala cuja capacidade não é a mais próxima adequada.
- **Equidade** — termo de variância na distribuição diária de aulas por professor (objetivo separado, não confundir com prioridade de fixação).

### Prioridade docente (usada para decidir ordem de fixação nos "Três Cenários Concorrentes")
Classificação institucional (50%) + vínculo/professor de casa (30%) + escassez de disponibilidade — menos slots livres = mais prioritário (20%). Turma tem prioridade estrutural sobre Professor: o solver aloca primeiro os professores de maior prioridade nos tempos fixos das turmas, depois distribui os restantes o mais próximo possível da disponibilidade registada.

## Passo 5 — Resolver (`solve.py`)

- Instanciar `CpModel()`, adicionar variáveis/constraints/objetivo, resolver com `CpSolver()` e `parameters.max_time_in_seconds` definido (nunca deixar sem limite).
- **Nunca** deixar `INFEASIBLE` propagar como exceção não tratada — devolver sempre um resultado estruturado que o service consegue transformar em diagnóstico JSON (RNF03, alimenta RF13/UC09).
- Ao investigar INFEASIBLE, considerar `model.AssumeConstraint` / `SufficientAssumptionsForInfeasibility` do CP-SAT para identificar quais constraints hard estão em conflito, e devolver isso no relatório em vez de um erro genérico.

## Passo 6 — Mapeamento do resultado (`result_mapper.py`)

Traduz `x[...] == 1` para entidades `Alocacao` (job_id, turma_id, disciplina_id, professor_id, sala_id, slot_id, penalizacao_aplicada). Quem persiste estas entidades é a service layer, não o solver.

## Testes

Validar com cenários pequenos e controlados primeiro (ex: 3 turmas) confirmando zero-conflitos antes de escalar para o tamanho real do ISAF (100+ professores, 60+ turmas — RNF01). Um teste de solver deve fixar `max_time_in_seconds` baixo e um caso conhecido (viável ou INFEASIBLE de propósito) para não deixar a suite lenta/instável.
