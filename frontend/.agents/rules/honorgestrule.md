---
trigger: always_on
---

# ISAF Timetabling System — Global Rules
> These rules are ALWAYS active. They are non-negotiable and apply to every
> file, every feature, and every agent action in this project.

---

## 1. Stack (Non-Negotiable)

| Layer | Technology | Hard Constraint |
|---|---|---|
| Frontend | Flutter + GoRouter | No alternative routing libraries |
| State Management | Provider (global) + ValueNotifier (local) | No Riverpod, Bloc, or GetX |
| Backend | Python 3.11+ + FastAPI + Pydantic v2 | No Django, Flask, or other frameworks |
| AI Engine | Google OR-Tools CP-SAT | Symbolic AI only — NO probabilistic ML (no TensorFlow, PyTorch, scikit-learn) |
| Serialization | JSON via Pydantic schemas (backend) and Dart models (frontend) | No raw dicts or dynamic maps |

**If a library or framework is not listed above, ask before using it.**

---

## 2. Language & Communication

- All code (variables, functions, classes, files): **English**
- All code comments explaining *why*: **English**
- All API error messages returned to the Flutter client: **Portuguese (Angola)**
- All user-facing strings in the Flutter UI: **Portuguese (Angola)**
- All documentation and SKILL files: **Portuguese**

---

## 3. Absolute Prohibitions

### Backend
- **NEVER** generate dense matrices in the solver (e.g., iterating all teachers × all classes × all slots blindly)
- **NEVER** call the CP-SAT solver directly from a FastAPI router — always go through a Service layer
- **NEVER** let an INFEASIBLE solver status crash the API — always return a structured JSON diagnostic
- **NEVER** use raw `dict` where a Pydantic model should exist
- **NEVER** block the HTTP connection for operations estimated to take more than 5 seconds — use the Job Queue pattern

### Frontend
- **NEVER** access a Provider directly inside a Component widget — pass data as parameters
- **NEVER** put business logic inside a Screen file — Screens are layout containers only
- **NEVER** put UI imports (material.dart) inside Domain layer files
- **NEVER** skip the `_init()` hydration method in a Controller
- **NEVER** implement `copyWith` without the sentinel pattern — null must be settable explicitly

### General
- **NEVER** suggest replacing any component of the defined stack
- **NEVER** mix solver mathematics with HTTP routing logic
- **NEVER** hardcode academic calendar values — they must come from configuration or API payload

---

## 4. Project Folder Map (Reference)

```
lib/
├── core/
│   ├── router/         # GoRouter configuration (app_router.dart)
│   ├── themes/         # AppTheme, AppColors, AppTextStyles
│   ├── constants/      # App-wide constants
│   └── errors/         # Failure classes, error handling
│
└── features/
    └── [feature_name]/
        ├── domain/
        │   ├── entities/
        │   ├── repositories/   # Abstract interfaces only
        │   └── usecases/
        ├── data/
        │   ├── dtos/
        │   ├── datasources/
        │   └── repositories/   # Concrete implementations
        └── presentation/
            ├── states/         # Immutable state classes
            ├── controllers/    # ValueNotifier<State>
            ├── providers/      # ChangeNotifier (global cache)
            ├── screens/        # Scaffold only
            └── components/
                └── [screen_name]_components/

api/                            # Python FastAPI backend
├── routers/                    # HTTP layer only
├── services/                   # Business logic + solver orchestration
├── schemas/                    # Pydantic input/output models
└── core/
    └── solver/                 # CP-SAT engine — isolated, no HTTP imports
```

---

## 5. Feature List (MVP Scope — Do Not Expand Without Confirmation)

**Actor: Gestor Académico**
- CRUD: Docentes, Turmas, Disciplinas, Salas
- Upload de entidades via ficheiro Excel
- Acionar geração de horário
- Visualizar grade horária gerada
- Visualizar relatório de inviabilidade

**Actor: Docente**
- Consultar o seu horário individual
- Registar disponibilidade semanal (grelha de slots)

**Features Complementares (não bloquear MVP)**
- Autenticação e perfis de acesso
- Relatórios operacionais (contagens, listas)
- Exportação para Google Calendar
- Persistência histórica de horários por semestre

---

## 6. API Contract Reference (updated 15/07 — backend Fases 0-7 complete)

> See `../CLAUDE.md` and `../README.md` for the full contract and integration plan.
> Kept here in sync per the note at the top of `../CLAUDE.md` — update both files together.

Every route below except `/auth/*` requires `Authorization: Bearer <idToken>` (401 if missing/invalid,
403 if the role lacks permission). The client never talks to Firebase directly — login, refresh,
and password recovery are all proxied through the backend.

```
# Auth (no token; RF15/RF16)
POST  /auth/login                        {email,password} → {id_token,refresh_token,expires_in}
POST  /auth/login-google                 {google_id_token} → same (token obtained via native Google Sign-In SDK)
POST  /auth/refresh                      {refresh_token} → same
POST  /auth/recuperar-password           {email} → 204 always
POST  /auth/registo-professor            {email,password,contacto_telefonico} → session + utilizador
                                          (403 if email doesn't match a Professor already created by Gestor)
GET   /auth/me                           → {email, papel, professor_id} — only /auth route requiring a token

# Gestor management (Superadmin only)
POST|GET|DELETE  /utilizadores[/{id}]

# Master data CRUD (Gestor only) — entity is "Professor", NOT "Docente"
POST|GET|PUT|DELETE  /cursos[/{id}]
POST|GET|PUT|DELETE  /professores[/{id}]
POST|GET|PUT|DELETE  /turmas[/{id}]
POST|GET|PUT|DELETE  /disciplinas[/{id}]
POST|GET|PUT|DELETE  /salas[/{id}]

# Professor availability (RF05) — Professor: own only; Gestor: any
GET|POST  /professores/{id}/disponibilidade

# Curriculum + qualification (solver prerequisites, Gestor only)
GET|POST  /turmas/{id}/disciplinas
GET|POST  /professores/{id}/disciplinas

# Bulk import (RF06/RF07/RF08, Gestor only) — see backend/templates_importacao/
POST  /upload/excel?entidade=cursos|professores|disciplinas|salas|turmas

# Schedule generation + query (RF09-RF12) — always async, never poll by job for the result
POST  /gerar-horario                     → {job_id, status:"PENDING"}
GET   /jobs/{job_id}                     → {status, diagnostico}
GET   /horarios/turma/{turma_id}         → grouped by day/slot (Gestor only)
GET   /horarios/professor/{professor_id} → grouped by day/slot (Gestor: any; Professor: own only)
```