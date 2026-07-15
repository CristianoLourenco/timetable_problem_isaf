# Implementa: RF03 (UC03) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import select

from app.models.disciplina import Disciplina
from app.repositories.base import BaseRepository


class DisciplinaRepository(BaseRepository[Disciplina]):
    model = Disciplina

    def get_by_codigo(self, codigo: str) -> Disciplina | None:
        return self.session.exec(select(Disciplina).where(Disciplina.codigo == codigo)).first()
