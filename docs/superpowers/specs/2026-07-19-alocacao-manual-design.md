# Alocação Manual (API) — Design

Sub-projeto 2 de 3 (ver conversa de brainstorming de 2026-07-18/19). Depende do
sub-projeto 1 (solver nunca INFEASIBLE, concluído — commit `5118178` da branch
`feat/backend-fase8-solver-performance`), que introduziu `SolverResult.pendencias`.

## Contexto

Depois de o solver gerar o horário, algumas `(turma, disciplina)` podem ficar
com tempos por preencher (défice de RN05, ver sub-projeto 1). O Gestor precisa
de conseguir:
1. Ver quais turmas/disciplinas ficaram por distribuir, e porquê.
2. Alocar manualmente um professor a um slot livre para preencher essa lacuna.
3. Reatribuir/mover alocações já existentes (trocar disciplina, professor, ou
   slot) mesmo fora do contexto de uma lacuna — correção geral pós-geração.

## Persistência de pendências — nova tabela `Pendencia`

Hoje `SolverResult.pendencias` (lista de `PendenciaDTO`) só existe em memória
durante a execução do `job_runner`. Passa a ser persistida, espelhando o
padrão já usado por `Alocacao` (RF11/RF12):

```python
# app/models/pendencia.py
class Pendencia(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="job.id", index=True)
    turma_id: int = Field(foreign_key="turma.id")
    disciplina_id: int = Field(foreign_key="disciplina.id")
    tempos_em_falta: int
    razao: str
    professores_conflitantes: str = ""  # CSV de IDs — SQLite/Postgres both suportam texto simples, sem tabela associativa extra
    turmas_conflitantes: str = ""       # idem
```

`job_runner.executar` grava as pendências no fim do job (sucesso ou não —
mesmo um job "DONE" pode ter pendências), tal como já grava `Alocacao`.

## Validações reaproveitadas do solver (RN01-RN06) para alocação manual

A alocação manual não passa pelo CP-SAT — é uma escrita direta e imperativa —
mas tem de respeitar as mesmas regras hard que o solver já impõe, verificadas
diretamente contra `Alocacao` existentes na BD (não contra variáveis do
modelo):

- **RN01** (professor sem dupla alocação): nenhuma outra `Alocacao` do mesmo
  `job_id` com o mesmo `professor_id` no mesmo `(dia_semana, periodo)`.
- **RN02** (turma sem dupla disciplina): idem para `turma_id`.
- **RN03** (sala sem dupla turma): idem para `sala_id`.
- **RN06** (bloco contíguo ≥2, sem tempo isolado): a alocação manual é sempre
  para um **bloco** (não um tempo isolado) — o Gestor escolhe um conjunto de
  slots contíguos do mesmo dia/turno, nunca um único tempo solto, mesmo
  professor e sala em todo o bloco.
- **Qualificação** (não é RN numerada, mas é hard de facto): o `professor_id`
  escolhido tem de ter `ProfessorDisciplina` para a `disciplina_id` alocada —
  reforça a decisão já tomada de que "no modelo manual o gestor só vai
  conseguir colocar o professor se ele tiver a disciplina exigida."

Qualquer violação devolve `409 Conflict` com mensagem específica de qual regra
falhou (nunca uma mensagem genérica) — o Gestor decide outro slot/professor/sala.

## Endpoints novos (`app/api/v1/routers/alocacao.py`)

Todos exigem `require_gestor` (mesma proteção de `/gerar-horario`).

### `GET /jobs/{job_id}/pendencias`
Lista as pendências desse job — `[{turma_id, disciplina_id, tempos_em_falta,
razao, professores_conflitantes: [int], turmas_conflitantes: [int]}]`.

### `GET /turmas/{turma_id}/professores-qualificados?disciplina_id=X`
Devolve `[{id, nome, classificacao, vinculo_casa}]` — só professores com
`ProfessorDisciplina(professor_id, disciplina_id=X)`. 404 se a turma ou
disciplina não existir.

### `GET /turmas/{turma_id}/slots-vagos?job_id=X`
Devolve os slots do turno da turma sem nenhuma `Alocacao(job_id=X,
turma_id=turma_id)`, agrupados em blocos contíguos ≥2 por dia — formato
`[{dia_semana, turno, periodos: [int, int, ...]}]` (cada entrada já é um bloco
válido de tamanho ≥2; a UI oferece o bloco inteiro, não períodos soltos).

### `POST /alocacoes`
Body: `{job_id, turma_id, disciplina_id, professor_id, sala_id, dia_semana,
turno, periodos: [int, ...]}` (`periodos` é a lista de tempos contíguos do
bloco, mínimo 2). Cria uma `Alocacao` por período do bloco, todas com o mesmo
professor/sala/disciplina — atomicamente (tudo ou nada: se qualquer período do
bloco falhar uma validação, nenhuma é criada). Se o défice da
`(turma_id, disciplina_id)` for coberto pela nova alocação, a `Pendencia`
correspondente é removida (ou o `tempos_em_falta` decrementado, se ainda
sobrar défice).

### `PATCH /alocacoes/{id}`
Body parcial: `{disciplina_id?, professor_id?, sala_id?, dia_semana?, turno?,
periodo?}` — move/reatribui uma única `Alocacao` existente (um período). Nunca
edita o bloco inteiro de uma vez (o Gestor edita período a período se quiser
reestruturar um bloco) — reaplica RN01-RN03 contra o novo valor; RN06 é
verificado no conjunto de `Alocacao` resultante do mesmo
`(job_id, turma_id, disciplina_id, professor_id, sala_id, dia_semana, turno)`
após a edição (o período editado não pode ficar isolado do resto do bloco).

### `DELETE /alocacoes/{id}`
Remove uma `Alocacao`. Se isso reabrir um défice na `(turma_id,
disciplina_id)` desse job (menos períodos alocados que
`carga_horaria_semanal`), cria/atualiza a `Pendencia` correspondente com razão
genérica "Removido manualmente pelo Gestor."

## Ficheiros afetados

- `app/models/pendencia.py` — nova tabela.
- `app/repositories/pendencia_repository.py` — CRUD + `listar_por_job`.
- `app/workers/job_runner.py` — persiste `resultado.pendencias` no fim do job.
- `app/schemas/alocacao_schema.py` — schemas de request/response dos endpoints novos.
- `app/services/alocacao_manual_service.py` — validações RN01-RN06 + qualificação, orquestra repositórios.
- `app/api/v1/routers/alocacao.py` — os 5 endpoints.
- `app/main.py` — registar o novo router.
- Testes: `tests/test_alocacao_manual_service.py`, `tests/test_alocacao_router_http.py` (ou nome consistente com `test_auth_router_http.py` já existente).

## Fora de âmbito (sub-projeto 3)

- UI Flutter (dropdowns, Ficha do Docente, grade colorida) — consome estes
  endpoints, mas o desenho da UI é tratado à parte.

## Testes

- Alocação manual bem-sucedida preenche défice e remove/reduz a `Pendencia`.
- Conflito RN01/RN02/RN03 devolve 409 com mensagem específica.
- Professor não qualificado devolve 409 (nunca 500).
- Bloco de tamanho 1 é rejeitado (RN06).
- `PATCH` que isola um período do seu bloco é rejeitado (RN06).
- `DELETE` que reabre défice recria/atualiza `Pendencia`.
- `GET /turmas/{id}/slots-vagos` nunca devolve blocos de tamanho 1.
