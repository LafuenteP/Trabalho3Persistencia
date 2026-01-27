from pydantic import BaseModel, Field
from beanie import PydanticObjectId

# --- O QUE JÁ EXISTIA ---
class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=2, example="Teclado Mecânico")
    descricao: str | None = Field(None, example="Switch Blue, RGB")
    preco: float = Field(..., gt=0, example=150.00)
    categoria: str = Field(..., example="Periféricos")
    estoque: int = Field(default=0, ge=0)

class ProdutoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    preco: float | None = None
    categoria: str | None = None
    estoque: int | None = None

# --- O QUE ESTAVA FALTANDO (Adicione isto) ---
class ProdutoResponse(BaseModel):
    id: PydanticObjectId
    nome: str
    preco: float
    categoria: str
    descricao: str | None = None