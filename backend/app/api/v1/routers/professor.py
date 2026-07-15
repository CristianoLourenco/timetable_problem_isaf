# Implementa: RF01 (UC01) — ver docs/analise_requisitos_v5.0.md
from app.api.v1.routers.factory import build_crud_router
from app.models.professor import Professor
from app.repositories.professor_repository import ProfessorRepository
from app.schemas.professor_schema import ProfessorCreate, ProfessorRead, ProfessorUpdate

router = build_crud_router(
    prefix="/professores",
    tags=["Professores"],
    model=Professor,
    create_schema=ProfessorCreate,
    update_schema=ProfessorUpdate,
    read_schema=ProfessorRead,
    repository_cls=ProfessorRepository,
)
