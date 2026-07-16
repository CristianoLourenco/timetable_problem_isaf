#!/usr/bin/env python3
"""Pré-resolve o campo do Índice (TOC) dentro do próprio DOCX, usando o motor
de campos do LibreOffice via UNO — ver docs/dist/README.md.

Passo opcional: o Word actualiza automaticamente o campo do Índice ao abrir
(o pandoc marca-o como "dirty"), por isso este passo não é estritamente
necessário para entregar o ficheiro. Mas sem ele, ferramentas que não
recalculam campos automaticamente (alguns visualizadores de PDF/DOCX
online, versões antigas do LibreOffice) mostram o Índice vazio. Este script
abre o documento num LibreOffice em modo servidor (invisível), pede para
recalcular todos os índices do documento, e grava o resultado de volta no
mesmo ficheiro .docx.

Uso: python3 resolve_toc_libreoffice.py TFC_Cristiano_Lourenco.docx
"""
import socket
import subprocess
import sys
import time
from pathlib import Path

PORT = 2002


def main(docx_path: str) -> None:
    docx_path = Path(docx_path).resolve()

    proc = subprocess.Popen([
        "soffice", "--headless", "--invisible", "--nocrashreport",
        "--nodefault", "--norestore", "--nologo", "--nofirststartwizard",
        f"--accept=socket,host=localhost,port={PORT};urp;",
    ])
    try:
        for _ in range(60):
            try:
                with socket.create_connection(("localhost", PORT), timeout=1):
                    break
            except OSError:
                time.sleep(0.5)
        else:
            sys.exit("ERRO: o LibreOffice não ficou disponível a tempo.")

        import uno
        from com.sun.star.beans import PropertyValue

        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx
        )

        ctx = None
        for _ in range(30):
            try:
                ctx = resolver.resolve(
                    f"uno:socket,host=localhost,port={PORT};urp;"
                    "StarOffice.ComponentContext"
                )
                break
            except Exception:
                time.sleep(0.5)
        if ctx is None:
            sys.exit("ERRO: não foi possível ligar ao LibreOffice via UNO.")

        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )

        def prop(name, value):
            p = PropertyValue()
            p.Name = name
            p.Value = value
            return p

        url = "file://" + str(docx_path)
        doc = desktop.loadComponentFromURL(
            url, "_blank", 0, (prop("Hidden", True),)
        )
        try:
            indexes = doc.getDocumentIndexes()
            for i in range(indexes.getCount()):
                indexes.getByIndex(i).update()
            doc.getTextFields().refresh()
            doc.store()
        finally:
            doc.close(False)

    finally:
        proc.terminate()

    print(f"OK: Índice pré-resolvido e gravado em {docx_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"uso: {sys.argv[0]} <ficheiro.docx>")
    main(sys.argv[1])
