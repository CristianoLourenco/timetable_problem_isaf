---
name: flutter-clean-firebase
description: Use ao criar ou alterar qualquer código em frontend/lib/, incluindo features novas (domain/data/presentation), controllers com ValueNotifier, providers globais, integração com Firebase Authentication, consumo da API FastAPI do ISAF, ou importação de Excel no lado do cliente. Também usar ao decidir onde colocar lógica (Screen vs Controller vs Provider vs UseCase).
---

# Frontend Flutter — Clean Architecture + Firebase (ISAF)

## Camadas por feature

```
domain/
  entities/       — objetos puros, sem dependência de Flutter/Firebase
  repositories/    — interfaces abstratas apenas (implementação fica em data/)
  usecases/        — uma classe por caso de uso, orquestra repository(ies)
data/
  dtos/            — modelos que espelham os schemas Pydantic do backend
  datasources/     — chamadas HTTP (API FastAPI) ou Firebase SDK
  repositories/    — implementação concreta da interface de domain/
presentation/
  states/          — classes de estado imutáveis (usar sentinel pattern em copyWith)
  controllers/      — ValueNotifier<State>, chama usecases, expõe estado à UI
  providers/        — ChangeNotifier para cache/estado global partilhado entre features
  screens/          — Scaffold + composição de components, zero lógica de negócio
  components/        — widgets reutilizáveis, recebem dados via parâmetros (nunca leem Provider diretamente)
```

## Regras de dependência (fluxo único)

`screens` → `controllers`/`providers` → `usecases` → `repositories` (interface) → `data/repositories` (impl) → `datasources` (HTTP/Firebase).

- `domain/` nunca importa `material.dart` nem qualquer package Flutter de UI.
- `components/` recebem tudo por parâmetro — nunca fazem `context.watch<Provider>()` diretamente; quem lê o Provider é a `screen` ou o `controller`, que passa os dados para baixo.
- Todo Controller expõe um método `_init()` (ou nome equivalente de hidratação) chamado no construtor/primeiro build — nunca deixar o estado inicial "vazio" sem plano de carregamento explícito.

## Padrão `copyWith` com sentinel

Como os states são imutáveis e alguns campos precisam aceitar `null` explicitamente (distinto de "não alterar"), usar um valor sentinel:

```dart
class _Unset { const _Unset(); }
const _unset = _Unset();

class TurmaState {
  final String? observacao;
  const TurmaState({this.observacao});

  TurmaState copyWith({Object? observacao = _unset}) {
    return TurmaState(
      observacao: observacao == _unset ? this.observacao : observacao as String?,
    );
  }
}
```

Sem isto, não é possível distinguir "não mudar `observacao`" de "definir `observacao` como `null`".

## Firebase Authentication

- Login email/senha e Google Sign-In, ambos nativos do Firebase (RF15).
- Reset de password via link de email nativo do Firebase (RF16) — só aplicável a contas email/senha.
- Após login, o ID Token Firebase vai em cada pedido HTTP à API FastAPI (header `Authorization: Bearer <token>`) — o backend valida (RN09).
- Professor cria a própria conta; o backend valida se o email corresponde ao registo criado pelo Gestor (RN10) — o frontend deve tratar o `403` de forma explícita na UI (conta sem correspondência), não como erro genérico.

## Consumo da API

- DTOs em `data/dtos/` espelham exatamente os schemas Pydantic do backend (ver `backend/CLAUDE.md` e `backend/app/schemas/`) — manter os dois lados sincronizados manualmente (sem gerador de código automático no MVP).
- Respostas de horário (`GET /horarios/turma/{id}`, `GET /horarios/professor/{id}`) já vêm estruturadas por dia/slot — desserializar diretamente em entities, sem reprocessar listas soltas no cliente.
- Polling de Job (`GET /status/{job_id}`) deve ter backoff razoável, não polling agressivo em loop apertado.

## Routing

GoRouter é a única lib de routing permitida. Configuração centralizada em `core/router/app_router.dart`. Controlo de acesso por perfil (Gestor vs Professor, RN11) deve ser refletido nas rotas disponíveis/redirects, não só escondido na UI.

## Escopo MVP

Ver `frontend/CLAUDE.md` secção "Escopo do MVP" — não implementar features complementares (Google Calendar, histórico por semestre, etc.) sem confirmação explícita.
