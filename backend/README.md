# Backend — ISAF

API FastAPI + motor de otimização Google OR-Tools CP-SAT para geração de horários. Este ficheiro é
o manual operacional: como pôr o backend a correr, como está configurado, como aceder à BD, e
nuances que não pertencem à documentação de arquitetura. Para o **porquê** das decisões (fases,
modelagem, RNs) ver `docs/CONVENCOES.md` e `../docs/06_arquitetura_backend.md` /
`../docs/analise_requisitos_v5.0.md` — essa continua a ser a fonte de verdade sobre requisitos.

## 1. Pré-requisitos

- Python 3.12+ (já traz `venv`/`pip`, sem instalação adicional a nível de sistema)
- Docker + Docker Compose (só para o Postgres local — o backend em si não depende de Docker)

## 2. Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# editar .env — ver secção 4 (Configuração) antes da primeira utilização real

docker compose up -d   # sobe o Postgres local (isaf/isaf/isaf_horarios em localhost:5432)
python init_db.py      # cria as tabelas e semeia os 45 Slot (9 tempos x 5 dias)
uvicorn app.main:app --reload
```

API disponível em `http://localhost:8000`, Swagger interativo em `http://localhost:8000/docs`,
health check em `GET /health`.

## 3. Base de dados (Postgres via Docker)

PostgreSQL via Docker Compose (decisão de `../docs/analise_requisitos_v5.0.md`, secção 8).
`docker-compose.yml` sobe um único serviço `db` (Postgres 16-alpine) com volume persistente
`isaf_pgdata`. Credenciais e porta já vêm fixas no compose (uso local, não produção): utilizador
`isaf`, password `isaf`, BD `isaf_horarios`, porta `5432`.

```bash
docker compose up -d          # arrancar em background
docker compose ps             # confirmar healthcheck "healthy"
docker compose down           # parar (mantém o volume — dados sobrevivem)
docker compose down -v        # parar E apagar o volume (perde todos os dados)
```

**Aceder à BD diretamente** (útil para inspecionar dados durante o desenvolvimento):

```bash
docker compose exec db psql -U isaf -d isaf_horarios
```

Dentro do `psql`: `\dt` lista as tabelas, `\d nome_tabela` mostra colunas/FKs, `SELECT * FROM job;`
etc. Também dá para ligar com qualquer cliente Postgres externo (DBeaver, TablePlus, `psql` local)
usando o `DATABASE_URL` do `.env` — é uma ligação Postgres normal em `localhost:5432`.

**Não há Alembic/migrações formais no MVP.** `init_db.py` usa
`SQLModel.metadata.create_all(engine)` — cria tabelas que ainda não existem, mas **não** altera
tabelas já criadas se um model mudar de forma incompatível. Se alterares um model existente durante
o desenvolvimento, o caminho mais simples é `docker compose down -v && docker compose up -d &&
python init_db.py` (recria tudo do zero). Migração formal fica para trabalho futuro pós-MVP.

## 4. Configuração (`.env`)

Todas as variáveis têm um default sensato em `app/core/config.py`, mas confirma estas antes da
primeira utilização real (os testes não dependem de nenhuma delas):

| Variável | Nuance |
|---|---|
| `DATABASE_URL` | Só muda se não usares o Postgres do `docker-compose.yml` tal como está. |
| `FIREBASE_PROJECT_ID` | `project_id` do Firebase Console (visível em `../frontend/lib/core/config/firebase_config.dart`). Usado como `audience` na verificação do ID Token — **não é preciso `firebase-service-account.json`** para isto (ver secção 5). |
| `SUPERADMIN_EMAILS` | Lista JSON de emails com papel Superadmin (bootstrap, sem tabela própria — ver secção 5). Sem isto configurado, ninguém consegue criar o primeiro Gestor. |
| `SOLVER_MAX_TIME_SECONDS` | Limite de tempo do CP-SAT por pedido de geração de horário. Cenários maiores podem precisar de mais que os 60s por omissão (ver `tests/test_solver_escala.py` para uma referência de tempo a uma escala intermédia). |
| `SLOT_*` | Calendário letivo (dias, tempos/dia, hora do 1º tempo, duração). Só é lido por `init_db.py` no momento do seed — mudar isto depois de já teres corrido `init_db.py` não atualiza os `Slot` já criados. |

`FIREBASE_CREDENTIALS_PATH` existe em `Settings` mas **não é usado por nenhum código atualmente**
— pensado para o Firebase Admin SDK completo, que este backend deliberadamente não usa (ver secção
5). Pode ser ignorado.

