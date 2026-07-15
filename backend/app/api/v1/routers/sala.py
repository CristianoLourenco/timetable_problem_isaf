# Implementa: RF04 (UC04) — ver docs/analise_requisitos_v5.0.md
from app.api.v1.routers.factory import build_crud_router
from app.models.sala import Sala
from app.repositories.sala_repository import SalaRepository
from app.schemas.sala_schema import SalaCreate, SalaRead, SalaUpdate

router = build_crud_router(
    prefix="/salas",
    tags=["Salas"],
    model=Sala,
    create_schema=SalaCreate,
    update_schema=SalaUpdate,
    read_schema=SalaRead,
    repository_cls=SalaRepository,
)
