from fastapi import APIRouter, HTTPException, status, Query
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from beanie import PydanticObjectId

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=Produto, status_code=status.HTTP_201_CREATED)
async def criar_produto(dados: ProdutoCreate):
    """Cria um novo produto."""
    novo_produto = Produto(**dados.model_dump())
    await novo_produto.insert()
    return novo_produto

@router.get("/", response_model=list[Produto])
async def listar_produtos(
    termo: str | None = Query(None, description="Busca por nome"),
    categoria: str | None = Query(None, description="Filtro por categoria"),
    min_preco: float | None = Query(None, description="Preço mínimo", gt=0),
    max_preco: float | None = Query(None, description="Preço máximo", gt=0)
):
    """Lista produtos com filtros opcionais."""
    query = Produto.find_all()
    
    if termo:
        query = query.find({"nome": {"$regex": termo, "$options": "i"}})
    
    if categoria:
        query = query.find(Produto.categoria == categoria)

    if min_preco:
        query = query.find(Produto.preco >= min_preco)
    
    if max_preco:
        query = query.find(Produto.preco <= max_preco)
        
    return await query.to_list()

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