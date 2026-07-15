# Implementa: RF04 (UC04) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import select

from app.models.sala import Sala
from app.repositories.base import BaseRepository


class SalaRepository(BaseRepository[Sala]):
    model = Sala

    def get_by_codigo(self, codigo: str) -> Sala | None:
        return self.session.exec(select(Sala).where(Sala.codigo == codigo)).first()
