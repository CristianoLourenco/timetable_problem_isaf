# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from collections import defaultdict

from sqlmodel import Session, delete, select

from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.turma import Turma


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

    def listar_turnos_por_disciplina(self, disciplina_ids: list[int]) -> dict[int, set[str]]:
        """Turnos em que cada disciplina realmente decorre, via as turmas das suas
        PlanoCurricularDisciplina — usado por disponibilidade_geracao_service.py
        para fundamentar a disponibilidade sintética nas qualificações reais do
        professor, nunca em turnos que ele nunca teria motivo para lecionar."""
        if not disciplina_ids:
            return {}
        linhas = self.session.exec(
            select(PlanoCurricularDisciplina.disciplina_id, Turma.turno)
            .join(Turma, Turma.plano_curricular_id == PlanoCurricularDisciplina.plano_curricular_id)
            .where(PlanoCurricularDisciplina.disciplina_id.in_(disciplina_ids))
        )
        turnos_por_disciplina: dict[int, set[str]] = defaultdict(set)
        for disciplina_id, turno in linhas:
            turnos_por_disciplina[disciplina_id].add(str(turno))
        return dict(turnos_por_disciplina)
