# Implementa: RF05 (UC05) — ver docs/04_04_analise_desenvolvimento.md
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.core.security import UtilizadorAutenticado, get_current_user, verificar_acesso_professor_proprio
from app.schemas.disponibilidade_schema import DisponibilidadeReadSchema, DisponibilidadeSetSchema
from app.services.disponibilidade_service import DisponibilidadeService

router = APIRouter(prefix="/professores", tags=["Disponibilidade"])


def _get_service(session: Session = Depends(get_session)) -> DisponibilidadeService:
    return DisponibilidadeService(session)


@router.get("/{professor_id}/disponibilidade", response_model=DisponibilidadeReadSchema)
def obter_disponibilidade(
    professor_id: int,
    service: DisponibilidadeService = Depends(_get_service),
    user: UtilizadorAutenticado = Depends(get_current_user),
):
    """RF05 — o próprio Professor gere a sua disponibilidade; Gestor/Superadmin têm acesso administrativo."""
    verificar_acesso_professor_proprio(user, professor_id)
    try:
        tempos = service.obter(professor_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return DisponibilidadeReadSchema(tempos=tempos)


@router.post("/{professor_id}/disponibilidade", response_model=DisponibilidadeReadSchema)
def definir_disponibilidade(
    professor_id: int,
    payload: DisponibilidadeSetSchema,
    service: DisponibilidadeService = Depends(_get_service),
    user: UtilizadorAutenticado = Depends(get_current_user),
):
    verificar_acesso_professor_proprio(user, professor_id)
    try:
        tempos = service.definir(professor_id, payload.tempos)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return DisponibilidadeReadSchema(tempos=tempos)
