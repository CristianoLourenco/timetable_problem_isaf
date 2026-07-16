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


class MeResponseSchema(SQLModel):
    """GET /auth/me — o frontend usa isto após o login para saber o papel (RN09-RN11) e,
    se for Professor, o professor_id (necessário para "o meu horário", "a minha disponibilidade")."""

    email: str
    papel: str
    professor_id: int | None
    nome: str | None = None
    """Nome do Professor (Professor.nome), quando papel=PROFESSOR. O Gestor não tem
    nome próprio no modelo actual (Utilizador só guarda email) — fica None."""
