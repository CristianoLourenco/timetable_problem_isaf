# Relatório compilado

`TFC_Cristiano_Lourenco.docx` é gerado a partir dos `.md` em `docs/` — nunca editado
directamente. Fica fora do git (ver `.gitignore`): é um artefacto derivado, não a fonte.

## Como regenerar

```bash
cd docs
pandoc \
  00_capa_pretextual.md 04_01_introducao.md 04_02_fundamentacao_teorica.md \
  04_03_metodologia.md 04_04_analise_desenvolvimento.md 04_05_conclusao.md \
  99_referencias_apendices.md \
  --citeproc --bibliography=referencias.bib --csl=apa.csl \
  --reference-doc=dist/custom-reference.docx \
  --toc --toc-depth=3 \
  -o dist/TFC_Cristiano_Lourenco.docx

python3 dist/postprocess_pagination.py dist/TFC_Cristiano_Lourenco.docx

# opcional mas recomendado — pré-resolve o campo do Índice no próprio
# .docx (exige LibreOffice instalado; ver docstring do script)
python3 dist/resolve_toc_libreoffice.py dist/TFC_Cristiano_Lourenco.docx
```

O segundo passo (`postprocess_pagination.py`) **é obrigatório** — faz três
coisas que o pandoc não expõe a partir do markdown/reference-doc, editando
directamente o pacote OOXML já compilado:

1. Insere a quebra de secção entre o pré-textual e o "1. INTRODUÇÃO" e liga um
   rodapé com numeração de página: romano minúsculo (i, ii, iii...) no
   pré-textual, arábico a partir de 1 do "1. INTRODUÇÃO" até ao fim (textual +
   pós-textual).
2. Reposiciona o campo `ÍNDICE` (Índice/TOC), que o pandoc `--toc` insere
   sempre no início absoluto do documento (antes da capa), para o local
   correcto: depois da "Lista de Abreviaturas e Siglas" e antes do "1.
   INTRODUÇÃO".
3. Abre uma página nova a seguir ao Índice, para que "1. INTRODUÇÃO" comece
   sempre em página própria.

Se não correr o passo opcional `resolve_toc_libreoffice.py`, o Word ainda
assim resolve o campo do Índice automaticamente ao abrir o ficheiro (o
pandoc marca-o como "dirty"); se por algum motivo isso não acontecer,
actualize manualmente com botão direito sobre o Índice → "Atualizar campo"
→ "Atualizar índice inteiro".

Se a estrutura de `00_capa_pretextual.md` ou `04_01_introducao.md` mudar
(nomeadamente o heading "1. INTRODUÇÃO"), reveja o script — ele falha alto
(`sys.exit`) em vez de produzir um DOCX com numeração ou Índice errados caso
não encontre os marcadores esperados.

- `referencias.bib` — exportado do Zotero (Better BibTeX); manter sincronizado lá, não
  editar as entradas manualmente aqui.
- `apa.csl` — estilo de citação (APA 7).
- `dist/custom-reference.docx` — define fonte (Times New Roman 12pt), espaçamento
  duplo e hierarquia de títulos (APA: Nível 1 centrado, Nível 2/3 alinhados à
  esquerda) usados na compilação. Não é gerado a partir de `pandoc --print-default-data-file`
  directamente — foi editado manualmente (`word/styles.xml` e `word/theme/theme1.xml`)
  a partir desse ficheiro base.
- **Não usar `--metadata title=`/`--metadata author=`**: o pandoc insere
  automaticamente um bloco de título/autor no topo do documento a partir destes
  metadados, duplicando o conteúdo da capa/folha de rosto já escrito em
  `00_capa_pretextual.md`.
- `01_diagrama_contexto.md`, `02_diagrama_casos_uso.md`, `03_especificacao_casos_uso.md`
  ficam de fora de propósito — são o documento de trabalho "Modelagem do Sistema", não o
  corpo do TFC.
- Diagramas (`media/*.png`) são gerados a partir das fontes em `media/src/*.puml` — ver
  `media/src/` para reeditar sem partir do zero (`java -jar plantuml.jar -tpng ficheiro.puml`).
