# Frontend — ISAF (Flutter)

> Equivalente para Claude Code de `.agents/rules/honorgestrule.md` (regras usadas pelo Antigravity). Manter os dois ficheiros sincronizados — qualquer alteração de regra deve ser replicada em ambos.

## Stack (não-negociável)

| Camada | Tecnologia | Restrição |
|---|---|---|
| Routing | GoRouter | sem outras libs de routing |
| Estado | Provider (global) + ValueNotifier (local) | sem Riverpod, Bloc, GetX |
| Serialização | Dart models a partir dos schemas Pydantic do backend | sem `dynamic`/mapas crus |
| Autenticação | Firebase Authentication (email/senha + Google Sign-In) | |

Se uma biblioteca não está nesta lista, perguntar antes de introduzir.

## Idioma

- Código: inglês. Comentários (*porquê*): inglês.
- Strings visíveis na UI: português (Angola).

## Proibições absolutas

- **NUNCA** aceder a um Provider diretamente dentro de um widget Component — passar dados como parâmetros.
- **NUNCA** colocar lógica de negócio num ficheiro Screen — Screens são apenas contentores de layout.
- **NUNCA** colocar imports de UI (`material.dart`) em ficheiros da camada Domain.
- **NUNCA** saltar o método de hidratação `_init()` num Controller.
- **NUNCA** implementar `copyWith` sem o padrão sentinel — `null` deve poder ser definido explicitamente.
- **NUNCA** sugerir substituir qualquer componente da stack definida.

## Estrutura de pastas

```
lib/
├── core/
│   ├── router/          # GoRouter (app_router.dart)
│   ├── themes/           # AppTheme, AppColors, AppTextStyles
│   ├── constants/
│   └── errors/           # Failure classes, error handling
└── features/
    └── [feature_name]/
        ├── domain/
        │   ├── entities/
        │   ├── repositories/   # interfaces abstratas apenas
        │   └── usecases/
        ├── data/
        │   ├── dtos/
        │   ├── datasources/
        │   └── repositories/   # implementações concretas
        └── presentation/
            ├── states/         # classes de estado imutáveis
            ├── controllers/    # ValueNotifier<State>
            ├── providers/      # ChangeNotifier (cache global)
            ├── screens/        # Scaffold apenas
            └── components/
                └── [screen_name]_components/
```

## Escopo do MVP (não expandir sem confirmação)

**Ator: Gestor Académico** — CRUD Docentes/Turmas/Disciplinas/Salas; upload de entidades via Excel; acionar geração de horário; visualizar grade gerada; visualizar relatório de inviabilidade.

**Ator: Docente** — consultar horário individual; registar disponibilidade semanal (grelha de slots).

**Complementares (não bloquear MVP)** — autenticação/perfis, relatórios operacionais, exportação Google Calendar, histórico de horários por semestre.

## Contrato de API (referência — atualizado 15/07, backend Fases 0-7 completas)

> Ver `../backend/README.md` para como correr o backend localmente, e `README.md` (nesta pasta)
> para o plano de integração faseado e o estado atual do código já gerado.

Todas as rotas abaixo (exceto as de `/auth`) exigem `Authorization: Bearer <idToken>` — 401 se
ausente/inválido/expirado, 403 se o papel não tiver permissão. **O cliente nunca fala com o
Firebase diretamente** — login, refresh e recuperação de password passam todos pelo backend.

```
# Autenticação (sem token; RF15/RF16)
POST  /auth/login                        {email,password} → {id_token,refresh_token,expires_in}
POST  /auth/login-google                 {google_id_token} → idem (google_id_token vem do SDK nativo do Google Sign-In)
POST  /auth/refresh                      {refresh_token} → idem
POST  /auth/recuperar-password           {email} → 204 (sempre, mesmo email inexistente)
POST  /auth/registo-professor            {email,password,contacto_telefonico} → {..., utilizador}
                                          (403 se email não corresponder a um Professor já criado pelo Gestor)

# Com token (RN09) — GET /auth/me é a única forma de saber o papel/professor_id
GET   /auth/me                           → {email, papel: "SUPERADMIN"|"GESTOR"|"PROFESSOR", professor_id}

# Gestão de Gestores (só Superadmin)
POST|GET|DELETE  /utilizadores[/{id}]    POST agora exige password também

# CRUD de dados mestre (só Gestor) — nomes em português, singular na BD/plural na rota
POST|GET|PUT|DELETE  /cursos[/{id}]
POST|GET|PUT|DELETE  /professores[/{id}]        # backend chama-lhe "Professor", não "Docente"
POST|GET|PUT|DELETE  /turmas[/{id}]
POST|GET|PUT|DELETE  /disciplinas[/{id}]
POST|GET|PUT|DELETE  /salas[/{id}]

# Disponibilidade do professor (RF05) — Professor só a sua própria; Gestor qualquer uma
# Não existe tabela Slot nem slot_id (ver backend/app/core/calendario.py) — periodo
# reinicia em 1 a cada turno (manha:1-6, tarde/noite:1-5), por isso vai sempre com turno.
GET|POST  /professores/{id}/disponibilidade     {tempos: [{dia_semana, turno, periodo}]}
GET       /slots                                {dia_semana, turno, periodo, hora_inicio, hora_fim}[]

# Grade curricular e qualificação (pré-requisito do solver, só Gestor)
GET|POST  /turmas/{id}/disciplinas              {itens: [{disciplina_id, carga_horaria_semanal}]}
GET|POST  /professores/{id}/disciplinas         {disciplina_ids: [int]}

# Importação em massa (RF06/RF07/RF08, só Gestor) — ver backend/templates_importacao/
POST  /upload/excel?entidade=cursos|professores|disciplinas|salas|turmas

# Geração e consulta de horário (RF09-RF12)
POST  /gerar-horario                     → {job_id, status:"PENDING"} (só Gestor; sempre assíncrono)
GET   /jobs/{job_id}                     → {id, status: PENDING|RUNNING|DONE|INFEASIBLE, diagnostico} (só Gestor)
GET   /horarios/turma/{turma_id}         → {job_id, dias:[{dia_semana, tempos:[...]}]} (só Gestor)
GET   /horarios/professor/{professor_id} → idem (Gestor: qualquer; Professor: só o seu, 403 senão)
```

**Diferenças importantes vs. o que estava aqui antes** (o código já gerado no repo segue a versão
antiga — ver `README.md` para a lista de correções pendentes):
- Não é `/status/{job_id}` nem `/horario/{job_id}` — é `/jobs/{job_id}` e `/horarios/turma|professor/{id}`
  (a consulta é sempre por turma/professor, nunca por job_id — mostra sempre o Job DONE mais recente).
- Entidade é `Professor`, não `Docente` (campos: `nome`, `email`, `classificacao` 1-5, `vinculo_casa`).
- Não existe `/docentes/{id}/disponibilidade` — é `/professores/{id}/disponibilidade`.
- Faltavam `/cursos`, grade curricular, qualificação, e todo o `/auth/*` — sem isso o solver não tem
  dados para gerar (ver `backend/README.md` secção "O que ainda falta").

Para detalhe de Clean Architecture, gestão de estado com Provider/Firebase, ver skill `flutter-clean-firebase`.
