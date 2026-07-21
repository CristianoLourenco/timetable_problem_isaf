# Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/04_04_analise_desenvolvimento.md
#
# Regressão: bool(dados.get("vinculo_casa")) tratava QUALQUER string não vazia (incl.
# "Não") como True, invertendo silenciosamente a intenção do Gestor — ver correção em
# app/services/importacao_service.py::_parse_booleano_pt.
from io import BytesIO

import openpyxl
from sqlmodel import Session, SQLModel, create_engine, select

import app.models  # noqa: F401 - garante que todos os modelos entram no metadata
from app.models.professor import Professor
from app.services import importacao_service


def _criar_engine_teste():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _planilha(cabecalho: list[str], linhas: list[tuple]) -> bytes:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(cabecalho)
    for linha in linhas:
        sheet.append(linha)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_importar_professores_interpreta_vinculo_casa_em_varios_formatos():
    engine = _criar_engine_teste()
    with Session(engine) as session:
        conteudo = _planilha(
            ["nome", "email", "classificacao", "vinculo_casa"],
            [
                ("Ana Costa", "ana@isaf.co.ao", 4, "Sim"),
                ("Bruno Silva", "bruno@isaf.co.ao", 3, "Não"),
                ("Carla Reis", "carla@isaf.co.ao", 5, "sim"),
                ("Duarte Mendes", "duarte@isaf.co.ao", 2, 1),
                ("Elsa Neto", "elsa@isaf.co.ao", 3, 0),
                ("Fábio Lopes", "fabio@isaf.co.ao", 4, ""),
                ("Gina Paulo", "gina@isaf.co.ao", 3, True),
                ("Hugo Vieira", "hugo@isaf.co.ao", 3, False),
            ],
        )
        relatorio = importacao_service.importar("professores", conteudo, session)

        assert relatorio.importados == 8
        assert relatorio.erros == []

        professores = {p.email: p for p in session.exec(select(Professor))}
        assert professores["ana@isaf.co.ao"].vinculo_casa is True
        assert professores["bruno@isaf.co.ao"].vinculo_casa is False  # o bug tratava "Não" como True
        assert professores["carla@isaf.co.ao"].vinculo_casa is True
        assert professores["duarte@isaf.co.ao"].vinculo_casa is True
        assert professores["elsa@isaf.co.ao"].vinculo_casa is False
        assert professores["fabio@isaf.co.ao"].vinculo_casa is False
        assert professores["gina@isaf.co.ao"].vinculo_casa is True
        assert professores["hugo@isaf.co.ao"].vinculo_casa is False
