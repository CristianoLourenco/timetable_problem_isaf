# Frontend — ISAF (Flutter)

> Documento de continuidade para a integração do frontend com o backend (Fases 0-7 completas,
> ver `../backend/README.md`). Escrito a partir de uma análise do código já gerado neste
> repositório — mantém-se atualizado à medida que a integração avança.

## 1. Estado atual — o que já existe

O projeto já tem o esqueleto completo em Clean Architecture, com **7 features scaffolded**:
`feature_auth`, `feature_dashboard`, `feature_docentes`, `feature_turmas` (inclui ecrã de
`cursos`), `feature_disciplinas`, `feature_salas`, `feature_horario`. Cada uma segue
consistentemente `domain/` (entities, repository interface, usecases) → `data/` (DTOs,
datasource remoto, repository impl) → `presentation/` (states, controllers `ValueNotifier`,
providers `ChangeNotifier`) → `ui/` (screens, components). Isto está bem-feito e é para manter —
não é preciso redesenhar a arquitetura.

Peças de infraestrutura já sólidas e reutilizáveis tal como estão:
- `core/resources/network/dio/dio_client_interceptor.dart` — `DioClient` implementa `IHttpMethods`,
  já mapeia erros Dio para `IExceptionError` (401/403 → `UnauthorizedError`, 404 → `NotFoundError`,
  etc.) e já lê `detail`/`message` do corpo do erro — **compatível com o formato de erro do backend**
  (`{"detail": "..."}`) sem alterações.
- `core/resources/storage/hive/provider_state_hive_box.dart` — wrapper Hive genérico
  (`save`/`read`/`delete`/`clear` por chave), pronto para guardar `id_token`/`refresh_token`.
- `core/routes/app_router.dart` — GoRouter com `ShellRoute` para o dashboard persistente.
- `multiproviders/multiproviders.dart` — injeção de dependências central, um bloco por feature.

## 2. O que está mockado e precisa de correção

Todos os `*_remote_impl.dart` seguem o mesmo padrão problemático: tentam uma chamada HTTP real,
mas **em qualquer falha (incluindo simplesmente o backend não estar a correr) caem silenciosamente
para dados fixos** (ex: "Programação Orientada a Objectos" em disciplinas, "José Neto" em horário).
Isto tem de ser removido nesta integração — esconde falhas reais em vez de as reportar ao
`DataState.error`, e não há como saber se a integração está mesmo a funcionar.

Além disso, **nenhum DTO atual corresponde ao schema real do backend**. Foram todos gerados como
placeholder genérico. Por entidade:

| Feature | DTO atual (campos) | Backend real (campos) | Nota |
|---|---|---|---|
| `feature_auth` (`UserDto`) | `id, username, token, role` | login devolve `{id_token, refresh_token, expires_in}`; papel só se sabe via `GET /auth/me` → `{email, papel, professor_id}` | Repensar por completo — ver secção 4 |
| `feature_docentes` (`DocenteDto`) | `id, name, email, phone, createdAt, updatedAt` | `Professor`: `id, nome, email, classificacao (1-5), vinculo_casa` | Sem `phone`/timestamps no backend; entidade chama-se **Professor**, não Docente (decisão: manter "Docente" só como nome de feature/UI, ver secção 5) |
| `feature_turmas` (`TurmaDto`) | `id, name, year, period, createdAt, updatedAt` | `Turma`: `id, codigo, nome, ano_letivo, turno, numero_alunos, curso_id` | Faltam `codigo`, `numero_alunos`, `curso_id` por completo |
| `feature_turmas` (`Curso`) | entidade existe mas sem datasource/repository próprios | `Curso`: `id, codigo, nome` | Precisa de CRUD próprio — é pré-requisito de Turma |
| `feature_disciplinas` (`DisciplinaDto`) | `id, name, code, weeklyHours` | `Disciplina`: `id, codigo, nome` (carga horária não é da Disciplina — é de `TurmaDisciplina`, ver secção 6) | `weeklyHours` está no sítio errado |
| `feature_salas` | (não inspecionado em detalhe, mesmo padrão esperado) | `Sala`: `id, codigo, nome, capacidade` | |
| `feature_horario` | `checkStatus` chama `/status/{jobId}`; `getTimetable` chama `/horario/{jobId}` | é `/jobs/{job_id}` e `/horarios/turma/{turma_id}` \| `/horarios/professor/{professor_id}` | **Mudança conceptual**: não se consulta o horário "de um job" — consulta-se sempre o horário atual de uma turma/professor (o Job DONE mais recente). Ver secção 6 |

## 3. Duas peças de infraestrutura a criar antes de tudo

