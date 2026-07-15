from app.models.alocacao import Alocacao
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.disponibilidade import Disponibilidade
from app.models.job import Job, JobStatus
from app.models.professor import Professor
from app.models.professor_disciplina import ProfessorDisciplina
from app.models.sala import Sala
from app.models.slot import Slot
from app.models.turma import Turma
from app.models.turma_disciplina import TurmaDisciplina

__all__ = [
    "Alocacao",
    "Curso",
    "Disciplina",
    "Disponibilidade",
    "Job",
    "JobStatus",
    "Professor",
    "ProfessorDisciplina",
    "Sala",
    "Slot",
    "Turma",
    "TurmaDisciplina",
]
