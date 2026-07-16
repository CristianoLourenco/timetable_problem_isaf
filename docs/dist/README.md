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
  --metadata title="Desenvolvimento de um Sistema Inteligente para a Geração Automática de Horários Académicos" \
  --metadata author="Cristiano Francisco Lourenço" \
  -o dist/TFC_Cristiano_Lourenco.docx
```

- `referencias.bib` — exportado do Zotero (Better BibTeX); manter sincronizado lá, não
  editar as entradas manualmente aqui.
- `apa.csl` — estilo de citação (APA 7).
- `01_diagrama_contexto.md`, `02_diagrama_casos_uso.md`, `03_especificacao_casos_uso.md`
  ficam de fora de propósito — são o documento de trabalho "Modelagem do Sistema", não o
  corpo do TFC.
- Diagramas (`media/*.png`) são gerados a partir das fontes em `media/src/*.puml` — ver
  `media/src/` para reeditar sem partir do zero (`java -jar plantuml.jar -tpng ficheiro.puml`).
