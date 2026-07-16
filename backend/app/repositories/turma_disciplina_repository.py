# Grade curricular — pré-requisito de dados do solver (conjunto E da definição formal UCTP)
from sqlmodel import Session, delete, select

from app.models.turma_disciplina import TurmaDisciplina


class TurmaDisciplinaRepository:
    def __init__(self, session: Session):
        self.session = session

    def listar_por_turma(self, turma_id: int) -> list[TurmaDisciplina]:
        return list(self.session.exec(select(TurmaDisciplina).where(TurmaDisciplina.turma_id == turma_id)))

    def listar_todas(self) -> list[TurmaDisciplina]:
        return list(self.session.exec(select(TurmaDisciplina)))

    def substituir(self, turma_id: int, itens: list[tuple[int, int]]) -> None:
        self.session.exec(delete(TurmaDisciplina).where(TurmaDisciplina.turma_id == turma_id))
        for disciplina_id, carga_horaria_semanal in itens:
            self.session.add(
                TurmaDisciplina(
                    turma_id=turma_id,
                    disciplina_id=disciplina_id,
                    carga_horaria_semanal=carga_horaria_semanal,
                )
            )
        self.session.commit()

    def existe(self, turma_id: int, disciplina_id: int) -> bool:
        return (
            self.session.exec(
                select(TurmaDisciplina).where(
                    TurmaDisciplina.turma_id == turma_id,
                    TurmaDisciplina.disciplina_id == disciplina_id,
                )
            ).first()
            is not None
        )

    def adicionar(self, turma_id: int, disciplina_id: int, carga_horaria_semanal: int) -> None:
        """Insere um item sem apagar os já existentes — usado pela importação
        em massa (RF06/RF08), que é aditiva e idempotente por par, ao contrário
        de `substituir` (usado pelo diálogo manual, que troca a grade toda)."""
        self.session.add(
            TurmaDisciplina(
                turma_id=turma_id,
                disciplina_id=disciplina_id,
                carga_horaria_semanal=carga_horaria_semanal,
            )
        )
        self.session.commit()
