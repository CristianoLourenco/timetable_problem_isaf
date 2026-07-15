# Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/analise_requisitos_v5.0.md
# Fluxo (ver skill excel-import-openpyxl): parse -> validar (RF07) -> gravar com idempotência por
# chave única (RF08). Nunca aborta no primeiro erro de linha — reporta todos.
from collections.abc import Callable, Sequence
from io import BytesIO
from typing import Any

import openpyxl
from sqlmodel import Session

from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.sala import Sala
from app.models.turma import Turma
from app.repositories.curso_repository import CursoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.sala_repository import SalaRepository
from app.repositories.turma_repository import TurmaRepository
from app.schemas.importacao_schema import ErroImportacaoSchema, RelatorioImportacaoSchema

COLUNAS_ESPERADAS: dict[str, list[str]] = {
    "cursos": ["codigo", "nome"],
    "professores": ["nome", "email", "classificacao", "vinculo_casa"],
    "disciplinas": ["codigo", "nome"],
    "salas": ["codigo", "nome", "capacidade"],
    # turmas depende de "cursos" já estar importado (curso_codigo tem de existir)
    "turmas": ["codigo", "nome", "ano_letivo", "turno", "numero_alunos", "curso_codigo"],
}


def _ler_planilha(conteudo: bytes) -> tuple[list[str], list[tuple[Any, ...]]]:
    try:
        workbook = openpyxl.load_workbook(BytesIO(conteudo), read_only=True, data_only=True)
    except Exception as exc:  # ficheiro corrompido ou não é .xlsx
        raise ValueError("Ficheiro Excel inválido ou corrompido.") from exc

    sheet = workbook.active
    linhas = list(sheet.iter_rows(values_only=True))
    if not linhas:
        return [], []
    cabecalho = [str(c).strip().lower() if c is not None else "" for c in linhas[0]]
    return cabecalho, linhas[1:]


def _importar_professores(
    session: Session, colunas: list[str], linhas: Sequence[tuple[Any, ...]], relatorio: RelatorioImportacaoSchema
) -> None:
    repo = ProfessorRepository(session)
    for numero_linha, linha in enumerate(linhas, start=2):
        dados = dict(zip(colunas, linha, strict=False))
        nome, email = dados.get("nome"), dados.get("email")
        if not nome:
            relatorio.erros.append(ErroImportacaoSchema(linha=numero_linha, campo="nome", motivo="Nome em falta"))
            continue
        if not email:
            relatorio.erros.append(
                ErroImportacaoSchema(linha=numero_linha, campo="email", motivo="Email institucional em falta")
            )
            continue
        classificacao = int(dados.get("classificacao") or 3)
        if not (1 <= classificacao <= 5):
            relatorio.erros.append(
                ErroImportacaoSchema(
                    linha=numero_linha, campo="classificacao", motivo="Classificação deve ser entre 1 e 5"
                )
            )
            continue
        if repo.get_by_email(str(email)):
            relatorio.ignorados_idempotencia += 1
            continue
        repo.create(
            Professor(
                nome=str(nome),
                email=str(email),
                classificacao=classificacao,
                vinculo_casa=bool(dados.get("vinculo_casa")),
            )
        )
        relatorio.importados += 1


def _importar_cursos(
    session: Session, colunas: list[str], linhas: Sequence[tuple[Any, ...]], relatorio: RelatorioImportacaoSchema
) -> None:
    repo = CursoRepository(session)
    for numero_linha, linha in enumerate(linhas, start=2):
        dados = dict(zip(colunas, linha, strict=False))
        codigo, nome = dados.get("codigo"), dados.get("nome")
        if not codigo or not nome:
            relatorio.erros.append(
                ErroImportacaoSchema(linha=numero_linha, campo="codigo/nome", motivo="Código ou nome em falta")
            )
            continue
        if repo.get_by_codigo(str(codigo)):
            relatorio.ignorados_idempotencia += 1
            continue
        repo.create(Curso(codigo=str(codigo), nome=str(nome)))
        relatorio.importados += 1


def _importar_disciplinas(
    session: Session, colunas: list[str], linhas: Sequence[tuple[Any, ...]], relatorio: RelatorioImportacaoSchema
) -> None:
    repo = DisciplinaRepository(session)
    for numero_linha, linha in enumerate(linhas, start=2):
        dados = dict(zip(colunas, linha, strict=False))
        codigo, nome = dados.get("codigo"), dados.get("nome")
        if not codigo or not nome:
            relatorio.erros.append(
                ErroImportacaoSchema(linha=numero_linha, campo="codigo/nome", motivo="Código ou nome em falta")
            )
            continue
        if repo.get_by_codigo(str(codigo)):
            relatorio.ignorados_idempotencia += 1
            continue
        repo.create(Disciplina(codigo=str(codigo), nome=str(nome)))
        relatorio.importados += 1


