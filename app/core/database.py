from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

# 1. IMPORTANTE: Importe o modelo aqui
from app.models.produto import Produto
from app.models.cliente import Cliente
from app.models.pedido import Pedido

# Cliente global do MongoDB
client: AsyncIOMotorClient = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DATABASE_NAME]
    
    await init_beanie(
        database=db,
        document_models=[
            Produto,
            Cliente,
            Pedido
        ]
    )