from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr

class Endereco(BaseModel):
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str

class Cliente(Document):
    nome: str
    email: Indexed(str, unique=True) # type: ignore
    cpf: Indexed(str, unique=True)   # type: ignore
    endereco: Endereco | None = None

    class Settings:
        name = "clientes"
