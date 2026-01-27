from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError
from beanie.exceptions import DocumentNotFound


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação (HTTP 422)."""
    erros = []
    for error in exc.errors():
        campo = error.get("loc", ["desconhecido"])[-1]
        tipo = error.get("type", "")
        msg = error.get("msg", "Valor inválido")
        
        if tipo == "missing":
            erros.append(f"Campo '{campo}' é obrigatório.")
        elif tipo == "string_type":
            erros.append(f"Campo '{campo}' deve ser um texto.")
        elif tipo == "int_type":
            erros.append(f"Campo '{campo}' deve ser um número inteiro.")
        elif tipo == "float_type":
            erros.append(f"Campo '{campo}' deve ser um número decimal.")
        else:
            erros.append(f"Campo '{campo}': {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "erro_validacao",
            "mensagem": "Os dados enviados contêm erros.",
            "detalhes": erros
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler para erros HTTP gerais (400, 404, etc)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "erro",
            "codigo": exc.status_code,
            "mensagem": exc.detail
        }
    )


async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    """Handler para erros de duplicidade no MongoDB (HTTP 409)."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "status": "erro_duplicidade",
            "mensagem": "Já existe um registro com estes dados únicos.",
            "detalhes": str(exc.details.get("keyValue", {}))
        }
    )


async def pymongo_exception_handler(request: Request, exc: PyMongoError):
    """Handler para erros de conexão com MongoDB (HTTP 503)."""
    print(f"❌ ERRO DE BANCO DE DADOS: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "erro_banco",
            "mensagem": "Erro de comunicação com o banco de dados."
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler genérico para erros não tratados (HTTP 500)."""
    print(f"❌ ERRO CRÍTICO: {type(exc).__name__}: {exc}") 
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "erro_interno",
            "mensagem": "Ocorreu um erro inesperado no servidor."
        }
    )

