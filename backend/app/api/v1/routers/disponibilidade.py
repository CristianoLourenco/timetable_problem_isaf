# Implementa: RF05 (UC05) — ver docs/analise_requisitos_v5.0.md
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError
from app.schemas.disponibilidade_schema import DisponibilidadeReadSchema, DisponibilidadeSetSchema
from app.services.disponibilidade_service import DisponibilidadeService

router = APIRouter(prefix="/professores", tags=["Disponibilidade"])


def _get_service(session: Session = Depends(get_session)) -> DisponibilidadeService:
    return DisponibilidadeService(session)


@router.get("/{professor_id}/disponibilidade", response_model=DisponibilidadeReadSchema)
def obter_disponibilidade(professor_id: int, service: DisponibilidadeService = Depends(_get_service)):
    try:
        slot_ids = service.obter(professor_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return DisponibilidadeReadSchema(slot_ids=slot_ids)


@router.post("/{professor_id}/disponibilidade", response_model=DisponibilidadeReadSchema)
def definir_disponibilidade(
    professor_id: int,
    payload: DisponibilidadeSetSchema,
    service: DisponibilidadeService = Depends(_get_service),
):
    try:
        slot_ids = service.definir(professor_id, payload.slot_ids)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
    return DisponibilidadeReadSchema(slot_ids=slot_ids)
