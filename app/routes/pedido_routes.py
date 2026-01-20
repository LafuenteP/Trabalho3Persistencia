from typing import List
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId, WriteRules

from app.models.pedido import Pedido, ItemPedido
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.schemas.pedido import PedidoCreate, PedidoResponse

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def criar_pedido(dados: PedidoCreate):
    # 1. Validar e Buscar o Cliente
    cliente = await Cliente.get(dados.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    itens_processados = []
    valor_total_calculado = 0.0

    # 2. Processar cada item do pedido
    for item_input in dados.itens:
        produto_db = await Produto.get(item_input.produto_id)
        
        if not produto_db:
            raise HTTPException(status_code=404, detail=f"Produto {item_input.produto_id} não encontrado")
        
        # Opcional: Verificar estoque aqui (produto_db.estoque >= item_input.quantidade)

        # 3. Criar o ItemPedido com o preço ATUAL do produto
        # Note que não passamos o ID, passamos o objeto produto_db para o Link
        novo_item = ItemPedido(
            produto=produto_db,
            quantidade=item_input.quantidade,
            preco_unitario=produto_db.preco
        )
        
        itens_processados.append(novo_item)
        valor_total_calculado += (produto_db.preco * item_input.quantidade)

    # 4. Criar o Pedido
    novo_pedido = Pedido(
        cliente=cliente, # Passamos o objeto cliente (Link)
        itens=itens_processados,
        valor_total=valor_total_calculado,
        status="PENDENTE"
    )

    # 5. Salvar usando WriteRules.WRITE (Salva links se necessário, embora aqui já existam)
    await novo_pedido.insert(link_rule=WriteRules.WRITE)
    
    return novo_pedido

# --- REQUISITO A: Obter Pedido com dados do Cliente (Fetch Links) ---
@router.get("/{id}", response_model=PedidoResponse)
async def obter_pedido(id: PydanticObjectId):
    # O segredo está no fetch_links=True
    # Isso instrui o Beanie a ir na coleção 'clientes' e 'produtos' 
    # e preencher os objetos dentro do pedido automaticamente.
    pedido = await Pedido.get(id, fetch_links=True)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return pedido

# --- REQUISITO B: Listar Pedidos de um Cliente específico ---
@router.get("/cliente/{cliente_id}", response_model=List[PedidoResponse])
async def listar_pedidos_por_cliente(cliente_id: PydanticObjectId):
    # Verificamos se o cliente existe
    cliente = await Cliente.get(cliente_id)
    if not cliente:
         raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Filtramos onde o campo 'cliente.id' é igual ao ID fornecido
    # E usamos fetch_links=True para trazer os detalhes dos produtos também
    pedidos = await Pedido.find(Pedido.cliente.id == cliente_id, fetch_links=True).to_list()
    
    return pedidos
