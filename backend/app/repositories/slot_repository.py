# Corresponde ao conjunto formal T da definição UCTP — ver docs/06_arquitetura_backend.md
from app.models.slot import Slot
from app.repositories.base import BaseRepository


class SlotRepository(BaseRepository[Slot]):
    model = Slot
