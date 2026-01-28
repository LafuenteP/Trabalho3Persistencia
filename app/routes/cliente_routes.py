from fastapi import APIRouter, HTTPException, status, Query
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
import math

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from app.schemas.pedido import PaginatedResponse

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_cliente(dados: ClienteCreate):
    """Cria um novo cliente. Verifica duplicidade de Email e CPF."""
    existente = await Cliente.find_one({
        "$or": [{"email": dados.email}, {"cpf": dados.cpf}]
    })
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cliente com este Email ou CPF."
        )

    novo_cliente = Cliente(**dados.model_dump())
    await novo_cliente.insert()
    
    return novo_cliente

@router.get("/", response_model=PaginatedResponse[ClienteResponse])
async def listar_clientes(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """Retorna todos os clientes cadastrados com paginação."""
    # Conta total de documentos
    total_items = await Cliente.count()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    # Calcula o skip para a paginação
    skip = (page - 1) * page_size
    
    # Busca clientes com paginação
    clientes = await Cliente.find_all().skip(skip).limit(page_size).to_list()
    
    return PaginatedResponse(
        items=clientes,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )

@router.get("/{id}", response_model=ClienteResponse)
async def obter_cliente(id: PydanticObjectId):
    """Busca um cliente pelo ID."""
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/{id}", response_model=ClienteResponse)
async def atualizar_cliente(id: PydanticObjectId, dados: ClienteUpdate):
    """Atualiza dados do cliente. Aceita atualização parcial."""
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados_para_atualizar = dados.model_dump(exclude_unset=True)
    await cliente.set(dados_para_atualizar)
    
    return cliente

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cliente(id: PydanticObjectId):
    """Remove um cliente do banco."""
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    await cliente.delete()
    return None
