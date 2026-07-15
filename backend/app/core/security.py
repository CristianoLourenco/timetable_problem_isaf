# Implementa: RN09, RN10, RN11 (UC13, UC15) — ver docs/analise_requisitos_v5.0.md
#
# Verificação do ID Token via google-auth (google.oauth2.id_token.verify_firebase_token)
# contra os certificados públicos do Google — não exige firebase-service-account.json
# (indisponível neste projeto; só seria necessário para operações administrativas do
# Firebase Admin SDK, que este backend não usa).
from dataclasses import dataclass
from enum import StrEnum

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlmodel import Session, select

from app.api.v1.deps import get_session
from app.core.config import settings
from app.core.exceptions import AcessoNegadoError, TokenInvalidoError
from app.models.utilizador import PerfilUtilizador, Utilizador

_bearer_scheme = HTTPBearer(auto_error=False)
_google_request = google_requests.Request()


class Papel(StrEnum):
    SUPERADMIN = "SUPERADMIN"
    GESTOR = "GESTOR"
    PROFESSOR = "PROFESSOR"


@dataclass(frozen=True)
class UtilizadorAutenticado:
    email: str
    papel: Papel
    professor_id: int | None = None
    utilizador_id: int | None = None


def verificar_id_token(token: str) -> str:
    """RN09 — devolve o email do ID Token verificado, ou levanta TokenInvalidoError."""
    try:
        claims = id_token.verify_firebase_token(token, _google_request, audience=settings.firebase_project_id)
    except ValueError as exc:
        raise TokenInvalidoError("Token Firebase inválido ou expirado.") from exc

    email = claims.get("email")
    if not email:
        raise TokenInvalidoError("Token Firebase não contém email associado.")
    return email


def get_verified_email(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """RN09 — exige `Authorization: Bearer <ID Token>`; não resolve papel (usado no auto-registo)."""
    if credentials is None:
        raise TokenInvalidoError("Token de autenticação em falta.")
    return verificar_id_token(credentials.credentials)


def get_current_user(
    session: Session = Depends(get_session),
    email: str = Depends(get_verified_email),
) -> UtilizadorAutenticado:
    """RN09/RN10 — resolve o papel do email autenticado: Superadmin (bootstrap) > Utilizador (Gestor/Professor)."""
    if email in settings.superadmin_emails:
        return UtilizadorAutenticado(email=email, papel=Papel.SUPERADMIN)

    utilizador = session.exec(select(Utilizador).where(Utilizador.email == email)).first()
    if utilizador is None:
        raise AcessoNegadoError("Esta conta ainda não está registada no sistema.")

    papel = Papel.GESTOR if utilizador.perfil == PerfilUtilizador.GESTOR else Papel.PROFESSOR
    return UtilizadorAutenticado(
        email=email, papel=papel, professor_id=utilizador.professor_id, utilizador_id=utilizador.id
    )


def require_gestor(user: UtilizadorAutenticado = Depends(get_current_user)) -> UtilizadorAutenticado:
    if user.papel not in (Papel.SUPERADMIN, Papel.GESTOR):
        raise AcessoNegadoError("Apenas o Gestor pode aceder a este recurso.")
    return user


def require_superadmin(user: UtilizadorAutenticado = Depends(get_current_user)) -> UtilizadorAutenticado:
    if user.papel != Papel.SUPERADMIN:
        raise AcessoNegadoError("Apenas o Superadmin pode aceder a este recurso.")
    return user


def verificar_acesso_professor_proprio(user: UtilizadorAutenticado, professor_id: int) -> None:
    """RN11 — Gestor/Superadmin acedem a qualquer professor; Professor só ao seu próprio."""
    if user.papel == Papel.PROFESSOR and user.professor_id != professor_id:
        raise AcessoNegadoError("Só pode aceder aos seus próprios dados.")
