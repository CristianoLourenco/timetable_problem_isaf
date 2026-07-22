#!/usr/bin/env python3
"""Pos-processamento do DOCX compilado: numeração romana no pré-textual,
arábica (a partir de 1) no textual/pós-textual — ver docs/dist/README.md.

O pandoc/--reference-doc não expõe forma de inserir uma quebra de secção
com w:pgNumType diferente a meio do documento; por isso este passo edita
directamente o pacote OOXML já compilado.

Uso: python3 postprocess_pagination.py TFC_Cristiano_Lourenco.docx
"""
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# Margens do Regulamento TCC do ISAF (Artigo 9º, ponto 6): superior/direita/
# inferior 2,5cm (1417 twips), esquerda 3,5cm (1984 twips, folga extra para
# encadernação com argolas plásticas — Artigo 9º, ponto 7).
PGSZPGMAR = (
    '<w:pgSz w:h="16838" w:w="11906"/>'
    '<w:pgMar w:bottom="1417" w:footer="708" w:gutter="0" w:header="708" '
    'w:left="1984" w:right="1417" w:top="1417"/>'
)

# Título do trabalho no cabeçalho (Regulamento, Artigo 9º ponto 6.j: fonte
# 10pt, alinhado à margem direita) — só a partir do corpo textual (RF/UC não
# se aplica ao pré-textual, onde não há cabeçalho por convenção académica).
TITULO_TRABALHO = (
    "DESENVOLVIMENTO DE UM SISTEMA INTELIGENTE PARA A GERAÇÃO AUTOMÁTICA "
    "DE HORÁRIOS ACADÉMICOS"
)

HEADER_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:p><w:pPr><w:pStyle w:val="Header"/><w:jc w:val="right"/>'
    '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
    '<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:pPr>'
    f'<w:r><w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t>{TITULO_TRABALHO}</w:t></w:r>'
    '</w:p></w:hdr>'
)

FOOTER_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:p><w:pPr><w:pStyle w:val="Footer"/><w:jc w:val="center"/>'
    '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
    '<w:fldSimple w:instr=" PAGE "><w:r><w:t>1</w:t></w:r></w:fldSimple>'
    '</w:p></w:ftr>'
)

FOOTER_STYLE = (
    '  <w:style w:type="paragraph" w:styleId="Footer">\n'
    '    <w:name w:val="footer" />\n'
    '    <w:basedOn w:val="Normal" />\n'
    '    <w:link w:val="FooterChar" />\n'
    '    <w:pPr>\n'
    '      <w:tabs><w:tab w:val="center" w:pos="4680" /><w:tab w:val="right" w:pos="9360" /></w:tabs>\n'
    '      <w:spacing w:after="0" w:line="240" w:lineRule="auto" />\n'
    '    </w:pPr>\n'
    '  </w:style>\n'
    '  <w:style w:type="character" w:customStyle="1" w:styleId="FooterChar">\n'
    '    <w:name w:val="Footer Char" />\n'
    '    <w:basedOn w:val="DefaultParagraphFont" />\n'
    '    <w:link w:val="Footer" />\n'
    '  </w:style>\n'
    '  <w:style w:type="paragraph" w:styleId="Header">\n'
    '    <w:name w:val="header" />\n'
    '    <w:basedOn w:val="Normal" />\n'
    '    <w:link w:val="HeaderChar" />\n'
    '    <w:pPr>\n'
    '      <w:tabs><w:tab w:val="center" w:pos="4680" /><w:tab w:val="right" w:pos="9360" /></w:tabs>\n'
    '      <w:spacing w:after="0" w:line="240" w:lineRule="auto" />\n'
    '    </w:pPr>\n'
    '  </w:style>\n'
    '  <w:style w:type="character" w:customStyle="1" w:styleId="HeaderChar">\n'
    '    <w:name w:val="Header Char" />\n'
    '    <w:basedOn w:val="DefaultParagraphFont" />\n'
    '    <w:link w:val="Header" />\n'
    '  </w:style>\n'
)


