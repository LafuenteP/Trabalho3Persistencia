from datetime import datetime
from beanie import Document, Link
from pydantic import BaseModel, Field

from app.models.cliente import Cliente
from app.models.produto import Produto

class ItemPedido(BaseModel):
    produto: Link[Produto]
    quantidade: int = Field(gt=0)
    preco_unitario: float = Field(gt=0)

class Pedido(Document):
    cliente: Link[Cliente]
    data_emissao: datetime = Field(default_factory=datetime.now)
    itens: list[ItemPedido]
    status: str = Field(default="PENDENTE")
    valor_total: float = 0.0

    class Settings:
        name = "pedidos"