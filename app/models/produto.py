from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel, TEXT

class Produto(Document):
    # Indexed() cria um índice no Mongo para deixar as buscas rápidas
    nome: Indexed(str) # type: ignore
    descricao: str | None = None
    
    # Validação: Preço deve ser maior que 0
    preco: float = Field(gt=0, description="Preço deve ser positivo")
    
    categoria: str
    estoque: int = Field(default=0, ge=0) # ge=0 significa maior ou igual a 0

    class Settings:
        # Nome da coleção que será criada no MongoDB
        name = "produtos"
        
        # Cria um índice de texto para facilitar a busca por palavras-chave (Requisito C)
        indexes = [
            [("nome", TEXT), ("descricao", TEXT)],
        ]

    # Opcional: Exemplo de estrutura para documentação automática
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Notebook Gamer",
                "descricao": "Notebook com placa de vídeo dedicada",
                "preco": 4500.00,
                "categoria": "Eletronicos",
                "estoque": 10
            }
        }