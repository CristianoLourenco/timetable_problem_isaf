from sqlmodel import Field, SQLModel


class Curso(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nome: str