1. **Interceptor de autenticação** — `DioClient` hoje não anexa `Authorization: Bearer <token>` a
   nenhum pedido. Quase todas as rotas exigem-no (RN09). Adicionar um `Interceptor` do Dio que lê o
   `id_token` do Hive e o injeta em `onRequest`, e que trata 401 (token expirado) chamando
   `POST /auth/refresh` com o `refresh_token` guardado e repetindo o pedido original uma vez.
2. **`google_sign_in` package** — ainda não está no `pubspec.yaml`. Só é preciso quando
   implementares o botão "Login com Google" (`POST /auth/login-google` espera um
   `google_id_token` já obtido pelo SDK nativo — o backend nunca faz o fluxo OAuth de redirect).

## 4. `feature_auth` — repensar por completo

O `AuthProvider.checkCurrentUser()` já assume um fluxo "verificar sessão guardada ao abrir a app",
o que está certo — só é preciso ajustar o que cada chamada devolve:

- **Login**: `POST /auth/login` → guardar `id_token`+`refresh_token` no Hive → chamar
  `GET /auth/me` para saber `papel`/`professor_id` → só então marcar `currentUser` como preenchido.
- **`checkCurrentUser()` ao abrir a app**: ler `id_token` do Hive; se existir, chamar `GET /auth/me`
  diretamente (se der 401, tentar `POST /auth/refresh` primeiro; se isso também falhar, limpar Hive
  e mandar para `/login`).
- **Logout**: limpar o Hive (não há endpoint de logout no backend — sessões Firebase não têm
  server-side revoke simples via REST; expiram sozinhas).
- **Registo de Professor**: ecrã novo (não existe ainda) — `POST /auth/registo-professor`
  `{email, password, contacto_telefonico}`, sem token prévio. 403 quer dizer "o Gestor ainda não te
  criou como Professor".
- **Recuperar password**: ecrã novo — `POST /auth/recuperar-password` `{email}`, sempre mostra a
  mesma mensagem de sucesso (o backend nunca revela se o email existe).
- **Papel para controlo de UI**: `papel` de `GET /auth/me` é `"SUPERADMIN" | "GESTOR" | "PROFESSOR"`.
  Superadmin tem acesso igual a Gestor em tudo (mais a gestão de `/utilizadores`, provavelmente fora
  do MVP do frontend).

## 5. Naming: Docente vs. Professor

Decisão a tomar (não bloqueia o arranque): o backend chama-lhe `Professor` em toda a parte
(modelo, rotas, RF01). O frontend já escolheu `Docente` como nome de feature/UI. Como o
`analise_requisitos_v5.0.md` também usa "Professor" consistentemente, a opção mais simples é
**manter `feature_docentes` como está** (é só uma etiqueta de UI/pasta) e fazer o `DocenteDto`
mapear os campos reais do `Professor` do backend — não vale a pena renomear a feature inteira.

## 6. Duas relações que faltam por completo: grade curricular e qualificação

Sem isto o solver não tem nada para resolver (ver `backend/README.md`). Precisam de UI própria,
provavelmente como parte dos ecrãs de Turma e Professor respetivamente, não como features
separadas:
- **Grade curricular** (`GET|POST /turmas/{id}/disciplinas`) — que disciplinas a turma tem e quantos
  tempos/semana de cada. É aqui que a "carga horária" pertence, não em `Disciplina`.
- **Qualificação docente** (`GET|POST /professores/{id}/disciplinas`) — que disciplinas o professor
  pode lecionar.

## 7. Plano de integração sugerido (ordem)

1. Interceptor de auth + Hive (secção 3) — sem isto nada mais funciona.
2. `feature_auth` completo: login, `GET /auth/me`, persistência de sessão, logout, e os dois ecrãs
   novos (registo de professor, recuperar password).
3. Corrigir DTOs + remover fallback para mock em `feature_turmas` (+ Curso), `feature_docentes`,
   `feature_disciplinas`, `feature_salas` — CRUD simples, mesmo padrão em todas.
4. Grade curricular e qualificação (secção 6) — UI dentro dos ecrãs de Turma/Professor existentes.
5. Disponibilidade do professor (`/professores/{id}/disponibilidade`) — grelha semanal de slots
   (45 = 9 tempos × 5 dias, ver `backend/app/core/config.py`).
6. `feature_horario`: corrigir os 3 endpoints errados (secção 2), e mudar o modelo mental de
   "consultar por job_id" para "consultar por turma/professor" — o `job_id` só serve para o
   polling logo a seguir a disparar a geração, nunca para a consulta seguinte.
7. Importação Excel (upload de ficheiro para `/upload/excel?entidade=...`) — ver
   `backend/templates_importacao/` para o formato exato de cada `.xlsx`.

## 8. Como testar contra o backend real

Ver `../backend/README.md` secções 2-3 (Docker/Postgres) e a secção "Autenticação" para como obter
um `id_token` real via `POST /auth/login` sem precisar de UI (`curl`/Postman) enquanto o login não
estiver pronto no Flutter.
