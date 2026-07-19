# Backend — ISAF

API FastAPI + motor de otimização Google OR-Tools CP-SAT para geração de horários. Este ficheiro é
o manual operacional: como pôr o backend a correr, como está configurado, como aceder à BD, e
nuances que não pertencem à documentação de arquitetura. Para o **porquê** das decisões (fases,
modelagem, RNs) ver `CLAUDE.md` e `../docs/06_arquitetura_backend.md` /
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
| `FIREBASE_WEB_API_KEY` | Web API Key do Firebase (também pública, mesma origem). Usada para o backend chamar a REST API de login/refresh/recuperação de password/login Google (ver secção 5) — **não é um segredo**, mas ainda assim configurável via `.env` para outros ambientes/projetos Firebase. |
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
- **O cliente Flutter nunca fala com o Firebase diretamente.** Login (email/senha e Google),
  refresh e recuperação de password são todos endpoints deste backend (`app/api/v1/routers/auth.py`
  chama `app/core/firebase_rest.py`, que fala com a REST API do Identity Toolkit/Secure Token do
  Firebase por trás). Isto não precisa de `firebase-service-account.json` nem de Client
  ID/Secret OAuth — só da `FIREBASE_WEB_API_KEY` (pública, ver `Settings`).
- **Professor regista-se a si próprio pelo backend.** `POST /auth/registo-professor` (`email` +
  `password` + `contacto_telefonico`, sem precisar de nenhum token prévio) cria a conta Firebase E o
  registo no sistema num único passo — valida primeiro que o email corresponde a um `Professor` já
  criado pelo Gestor (`POST /professores`); 403 se não houver correspondência, e **nunca chega a
  criar a conta Firebase** nesse caso (evita contas órfãs).
- **Login com Google não usa OAuth redirect.** O cliente obtém o Google ID Token através do SDK
  nativo do Google Sign-In (isso continua no telemóvel/browser — é padrão para apps móveis), e
  envia-o a `POST /auth/login-google`; o backend troca-o por uma sessão Firebase via
  `accounts:signInWithIdp`. Não precisamos de gerir nenhum Client Secret OAuth.
- Para testar localmente sem tocar no Firebase real (nos testes automáticos): `tests/test_firebase_rest.py`,
  `tests/test_auth_router_http.py` e `tests/test_security.py` mostram como isto é feito — mockando
  `app.core.firebase_rest` (chamadas HTTP) e `app.core.security.verificar_id_token` (verificação de
  token), sem rede real.

### Testar manualmente (Swagger, curl, Postman)

```bash
# 1. Login — cria conta de teste primeiro via Firebase Console (Authentication > Users > Add user)
#    ou via POST /auth/registo-professor se já tiveres um Professor criado.
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@isaf.co.ao","password":"palavra-passe-teste"}'
# resposta: {"id_token": "...", "refresh_token": "...", "expires_in": 3600}
```

Antes de usar o `id_token`, garante que esse email tem papel no sistema (senão é 403, RN10/RN11) —
a forma mais simples para testes é pôr esse email em `SUPERADMIN_EMAILS` no `.env` e reiniciar o
`uvicorn`. Depois usa o `id_token` como Bearer: no Swagger (`/docs`) no botão "Authorize", ou
`curl -H "Authorization: Bearer <id_token>" http://localhost:8000/cursos`. Quando expirar (~1h),
`POST /auth/refresh` com o `refresh_token` dá um novo `id_token` sem repetir o login.

## 5.5. Limpar a BD e semear de novo (dados de teste do ISAF)

Para repetir um teste manual do zero (BD real via Docker/Postgres, não a suite automática):

```bash
# 1. Parar o backend se estiver a correr (Ctrl+C no terminal do uvicorn, ou:)
pkill -f "uvicorn app.main"

# 2. Apagar a BD por completo (para o container e destrói o volume — perde TODOS os dados)
docker compose down -v

# 3. Recriar o Postgres vazio
docker compose up -d
docker compose ps   # confirmar "healthy" antes de continuar

# 4. Recriar as tabelas (inclui os 45 Slot)
source .venv/bin/activate
python init_db.py

# 5. Semear o currículo real do ISAF (cursos, turmas, professores, disciplinas,
#    salas, qualificações, contas de teste Firebase — ver docstring do próprio
#    ficheiro para a lista de credenciais criadas)
python seed_dados_teste.py

# 6. Arrancar o backend
uvicorn app.main:app --reload
```

Passos 2-3 são o "reset total": qualquer horário gerado, alocação manual ou pendência
anterior desaparece junto com o resto. Se só quiseres limpar `Job`/`Alocacao`/`Pendencia`
(gerações de horário) sem tocar no currículo semeado, usa antes:

```bash
docker compose exec db psql -U isaf -d isaf_horarios -c \
  "TRUNCATE TABLE alocacao, pendencia, job CASCADE;"
```

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
- `app/solver/` — isolado, nunca importa nada de `api/` (ver `../CLAUDE.md`).
- `init_db.py` — cria tabelas + semeia `Slot` (não há endpoint HTTP para isto).

## 8. O que ainda falta (não é bug, é âmbito)

- RF18 (exportação PDF/Excel do horário) ainda não está implementado.
- Sem Alembic — ver nota na secção 3.
- Sem Celery/Redis — filas assíncronas usam `BackgroundTasks` do FastAPI (decisão deliberada do
  MVP, ver `../CLAUDE.md`).

## 9. Deploy — opções de hosting avaliadas (ainda não decidido)

Discussão de 2026-07-19, antes de qualquer conta/infra real ser criada. Frontend já hospedado
(Firebase Hosting, só falta `flutter build web` + deploy). O backend é a peça em aberto —
requisitos que restringem as opções:

- Job de geração de horário corre **dentro do próprio processo web**, via `BackgroundTasks` (sem
  fila/worker separado) — pode demorar minutos (ver secção 10, trabalho em curso para baixar isto
  para <3min). Isto **exclui serverless clássico** (Vercel/Netlify Functions/Cloud Functions): o
  timeout dessas plataformas (segundos a poucos minutos) mataria o job a meio.
- CP-SAT usa `solver_num_search_workers=8` — precisa de CPU real disponível, não um tier
  "hobby"/0.1 vCPU.
- Postgres persistente, com acesso `psql`/DBeaver para debug.
- Um único container Docker — sem Swarm/K8s.

| Serviço | Prós | Contras |
|---|---|---|
| **Railway** (favorito) | Deploy direto do Dockerfile, Postgres gerido incluído, mínima gestão | Custo escala com uso; free tier limitado para uso contínuo |
| **Render** | Muito parecido ao Railway, Postgres gerido | Web services no free tier "dormem" após inatividade — problemático a meio de um job longo |
| **Fly.io** | Controlo fino de CPU/memória, bom para processos longos | Mais configuração manual (`fly.toml`) |
| VPS genérico (Hetzner/DigitalOcean) | Controlo total, mais barato a longo prazo | Gestão manual de systemd/nginx/TLS/backups |

Decisão adiada até o solver estar mais rápido — sem sentido dimensionar infraestrutura para um
pior caso de 17min que estamos ativamente a eliminar.

## 10. Privacidade dos dados de demonstração (adiado)

`seed_dados_teste.py` usa nomes e emails reais extraídos dos PDFs do ISAF (para a tese). Antes de
qualquer deploy público: trocar o domínio de email (`isaf.co.ao` → algo genérico tipo `mvp.local`)
e, depois, os nomes reais dos professores por nomes fictícios — evita expor dados reais de
pessoas. Afeta só este ficheiro de seed de demonstração, não o domínio de negócio do sistema.
