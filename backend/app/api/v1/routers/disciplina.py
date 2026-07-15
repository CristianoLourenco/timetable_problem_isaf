# Implementa: RF03 (UC03) — ver docs/analise_requisitos_v5.0.md
from app.api.v1.routers.factory import build_crud_router
from app.models.disciplina import Disciplina
from app.repositories.disciplina_repository import DisciplinaRepository
from app.schemas.disciplina_schema import DisciplinaCreate, DisciplinaRead, DisciplinaUpdate

router = build_crud_router(
    prefix="/disciplinas",
    tags=["Disciplinas"],
    model=Disciplina,
    create_schema=DisciplinaCreate,
    update_schema=DisciplinaUpdate,
    read_schema=DisciplinaRead,
    repository_cls=DisciplinaRepository,
)
