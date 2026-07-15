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

## Contrato de API (referência)

```
POST   /gerar-horario                    → aciona o solver (job_id se > 5s)
GET    /status/{job_id}                  → estado de tarefa assíncrona
GET    /horario/{job_id}                 → grade horária em JSON estruturado

POST|GET|PUT|DELETE  /docentes[/{id}]
POST|GET|PUT|DELETE  /turmas[/{id}]
POST|GET|PUT|DELETE  /disciplinas[/{id}]
POST|GET|PUT|DELETE  /salas[/{id}]

POST/GET  /docentes/{id}/disponibilidade
POST      /upload/excel
```

Para detalhe de Clean Architecture, gestão de estado com Provider/Firebase, ver skill `flutter-clean-firebase`.
