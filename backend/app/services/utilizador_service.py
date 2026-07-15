# Implementa: RN09, RN10 (UC13) — ver docs/analise_requisitos_v5.0.md
from dataclasses import dataclass

from sqlmodel import Session

from app.core import firebase_rest
from app.core.exceptions import AcessoNegadoError, EntidadeNaoEncontradaError, IntegridadeVioladaError
from app.models.utilizador import PerfilUtilizador, Utilizador
from app.repositories.professor_repository import ProfessorRepository
from app.repositories.utilizador_repository import UtilizadorRepository


@dataclass(frozen=True)
class SessaoCriada:
    """Utilizador recém-criado + tokens da sessão Firebase já aberta (evita um login extra)."""

    utilizador: Utilizador
    id_token: str
    refresh_token: str
    expires_in: int


class UtilizadorService:
    def __init__(self, session: Session):
        self.utilizador_repo = UtilizadorRepository(session)
        self.professor_repo = ProfessorRepository(session)

    def listar(self) -> list[Utilizador]:
        return self.utilizador_repo.list()

    def criar_gestor(self, email: str, password: str, contacto_telefonico: str) -> SessaoCriada:
        """Só o Superadmin invoca isto (garantido por core.security.require_superadmin).

        Cria também a conta Firebase (email/senha) do novo Gestor — sem isto o Gestor
        nunca teria como criar a própria conta, já que o cliente não fala com o
        Firebase diretamente (ver core/firebase_rest.py).
        """
        if self.utilizador_repo.get_by_email(email) is not None:
            raise IntegridadeVioladaError("Já existe um utilizador registado com este email.")

        sessao_firebase = firebase_rest.criar_conta_com_password(email, password)

        utilizador = self.utilizador_repo.create(
            Utilizador(email=email, contacto_telefonico=contacto_telefonico, perfil=PerfilUtilizador.GESTOR)
        )
        return SessaoCriada(
            utilizador=utilizador,
            id_token=sessao_firebase["idToken"],
            refresh_token=sessao_firebase["refreshToken"],
            expires_in=int(sessao_firebase["expiresIn"]),
        )

    def remover(self, utilizador_id: int) -> None:
        obj = self.utilizador_repo.get(utilizador_id)
        if obj is None:
            raise EntidadeNaoEncontradaError("Utilizador não encontrado.")
        self.utilizador_repo.delete(obj)

    def registar_professor(self, email: str, password: str, contacto_telefonico: str) -> SessaoCriada:
        """RN10 — só cria a conta Firebase se o email já corresponder a um Professor
        registado pelo Gestor (RF01); valida ANTES de criar a conta, para nunca criar
        contas Firebase órfãs para quem não tem direito a aceder ao sistema."""
        if self.utilizador_repo.get_by_email(email) is not None:
            raise IntegridadeVioladaError("Esta conta já está registada.")

        professor = self.professor_repo.get_by_email(email)
        if professor is None:
            raise AcessoNegadoError("Este email não corresponde a nenhum Professor registado pelo Gestor.")

        sessao_firebase = firebase_rest.criar_conta_com_password(email, password)

        utilizador = self.utilizador_repo.create(
            Utilizador(
                email=email,
                contacto_telefonico=contacto_telefonico,
                perfil=PerfilUtilizador.PROFESSOR,
                professor_id=professor.id,
            )
        )
        return SessaoCriada(
            utilizador=utilizador,
            id_token=sessao_firebase["idToken"],
            refresh_token=sessao_firebase["refreshToken"],
            expires_in=int(sessao_firebase["expiresIn"]),
        )
