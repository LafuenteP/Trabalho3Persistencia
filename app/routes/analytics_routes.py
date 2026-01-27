from fastapi import APIRouter
from datetime import datetime

# Importamos os Models
from app.models.pedido import Pedido
from app.models.produto import Produto

router = APIRouter(prefix="/analytics", tags=["Analytics & Relatórios"])

# --- REQUISITO H: Quantidade de produtos por Categoria ---
@router.get("/produtos-por-categoria")
async def contar_produtos_por_categoria():
    """
    Retorna quantos produtos existem em cada categoria.
    Usa Aggregation: $group + $sum
    """
    pipeline = [
        {
            "$group": {
                "_id": "$categoria",  # Agrupa pelo campo 'categoria'
                "total_produtos": {"$sum": 1}  # Conta 1 para cada documento encontrado
            }
        },
        {
            "$project": {
                "categoria": "$_id",
                "total_produtos": 1,
                "_id": 0
            }
        },
        { "$sort": { "total_produtos": -1 } } # Ordena descrescente
    ]
    
    # Usando a coleção do Motor diretamente para aggregate
    collection = Produto.get_motor_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    return resultado

# --- REQUISITO I: Média de valor dos pedidos (Ticket Médio) ---
@router.get("/ticket-medio")
async def calcular_ticket_medio():
    """
    Calcula a média do valor total de todos os pedidos.
    Usa Aggregation: $group (null) + $avg
    """
    pipeline = [
        {
            # Agrupar por null significa "pegar a coleção inteira como um só grupo"
            "$group": {
                "_id": None, 
                "media_valor": {"$avg": "$valor_total"},
                "total_pedidos": {"$sum": 1},
                "faturamento_total": {"$sum": "$valor_total"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "ticket_medio": { "$round": ["$media_valor", 2] }, # Arredonda para 2 casas
                "total_pedidos": 1,
                "faturamento_total": 1
            }
        }
    ]
    
    # Usando a coleção do Motor diretamente para aggregate
    collection = Pedido.get_motor_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    
    # Se não houver pedidos, retorna zero para evitar lista vazia
    if not resultado:
        return {"ticket_medio": 0.0, "total_pedidos": 0}
        
    return resultado[0]

# --- REQUISITO D/F: Listar pedidos por Ano e Mês ---
@router.get("/pedidos-por-periodo")
async def listar_pedidos_por_data(ano: int, mes: int | None = None):
    """
    Lista pedidos filtrados por Ano e opcionalmente por Mês.
    Usa Aggregation com $expr para extrair partes da data.
    """
    match_stage = {
        "$match": {
            "$expr": {
                "$and": [
                    # Compara o ano do campo 'data_emissao' com o parametro 'ano'
                    {"$eq": [{"$year": "$data_emissao"}, ano]}
                ]
            }
        }
    }

    # Se o utilizador informou o mês, adicionamos essa condição ao filtro
    if mes:
        match_stage["$match"]["$expr"]["$and"].append(
            {"$eq": [{"$month": "$data_emissao"}, mes]}
        )

    pipeline = [
        match_stage,
        { "$sort": { "data_emissao": -1 } }, # Mais recentes primeiro
        # Opcional: projetar apenas campos essenciais para o relatório
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "data": "$data_emissao",
                "valor": "$valor_total",
                "status": "$status",
                "cliente_id": "$cliente.$id" # Mostra apenas o ID do cliente
            }
        }
    ]

    # Usando a coleção do Motor diretamente para aggregate
    collection = Pedido.get_motor_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    return resultado


# --- REQUISITO G: Consulta complexa multi-coleções (Vendas por Categoria) ---
@router.get("/vendas-por-categoria")
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


