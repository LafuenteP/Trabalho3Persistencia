from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr

# 1. Modelo auxiliar para o Endereço (Será embutido no Cliente)
class Endereco(BaseModel):
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str

# 2. O Documento Principal do Cliente
class Cliente(Document):
    nome: str
    # Indexed(..., unique=True) garante que o MongoDB não aceite dois clientes com mesmo email
    email: Indexed(str, unique=True) # type: ignore
    cpf: Indexed(str, unique=True)   # type: ignore
    
    # O endereço é opcional na criação, mas se vier, segue a estrutura da classe Endereco
    endereco: Optional[Endereco] = None

    class Settings:
        name = "clientes"  # Nome da coleção no MongoDB
