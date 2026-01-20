from typing import List, Optional
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
async def listar_pedidos_por_data(ano: int, mes: Optional[int] = None):
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


