# Relatório compilado

`TFC_Cristiano_Lourenco.docx`/`.pdf` são gerados a partir dos `.md` em
`docs/relatorio/<capitulo>/<seccao>.md` — nunca editados directamente. Ficam fora do
git (ver `.gitignore`): são artefactos derivados, não a fonte.

A fonte está organizada em oito pastas de capítulo, cada uma com um ficheiro `.md` por
secção de 2º nível (`##`), numerados por ordem de compilação:

```
docs/relatorio/
├── 00_pretextual/                 # capa, compromisso, resumo/abstract, listas
├── 01_introducao/                 # 1.1 a 1.8
├── 02_fundamentacao_teorica/      # 2.1 a 2.4
├── 03_metodologia/                # 3.1 a 3.10
├── 04_analise_desenvolvimento/    # 4.1 a 4.6
├── 05_conclusao/                  # 5.1 a 5.2
└── 06_referencias_apendices/      # referências, apêndices, anexos
```

A ordem alfabética dos ficheiros dentro de cada pasta corresponde à ordem de leitura do
relatório — a compilação usa glob (`relatorio/*/*.md`), pelo que renomear um ficheiro
fora do padrão `NN_nome.md` quebra a ordem de compilação.

Há duas rotas de compilação para PDF a partir da mesma fonte `.md`:

1. **docx → LibreOffice** (rota histórica, produz também o `.docx` editável em Word) —
   secção "Como regenerar" abaixo.
2. **LaTeX** (rota alternativa, controlo tipográfico absoluto, sem passos de
   pós-processamento OOXML) — secção "Rota alternativa: LaTeX" mais abaixo.

Ambas aplicam a mesma formatação exigida pelo Artigo 9º do Regulamento TCC do ISAF
(margens, espaçamento, numeração romano/arábico, cabeçalho com o título do trabalho).

## Como regenerar (rota docx)

```bash
cd docs
pandoc \
  relatorio/00_pretextual/*.md relatorio/01_introducao/*.md \
  relatorio/02_fundamentacao_teorica/*.md relatorio/03_metodologia/*.md \
  relatorio/04_analise_desenvolvimento/*.md relatorio/05_conclusao/*.md \
  relatorio/06_referencias_apendices/*.md \
  --citeproc --bibliography=referencias.bib --csl=apa.csl \
  --reference-doc=dist/custom-reference.docx \
  --toc --toc-depth=3 \
  -o dist/TFC_Cristiano_Lourenco.docx

python3 dist/postprocess_pagination.py dist/TFC_Cristiano_Lourenco.docx

# opcional mas recomendado — pré-resolve o campo do Índice no próprio
# .docx (exige LibreOffice instalado; ver docstring do script)
python3 dist/resolve_toc_libreoffice.py dist/TFC_Cristiano_Lourenco.docx
```

O segundo passo (`postprocess_pagination.py`) **é obrigatório** — faz quatro
coisas que o pandoc não expõe a partir do markdown/reference-doc, editando
directamente o pacote OOXML já compilado:

1. Insere a quebra de secção entre o pré-textual e o "1. INTRODUÇÃO" e liga um
   rodapé com numeração de página: romano minúsculo (i, ii, iii...) no
   pré-textual, arábico a partir de 1 do "1. INTRODUÇÃO" até ao fim (textual +
   pós-textual). Página centrada, 10pt, margem inferior — conforme Artigo 9º
   do Regulamento TCC do ISAF.
2. Reposiciona o campo `ÍNDICE` (Índice/TOC), que o pandoc `--toc` insere
   sempre no início absoluto do documento (antes da capa), para o local
   correcto: depois da "Lista de Abreviaturas e Siglas" e antes do "1.
   INTRODUÇÃO".
3. Abre uma página nova a seguir ao Índice, para que "1. INTRODUÇÃO" comece
   sempre em página própria.
4. Insere um cabeçalho com o título do trabalho (10pt, alinhado à direita),
   activo apenas a partir de "1. INTRODUÇÃO" — capa, folha de rosto e
   pré-textual (numeração romana) não têm cabeçalho, por opção editorial.
   Aplica também as margens do Regulamento TCC (Artigo 9º): 2,5cm topo/direita/
   fundo, 3,5cm esquerda (para encadernação).

Se não correr o passo opcional `resolve_toc_libreoffice.py`, o Word ainda
assim resolve o campo do Índice automaticamente ao abrir o ficheiro (o
pandoc marca-o como "dirty"); se por algum motivo isso não acontecer,
actualize manualmente com botão direito sobre o Índice → "Atualizar campo"
→ "Atualizar índice inteiro".

Se a estrutura de `relatorio/00_pretextual/` ou `relatorio/01_introducao/01_contextualizacao.md`
mudar (nomeadamente o heading "1. INTRODUÇÃO"), reveja o script — ele falha alto
(`sys.exit`) em vez de produzir um DOCX com numeração ou Índice errados caso
não encontre os marcadores esperados.

- `referencias.bib` — exportado do Zotero (Better BibTeX); manter sincronizado lá, não
  editar as entradas manualmente aqui.
