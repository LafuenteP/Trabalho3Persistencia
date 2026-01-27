from fastapi import APIRouter, HTTPException, status, Query
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate
from beanie import PydanticObjectId

router = APIRouter(prefix="/produtos", tags=["Produtos"])

# --- CREATE (Criar) ---
@router.post("/", response_model=Produto, status_code=status.HTTP_201_CREATED)
async def criar_produto(dados: ProdutoCreate):
    """
    Cria um novo produto no banco de dados.
    """
    novo_produto = Produto(**dados.model_dump())
    await novo_produto.insert()
    return novo_produto

# --- READ (Listar com Filtros de Texto, Categoria e Preço) ---
# AQUI ESTÁ A MUDANÇA PRINCIPAL
@router.get("/", response_model=list[Produto])
async def listar_produtos(
    termo: str | None = Query(None, description="Busca por nome (parcial/case-insensitive)"),
    categoria: str | None = Query(None, description="Filtro exato de categoria"),
    min_preco: float | None = Query(None, description="Preço mínimo", gt=0),
    max_preco: float | None = Query(None, description="Preço máximo", gt=0)
):
    """
    Lista produtos. Suporta filtros por Texto, Categoria e Faixa de Preço.
    """
    # Começa buscando tudo
    query = Produto.find_all()
    
    # Requisito C: Busca por texto parcial e case-insensitive
    if termo:
        query = query.find({"nome": {"$regex": termo, "$options": "i"}})
    
    # Filtro por Categoria
    if categoria:
        query = query.find(Produto.categoria == categoria)

    # Requisito J: Filtro por Preço Mínimo (maior ou igual)
    if min_preco:
        query = query.find(Produto.preco >= min_preco)
    
    # Requisito J: Filtro por Preço Máximo (menor ou igual)
    if max_preco:
        query = query.find(Produto.preco <= max_preco)
        
    return await query.to_list()

# --- READ (Buscar por ID) ---
@router.get("/{id}", response_model=Produto)
async def obter_produto(id: PydanticObjectId):
    produto = await Produto.get(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

# --- UPDATE (Atualizar) ---
@router.put("/{id}", response_model=Produto)
async def atualizar_produto(id: PydanticObjectId, dados: ProdutoUpdate):
    produto = await Produto.get(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    atualizacao = {k: v for k, v in dados.model_dump().items() if v is not None}
    
    await produto.update({"$set": atualizacao})
    return produto

# --- DELETE (Deletar) ---
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_produto(id: PydanticObjectId):
    produto = await Produto.get(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    await produto.delete()
    return None