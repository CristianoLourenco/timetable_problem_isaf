from app.models.alocacao import Alocacao
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.disponibilidade import Disponibilidade
from app.models.job import Job, JobStatus
from app.models.plano_curricular import PlanoCurricular
from app.models.plano_curricular_disciplina import PlanoCurricularDisciplina
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.turma import Turma
from app.models.utilizador import PerfilUtilizador, Utilizador

__all__ = [
    "Alocacao",
    "Curso",
    "Disciplina",
    "Disponibilidade",
    "Job",
    "JobStatus",
    "PerfilUtilizador",
    "PlanoCurricular",
    "PlanoCurricularDisciplina",
    "Professor",
    "ProfessorDisciplina",
    "Sala",
    "Turma",
    "Utilizador",
]
