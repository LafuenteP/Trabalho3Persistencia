from fastapi import APIRouter
from datetime import datetime

from app.models.pedido import Pedido
from app.models.produto import Produto

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/produtos-por-categoria")
async def contar_produtos_por_categoria():
    """Retorna a quantidade de produtos por categoria."""
    pipeline = [
        {"$group": {"_id": "$categoria", "total_produtos": {"$sum": 1}}},
        {"$project": {"categoria": "$_id", "total_produtos": 1, "_id": 0}},
        {"$sort": {"total_produtos": -1}}
    ]
    
    collection = Produto.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    return resultado

@router.get("/ticket-medio")
async def calcular_ticket_medio():
    """Calcula o ticket médio dos pedidos."""
    pipeline = [
        {
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
                "ticket_medio": {"$round": ["$media_valor", 2]},
                "total_pedidos": 1,
                "faturamento_total": 1
            }
        }
    ]
    
    collection = Pedido.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    
    if not resultado:
        return {"ticket_medio": 0.0, "total_pedidos": 0}
        
    return resultado[0]

@router.get("/pedidos-por-periodo")
async def listar_pedidos_por_data(ano: int, mes: int | None = None):
    """Lista pedidos filtrados por ano e opcionalmente por mês."""
    match_stage = {
        "$match": {
            "$expr": {
                "$and": [{"$eq": [{"$year": "$data_emissao"}, ano]}]
            }
        }
    }

    if mes:
        match_stage["$match"]["$expr"]["$and"].append(
            {"$eq": [{"$month": "$data_emissao"}, mes]}
        )

    pipeline = [
        match_stage,
        {"$sort": {"data_emissao": -1}},
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "data": "$data_emissao",
                "valor": "$valor_total",
                "status": "$status",
                "cliente_id": "$cliente.$id"
            }
        }
    ]

    collection = Pedido.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    return resultado

@router.get("/vendas-por-categoria")
async def relatorio_vendas_por_categoria():
    """Retorna o total vendido agrupado por categoria de produto."""
    pipeline = [
        {"$match": {"status": {"$ne": "CANCELADO"}}},
        {"$unwind": "$itens"},
        {
            "$group": {
                "_id": "$itens.produto.categoria",
                "total_vendido": {
                    "$sum": {"$multiply": ["$itens.quantidade", "$itens.preco_unitario"]}
                },
                "quantidade_itens": {"$sum": "$itens.quantidade"}
            }
        },
        {"$sort": {"total_vendido": -1}},
        {
            "$project": {
                "_id": 0,
                "categoria": "$_id",
                "total_vendido": 1,
                "quantidade_itens": 1
            }
        }
    ]

    collection = Pedido.get_pymongo_collection()
    cursor = collection.aggregate(pipeline)
    resultado = await cursor.to_list(length=None)
    return resultado


