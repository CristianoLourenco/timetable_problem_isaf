#!/usr/bin/env python3
"""Pos-processamento do DOCX compilado: numeração romana no pré-textual,
arábica (a partir de 1) no textual/pós-textual — ver docs/dist/README.md.

O pandoc/--reference-doc não expõe forma de inserir uma quebra de secção
com w:pgNumType diferente a meio do documento; por isso este passo edita
directamente o pacote OOXML já compilado.

Uso: python3 postprocess_pagination.py TFC_Cristiano_Lourenco.docx
"""
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PGSZPGMAR = (
    '<w:pgSz w:h="16838" w:w="11906"/>'
    '<w:pgMar w:bottom="1440" w:footer="708" w:gutter="0" w:header="708" '
    'w:left="1440" w:right="1440" w:top="1440"/>'
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
)


def main(docx_path: str) -> None:
    docx_path = Path(docx_path).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(docx_path) as z:
            z.extractall(tmp)

        # 1. footer1.xml
        (tmp / "word" / "footer1.xml").write_text(FOOTER_XML, encoding="utf-8")

        # 2. relationship
        rels_path = tmp / "word" / "_rels" / "document.xml.rels"
        rels = rels_path.read_text(encoding="utf-8")
        if "rIdFooterMain" not in rels:
            rel = (
                '<Relationship Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/footer" Id="rIdFooterMain" '
                'Target="footer1.xml"/>'
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
            ct_path.write_text(ct, encoding="utf-8")

        # 4. Footer paragraph style
        styles_path = tmp / "word" / "styles.xml"
        styles = styles_path.read_text(encoding="utf-8")
        if 'w:styleId="Footer"' not in styles:
            styles = styles.replace("</w:styles>", FOOTER_STYLE + "</w:styles>")
            styles_path.write_text(styles, encoding="utf-8")

        # 5. document.xml: section break before "1. INTRODUÇÃO" + pgNumType wiring
        doc_path = tmp / "word" / "document.xml"
        doc = doc_path.read_text(encoding="utf-8")

        marker = '<w:bookmarkStart w:id="39" w:name="introdução" />'
        if marker not in doc:
            sys.exit(
                "ERRO: marcador do início da Introdução não encontrado — "
                "o documento pode ter sido recompilado com uma estrutura "
                "diferente; reveja o script."
            )
        if doc.count(marker) != 1:
            sys.exit("ERRO: marcador do início da Introdução não é único.")

        section_break = (
            "<w:p><w:pPr><w:sectPr>"
            '<w:footerReference w:type="default" r:id="rIdFooterMain"/>'
            + PGSZPGMAR
            + '<w:pgNumType w:fmt="lowerRoman" w:start="1"/>'
            "</w:sectPr></w:pPr></w:p>"
        )
        doc = doc.replace(marker, section_break + marker, 1)

        old_final_sectpr = (
            "<w:sectPr>"
            '<w:pgSz w:h="16838" w:w="11906" />'
            '<w:pgMar w:bottom="1440" w:footer="708" w:gutter="0" w:header="708" '
            'w:left="1440" w:right="1440" w:top="1440" />'
            "</w:sectPr></w:body>"
        )
        if old_final_sectpr not in doc:
            sys.exit(
                "ERRO: sectPr final não encontrado no formato esperado — "
                "reveja o script após alterar dist/custom-reference.docx."
            )
        new_final_sectpr = (
            "<w:sectPr>"
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
