# Timetable Problem — ISAF

Sistema de geração automática de horários académicos para o Instituto Superior de
Administração e Finanças (ISAF), baseado em Programação por Restrições (Constraint
Programming) com o solver CP-SAT do Google OR-Tools.

## Arquitectura

Monorepo com duas aplicações:

| Camada | Tecnologia |
|---|---|
| Frontend | Flutter + GoRouter + Provider |
| Backend | Python 3.11+ / FastAPI / Pydantic v2 |
| Persistência | PostgreSQL + SQLModel |
| Motor de optimização | Google OR-Tools (CP-SAT) |
| Autenticação | Firebase Authentication |
| Importação de dados | Excel (.xlsx) via openpyxl |

O motor de optimização (`backend/app/solver/`) é isolado do resto da aplicação: nunca
importa nada da camada de API. Fluxo unidirecional `api → services → solver`, com o
solver a receber apenas estruturas de dados Python já preparadas pelos serviços — nunca
sessões de base de dados nem objectos HTTP.

## Estrutura do repositório

```
backend/    API REST (FastAPI), modelos, serviços, solver CP-SAT, testes
frontend/   Aplicação Flutter (Android/iOS/Web/Desktop)
```

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d          # PostgreSQL local
uvicorn app.main:app --reload
```

Ver `backend/README.md` para detalhes de configuração, variáveis de ambiente e execução
de testes.

## Frontend

```bash
cd frontend
flutter pub get
flutter run
```

## Licença

Ver [LICENSE](LICENSE).
