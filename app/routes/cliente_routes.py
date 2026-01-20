from typing import List
from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate

# Define o prefixo e a tag para a documentação automática (Swagger)
router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_cliente(dados: ClienteCreate):
    """
    Cria um novo cliente. Verifica duplicidade de Email e CPF.
    """
    # Verifica se já existe cliente com este email ou CPF
    # Usamos o operador $or do MongoDB para verificar ambos numa só consulta
    existente = await Cliente.find_one({
        "$or": [{"email": dados.email}, {"cpf": dados.cpf}]
    })
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cliente com este Email ou CPF."
        )

    # Cria a instância do Model e salva no banco
    novo_cliente = Cliente(**dados.model_dump())
    await novo_cliente.insert()
    
    return novo_cliente

@router.get("/", response_model=List[ClienteResponse])
async def listar_clientes():
    """
    Retorna todos os clientes cadastrados.
    """
    # .find_all().to_list() converte o cursor do Mongo numa lista Python
    clientes = await Cliente.find_all().to_list()
    return clientes

# ... (outros imports já existentes)

@router.get("/relatorios/vendas-por-categoria")
async def relatorio_vendas_por_categoria():
    """
    REQ G: Consulta complexa envolvendo múltiplas coleções (Pedidos + Produtos).
    Retorna o total faturado agrupado por categoria de produto.
    """
    pipeline = [
        # 1. Filtra apenas pedidos que não foram cancelados (Boa prática)
        {
            "$match": {"status": {"$ne": "CANCELADO"}}
        },
        # 2. Desconstrói o array 'itens'. 
        # Se um pedido tem 3 itens, ele transforma-se em 3 documentos na memória.
        {
            "$unwind": "$itens"
        },
        # 3. Faz o JOIN com a coleção 'produtos'.
        # Liga o ID guardado em 'itens.produto.$id' com o '_id' da coleção 'produtos'.
        {
            "$lookup": {
                "from": "produtos",          # Nome da coleção alvo no Mongo
                "localField": "itens.produto.$id", # Onde está o ID no Pedido
                "foreignField": "_id",       # Onde está o ID no Produto
                "as": "detalhes_produto"     # Onde guardar o resultado
            }
        },
        # 4. O $lookup retorna um array (mesmo sendo 1:1), fazemos unwind para o tornar objeto
        {
            "$unwind": "$detalhes_produto"
        },
        # 5. Agrupa pela Categoria do Produto e soma o valor total
        {
            "$group": {
                "_id": "$detalhes_produto.categoria",
                "total_vendido": {
                    "$sum": {
                        "$multiply": ["$itens.quantidade", "$itens.preco_unitario"]
                    }
                },
                "quantidade_itens": {"$sum": "$itens.quantidade"}
            }
        },
        # 6. (Opcional) Ordena do que vendeu mais para o que vendeu menos
        {
            "$sort": {"total_vendido": -1}
        },
        # 7. (Opcional) Formata a saída para ficar bonita no JSON
        {
            "$project": {
                "_id": 0,
                "categoria": "$_id",
                "total_vendido": 1,
                "quantidade_itens": 1
            }
        }
    ]

    # Executa a agregação diretamente no modelo Pedido
    resultado = await Pedido.aggregate(pipeline).to_list()
    
    return resultado

@router.get("/{id}", response_model=ClienteResponse)
async def obter_cliente(id: PydanticObjectId):
    """
    Busca um cliente pelo ID único do MongoDB.
    """
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/{id}", response_model=ClienteResponse)
async def atualizar_cliente(id: PydanticObjectId, dados: ClienteUpdate):
    """
    Atualiza dados do cliente. Aceita atualização parcial (apenas campos enviados).
    """
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # exclude_unset=True garante que só atualizamos o que foi enviado no JSON
    # Se o usuário não mandou "cpf", não vamos sobrescrever o cpf atual com null
    dados_para_atualizar = dados.model_dump(exclude_unset=True)
    
    # Atualiza e salva
    await cliente.set(dados_para_atualizar)
    
    return cliente

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cliente(id: PydanticObjectId):
    """
    Remove um cliente do banco.
    """
    cliente = await Cliente.get(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    await cliente.delete()
    return None
