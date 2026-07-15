# Implementa: RN09, RN10 — ver docs/analise_requisitos_v5.0.md
from sqlmodel import SQLModel

from app.models.utilizador import PerfilUtilizador


class UtilizadorGestorCreate(SQLModel):
    """Só o Superadmin invoca isto — cria um novo Gestor (ver core/security.py).

    `password` cria a conta Firebase do Gestor no mesmo passo — o Gestor pode
    trocá-la depois via POST /auth/recuperar-password.
    """

    email: str
    password: str
    contacto_telefonico: str


class UtilizadorRead(SQLModel):
    id: int
    email: str
    contacto_telefonico: str
    perfil: PerfilUtilizador
    professor_id: int | None
