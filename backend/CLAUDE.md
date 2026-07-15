# Backend — ISAF (FastAPI + OR-Tools CP-SAT)

> Especificação completa em `../docs/06_arquitetura_backend.md` e `../docs/analise_requisitos_v5.0.md`. Este ficheiro é o resumo operacional para desenvolvimento no dia-a-dia — em caso de conflito, os docs em `docs/` são a fonte de verdade.

## Princípio fundamental — BD ≠ variáveis do solver

O CP-SAT não lê a BD diretamente. Fluxo sempre em três passos:
1. **Extração** — ler entidades relevantes da BD para memória (objetos Python/Pydantic).
2. **Geração esparsa do modelo** — criar `BoolVar` do CP-SAT apenas para combinações válidas, filtradas pelas relações da BD. Nunca modelagem densa.
3. **Persistência do resultado** — output do solver gravado em `Job` e `Alocacao`.

## Estrutura de pastas (Clean Architecture — solver isolado da API)

```
backend/
├── app/
│   ├── main.py                  # instancia FastAPI, routers, middleware Firebase
│   ├── core/
│   │   ├── config.py            # settings via env vars
│   │   ├── security.py          # validação do Firebase ID Token → 401
│   │   └── database.py          # engine + sessão SQLModel
│   ├── models/                  # SQLModel — entidades ORM (mapeiam o ER)
│   ├── schemas/                 # Pydantic — contratos de entrada/saída da API
│   ├── repositories/            # CRUD puro, sem lógica de negócio
│   ├── services/                # lógica de negócio (RN01-RN11), orquestra repositórios
│   ├── solver/                  # ⚠️ ISOLADO — nunca importa FastAPI/routers
│   │   ├── builder.py           # gera variáveis esparsas
│   │   ├── constraints_hard.py  # RN01, RN02, RN03, RN05, RN06
│   │   ├── constraints_soft.py  # RN04, RN08 + função objetivo
│   │   ├── solve.py             # CpModel, CpSolver, resultado bruto
│   │   └── result_mapper.py     # resultado do solver → entidades Alocacao
│   ├── api/v1/
│   │   ├── routers/             # rotas finas — chamam services, nunca o solver diretamente
│   │   └── deps.py              # dependências (auth, sessão BD)
│   └── workers/
│       └── job_runner.py        # executa o solver em background, atualiza Job.status
├── tests/
└── requirements.txt
```

**Regra inegociável:** `solver/` nunca importa nada de `api/`. Comunicação unidirecional: `api → services → solver`. O solver recebe listas Python simples já filtradas, nunca sessões de BD.

## Proibições absolutas

- **NUNCA** gerar matrizes densas no solver (ex: iterar todos os professores × todas as turmas × todos os slots às cegas).
- **NUNCA** chamar o CP-SAT solver diretamente de um router FastAPI — sempre através da camada Service.
- **NUNCA** deixar um status INFEASIBLE do solver rebentar a API — devolver sempre um diagnóstico JSON estruturado (RNF03).
- **NUNCA** usar `dict` cru onde deveria existir um modelo Pydantic.
- **NUNCA** bloquear a ligação HTTP em operações estimadas a demorar mais de 5s — usar o padrão Job Queue (`BackgroundTasks`, sem Celery/Redis no MVP).

## Persistência — nota de decisão

`docs/06_arquitetura_backend.md` (Fase 0) propõe SQLite para simplicidade do MVP. `docs/analise_requisitos_v5.0.md` (secção 8, decisão de 15/07 — mais recente) fixa **PostgreSQL + SQLModel**. Seguir a decisão mais recente (PostgreSQL) salvo indicação contrária do utilizador — confirmar antes de gerar `requirements.txt`/`database.py` na Fase 0.

## Modelos SQLModel de referência

Ver `../docs/06_arquitetura_backend.md` secção 4 para os campos exatos de `Slot`, `Turma`, `TurmaDisciplina`, `ProfessorDisciplina`, `Disponibilidade`, `Job`, `Alocacao`. Nomes e FKs devem seguir exatamente essa especificação (é o contrato com o Diagrama ER da tese).

## Fases de implementação (ordem estrita)

0. **Setup** — venv, `requirements.txt` (`fastapi`, `uvicorn`, `sqlmodel`, `ortools`, `firebase-admin`, `python-multipart`, `openpyxl`, `pytest`, driver Postgres).
1. **Camada de dados** — todos os modelos SQLModel; `init_db.py` cria tabelas; seed dos 45 `Slot` (9 tempos × 5 dias).
2. **CRUD + Importação (RF01-RF08)** — repositórios CRUD por entidade; `importacao_service.py` (parser Excel, validar → confirmar, idempotência por `codigo` único); rotas REST finas.
3. **Solver (núcleo científico)** — usar a skill `ortools-timetabling-solver` para o design do `builder.py`/constraints/`solve.py`.
4. **Assíncrono (RF09/RF10)** — `POST /gerar-horario` cria `Job(PENDING)`, dispara `job_runner.py` via `BackgroundTasks`, devolve `job_id` imediato; `GET /jobs/{job_id}` para polling; INFEASIBLE → `Job.status="INFEASIBLE"` (RF13/UC09), nunca erro genérico.
5. **Consulta (RF11/RF12)** — `GET /horarios/turma/{id}` e `GET /horarios/professor/{id}` devolvem JSON estruturado por dia/slot, pronto para o Flutter desserializar — nunca linhas soltas de `Alocacao`.
6. **Segurança (RF15/RF16/RN09/RN10)** — middleware valida Firebase ID Token em todas as rotas exceto login/reset; 401 se ausente/inválido; RN10 valida email do Professor vs. registo do Gestor → 403 se não corresponder.
7. **Testes** — cenários pequenos e controlados (ex: 3 turmas) validando zero-conflitos antes de escalar.

Cada fase concluída = um commit (ver convenção em `../CLAUDE.md`).

## Regras de negócio do solver (referência rápida)

| ID | Regra | Tipo |
|---|---|---|
| RN01 | Professor sem dupla alocação no mesmo slot | Hard |
| RN02 | Turma sem duas disciplinas no mesmo slot | Hard |
| RN03 | Sala sem duas turmas no mesmo slot | Hard |
| RN04 | Alocação mais próxima da disponibilidade do Professor | Soft (peso alto) |
| RN05 | Carga horária semanal da Disciplina cumprida integralmente | Hard |
| RN06 | Aulas agrupadas em blocos — sem tempos isolados | Hard |
| RN07 | Professor sem disponibilidade registada = totalmente disponível | Fallback |
| RN08 | Sala com capacidade adequada preferencial | Soft (peso muito alto) |
| RN09 | ID Token Firebase válido em todos os pedidos exceto RF15/RF16 | Hard → 401 |
| RN10 | Email da conta Firebase do Professor corresponde ao registo do Gestor | Hard → 403 |
| RN11 | Gestor consulta/exporta qualquer horário; Professor só o seu | Hard |

Detalhe de modelagem completo (função objetivo, agrupamento em blocos, prioridade docente) está na skill `ortools-timetabling-solver`.
