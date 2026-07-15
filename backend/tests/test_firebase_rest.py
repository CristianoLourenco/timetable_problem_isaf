# Implementa: RF15, RF16 — cliente REST do Firebase Authentication (sem rede real)
import pytest

from app.core import firebase_rest
from app.core.firebase_rest import FirebaseAuthError


class _RespostaFake:
    def __init__(self, status_code: int, corpo: dict):
        self.status_code = status_code
        self._corpo = corpo

    def json(self) -> dict:
        return self._corpo


def test_login_com_password_sucesso(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(200, {"idToken": "tok", "refreshToken": "refresh", "expiresIn": "3600"}),
    )
    resultado = firebase_rest.login_com_password("prof@isaf.co.ao", "palavra-passe")
    assert resultado["idToken"] == "tok"


def test_login_com_password_credenciais_invalidas(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(400, {"error": {"message": "INVALID_LOGIN_CREDENTIALS"}}),
    )
    with pytest.raises(FirebaseAuthError) as exc_info:
        firebase_rest.login_com_password("prof@isaf.co.ao", "errada")
    assert exc_info.value.status_http == 401


def test_renovar_token_normaliza_snake_case_para_camel_case(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(200, {"id_token": "novo-tok", "refresh_token": "novo-refresh", "expires_in": "3600"}),
    )
    resultado = firebase_rest.renovar_token("refresh-antigo")
    assert resultado == {"idToken": "novo-tok", "refreshToken": "novo-refresh", "expiresIn": "3600"}


def test_renovar_token_refresh_invalido(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(400, {"error": {"message": "INVALID_REFRESH_TOKEN"}}),
    )
    with pytest.raises(FirebaseAuthError):
        firebase_rest.renovar_token("invalido")


def test_criar_conta_com_password_email_existente(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(400, {"error": {"message": "EMAIL_EXISTS"}}),
    )
    with pytest.raises(FirebaseAuthError) as exc_info:
        firebase_rest.criar_conta_com_password("ja.existe@isaf.co.ao", "palavra-passe")
    assert exc_info.value.status_http == 409


def test_weak_password_normaliza_codigo_com_sufixo_descritivo(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(
            400, {"error": {"message": "WEAK_PASSWORD : Password should be at least 6 characters"}}
        ),
    )
    with pytest.raises(FirebaseAuthError) as exc_info:
        firebase_rest.criar_conta_com_password("novo@isaf.co.ao", "123")
    assert exc_info.value.codigo == "WEAK_PASSWORD"
    assert exc_info.value.status_http == 400


def test_enviar_email_recuperacao_password_sucesso(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda url, **k: chamadas.append(url) or _RespostaFake(200, {"email": "prof@isaf.co.ao"}),
    )
    firebase_rest.enviar_email_recuperacao_password("prof@isaf.co.ao")
    assert chamadas[0].endswith("accounts:sendOobCode")


def test_login_com_google_sucesso(monkeypatch):
    monkeypatch.setattr(
        firebase_rest.httpx,
        "post",
        lambda *a, **k: _RespostaFake(200, {"idToken": "tok-google", "refreshToken": "refresh-google", "expiresIn": "3600"}),
    )
    resultado = firebase_rest.login_com_google("google-id-token-qualquer")
    assert resultado["idToken"] == "tok-google"
