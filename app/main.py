from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError

# Imports de Configuração e Banco
from app.core.database import init_db
from app.core.config import settings
from app.utils.seeder import popular_banco

# Imports dos Handlers de Erro (Tratamento Global)
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    duplicate_key_exception_handler,
    pymongo_exception_handler,
    general_exception_handler
)

# Imports das Rotas
from app.routes import produto_routes
from app.routes import cliente_routes
from app.routes import pedido_routes
from app.routes import analytics_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Conectando ao Banco de Dados...")
    await init_db()
    print("✅ Banco de Dados Conectado!")
    
    # Executa o seeder para popular o banco se necessário
    await popular_banco()
    
    yield
    print("🛑 Desligando API...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# --- 1. REGISTRO DE TRATAMENTO DE ERROS (Blindagem da API) ---
# Conecta as funções do arquivo exceptions.py ao FastAPI
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # 422
app.add_exception_handler(StarletteHTTPException, http_exception_handler)         # 400, 404, etc
app.add_exception_handler(DuplicateKeyError, duplicate_key_exception_handler)     # 409
app.add_exception_handler(PyMongoError, pymongo_exception_handler)                # 503
app.add_exception_handler(Exception, general_exception_handler)                   # 500

# --- 2. REGISTRO DE ROTAS ---
app.include_router(produto_routes.router)
app.include_router(cliente_routes.router)
app.include_router(pedido_routes.router)
app.include_router(analytics_routes.router)

@app.get("/")
async def root():
    return {"message": "API rodando! Acesse /docs para testar."}

@app.post("/admin/reseed", tags=["Admin"])
async def forcar_reseed():
    """
    Limpa o banco e repopula com dados fictícios.
    ATENÇÃO: Isso apaga todos os dados!
    """
    await popular_banco(force=True)
    return {"message": "Banco limpo e repopulado com sucesso!"}