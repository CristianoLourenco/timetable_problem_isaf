# Implementa: RN09, RN10 (UC13) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import Session

from app.core.exceptions import AcessoNegadoError, EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.models.utilizador import PerfilUtilizador, Utilizador
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.utilizador_repository import UtilizadorRepository


class UtilizadorService:
    def __init__(self, session: Session):
        self.utilizador_repo = UtilizadorRepository(session)
        self.professor_repo = ProfessorRepository(session)

    def listar(self) -> list[Utilizador]:
        return self.utilizador_repo.list()

    def criar_gestor(self, email: str, contacto_telefonico: str) -> Utilizador:
        """Só o Superadmin invoca isto (garantido por core.security.require_superadmin)."""
        if self.utilizador_repo.get_by_email(email) is not None:
            raise IntegridadeVioladaError("Já existe um utilizador registado com este email.")

        return self.utilizador_repo.create(
            Utilizador(email=email, contacto_telefonico=contacto_telefonico, perfil=PerfilUtilizador.GESTOR)
        )

    def remover(self, utilizador_id: int) -> None:
        obj = self.utilizador_repo.get(utilizador_id)
        if obj is None:
            raise EntidadeNaoEncontradaError("Utilizador não encontrado.")
        self.utilizador_repo.delete(obj)

    def registar_professor(self, email: str, contacto_telefonico: str) -> Utilizador:
        """RN10 — só completa o registo se o email já corresponder a um Professor
        registado pelo Gestor (RF01); o Professor cria a própria conta Firebase antes
        disto, este passo apenas liga essa conta ao registo já existente."""
        if self.utilizador_repo.get_by_email(email) is not None:
            raise IntegridadeVioladaError("Esta conta já está registada.")

        professor = self.professor_repo.get_by_email(email)
        if professor is None:
            raise AcessoNegadoError("Este email não corresponde a nenhum Professor registado pelo Gestor.")

        return self.utilizador_repo.create(
            Utilizador(
                email=email,
                contacto_telefonico=contacto_telefonico,
                perfil=PerfilUtilizador.PROFESSOR,
                professor_id=professor.id,
            )
        )
