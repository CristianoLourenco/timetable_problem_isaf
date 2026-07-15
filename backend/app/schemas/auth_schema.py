# Implementa: RF15, RF16 (UC13, UC14) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel

from app.schemas.utilizador_schema import UtilizadorRead


class LoginSchema(SQLModel):
    email: str
    password: str


class RefreshTokenSchema(SQLModel):
    refresh_token: str


class LoginGoogleSchema(SQLModel):
    google_id_token: str


class RecuperarPasswordSchema(SQLModel):
    email: str


class TokenResponseSchema(SQLModel):
    id_token: str
    refresh_token: str
    expires_in: int


class RegistoProfessorSchema(SQLModel):
    """Auto-registo do Professor — cria a conta Firebase e associa ao registo do Gestor (RN10)."""

    email: str
    password: str
    contacto_telefonico: str


class RegistoResponseSchema(SQLModel):
    """Devolvida após registo (Professor ou Gestor) — já inclui sessão, sem exigir login extra."""

    id_token: str
    refresh_token: str
    expires_in: int
    utilizador: UtilizadorRead
