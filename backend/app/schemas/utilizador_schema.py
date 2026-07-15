# Implementa: RN09, RN10 — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel

from app.models.utilizador import PerfilUtilizador


class UtilizadorGestorCreate(SQLModel):
    """Só o Superadmin invoca isto — cria um novo Gestor (ver core/security.py)."""

    email: str
    contacto_telefonico: str


class RegistoProfessorSchema(SQLModel):
    """Auto-registo do Professor — o email vem do ID Token, não deste payload."""

    contacto_telefonico: str


class UtilizadorRead(SQLModel):
    id: int
    email: str
    contacto_telefonico: str
    perfil: PerfilUtilizador
    professor_id: int | None
