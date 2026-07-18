# Implementa: RF13 (UC09) — persistência de SolverResult.pendencias (ver app/solver/dto.py)
#
# Entidade de output — resultado do solver persistido, tal como Alocacao. Um Job pode
# terminar DONE (ou até INFEASIBLE por timeout, ver sub-projeto "solver nunca INFEASIBLE")
# com pendências: (turma, disciplina) que ficaram com tempos por preencher. Guardadas
# aqui para o Gestor consultar depois e resolver por alocação manual.
from sqlmodel import Field, SQLModel


class Pendencia(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="job.id", index=True)
    turma_id: int = Field(foreign_key="turma.id")
    disciplina_id: int = Field(foreign_key="disciplina.id")
    tempos_em_falta: int
    razao: str
    # CSV de IDs — nunca uma tabela associativa extra só para auditoria textual;
    # estes campos existem apenas para a UI destacar turmas/professores relacionados
    # na razão, nunca para queries relacionais (ver PendenciaDTO em app/solver/dto.py).
    professores_conflitantes: str = ""
    turmas_conflitantes: str = ""
