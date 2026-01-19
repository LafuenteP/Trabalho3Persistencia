from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

# 1. IMPORTANTE: Importe o modelo aqui
from app.models.produto import Produto

async def init_db():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            # 2. Adicione a classe na lista
            Produto
            # Futuramente: Cliente, Pedido...
        ]
    )