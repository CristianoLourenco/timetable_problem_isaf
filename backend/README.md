# Backend — ISAF

API FastAPI + motor de otimização Google OR-Tools CP-SAT para geração de horários. Ver `CLAUDE.md` (arquitetura) e `../docs/06_arquitetura_backend.md` (especificação completa).

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # ajustar valores se necessário

docker compose up -d   # sobe o Postgres local (isaf/isaf/isaf_horarios em localhost:5432)

python init_db.py      # cria as tabelas (Fase 1)

uvicorn app.main:app --reload
```

API disponível em `http://localhost:8000`, docs interativos em `http://localhost:8000/docs`, health check em `GET /health`.

## Testes

```bash
pytest
```

## Base de dados

PostgreSQL via Docker Compose (decisão de `../docs/analise_requisitos_v5.0.md`, secção 8). `docker-compose.yml` sobe um único serviço `db` com volume persistente `isaf_pgdata`.
