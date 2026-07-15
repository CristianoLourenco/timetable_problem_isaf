# Implementa: RF15, RF16 (UC13, UC14), RN10 — ver docs/analise_requisitos_v5.0.md
#
# RN09 não se aplica a estas rotas — não faz sentido exigir um ID Token válido para
# obter um ID Token. O login (email/senha e Google) e o refresh são feitos aqui no
# backend, nunca diretamente pelo cliente Flutter contra o Firebase (decisão do
# utilizador, 2026-07-15) — ver core/firebase_rest.py para o porquê disto não exigir
# firebase-service-account.json nem client secret OAuth.
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.v1.deps import get_session
from app.core.exceptions import IntegridadeVioladaError
from app.core.firebase_rest import (
    FirebaseAuthError,
    enviar_email_recuperacao_password,
    login_com_google,
    login_com_password,
    renovar_token,
)
from app.core.security import UtilizadorAutenticado, get_current_user
from app.schemas.auth_schema import (
    LoginGoogleSchema,
    LoginSchema,
    MeResponseSchema,
    RecuperarPasswordSchema,
    RefreshTokenSchema,
    RegistoProfessorSchema,
    RegistoResponseSchema,
    TokenResponseSchema,
)
from app.services.utilizador_service import UtilizadorService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _get_service(session: Session = Depends(get_session)) -> UtilizadorService:
    return UtilizadorService(session)


def _para_token_response(sessao_firebase: dict) -> TokenResponseSchema:
    return TokenResponseSchema(
        id_token=sessao_firebase["idToken"],
        refresh_token=sessao_firebase["refreshToken"],
        expires_in=int(sessao_firebase["expiresIn"]),
    )


@router.post("/login", response_model=TokenResponseSchema)
def login(payload: LoginSchema):
    """RF15 (UC13) — login por email/senha."""
    try:
        return _para_token_response(login_com_password(payload.email, payload.password))
    except FirebaseAuthError as exc:
        raise HTTPException(exc.status_http, str(exc)) from exc


@router.post("/login-google", response_model=TokenResponseSchema)
def login_google(payload: LoginGoogleSchema):
    """RF15 (UC13) — login com Google: o cliente obtém o Google ID Token via Google
    Sign-In nativo e envia-o aqui; o backend troca-o por uma sessão Firebase."""
    try:
        return _para_token_response(login_com_google(payload.google_id_token))
    except FirebaseAuthError as exc:
        raise HTTPException(exc.status_http, str(exc)) from exc


@router.post("/refresh", response_model=TokenResponseSchema)
def refresh(payload: RefreshTokenSchema):
    """RF15 — renova a sessão sem pedir email/senha outra vez."""
    try:
        return _para_token_response(renovar_token(payload.refresh_token))
    except FirebaseAuthError as exc:
        raise HTTPException(exc.status_http, str(exc)) from exc


@router.post("/recuperar-password", status_code=204)
def recuperar_password(payload: RecuperarPasswordSchema):
    """RF16 (UC14) — dispara o email de reset nativo do Firebase.

    Sempre 204, mesmo que o email não exista — evita confirmar a terceiros quais
    emails têm conta registada (enumeration).
    """
    try:
        enviar_email_recuperacao_password(payload.email)
    except FirebaseAuthError as exc:
        if exc.codigo == "EMAIL_NOT_FOUND":
            return
        raise HTTPException(exc.status_http, str(exc)) from exc


@router.post("/registo-professor", response_model=RegistoResponseSchema, status_code=201)
def registar_professor(payload: RegistoProfessorSchema, service: UtilizadorService = Depends(_get_service)):
    """RN10 — cria a conta Firebase e o registo no sistema, validado contra o email
    do registo já criado pelo Gestor (RF01). 403 (AcessoNegadoError) se não corresponder."""
    try:
        sessao = service.registar_professor(payload.email, payload.password, payload.contacto_telefonico)
    except IntegridadeVioladaError as exc:
        raise HTTPException(409, str(exc)) from exc
    except FirebaseAuthError as exc:
        raise HTTPException(exc.status_http, str(exc)) from exc

    return RegistoResponseSchema(
        id_token=sessao.id_token,
        refresh_token=sessao.refresh_token,
        expires_in=sessao.expires_in,
        utilizador=sessao.utilizador,
    )


@router.get("/me", response_model=MeResponseSchema)
def obter_utilizador_atual(user: UtilizadorAutenticado = Depends(get_current_user)):
    """Única rota de /auth que EXIGE token válido (RN09) — é precisamente para o
    cliente descobrir o próprio papel/professor_id depois de autenticar, e para
    verificar se uma sessão guardada localmente ainda é válida."""
    return MeResponseSchema(email=user.email, papel=user.papel.value, professor_id=user.professor_id)
