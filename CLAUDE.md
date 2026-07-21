# ISAF — Sistema Inteligente de Geração de Horários

Monorepo: `backend/` (FastAPI + OR-Tools CP-SAT), `frontend/` (Flutter + Firebase), `docs/` (fonte de verdade dos requisitos).

**Antes de qualquer alteração estrutural, ler:**
- `docs/04_04_analise_desenvolvimento.md` — RFs, RNFs, RNs (fonte de verdade única)
- `docs/03_especificacao_casos_uso.md` — UCs e fluxos
- `backend/CLAUDE.md` — regras específicas do backend (carregado automaticamente ao trabalhar em `backend/`)
- `frontend/CLAUDE.md` — regras específicas do frontend (carregado automaticamente ao trabalhar em `frontend/`)

## Stack (não-negociável)

| Camada | Tecnologia | Restrição |
|---|---|---|
| Frontend | Flutter + GoRouter | sem outras libs de routing |
| Estado (frontend) | Provider (global) + ValueNotifier (local) | sem Riverpod, Bloc, GetX |
| Backend | Python 3.11+ + FastAPI + Pydantic v2 | sem Django, Flask |
| Persistência | PostgreSQL + SQLModel | ver `backend/CLAUDE.md` para estado da decisão |
| Motor de otimização | Google OR-Tools CP-SAT | IA simbólica apenas — sem TensorFlow/PyTorch/scikit-learn |
| Autenticação | Firebase Authentication (email/senha + Google Sign-In) | backend valida ID Token (RN09) |
| Importação de dados | Excel (.xlsx) via openpyxl | validar → confirmar → idempotência (RF06-08) |

Se uma biblioteca não está nesta lista, perguntar antes de introduzir.

## Regra de arquitetura mais importante do projeto

O solver (CP-SAT) nunca importa nada de `api/`/routers. Fluxo unidirecional: `api → services → solver`.
O solver recebe listas Python simples já filtradas pelos services — nunca sessões de BD, nunca objetos HTTP.
BD ≠ variáveis do solver: entidades da BD são dados mestre; o modelo CP-SAT é gerado de forma esparsa (nunca denso — nunca iterar cegamente professor × turma × slot).

## Rastreabilidade

Cada ficheiro de código relevante referencia o RF/RN/UC que implementa, em comentário no topo:

```python
# Implementa: RF09 (UC08), RF10 (UC10) — ver docs/04_04_analise_desenvolvimento.md
```

## Convenção de commits

```
feat(backend): implementa RF09 — endpoint POST /gerar-horario
feat(frontend): UC12 — página de consulta de horário por professor
docs: atualiza 04_04_analise_desenvolvimento.md — adiciona RN13
fix(solver): corrige modelagem esparsa para turmas sem disciplinas
```

Formato: `tipo(âmbito): descrição — referência ao RF/UC quando aplicável`.
Trabalhamos por fases (ver `backend/CLAUDE.md` secção "Fases"); cada fase concluída gera commit próprio.

## Idioma

- Código (variáveis, funções, classes, ficheiros): inglês.
- Comentários explicando o *porquê*: inglês.
- Mensagens de erro devolvidas pela API ao cliente Flutter: português (Angola).
- Strings visíveis na UI Flutter: português (Angola).
- Documentação e ficheiros de skill/CLAUDE.md: português.

## O que nunca vai para o repositório

`.env`, `*.key`, `*.pem`, `__pycache__/`, `build/`, `.venv/`, `.dart_tool/` — cobertos pelo `.gitignore` raiz.

## Skills disponíveis (`.claude/skills/`)

- `ortools-timetabling-solver` — modelagem esparsa CP-SAT, hard/soft constraints, função objetivo, INFEASIBLE.
- `fastapi-clean-architecture` — layering do backend (router → service → repository/solver), Pydantic, jobs assíncronos.
- `excel-import-openpyxl` — padrão de importação em massa (validar → confirmar → idempotência).
- `flutter-clean-firebase` — Clean Architecture no Flutter, Provider/ValueNotifier, Firebase, GoRouter.

Nota: `frontend/.agents/rules/honorgestrule.md` é o ficheiro de regras usado pelo Antigravity (outro IDE/agente). O `frontend/CLAUDE.md` é o equivalente para Claude Code — mantém as duas fontes sincronizadas se uma mudar.
