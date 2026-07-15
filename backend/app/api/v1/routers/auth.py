# Implementa: RN10 (UC13) — ver docs/analise_requisitos_v5.0.md
#
# O Professor cria a própria conta Firebase (fora do backend, no cliente Flutter);
# este endpoint completa o registo no sistema, validando o email contra o registo
# já criado pelo Gestor via RF01. RF15/RF16 (login, reset de password) são geridos
# inteiramente pelo Firebase Authentication no cliente — não têm rota aqui.
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import IntegridadeVioladaError
from app.core.security import get_verified_email
from app.schemas.utilizador_schema import RegistoProfessorSchema, UtilizadorRead
from app.services.utilizador_service import UtilizadorService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _get_service(session: Session = Depends(get_session)) -> UtilizadorService:
    return UtilizadorService(session)


@router.post("/registo-professor", response_model=UtilizadorRead, status_code=201)
def registar_professor(
    payload: RegistoProfessorSchema,
    email: str = Depends(get_verified_email),
    service: UtilizadorService = Depends(_get_service),
):
    """RN10 — 403 (via AcessoNegadoError) se o email não corresponder a nenhum Professor."""
    try:
        return service.registar_professor(email, payload.contacto_telefonico)
    except IntegridadeVioladaError as exc:
        raise HTTPException(409, str(exc)) from exc
