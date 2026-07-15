# Implementa: RN09, RN10 — ver docs/analise_requisitos_v5.0.md
from sqlmodel import select

from app.models.utilizador import Utilizador
from app.repositories.base import BaseRepository


class UtilizadorRepository(BaseRepository[Utilizador]):
    model = Utilizador

    def get_by_email(self, email: str) -> Utilizador | None:
        return self.session.exec(select(Utilizador).where(Utilizador.email == email)).first()
