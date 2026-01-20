from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId

# 1. Schema para o Endereço (Reutilizável)
class EnderecoSchema(BaseModel):
    rua: str = Field(..., min_length=3, description="Nome da rua")
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str

# 2. Schema Base (Campos partilhados entre criação e leitura)
class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=2, description="Nome completo do cliente")
    email: EmailStr  # Valida automaticamente se o formato é user@dominio.com
    cpf: str = Field(..., description="CPF do cliente")
    endereco: Optional[EnderecoSchema] = None

# 3. Schema para Criação (Input do POST)
class ClienteCreate(ClienteBase):
    pass  # Herda tudo de ClienteBase obrigando os campos a existirem

# 4. Schema para Atualização (Input do PUT/PATCH)
# Aqui tudo é opcional, pois o utilizador pode querer mudar apenas o nome
class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    endereco: Optional[EnderecoSchema] = None

# 5. Schema para Resposta (Output do GET)
class ClienteResponse(ClienteBase):
    id: PydanticObjectId  # O ID do MongoDB é adicionado aqui
