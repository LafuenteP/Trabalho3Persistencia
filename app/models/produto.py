from beanie import Document, Indexed
from pydantic import Field
from pymongo import TEXT

class Produto(Document):
    nome: Indexed(str) # type: ignore
    descricao: str | None = None
    preco: float = Field(gt=0)
    categoria: str
    estoque: int = Field(default=0, ge=0)

    class Settings:
        name = "produtos"
        indexes = [
            [("nome", TEXT), ("descricao", TEXT)],
        ]