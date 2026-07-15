---
name: fastapi-clean-architecture
description: Use ao criar ou alterar routers, services, repositories, schemas Pydantic ou models SQLModel em backend/app/, ao desenhar novos endpoints REST, ao implementar autenticação Firebase no backend, ou ao decidir onde deve viver uma peça de lógica (router vs service vs repository vs solver). Não cobre a modelagem CP-SAT em si — ver ortools-timetabling-solver para isso.
---

# Backend FastAPI — Clean Architecture (ISAF)

## Camadas e responsabilidade única

```
router  → apenas HTTP: parse de request, chamar 1 método de service, devolver response
service → lógica de negócio (RN01-RN11), orquestra repositories e (quando aplicável) o solver
repository → CRUD puro sobre SQLModel, sem regra de negócio
solver  → isolado (ver skill ortools-timetabling-solver) — nunca chamado diretamente por um router
schemas → Pydantic v2, contratos de entrada/saída — nunca expor models SQLModel diretamente na API
```

Um router nunca deve conter uma query SQLModel nem uma chamada ao `CpSolver` — sempre delega ao service correspondente.

## Padrão de endpoint (referência)

```python
# app/api/v1/routers/turma.py
# Implementa: RF02 (UC02) — ver docs/analise_requisitos_v5.0.md

@router.post("/turmas", response_model=TurmaSchema)
async def criar_turma(payload: TurmaCreateSchema, service: TurmaService = Depends(get_turma_service)):
    return await service.criar(payload)
```

O router não sabe como a turma é validada ou persistida — isso é do `TurmaService` + `TurmaRepository`.

## Schemas Pydantic

- Um schema por direção quando os campos diferem: `TurmaCreateSchema` (entrada) vs `TurmaSchema` (saída) — nunca reaproveitar cegamente o model SQLModel como schema de resposta se houver campos internos (ex: chaves de idempotência, timestamps de auditoria) que não devem ir para o cliente.
- Respostas de horário (`horario_schema.py`) devem estruturar por dia/slot, prontas para o Flutter desserializar diretamente em entities — nunca devolver uma lista solta de `Alocacao`.

## Padrão de job assíncrono (RF09/RF10)

Nenhuma operação estimada em mais de 5s bloqueia a conexão HTTP. Padrão:

1. `POST /gerar-horario` cria `Job(status="PENDING")`, dispara `BackgroundTasks` chamando `job_runner.py`, devolve `{job_id}` imediatamente (sem `await` no processamento pesado).
2. `job_runner.py` corre o service do solver, atualiza `Job.status` para `RUNNING` → `DONE`/`INFEASIBLE`.
3. `GET /jobs/{job_id}` devolve o estado atual para polling do frontend.

Sem Celery/Redis nesta fase (MVP) — `BackgroundTasks` do FastAPI é suficiente e é a decisão de arquitetura já fechada.

## Autenticação (RF15/RF16/RN09/RN10)

- Middleware/dependency em `core/security.py` valida o Firebase ID Token em todas as rotas exceto login/reset de password.
- Token ausente ou inválido → `401`.
- RN10: ao validar o Professor, o email do token Firebase deve corresponder ao registo criado pelo Gestor (RF01) → `403` se não corresponder.
- RN11: Gestor acede a qualquer horário; Professor só ao seu próprio — validar isto na service layer (`UC15`), não confiar em filtros do frontend.

## Erros

- Mensagens de erro devolvidas ao cliente: português (Angola) (ver `../../CLAUDE.md`).
- Nunca deixar uma exceção genérica de 500 chegar ao cliente sem contexto — usar `HTTPException` com `detail` estruturado, especialmente para o caso INFEASIBLE do solver (RNF03).

## Testes

- Testar services isoladamente com repositories em memória/mock ou BD de teste — não depender do solver real nos testes de CRUD.
- Testes de router usam `TestClient` do FastAPI, com dependência de auth substituída por override (`app.dependency_overrides`).
