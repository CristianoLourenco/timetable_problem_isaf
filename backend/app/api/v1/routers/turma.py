# Implementa: RF02 (UC02) — ver docs/analise_requisitos_v5.0.md
from app.api.v1.routers.factory import build_crud_router
from app.models.turma import Turma
from app.repositories.turma_repository import TurmaRepository
from app.schemas.turma_schema import TurmaCreate, TurmaRead, TurmaUpdate

router = build_crud_router(
    prefix="/turmas",
    tags=["Turmas"],
    model=Turma,
    create_schema=TurmaCreate,
    update_schema=TurmaUpdate,
    read_schema=TurmaRead,
    repository_cls=TurmaRepository,
)