- `apa.csl` — estilo de citação (APA 7).
- `dist/custom-reference.docx` — define fonte (Times New Roman 12pt), espaçamento
  1.5 entre linhas com espaço após parágrafo (`docDefaults` — `spacing
  after="480" line="360"`, actualizado 2026-07-20 conforme Artigo 9º do
  Regulamento TCC do ISAF — substitui o espaçamento 1.15 anterior, que seguia
  apenas o `TFC_Pandoc_Template.docx`) e hierarquia de títulos (APA: Nível 1
  centrado, Nível 2/3 alinhados à esquerda) usados na compilação. As margens
  (2,5/2,5/2,5/3,5cm) são aplicadas por `postprocess_pagination.py`, não por
  este ficheiro. Não é gerado a partir de `pandoc --print-default-data-file`
  directamente — foi editado manualmente (`word/styles.xml` e `word/theme/theme1.xml`)
  a partir desse ficheiro base.
- **Não usar `--metadata title=`/`--metadata author=`**: o pandoc insere
  automaticamente um bloco de título/autor no topo do documento a partir destes
  metadados, duplicando o conteúdo da capa/folha de rosto já escrito em
  `relatorio/00_pretextual/00_capa.md`.
- `01_diagrama_contexto.md`, `02_diagrama_casos_uso.md`, `03_especificacao_casos_uso.md`
  (na raiz de `docs/`, fora de `relatorio/`) ficam de fora de propósito — são o
  documento de trabalho "Modelagem do Sistema", não o corpo do TFC.
- Diagramas (`media/*.png`) são gerados a partir das fontes em `media/src/*.puml` — ver
  `media/src/` para reeditar sem partir do zero (`java -jar plantuml.jar -tpng ficheiro.puml`).
  As referências a imagens dentro de `relatorio/**/*.md` usam caminho relativo
  `../../media/...` (duas pastas acima: da secção até `relatorio/`, e daí até `docs/`).

## Rota alternativa: LaTeX

```bash
cd docs
pandoc \
  relatorio/00_pretextual/*.md relatorio/01_introducao/*.md \
  relatorio/02_fundamentacao_teorica/*.md relatorio/03_metodologia/*.md \
  relatorio/04_analise_desenvolvimento/*.md relatorio/05_conclusao/*.md \
  relatorio/06_referencias_apendices/*.md \
  --citeproc --bibliography=referencias.bib --csl=apa.csl \
  --template=dist/latex/isaf-template.tex \
  --top-level-division=chapter \
  --pdf-engine=lualatex \
  -o dist/TFC_Cristiano_Lourenco_LaTeX.pdf
```

**`--top-level-division=chapter` é obrigatório**: sem esta flag, o pandoc mapeia
`# Título` para `\section` em vez de `\chapter` (a classe `report` do
`isaf-template.tex` não é suficiente para o pandoc inferir isto sozinho) —
resultado: nenhuma quebra de página entre secções pré-textuais/capítulos, todas
fluindo na mesma página.

Um único passo, sem pós-processamento — `dist/latex/isaf-template.tex` controla
directamente em LaTeX tudo o que na rota docx exige editar o OOXML depois:

- Margens 2,5/2,5/2,5cm + 3,5cm esquerda (`geometry`).
- Espaçamento 1,5 linhas (`setspace`, `\onehalfspacing`).
- Numeração romana na capa/pré-textual → arábica a partir de "1. INTRODUÇÃO"
  (`\pagenumbering`), accionada por marcadores `` ```{=latex}...``` `` inseridos
  directamente em `relatorio/00_pretextual/00_capa.md` e
  `relatorio/00_pretextual/07_lista_abreviaturas.md` (blocos LaTeX crus — o writer
  docx ignora-os silenciosamente, confirmado por teste, por isso não afectam a rota docx).
- Cabeçalho com o título do trabalho (10pt, direita), activo só a partir do corpo
  textual, via `fancyhdr` (estilos `semcapa`/`pretextual`/`corpo`).
- `\contentsname` renomeado para "ÍNDICE"; numeração automática de secções desligada
  (`secnumdepth`) porque os títulos já trazem o número manualmente no `.md`.
- Legendas de tabela (`Table: Tabela N --- ...` no `.md`) com `labelformat=empty` no
  `caption` — evita duplicar o número ("Tabela 2 – Tabela 1 —...") que o LaTeX geraria
  por omissão.
- Fonte: `Tinos` (substituto métrico de Times New Roman, via `fontspec`/`lualatex` —
  Times New Roman não está disponível em Linux).

Requer `texlive-lang-portuguese`, `texlive-latex-extra`, `texlive-luatex` instalados
(pacote `polyglossia` para hifenização PT, `luaotfload` para carregar fontes do sistema
via `lualatex`).

Se a estrutura de `relatorio/00_pretextual/00_capa.md` mudar (nomeadamente os 3 blocos
de capa) ou a de `relatorio/00_pretextual/07_lista_abreviaturas.md` (posição do bloco
final que abre o `\tableofcontents`), reveja os blocos `` ```{=latex}``` `` inseridos
nesses ficheiros — não há validação automática como na rota docx.
