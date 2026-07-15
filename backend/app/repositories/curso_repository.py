from sqlmodel import select

from app.models.curso import Curso
from app.repositories.base import BaseRepository


class CursoRepository(BaseRepository[Curso]):
    model = Curso

    def get_by_codigo(self, codigo: str) -> Curso | None:
        return self.session.exec(select(Curso).where(Curso.codigo == codigo)).first()
