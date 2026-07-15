from sqlmodel import SQLModel


class CursoBase(SQLModel):
    codigo: str
    nome: str


class CursoCreate(CursoBase):
    pass


class CursoUpdate(SQLModel):
    codigo: str | None = None
    nome: str | None = None


class CursoRead(CursoBase):
    id: int