## 5. Autenticação — nuances que não estão na arquitetura

- **Não existe (nem é preciso) `firebase-service-account.json`** neste projeto. A verificação do
  ID Token (`app/core/security.py`) usa `google.oauth2.id_token.verify_firebase_token`, que valida
  a assinatura contra os certificados públicos do Google — só precisa do `FIREBASE_PROJECT_ID`. O
  ficheiro de credenciais da service account só seria necessário para operações administrativas do
  Firebase Admin SDK (criar utilizadores, custom claims, etc.), que este backend não faz.
- **Superadmin não tem tabela na BD.** É só a lista `SUPERADMIN_EMAILS` no `.env` — o único papel
  que existe fora da BD. É o único que pode criar `Utilizador(perfil=GESTOR)` via `POST
  /utilizadores`.
- **Professor regista-se a si próprio.** Cria a conta Firebase no cliente Flutter, depois chama
  `POST /auth/registo-professor` (token válido + `contacto_telefonico`) — o backend valida o email
  contra um `Professor` já criado pelo Gestor (`POST /professores`); 403 se não houver
  correspondência.
- Para testar localmente sem um token Firebase real (nos testes automáticos): `tests/test_security.py` e
  `tests/test_auth_http.py` mostram como isto é feito — substituindo
  `app.core.security.verificar_id_token` por uma função que devolve o email diretamente, sem
  contactar o Google.

### Obter um ID Token real para testar manualmente (Swagger, curl, Postman)

Não há atalho no código — o backend só aceita tokens assinados pelo Firebase de verdade. Sem a app
Flutter, o caminho mais rápido é a REST API do Firebase Authentication (`API_KEY` é a mesma já
pública em `../frontend/lib/core/config/firebase_config.dart` — identifica o projeto, não é
secreta):

```bash
# 1. Criar um utilizador de teste (ou usar signInWithPassword se já existir)
curl -X POST \
  "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyCcmvG_mtxbvyMQnIcFynm2WWv_SwS7wXI" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@isaf.co.ao","password":"palavra-passe-teste","returnSecureToken":true}'
# resposta inclui "idToken" (válido ~1h) e "refreshToken"
```

Se o utilizador já existir, troca `accounts:signUp` por `accounts:signInWithPassword` com o mesmo
corpo. Se der `EMAIL_NOT_FOUND`/`INVALID_LOGIN_CREDENTIALS`, confirma em Firebase Console →
Authentication → Sign-in method que o provedor **Email/Password** está ativado.

Antes de usar o token, garante que esse email tem papel no sistema (senão é 403, RN10/RN11) — a
forma mais simples para testes é pôr esse email em `SUPERADMIN_EMAILS` no `.env` e reiniciar o
`uvicorn`. Depois usa o `idToken` como Bearer: no Swagger (`/docs`) no botão "Authorize", ou
`curl -H "Authorization: Bearer <idToken>" http://localhost:8000/cursos`.

## 6. Testes

```bash
source .venv/bin/activate
pytest                                   # toda a suite, ~15s
pytest tests/test_solver_escala.py -v    # só o teste de escala (mais lento, ~10-13s)
```

Os testes **não tocam no Postgres real** — usam SQLite em memória (`create_engine("sqlite://")`),
por isso correm sem precisar do `docker compose up`. Os testes que passam pelo `TestClient` do
FastAPI (ex: `test_auth_http.py`, `test_golden_path_gestor.py`) usam `poolclass=StaticPool` — sem
isto, cada pedido corre numa thread diferente e vê uma BD SQLite em memória vazia (o pool
"singleton" por omissão do SQLite é por thread).

## 7. Estrutura rápida

Ver `../docs/06_arquitetura_backend.md` secção 3 para a árvore completa comentada. Pontos de
entrada mais usados no dia-a-dia:

- `app/main.py` — regista todos os routers e os exception handlers globais (401/403 de RN09/RN10).
- `app/core/config.py` — todas as variáveis de ambiente.
- `app/core/security.py` — autenticação/autorização (RN09-RN11).
- `app/solver/` — isolado, nunca importa nada de `api/` (ver `docs/CONVENCOES.md`).
- `init_db.py` — cria tabelas + semeia `Slot` (não há endpoint HTTP para isto).

## 8. O que ainda falta (não é bug, é âmbito)

- RF18 (exportação PDF/Excel do horário) ainda não está implementado.
- Sem Alembic — ver nota na secção 3.
- Sem Celery/Redis — filas assíncronas usam `BackgroundTasks` do FastAPI (decisão deliberada do
  MVP, ver `docs/CONVENCOES.md`).
