# Implementa: RF06, RF07, RF08 (UC06, UC07) — ver docs/analise_requisitos_v5.0.md
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.schemas.importacao_schema import RelatorioImportacaoSchema
from app.services import importacao_service

router = APIRouter(prefix="/upload", tags=["Importação"])

ENTIDADES_SUPORTADAS = frozenset({"professores", "turmas", "disciplinas", "salas"})


@router.post("/excel", response_model=RelatorioImportacaoSchema)
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
