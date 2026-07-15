# Implementa: RF02 (UC02) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import select

from app.models.turma import Turma
from app.repositories.base import BaseRepository


class TurmaRepository(BaseRepository[Turma]):
    model = Turma

    def get_by_codigo(self, codigo: str) -> Turma | None:
        return self.session.exec(select(Turma).where(Turma.codigo == codigo)).first()
