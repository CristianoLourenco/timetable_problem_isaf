# Implementa: RF02 (UC02) — disciplinas e carga horária semanal de um PlanoCurricular.
# Corresponde ao conjunto de eventos E da definição formal UCTP (ver skill
# ortools-timetabling-solver) — substitui TurmaDisciplina.carga_horaria_semanal.
from sqlmodel import Field, SQLModel


class PlanoCurricularDisciplina(SQLModel, table=True):
    plano_curricular_id: int = Field(foreign_key="planocurricular.id", primary_key=True)
    disciplina_id: int = Field(foreign_key="disciplina.id", primary_key=True)
    carga_horaria_semanal: int  # nº de tempos/semana — usado em RN05 e RN06
