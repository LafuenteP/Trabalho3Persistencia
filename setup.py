import os
from pathlib import Path

# Definição da estrutura
structure = {
    "app": ["__init__.py", "main.py"],
    "app/core": ["__init__.py", "config.py", "database.py", "exceptions.py"],
    "app/models": ["__init__.py", "cliente.py", "produto.py", "pedido.py"],
    "app/schemas": ["__init__.py"],
    "app/routes": ["__init__.py", "cliente_routes.py", "produto_routes.py", "pedido_routes.py"],
    "app/utils": ["__init__.py", "seeder.py"],
}

files_root = [".env", "divisao_tarefas.txt", "README.md"]

def create_structure():
    base_path = Path(".")
    
    # Criar pastas e arquivos dentro de app/
    for folder, files in structure.items():
        dir_path = base_path / folder
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"📂 Criada pasta: {folder}")
        
        for file in files:
            file_path = dir_path / file
            if not file_path.exists():
                file_path.touch()
                print(f"  📄 Criado arquivo: {file}")
    
    # Criar arquivos na raiz
    for file in files_root:
        file_path = base_path / file
        if not file_path.exists():
            file_path.touch()
            print(f"📄 Criado arquivo raiz: {file}")

if __name__ == "__main__":
    create_structure()
    print("\n✅ Estrutura do projeto criada com sucesso!")