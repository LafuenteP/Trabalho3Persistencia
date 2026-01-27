from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError
from beanie.exceptions import DocumentNotFound

# 1. Handler para Erros de Validação (Pydantic) - HTTP 422
# Acontece quando o usuário manda um JSON errado (ex: string no lugar de int)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = []
    for error in exc.errors():
        # Simplifica a mensagem de erro para ficar legível
        campo = error.get("loc", ["desconhecido"])[-1]  # Pega o nome do campo
        tipo = error.get("type", "")
        msg = error.get("msg", "Valor inválido")
        
        # Mensagens mais amigáveis para erros comuns
        if tipo == "missing":
            erros.append(f"Campo '{campo}' é obrigatório.")
        elif tipo == "string_type":
            erros.append(f"Campo '{campo}' deve ser um texto.")
        elif tipo == "int_type":
            erros.append(f"Campo '{campo}' deve ser um número inteiro.")
        elif tipo == "float_type":
            erros.append(f"Campo '{campo}' deve ser um número decimal.")
        elif "greater_than" in tipo:
            erros.append(f"Campo '{campo}': {msg}")
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

# 2. Handler para Erros HTTP Gerais (404, 403, 400 disparados manualmente)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "erro",
            "codigo": exc.status_code,
            "mensagem": exc.detail  # A mensagem que você escreveu no raise HTTPException
        }
    )

# 3. Handler para Erros de Duplicidade no MongoDB
async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "status": "erro_duplicidade",
            "mensagem": "Já existe um registro com estes dados únicos.",
            "detalhes": str(exc.details.get("keyValue", {}))
        }
    )

# 4. Handler para Erros Gerais do MongoDB (conexão, timeout, etc)
async def pymongo_exception_handler(request: Request, exc: PyMongoError):
    print(f"❌ ERRO DE BANCO DE DADOS: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "erro_banco",
            "mensagem": "Erro de comunicação com o banco de dados. Tente novamente."
        }
    )

# 5. Handler Genérico (Caindo aqui, é bug no código ou erro 500)
# Captura qualquer erro não previsto para o servidor não "quebrar"
async def general_exception_handler(request: Request, exc: Exception):
    # Aqui você poderia adicionar logs de sistema (sentry, arquivos de log, etc)
    print(f"❌ ERRO CRÍTICO NÃO TRATADO: {type(exc).__name__}: {exc}") 
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "erro_interno",
            "mensagem": "Ocorreu um erro inesperado no servidor. Tente novamente mais tarde."
        }
    )

