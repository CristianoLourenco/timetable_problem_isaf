from typing import Any, Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from app.core.exceptions import IntegridadeVioladaError

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """CRUD puro sobre um model SQLModel — sem lógica de negócio (ver backend/CLAUDE.md)."""

    model: type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def create(self, obj_in: ModelType) -> ModelType:
        self.session.add(obj_in)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise IntegridadeVioladaError from exc
        self.session.refresh(obj_in)
        return obj_in

    def get(self, id_: Any) -> ModelType | None:
        return self.session.get(self.model, id_)

    def list(self) -> list[ModelType]:
        return list(self.session.exec(select(self.model)))

    def update(self, db_obj: ModelType, data: dict[str, Any]) -> ModelType:
        for campo, valor in data.items():
            setattr(db_obj, campo, valor)
        self.session.add(db_obj)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise IntegridadeVioladaError from exc
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        self.session.delete(db_obj)
        self.session.commit()
