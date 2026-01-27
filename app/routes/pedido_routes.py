from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId, WriteRules

from app.models.pedido import Pedido, ItemPedido
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.schemas.pedido import PedidoCreate, PedidoResponse

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def criar_pedido(dados: PedidoCreate):
    """Cria um novo pedido para um cliente."""
    cliente = await Cliente.get(dados.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    itens_processados = []
    valor_total_calculado = 0.0

    for item_input in dados.itens:
        produto_db = await Produto.get(item_input.produto_id)
        
        if not produto_db:
            raise HTTPException(status_code=404, detail=f"Produto {item_input.produto_id} não encontrado")

        novo_item = ItemPedido(
            produto=produto_db,
            quantidade=item_input.quantidade,
            preco_unitario=produto_db.preco
        )
        
        itens_processados.append(novo_item)
        valor_total_calculado += (produto_db.preco * item_input.quantidade)

    novo_pedido = Pedido(
        cliente=cliente,
        itens=itens_processados,
        valor_total=valor_total_calculado,
        status="PENDENTE"
    )

    await novo_pedido.insert(link_rule=WriteRules.WRITE)
    
    return novo_pedido

@router.get("/{id}", response_model=PedidoResponse)
async def obter_pedido(id: PydanticObjectId):
    """Obtém um pedido pelo ID, incluindo dados do cliente e produtos."""
    pedido = await Pedido.get(id, fetch_links=True)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return pedido

@router.get("/cliente/{cliente_id}", response_model=list[PedidoResponse])
async def listar_pedidos_por_cliente(cliente_id: PydanticObjectId):
    """Lista todos os pedidos de um cliente específico."""
    cliente = await Cliente.get(cliente_id)
    if not cliente:
         raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    pedidos = await Pedido.find(Pedido.cliente.id == cliente_id, fetch_links=True).to_list()
    
    return pedidos