def main(docx_path: str) -> None:
    docx_path = Path(docx_path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(docx_path) as z:
            z.extractall(tmp)

        # 1. footer1.xml + header1.xml
        (tmp / "word" / "footer1.xml").write_text(FOOTER_XML, encoding="utf-8")
        (tmp / "word" / "header1.xml").write_text(HEADER_XML, encoding="utf-8")

        # 2. relationships
        rels_path = tmp / "word" / "_rels" / "document.xml.rels"
        rels = rels_path.read_text(encoding="utf-8")
        if "rIdFooterMain" not in rels:
            rel = (
                '<Relationship Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/footer" Id="rIdFooterMain" '
                'Target="footer1.xml"/>'
            )
            rels = rels.replace("</Relationships>", rel + "</Relationships>")
        if "rIdHeaderMain" not in rels:
            rel = (
                '<Relationship Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/header" Id="rIdHeaderMain" '
                'Target="header1.xml"/>'
            )
            rels = rels.replace("</Relationships>", rel + "</Relationships>")
        rels_path.write_text(rels, encoding="utf-8")

        # 3. content types
        ct_path = tmp / "[Content_Types].xml"
        ct = ct_path.read_text(encoding="utf-8")
        if "footer1.xml" not in ct:
            override = (
                '<Override PartName="/word/footer1.xml" ContentType='
                '"application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml" />'
            )
            ct = ct.replace("</Types>", override + "</Types>")
        if "header1.xml" not in ct:
            override = (
                '<Override PartName="/word/header1.xml" ContentType='
                '"application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml" />'
            )
            ct = ct.replace("</Types>", override + "</Types>")
        ct_path.write_text(ct, encoding="utf-8")

        # 4. Footer/Header paragraph styles
        styles_path = tmp / "word" / "styles.xml"
        styles = styles_path.read_text(encoding="utf-8")
        if 'w:styleId="Footer"' not in styles:
            styles = styles.replace("</w:styles>", FOOTER_STYLE + "</w:styles>")
            styles_path.write_text(styles, encoding="utf-8")

        # 5. document.xml: reposiciona o Índice (--toc do pandoc insere-o sempre
        #    no início absoluto do body, antes da capa) + secção break antes de
        #    "1. INTRODUÇÃO" + pgNumType wiring
        doc_path = tmp / "word" / "document.xml"
        doc = doc_path.read_text(encoding="utf-8")

        # As 3 primeiras páginas (capa, folha de rosto, Banca Examinadora) não
        # podem ter numeração nenhuma — a numeração romana do pré-textual só
        # começa na página seguinte, "COMPROMISSO DO AUTOR". Procurar pelo nome
        # do bookmark (estável, gerado a partir do heading) em vez de assumir
        # uma posição fixa.
        match_sem_numero = re.search(
            r'<w:bookmarkStart w:id="\d+" w:name="compromisso-do-autor" />', doc
        )
        if match_sem_numero is None:
            sys.exit(
                "ERRO: marcador do início de 'Compromisso do Autor' não "
                "encontrado — reveja o script."
            )
        marker_sem_numero = match_sem_numero.group(0)
        if doc.count(marker_sem_numero) != 1:
            sys.exit(
                "ERRO: marcador do início de 'Compromisso do Autor' não é único — "
                "reveja o script."
            )
        section_break_sem_numero = (
            "<w:p><w:pPr><w:sectPr>" + PGSZPGMAR + "</w:sectPr></w:pPr></w:p>"
        )
        doc = doc.replace(
            marker_sem_numero, section_break_sem_numero + marker_sem_numero, 1
        )

        # O id do bookmark é atribuído sequencialmente pelo pandoc consoante o
        # nº de elementos bookmarked antes deste ponto — muda sempre que o
        # pré-textual ganha/perde conteúdo (ex: novas secções, imagens),
        # mesmo sem tocar em 04_01_introducao.md. Procurar pelo nome (estável,
        # deriva do heading "1. Introdução") em vez do id hardcoded.
        match = re.search(r'<w:bookmarkStart w:id="\d+" w:name="introdução" />', doc)
        if match is None:
            sys.exit(
                "ERRO: marcador do início da Introdução não encontrado — "
                "o documento pode ter sido recompilado com uma estrutura "
                "diferente; reveja o script."
            )
        marker = match.group(0)
        if doc.count(marker) != 1:
            sys.exit("ERRO: marcador do início da Introdução não é único.")

        # extrai o bloco <w:sdt>...</w:sdt> do Índice, se presente (gerado por
        # --toc), do início do body, para o reinserir mais à frente
        toc_block = ""
        body_open = "<w:body>"
        i = doc.find(body_open)
        sdt_start = i + len(body_open)
        if doc[sdt_start:sdt_start + 7] == "<w:sdt>":
            sdt_end = doc.find("</w:sdt>", sdt_start) + len("</w:sdt>")
            toc_block = doc[sdt_start:sdt_end]
            doc = doc[:sdt_start] + doc[sdt_end:]
            # pandoc não expõe --toc-title na versão instalada; renomeia aqui
            toc_block = toc_block.replace(
                "<w:t xml:space=\"preserve\">Table of Contents</w:t>",
                "<w:t xml:space=\"preserve\">ÍNDICE</w:t>",
            )

        page_break = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
        section_break = (
            "<w:p><w:pPr><w:sectPr>"
            '<w:footerReference w:type="default" r:id="rIdFooterMain"/>'
            + PGSZPGMAR
            + '<w:pgNumType w:fmt="lowerRoman" w:start="1"/>'
            "</w:sectPr></w:pPr></w:p>"
        )
        doc = doc.replace(
            marker, toc_block + page_break + section_break + marker, 1
        )

        old_final_sectpr = (
            "<w:sectPr>"
            '<w:pgSz w:h="16838" w:w="11906" />'
            '<w:pgMar w:bottom="1417" w:footer="708" w:gutter="0" w:header="708" '
            'w:left="1984" w:right="1417" w:top="1417" />'
            "</w:sectPr></w:body>"
        )
        if old_final_sectpr not in doc:
            sys.exit(
                "ERRO: sectPr final não encontrado no formato esperado — "
                "reveja o script após alterar dist/custom-reference.docx."
            )
        new_final_sectpr = (
            "<w:sectPr>"
            '<w:headerReference w:type="default" r:id="rIdHeaderMain"/>'
            '<w:footerReference w:type="default" r:id="rIdFooterMain"/>'
            + PGSZPGMAR
            + '<w:pgNumType w:fmt="decimal" w:start="1"/>'
            "</w:sectPr></w:body>"
        )
        doc = doc.replace(old_final_sectpr, new_final_sectpr, 1)
        doc_path.write_text(doc, encoding="utf-8")

        # repackage
        docx_path.unlink()
        with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(tmp.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(tmp))

    print(f"OK: numeração pré-textual/textual aplicada em {docx_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"uso: {sys.argv[0]} <ficheiro.docx>")
    main(sys.argv[1])
