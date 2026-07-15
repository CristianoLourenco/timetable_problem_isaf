# Templates de importação Excel (RF06/RF07/RF08)

Um `.xlsx` por entidade nesta pasta, já com a primeira linha de exemplo. Endpoint:
`POST /upload/excel?entidade=<nome>` (multipart, campo `file`) — só Gestor (RN09/RN10).

Regras gerais (RF07/RF08):
- 1ª linha = cabeçalho, colunas **nesta ordem exata** (nomes não sensíveis a maiúsculas/minúsculas).
- Idempotência por chave única — reimportar uma linha cuja chave já exista é **ignorado**, nunca
  duplica nem atualiza.
- Nunca aborta na primeira linha inválida — o relatório devolve todos os erros de uma vez
  (`{total_linhas, importados, ignorados_idempotencia, erros: [{linha, campo, motivo}]}`).
- Se `turmas` referencia um `curso_codigo`, importa `cursos` primeiro (não há import em cascata).

## `cursos.xlsx`

| coluna | tipo | obrigatório | chave? |
|---|---|---|---|
| `codigo` | texto | sim | **sim** (idempotência) |
| `nome` | texto | sim | não |

## `professores.xlsx`

| coluna | tipo | obrigatório | chave? |
|---|---|---|---|
| `nome` | texto | sim | não |
| `email` | texto | sim | **sim** (idempotência; também usado por RN10 para ligar ao auto-registo) |
| `classificacao` | inteiro 1-5 | não (default 3) | não |
| `vinculo_casa` | booleano (`true`/`false`) | não (default falso) | não |

## `disciplinas.xlsx`

| coluna | tipo | obrigatório | chave? |
|---|---|---|---|
| `codigo` | texto | sim | **sim** (idempotência) |
| `nome` | texto | sim | não |

## `salas.xlsx`

| coluna | tipo | obrigatório | chave? |
|---|---|---|---|
| `codigo` | texto | sim | **sim** (idempotência) |
| `nome` | texto | sim | não |
| `capacidade` | inteiro > 0 | sim | não |

## `turmas.xlsx`

| coluna | tipo | obrigatório | chave? |
|---|---|---|---|
| `codigo` | texto | sim | **sim** (idempotência) |
| `nome` | texto | sim | não |
| `ano_letivo` | inteiro | sim | não |
| `turno` | texto | sim | não |
| `numero_alunos` | inteiro > 0 | sim | não |
| `curso_codigo` | texto | sim | não — referência a um `Curso.codigo` **já existente** |
