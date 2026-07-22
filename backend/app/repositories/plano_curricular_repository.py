# Implementa: RF02 (UC02) — ver docs/relatorio/04_analise_desenvolvimento/
from sqlmodel import select

from app.models.plano_curricular import PlanoCurricular
from app.repositories.base import BaseRepository


class PlanoCurricularRepository(BaseRepository[PlanoCurricular]):
    model = PlanoCurricular

    def get_by_curso_ano_semestre(self, curso_id: int, ano: int, semestre: str) -> PlanoCurricular | None:
        return self.session.exec(
            select(PlanoCurricular).where(
                PlanoCurricular.curso_id == curso_id,
                PlanoCurricular.ano == ano,
                PlanoCurricular.semestre == semestre,
            )
        ).first()
