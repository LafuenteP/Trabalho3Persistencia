from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import init_db
from app.core.config import settings

# 1. Importe a rota
from app.routes import produto_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Conectando ao Banco de Dados...")
    await init_db()
    print("✅ Banco de Dados Conectado!")
    yield
    print("🛑 Desligando API...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 2. Inclua o router na aplicação
app.include_router(produto_routes.router)

@app.get("/")
async def root():
    return {"message": "API rodando!"}