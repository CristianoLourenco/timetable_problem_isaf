# Grade curricular — corresponde ao conjunto de eventos E da definição formal UCTP
from sqlmodel import Field, SQLModel


class TurmaDisciplina(SQLModel, table=True):
    turma_id: int = Field(foreign_key="turma.id", primary_key=True)
    disciplina_id: int = Field(foreign_key="disciplina.id", primary_key=True)
    carga_horaria_semanal: int  # nº de tempos/semana — usado em RN05 e RN06
