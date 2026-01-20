from pydantic import BaseModel, Field
from typing import Optional
from beanie import PydanticObjectId

# --- O QUE JÁ EXISTIA ---
class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=2, example="Teclado Mecânico")
    descricao: Optional[str] = Field(None, example="Switch Blue, RGB")
    preco: float = Field(..., gt=0, example=150.00)
    categoria: str = Field(..., example="Periféricos")
    estoque: int = Field(default=0, ge=0)

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    categoria: Optional[str] = None
    estoque: Optional[int] = None

# --- O QUE ESTAVA FALTANDO (Adicione isto) ---
class ProdutoResponse(BaseModel):
    id: PydanticObjectId
    nome: str
    preco: float
    categoria: str
    descricao: Optional[str] = None