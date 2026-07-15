# Implementa: RN09, RN10 (UC13, UC15) — ver docs/analise_requisitos_v5.0.md
#
# Superadmin NÃO tem registo aqui — é uma lista de bootstrap em Settings
# (ver core/security.py). Esta tabela guarda apenas Gestores (perfil=GESTOR,
# criados exclusivamente pelo Superadmin) e Professores que já completaram o
# próprio registo (perfil=PROFESSOR, RN10 valida contra Professor.email).
from enum import StrEnum

from sqlmodel import Field, SQLModel


class PerfilUtilizador(StrEnum):
    GESTOR = "GESTOR"
    PROFESSOR = "PROFESSOR"


class Utilizador(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    contacto_telefonico: str
    perfil: PerfilUtilizador
    professor_id: int | None = Field(default=None, foreign_key="professor.id")  # nulo quando perfil=GESTOR
