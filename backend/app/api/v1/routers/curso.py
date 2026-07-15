# Entidade de suporte (sem RF próprio) — necessária para Turma.curso_id (RF02)
from app.api.v1.routers.factory import build_crud_router
from app.models.curso import Curso
from app.repositories.curso_repository import CursoRepository
from app.schemas.curso_schema import CursoCreate, CursoRead, CursoUpdate

router = build_crud_router(
    prefix="/cursos",
    tags=["Cursos"],
    model=Curso,
    create_schema=CursoCreate,
    update_schema=CursoUpdate,
    read_schema=CursoRead,
    repository_cls=CursoRepository,
)
