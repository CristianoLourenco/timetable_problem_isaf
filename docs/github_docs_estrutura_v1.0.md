# Guia de Organização da Documentação no GitHub
> Repositório: `isaf-horarios` (monorepo — frontend + backend + docs no mesmo repo)

---

## Estrutura de pastas

```
isaf-horarios/
│
├── README.md                          ← visão geral do projecto (o que é, stack, como correr)
│
├── docs/
│   └── tfc/
│       ├── analise_requisitos.md      ← fonte de verdade única de RFs, RNFs, RNs, UCs
│       ├── modelagem_sistema.md       ← índice de estado dos diagramas
│       └── diagramas/
│           ├── 01_diagrama_contexto.md
│           ├── 02_diagrama_casos_uso.md
│           ├── 03_especificacao_casos_uso.md
│           ├── 04_diagrama_classes.md
│           ├── 05_diagrama_er.md
│           └── 06_diagrama_sequencia.md
│
├── backend/
│   ├── .agents/                       ← skills do Claude Code (python_backend, python_structure)
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/                    ← SQLModel — espelha o Diagrama de Classes
│   │   ├── solver/                    ← Motor CP-SAT isolado (RNF04)
│   │   └── schemas/                   ← Pydantic — contratos JSON para o Flutter
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── .agents/                       ← skills do Claude Code (flutter_architecture, etc.)
│   ├── lib/
│   │   ├── core/
│   │   ├── features/
│   │   └── main.dart
│   ├── pubspec.yaml
│   └── README.md
│
└── .code-workspace                    ← abre as 3 pastas em simultâneo no Antigravity/VS Code
```

---

## Regras de rastreabilidade

Cada ficheiro de código deve referenciar o RF/UC/RN que implementa:

```python
# backend/app/routers/horario.py
# Implementa: RF09 (UC08), RF10 (UC10) — ver docs/tfc/diagramas/02_diagrama_casos_uso.md

@router.post("/gerar-horario")
async def gerar_horario(...):
    ...
```

```dart
// frontend/lib/features/horario/presentation/pages/horario_page.dart
// Implementa: RF11 (UC11), RF12 (UC12) — ver docs/tfc/diagramas/02_diagrama_casos_uso.md
```

Isto dá rastreabilidade directa entre código e documentação — valorizado na banca.

---

## Como usar o Mermaid no GitHub

Os ficheiros `.md` em `docs/tfc/diagramas/` contêm blocos Mermaid:

````markdown
```mermaid
flowchart LR
    ...
```
````

O GitHub renderiza automaticamente. Não precisas de exportar imagens para ver os diagramas no repositório — mas para o documento Word/PDF final usas os ficheiros exportados do Visual Paradigm.

---

## Ficheiro `.code-workspace`

Coloca na raiz do repositório:

```json
{
  "folders": [
    { "path": "backend",  "name": "Backend (FastAPI + CP-SAT)" },
    { "path": "frontend", "name": "Frontend (Flutter)" },
    { "path": "docs/tfc", "name": "TFC — Documentação" }
  ],
  "settings": {
    "search.exclude": {
      "**/build": true,
      "**/.venv": true,
      "**/.dart_tool": true
    }
  }
}
```

Abre com: `antigravity isaf-horarios.code-workspace`

---

## Convenção de commits

```
feat(backend): implementa RF09 — endpoint POST /gerar-horario
feat(frontend): UC12 — página de consulta de horário por professor
docs: actualiza analise_requisitos.md — adiciona RN10 e RF18
fix(solver): corrige modelagem esparsa para turmas sem disciplinas
```

Formato: `tipo(âmbito): descrição — referência ao RF/UC quando aplicável`

---

## O que NÃO colocar no repositório

```
.env                    ← credenciais Firebase, chave de BD — usar .env.example com campos vazios
*.key, *.pem            ← chaves privadas
__pycache__/            ← artefactos Python
build/                  ← artefactos Flutter
.venv/                  ← ambiente virtual Python
```

Garante que tens um `.gitignore` na raiz que cobre todas estas pastas.
