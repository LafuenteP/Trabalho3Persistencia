from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

# Precisamos importar os schemas de Cliente e Produto para aninhar na resposta
from app.schemas.cliente import ClienteResponse
from app.schemas.produto import ProdutoResponse

# --- INPUTS (O que o usuário envia) ---

class ItemPedidoCreate(BaseModel):
    produto_id: PydanticObjectId
    quantidade: int = Field(gt=0, description="Quantidade de itens")

class PedidoCreate(BaseModel):
    cliente_id: PydanticObjectId
    itens: List[ItemPedidoCreate]

# --- OUTPUTS (O que a API devolve) ---

class ItemPedidoResponse(BaseModel):
    # Aqui usamos o ProdutoResponse para mostrar detalhes do produto (nome, etc)
    # ou podemos devolver apenas o ID se preferir. Vamos mostrar detalhes:
    produto: Optional[ProdutoResponse] = None 
    quantidade: int
    preco_unitario: float # Preço histórico (do momento da compra)

class PedidoResponse(BaseModel):
    id: PydanticObjectId
    data_emissao: datetime
    status: str
    valor_total: float
    
    # Aqui está o truque para o Req A:
    # Se carregarmos o link, o Beanie preenche este campo.
    cliente: Optional[ClienteResponse] = None
    
    itens: List[ItemPedidoResponse]