def _importar_salas(
    session: Session, colunas: list[str], linhas: Sequence[tuple[Any, ...]], relatorio: RelatorioImportacaoSchema
) -> None:
    repo = SalaRepository(session)
    for numero_linha, linha in enumerate(linhas, start=2):
        dados = dict(zip(colunas, linha, strict=False))
        codigo, nome, capacidade = dados.get("codigo"), dados.get("nome"), dados.get("capacidade")
        if not codigo or not nome:
            relatorio.erros.append(
                ErroImportacaoSchema(linha=numero_linha, campo="codigo/nome", motivo="Código ou nome em falta")
            )
            continue
        if not capacidade or int(capacidade) <= 0:
            relatorio.erros.append(
                ErroImportacaoSchema(linha=numero_linha, campo="capacidade", motivo="Capacidade deve ser maior que 0")
            )
            continue
        if repo.get_by_codigo(str(codigo)):
            relatorio.ignorados_idempotencia += 1
            continue
        repo.create(Sala(codigo=str(codigo), nome=str(nome), capacidade=int(capacidade)))
        relatorio.importados += 1


def _importar_turmas(
    session: Session, colunas: list[str], linhas: Sequence[tuple[Any, ...]], relatorio: RelatorioImportacaoSchema
) -> None:
    turma_repo = TurmaRepository(session)
    curso_repo = CursoRepository(session)
    for numero_linha, linha in enumerate(linhas, start=2):
        dados = dict(zip(colunas, linha, strict=False))
        codigo, curso_codigo = dados.get("codigo"), dados.get("curso_codigo")
        if not codigo:
            relatorio.erros.append(ErroImportacaoSchema(linha=numero_linha, campo="codigo", motivo="Código em falta"))
            continue
        if not curso_codigo:
            relatorio.erros.append(
                ErroImportacaoSchema(linha=numero_linha, campo="curso_codigo", motivo="Código do curso em falta")
            )
            continue
        curso = curso_repo.get_by_codigo(str(curso_codigo))
        if curso is None:
            relatorio.erros.append(
                ErroImportacaoSchema(
                    linha=numero_linha, campo="curso_codigo", motivo=f"Curso '{curso_codigo}' não existe"
                )
            )
            continue
        numero_alunos = int(dados.get("numero_alunos") or 0)
        if numero_alunos <= 0:
            relatorio.erros.append(
                ErroImportacaoSchema(
                    linha=numero_linha, campo="numero_alunos", motivo="Número de alunos deve ser maior que 0"
                )
            )
            continue
        if turma_repo.get_by_codigo(str(codigo)):
            relatorio.ignorados_idempotencia += 1
            continue
        turma_repo.create(
            Turma(
                codigo=str(codigo),
                nome=str(dados.get("nome") or ""),
                ano_letivo=int(dados.get("ano_letivo") or 0),
                turno=str(dados.get("turno") or ""),
                numero_alunos=numero_alunos,
                curso_id=curso.id,  # type: ignore[arg-type]
            )
        )
        relatorio.importados += 1


_IMPORTADORES: dict[str, Callable[[Session, list[str], Sequence[tuple[Any, ...]], RelatorioImportacaoSchema], None]] = {
    "cursos": _importar_cursos,
    "professores": _importar_professores,
    "disciplinas": _importar_disciplinas,
    "salas": _importar_salas,
    "turmas": _importar_turmas,
}


def importar(entidade: str, conteudo: bytes, session: Session) -> RelatorioImportacaoSchema:
    if entidade not in COLUNAS_ESPERADAS:
        raise ValueError(f"Entidade '{entidade}' não suportada para importação.")

    cabecalho, linhas_dados = _ler_planilha(conteudo)
    relatorio = RelatorioImportacaoSchema(total_linhas=len(linhas_dados))

    esperadas = COLUNAS_ESPERADAS[entidade]
    if cabecalho[: len(esperadas)] != esperadas:
        relatorio.erros.append(
            ErroImportacaoSchema(
                linha=1, campo="cabecalho", motivo=f"Colunas esperadas (nesta ordem): {', '.join(esperadas)}"
            )
        )
        return relatorio

    _IMPORTADORES[entidade](session, cabecalho, linhas_dados, relatorio)
    return relatorio
