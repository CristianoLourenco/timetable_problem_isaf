# Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/analise_requisitos_v5.0.md
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.security import require_gestor
from app.schemas.importacao_schema import RelatorioImportacaoSchema
from app.services import importacao_service

# RN09/RN10 — importação em massa é reservada ao Gestor (RF06).
router = APIRouter(prefix="/upload", tags=["Importação"], dependencies=[Depends(require_gestor)])

ENTIDADES_SUPORTADAS = frozenset({"cursos", "professores", "turmas", "disciplinas", "salas"})


@router.post(
    "/excel",
    response_model=RelatorioImportacaoSchema,
    description="""
Importação em massa via .xlsx (RF06/RF07/RF08). Primeira linha = cabeçalho, com as colunas
exatamente pela ordem abaixo (nomes não sensíveis a maiúsculas/minúsculas). Idempotência por
chave única — reimportar ignora linhas cuja chave já exista (não atualiza, não duplica).
Nunca aborta na primeira linha inválida — devolve um relatório com todos os erros.

Se `turmas` referencia um `curso_codigo`, importa `cursos` primeiro.

| entidade | colunas (nesta ordem) | chave de idempotência |
|---|---|---|
| `cursos` | codigo, nome | codigo |
| `professores` | nome, email, classificacao (1-5), vinculo_casa (true/false) | email |
| `disciplinas` | codigo, nome | codigo |
| `salas` | codigo, nome, capacidade (>0) | codigo |
| `turmas` | codigo, nome, ano_letivo, turno, numero_alunos (>0), curso_codigo | codigo (curso_codigo tem de já existir) |
""",
)
async def importar_excel(
    entidade: str,
    file: UploadFile,
    session: Session = Depends(get_session),
) -> RelatorioImportacaoSchema:
    if entidade not in ENTIDADES_SUPORTADAS:
        raise HTTPException(400, f"Entidade inválida. Use uma de: {sorted(ENTIDADES_SUPORTADAS)}")
    conteudo = await file.read()
    try:
        return importacao_service.importar(entidade, conteudo, session)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
