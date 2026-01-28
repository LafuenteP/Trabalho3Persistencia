from fastapi import APIRouter, HTTPException, status, Query
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from app.schemas.pedido import PaginatedResponse
from beanie import PydanticObjectId
import math

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=Produto, status_code=status.HTTP_201_CREATED)
async def criar_produto(dados: ProdutoCreate):
    """Cria um novo produto."""
    novo_produto = Produto(**dados.model_dump())
    await novo_produto.insert()
    return novo_produto

@router.get("/", response_model=PaginatedResponse[Produto])
async def listar_produtos(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    termo: str | None = Query(None, description="Busca por nome"),
    categoria: str | None = Query(None, description="Filtro por categoria"),
    min_preco: float | None = Query(None, description="Preço mínimo", gt=0),
    max_preco: float | None = Query(None, description="Preço máximo", gt=0)
):
    """Lista produtos com filtros opcionais e paginação."""
    query = Produto.find_all()
    
    if termo:
        query = query.find({"nome": {"$regex": termo, "$options": "i"}})
    
    if categoria:
        query = query.find(Produto.categoria == categoria)

    if min_preco:
        query = query.find(Produto.preco >= min_preco)
    
    if max_preco:
        query = query.find(Produto.preco <= max_preco)
    
    # Conta total de documentos que correspondem aos filtros
    total_items = await query.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    # Calcula o skip para a paginação
    skip = (page - 1) * page_size
    
    # Aplica paginação
    produtos = await query.skip(skip).limit(page_size).to_list()
    
    return PaginatedResponse(
        items=produtos,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )

@router.get("/{id}", response_model=Produto)
async def obter_produto(id: PydanticObjectId):
    """Busca um produto pelo ID."""
    produto = await Produto.get(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@router.put("/{id}", response_model=Produto)
async def atualizar_produto(id: PydanticObjectId, dados: ProdutoUpdate):
    """Atualiza um produto."""
    produto = await Produto.get(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    atualizacao = {k: v for k, v in dados.model_dump().items() if v is not None}
    await produto.update({"$set": atualizacao})
    return produto

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_produto(id: PydanticObjectId):
    """Remove um produto."""
    produto = await Produto.get(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    await produto.delete()
    return None