from datetime import datetime
from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from typing import Generic, TypeVar

# Precisamos importar os schemas de Cliente e Produto para aninhar na resposta
from app.schemas.cliente import ClienteResponse
from app.schemas.produto import ProdutoResponse

# --- INPUTS (O que o usuário envia) ---

class ItemPedidoCreate(BaseModel):
    produto_id: PydanticObjectId
    quantidade: int = Field(gt=0, description="Quantidade de itens")

class PedidoCreate(BaseModel):
    cliente_id: PydanticObjectId
    itens: list[ItemPedidoCreate]

class PedidoUpdate(BaseModel):
    """Schema para atualização de pedido."""
    status: str | None = Field(None, description="Status do pedido (PENDENTE, PROCESSANDO, ENVIADO, ENTREGUE, CANCELADO)")
    itens: list[ItemPedidoCreate] | None = Field(None, description="Lista de itens atualizada")

# --- OUTPUTS (O que a API devolve) ---

class ItemPedidoResponse(BaseModel):
    # Aqui usamos o ProdutoResponse para mostrar detalhes do produto (nome, etc)
    # ou podemos devolver apenas o ID se preferir. Vamos mostrar detalhes:
    produto: ProdutoResponse | None = None 
    quantidade: int
    preco_unitario: float # Preço histórico (do momento da compra)

class PedidoResponse(BaseModel):
    id: PydanticObjectId
    data_emissao: datetime
    status: str
    valor_total: float
    
    # Aqui está o truque para o Req A:
    # Se carregarmos o link, o Beanie preenche este campo.
    cliente: ClienteResponse | None = None
    
    itens: list[ItemPedidoResponse]

# --- PAGINAÇÃO ---
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico para respostas paginadas."""
    items: list[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int