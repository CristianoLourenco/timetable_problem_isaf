# Implementa: RN09, RN10 — gestão de Gestores, restrita ao Superadmin (ver core/security.py)
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.core.security import require_superadmin
from app.schemas.utilizador_schema import UtilizadorGestorCreate, UtilizadorRead
from app.services.utilizador_service import UtilizadorService

router = APIRouter(prefix="/utilizadores", tags=["Utilizadores"], dependencies=[Depends(require_superadmin)])


def _get_service(session: Session = Depends(get_session)) -> UtilizadorService:
    return UtilizadorService(session)


@router.get("", response_model=list[UtilizadorRead])
def listar(service: UtilizadorService = Depends(_get_service)):
    return service.listar()


@router.post("", response_model=UtilizadorRead, status_code=201)
def criar_gestor(payload: UtilizadorGestorCreate, service: UtilizadorService = Depends(_get_service)):
    try:
        return service.criar_gestor(payload.email, payload.contacto_telefonico)
    except IntegridadeVioladaError as exc:
        raise HTTPException(409, str(exc)) from exc


@router.delete("/{utilizador_id}", status_code=204)
def remover(utilizador_id: int, service: UtilizadorService = Depends(_get_service)):
    try:
        service.remover(utilizador_id)
    except EntidadeNaoEncontradaError as exc:
        raise HTTPException(404, str(exc)) from exc
