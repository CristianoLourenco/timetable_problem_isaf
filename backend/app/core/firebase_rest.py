# Implementa: RF15, RF16 (UC13, UC14) — ver docs/analise_requisitos_v5.0.md
#
# O backend é quem fala com a REST API do Firebase Authentication (Identity Toolkit +
# Secure Token) — o cliente Flutter nunca chama o Firebase diretamente para login,
# refresh, recuperação de password ou login com Google (decisão do utilizador,
# 2026-07-15). Isto não precisa de firebase-service-account.json nem do Firebase
# Admin SDK — é a mesma REST API pública que os SDKs cliente do Firebase usam por
# trás, autenticada só pela Web API Key (pública, não é segredo).
import httpx

from app.core.config import settings

_IDENTITY_TOOLKIT_URL = "https://identitytoolkit.googleapis.com/v1"
_SECURE_TOKEN_URL = "https://securetoken.googleapis.com/v1/token"

_MENSAGENS_PT = {
    "EMAIL_NOT_FOUND": "Não existe nenhuma conta com este email.",
    "INVALID_PASSWORD": "Palavra-passe incorreta.",
    "INVALID_LOGIN_CREDENTIALS": "Email ou palavra-passe incorretos.",
    "USER_DISABLED": "Esta conta foi desativada.",
    "EMAIL_EXISTS": "Já existe uma conta Firebase com este email.",
    "INVALID_REFRESH_TOKEN": "Sessão inválida — inicie sessão novamente.",
    "TOKEN_EXPIRED": "Sessão expirada — inicie sessão novamente.",
    "USER_NOT_FOUND": "Não existe nenhuma conta com este email.",
    "INVALID_ID_TOKEN": "Token do Google inválido ou expirado.",
    "WEAK_PASSWORD": "A palavra-passe deve ter pelo menos 6 caracteres.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Demasiadas tentativas — tente novamente mais tarde.",
}

_STATUS_HTTP = {
    "EMAIL_NOT_FOUND": 401,
    "INVALID_PASSWORD": 401,
    "INVALID_LOGIN_CREDENTIALS": 401,
    "USER_DISABLED": 403,
    "EMAIL_EXISTS": 409,
    "INVALID_REFRESH_TOKEN": 401,
    "TOKEN_EXPIRED": 401,
    "USER_NOT_FOUND": 401,
    "INVALID_ID_TOKEN": 401,
    "WEAK_PASSWORD": 400,
    "TOO_MANY_ATTEMPTS_TRY_LATER": 429,
}


class FirebaseAuthError(Exception):
    """Erro devolvido pela REST API do Firebase Authentication (RF15/RF16)."""

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.status_http = _STATUS_HTTP.get(codigo, 401)
        super().__init__(_MENSAGENS_PT.get(codigo, "Erro de autenticação — tente novamente."))


def _pedir(url: str, *, params: dict, json: dict | None = None, data: dict | None = None) -> dict:
    resposta = httpx.post(url, params=params, json=json, data=data, timeout=10.0)
    if resposta.status_code != 200:
        mensagem_erro = resposta.json().get("error", {}).get("message", "ERRO_DESCONHECIDO")
        # WEAK_PASSWORD vem como "WEAK_PASSWORD : Password should be at least 6
        # characters" — normaliza para o código isolado antes de mapear.
        codigo = mensagem_erro.split(" ")[0]
        raise FirebaseAuthError(codigo)
    return resposta.json()


def login_com_password(email: str, password: str) -> dict:
    """RF15 (UC13) — devolve idToken/refreshToken/expiresIn."""
    return _pedir(
        f"{_IDENTITY_TOOLKIT_URL}/accounts:signInWithPassword",
        params={"key": settings.firebase_web_api_key},
        json={"email": email, "password": password, "returnSecureToken": True},
    )


def criar_conta_com_password(email: str, password: str) -> dict:
    """Cria a conta Firebase (email/senha) e já devolve idToken/refreshToken."""
    return _pedir(
        f"{_IDENTITY_TOOLKIT_URL}/accounts:signUp",
        params={"key": settings.firebase_web_api_key},
        json={"email": email, "password": password, "returnSecureToken": True},
    )


def renovar_token(refresh_token: str) -> dict:
    """RF15 — troca um refreshToken por um novo idToken (a chamada `grant_type=refresh_token`
    do Secure Token API devolve `id_token`/`refresh_token` em snake_case, ao contrário do
    Identity Toolkit — normalizado aqui para o mesmo formato camelCase dos outros métodos."""
    corpo = _pedir(
        _SECURE_TOKEN_URL,
        params={"key": settings.firebase_web_api_key},
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )
    return {
        "idToken": corpo["id_token"],
        "refreshToken": corpo["refresh_token"],
        "expiresIn": corpo["expires_in"],
    }


def enviar_email_recuperacao_password(email: str) -> None:
    """RF16 (UC14) — dispara o email de reset nativo do Firebase."""
    _pedir(
        f"{_IDENTITY_TOOLKIT_URL}/accounts:sendOobCode",
        params={"key": settings.firebase_web_api_key},
        json={"requestType": "PASSWORD_RESET", "email": email},
    )


def login_com_google(google_id_token: str) -> dict:
    """RF15 — troca um Google ID Token (obtido no cliente via Google Sign-In nativo)
    por uma sessão Firebase. O Google ID Token é validado pelo próprio Firebase."""
    return _pedir(
        f"{_IDENTITY_TOOLKIT_URL}/accounts:signInWithIdp",
        params={"key": settings.firebase_web_api_key},
        json={
            "postBody": f"id_token={google_id_token}&providerId=google.com",
            "requestUri": settings.google_login_request_uri,
            "returnSecureToken": True,
        },
    )
