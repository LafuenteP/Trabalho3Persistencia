from datetime import datetime
from beanie import Document, Link
from pydantic import BaseModel, Field

# Importamos os models para criar as referências
from app.models.cliente import Cliente
from app.models.produto import Produto

# 1. Modelo Auxiliar para os Itens do Pedido (Embedded)
# Isso resolve o N:N permitindo guardar "Quantidade" para cada Produto
class ItemPedido(BaseModel):
    produto: Link[Produto]  # Referência (Link) ao documento Produto
    quantidade: int = Field(gt=0, description="Quantidade comprada")
    preco_unitario: float = Field(gt=0, description="Preço congelado no momento da compra")

# 2. O Documento Principal do Pedido
class Pedido(Document):
    # Relacionamento 1:N -> Um pedido pertence a UM cliente
    # O Beanie guarda apenas o _id aqui, mas permite carregar o objeto todo depois
    cliente: Link[Cliente]
    
    # Data automática do servidor
    data_emissao: datetime = Field(default_factory=datetime.now)
    
    # Lista de itens (Relacionamento N:N com atributos extras)
    itens: list[ItemPedido]
    
    status: str = Field(default="PENDENTE") # Ex: PENDENTE, PAGO, CANCELADO
    valor_total: float = 0.0

    class Settings:
        name = "pedidos"