# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from sqlmodel import Session, delete, select

from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina


class PlanoCurricularDisciplinaRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_por_plano(self, plano_curricular_id: int) -> list[PlanoCurricularDisciplina]:
        return list(
            self.session.exec(
                select(PlanoCurricularDisciplina).where(
                    PlanoCurricularDisciplina.plano_curricular_id == plano_curricular_id
                )
            )
        )

    def listar_todas(self) -> list[PlanoCurricularDisciplina]:
        return list(self.session.exec(select(PlanoCurricularDisciplina)))

    def substituir(self, plano_curricular_id: int, itens: list[tuple[int, int]]) -> None:
        self.session.exec(
            delete(PlanoCurricularDisciplina).where(
                PlanoCurricularDisciplina.plano_curricular_id == plano_curricular_id
            )
        )
        for disciplina_id, carga_horaria_semanal in itens:
            self.session.add(
                PlanoCurricularDisciplina(
                    plano_curricular_id=plano_curricular_id,
                    disciplina_id=disciplina_id,
                    carga_horaria_semanal=carga_horaria_semanal,
                )
            )
        self.session.commit()

    def existe(self, plano_curricular_id: int, disciplina_id: int) -> bool:
        return (
            self.session.exec(
                select(PlanoCurricularDisciplina).where(
                    PlanoCurricularDisciplina.plano_curricular_id == plano_curricular_id,
                    PlanoCurricularDisciplina.disciplina_id == disciplina_id,
                )
            ).first()
            is not None
        )

    def adicionar(self, plano_curricular_id: int, disciplina_id: int, carga_horaria_semanal: int) -> None:
        """Insere um item sem apagar os já existentes — usado pela importação em
        massa (RF06/RF08), que é aditiva e idempotente por par, ao contrário de
        `substituir` (usado pelo diálogo manual, que troca o plano todo)."""
        self.session.add(
            PlanoCurricularDisciplina(
                plano_curricular_id=plano_curricular_id,
                disciplina_id=disciplina_id,
                carga_horaria_semanal=carga_horaria_semanal,
            )
        )
        self.session.commit()
