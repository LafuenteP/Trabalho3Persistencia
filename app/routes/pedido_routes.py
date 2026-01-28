from fastapi import APIRouter, HTTPException, status, Query
from beanie import PydanticObjectId, WriteRules
import math

from app.models.pedido import Pedido, ItemPedido
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.schemas.pedido import PedidoCreate, PedidoResponse, PedidoUpdate, PaginatedResponse

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
    
    # O pedido já tem os objetos carregados, retorna diretamente
    return novo_pedido


@router.get("/", response_model=PaginatedResponse[PedidoResponse])
async def listar_pedidos(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """Lista todos os pedidos com paginação e eager loading dos relacionamentos."""
    # Conta total de documentos
    total_items = await Pedido.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    # Calcula o skip para a paginação
    skip = (page - 1) * page_size
    
    # Busca pedidos com paginação e fetch_links=True para eager loading
    pedidos = await Pedido.find_all(fetch_links=True).skip(skip).limit(page_size).to_list()
    
    return PaginatedResponse(
        items=pedidos,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )


@router.get("/{id}", response_model=PedidoResponse)
async def obter_pedido(id: PydanticObjectId):
    """Obtém um pedido pelo ID com eager loading dos relacionamentos."""
    # Usa fetch_links=True para carregar cliente e produtos automaticamente
    pedido = await Pedido.get(id, fetch_links=True)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return pedido


@router.get("/cliente/{cliente_id}", response_model=PaginatedResponse[PedidoResponse])
async def listar_pedidos_por_cliente(
    cliente_id: PydanticObjectId,
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """Lista todos os pedidos de um cliente específico com paginação e eager loading."""
    cliente = await Cliente.get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Conta total de pedidos do cliente
    total_items = await Pedido.find(Pedido.cliente.id == cliente_id).count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    # Calcula o skip para a paginação
    skip = (page - 1) * page_size
    
    # Busca com paginação e fetch_links=True para eager loading
    pedidos = await Pedido.find(
        Pedido.cliente.id == cliente_id,
        fetch_links=True
    ).skip(skip).limit(page_size).to_list()
    
    return PaginatedResponse(
        items=pedidos,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )


@router.put("/{id}", response_model=PedidoResponse)
async def atualizar_pedido(id: PydanticObjectId, dados: PedidoUpdate):
    """Atualiza um pedido existente (status e/ou itens)."""
    pedido = await Pedido.get(id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Atualiza o status se fornecido
    if dados.status is not None:
        status_validos = ["PENDENTE", "PROCESSANDO", "ENVIADO", "ENTREGUE", "CANCELADO"]
        if dados.status.upper() not in status_validos:
            raise HTTPException(
                status_code=400, 
                detail=f"Status inválido. Valores permitidos: {status_validos}"
            )
        pedido.status = dados.status.upper()
    
    # Atualiza os itens se fornecidos
    if dados.itens is not None:
        itens_processados = []
        valor_total_calculado = 0.0
        
        for item_input in dados.itens:
            produto_db = await Produto.get(item_input.produto_id)
            
            if not produto_db:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Produto {item_input.produto_id} não encontrado"
                )
            
            novo_item = ItemPedido(
                produto=produto_db,
                quantidade=item_input.quantidade,
                preco_unitario=produto_db.preco
            )
            
            itens_processados.append(novo_item)
            valor_total_calculado += (produto_db.preco * item_input.quantidade)
        
        pedido.itens = itens_processados
        pedido.valor_total = valor_total_calculado
    
    await pedido.save(link_rule=WriteRules.WRITE)
    
    # Recarrega o pedido com fetch_links=True para eager loading
    pedido_atualizado = await Pedido.get(id, fetch_links=True)
    return pedido_atualizado


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_pedido(id: PydanticObjectId):
    """Remove um pedido do banco."""
    pedido = await Pedido.get(id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    await pedido.delete()
    return None
