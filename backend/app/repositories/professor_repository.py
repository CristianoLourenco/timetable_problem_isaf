# Implementa: RF01 (UC01) — ver docs/analise_requisitos_v5.0.md
from sqlmodel import select

from app.models.professor import Professor
from app.repositories.base import BaseRepository


class ProfessorRepository(BaseRepository[Professor]):
    model = Professor

    def get_by_email(self, email: str) -> Professor | None:
        return self.session.exec(select(Professor).where(Professor.email == email)).first()
