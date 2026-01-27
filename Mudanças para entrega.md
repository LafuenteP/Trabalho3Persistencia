
## Mudança número 1 - mais básica

ajuste no UV.lock, o projeto tava com o UV.lock bugado, primeira coisa que fiz foi ajustar e rodar pra garantir o travamento e o alinhamento das depedências


## Mudança número 2

- **Arquivo modificado:** [cliente_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)
- **Linha alterada:** Linha 7 (adicionada)
- **Mudança feita:** Adicionei [from app.models.pedido import Pedido](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)
- **Por que era necessário:** A função [relatorio_vendas_por_categoria()](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) usava [Pedido.aggregate(pipeline)](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) na linha 104, mas o modelo [Pedido](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) não estava importado. Sem esse import, o código geraria um erro `NameError: name 'Pedido' is not defined` ao executar essa rota.



✅ **Passo 3 concluído!**

**Para o seu caderno:**

### Alterações realizadas:

|Arquivo|Ação|Descrição|
|---|---|---|
|[analytics_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**Adicionada**|Rota `GET /analytics/vendas-por-categoria` (linhas 125-187)|
|[cliente_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**Removida**|Rota `GET /clientes/relatorios/vendas-por-categoria` (~60 linhas)|
|[cliente_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**Removido**|Import do [Pedido](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) que não era mais necessário|

### Por que essa mudança foi feita:

- **Organização**: A rota `vendas-por-categoria` é um relatório analítico, não uma operação de CRUD de clientes
- **Consistência**: Agora todas as rotas de relatórios/analytics estão no mesmo arquivo
- **Novo endpoint**: `GET /analytics/vendas-por-categoria` (antes era [/clientes/relatorios/vendas-por-categoria](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html))

### O que a rota faz:

- Consulta complexa com `$lookup` (JOIN entre Pedidos e Produtos)
- Agrupa vendas por categoria de produto
- Retorna total vendido e quantidade de itens por categoria


## Mudança número 3

✅ **Passo 4 concluído!**

**Para o seu caderno:**

### Arquivos modificados (10 arquivos):

| Arquivo                                                                                                                                                                         | Mudanças                                                                                                                                                                                                                                                                                                                                                                                                           |                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [cliente_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)   | Removido `from typing import List`, alterado `List[...]` → [list[...]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)                                                                                                                                                                                   |                                                                                                                                                                 |
| [pedido_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)    | Removido `from typing import List`, alterado `List[...]` → [list[...]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)                                                                                                                                                                                   |                                                                                                                                                                 |
| [produto_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)   | Removido `from typing import List, Optional`, alterado `Optional[X]` → `X \| None`                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                 |
| [analytics_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | Removido `from typing import List, Optional`, alterado [Optional[int]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) → [int \\                                                                                                                                                                         | None](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| models/cliente.py                                                                                                                                                               | Removido `from typing import Optional`, alterado [Optional[Endereco]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) → [Endereco \\                                                                                                                                                                     | None](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| models/pedido.py                                                                                                                                                                | Removido `from typing import List, Optional`, alterado [List[ItemPedido]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) → [list[ItemPedido]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |                                                                                                                                                                 |
| models/produto.py                                                                                                                                                               | Removido `from typing import Optional`, alterado [Optional[str]](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) → [str \\                                                                                                                                                                               | None](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| schemas/cliente.py                                                                                                                                                              | Removido `from typing import Optional`, todos os campos opcionais agora usam `X \| None`                                                                                                                                                                                                                                                                                                                           |                                                                                                                                                                 |
| schemas/pedido.py                                                                                                                                                               | Removido `from typing import List, Optional`, `List` → [list](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html), `Optional` → `\| None`                                                                                                                                                                    |                                                                                                                                                                 |
| schemas/produto.py                                                                                                                                                              | Removido `from typing import Optional`, `Optional` → `\| None`                                                                                                                                                                                                                                                                                                                                                     |                                                                                                                                                                 |



## Mudança número 4

✅ **Passo 5 concluído!**

**Para o seu caderno:**

### Ações realizadas:

|Ação|Comando|Descrição|
|---|---|---|
|Remover `__pycache__` do Git|`git rm -r --cached app/__pycache__/` (e outras)|Remove do rastreamento do Git, mas mantém os arquivos localmente|
|Atualizar [.gitignore](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|Edição do arquivo|Adicionado [.venv](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) e [.obsidian](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|

### Arquivos [.gitignore](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) atualizado:

__pycache__/
*.pyc
.env
venv/
.venv/        # ← ADICIONADO
.idea/
.vscode/
.obsidian/    # ← ADICIONADO

### O que o [git status](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) mostra agora:

- **D** (Deleted) = Arquivos `__pycache__` marcados para remoção do repositório
- **M** (Modified) = Seus arquivos de código atualizados
- A pasta [.obsidian](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) agora é ignorada

### Por que isso é importante:

- `__pycache__/` são arquivos compilados do Python gerados automaticamente - não devem ir para o repositório
- [.venv](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) é a pasta do ambiente virtual - cada desenvolvedor cria a sua
- [.obsidian](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) é configuração do editor Obsidian - pessoal de cada um


## Mudança 5

✅ **Passo 6 concluído!**

**Para o seu caderno:**

### Arquivos modificados:

|Arquivo|Mudança|
|---|---|
|[exceptions.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|Adicionados 2 novos handlers + melhorias no handler 422|
|[main.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|Registrados os novos handlers|

### Handlers de exceção agora disponíveis:

|Handler|Código HTTP|Quando é acionado|
|---|---|---|
|[validation_exception_handler](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**422**|JSON inválido, campos faltando, tipos errados|
|[http_exception_handler](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**400, 404, etc**|[raise HTTPException(...)](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) manual no código|
|[duplicate_key_exception_handler](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**409**|Tentativa de inserir email/CPF duplicado no MongoDB|
|[pymongo_exception_handler](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**503**|Problemas de conexão com o banco de dados|
|[general_exception_handler](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|**500**|Qualquer erro não previsto (bugs)|

### Melhorias no handler 422:

- Mensagens mais amigáveis em português
- Tratamento especial para erros comuns:
    - `"missing"` → "Campo 'X' é obrigatório."
    - `"string_type"` → "Campo 'X' deve ser um texto."
    - `"int_type"` → "Campo 'X' deve ser um número inteiro."

---

**Resumo final de todas as mudanças feitas:**

| Passo | Descrição                                                                                                                                                                                                      | Status |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 1     | Gerar [uv.lock](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)                                      | ✅      |
| 2     | Corrigir import do [Pedido](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)                          | ✅      |
| 3     | Mover rota para [analytics_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)                | ✅      |
| 4     | Atualizar sintaxe Python moderna                                                                                                                                                                               | ✅      |
| 5     | Limpar `__pycache__` do Git + atualizar [.gitignore](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | ✅      |
| 6     | Melhorar tratamento de exceções                                                                                                                                                                                | ✅      |


## Última mudança:

### Correção: Erro 500 em `/analytics/produtos-por-categoria`

|Item|Descrição|
|---|---|
|**Erro encontrado**|`AttributeError: 'Type[Produto]' object has no attribute 'get_motor_collection'`|
|**Causa raiz**|O Beanie 2.0+ renomeou o método de acesso à coleção do MongoDB|
|**Arquivo corrigido**|[analytics_routes.py](vscode-file://vscode-app/c:/Users/lafue/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)|
|**Linhas alteradas**|3 ocorrências (linhas ~15, ~45, ~75)|

### Sintaxe alterada:

# ANTES (Beanie 1.x)
collection = Produto.get_motor_collection()

# DEPOIS (Beanie 2.x)
collection = Produto.get_pymongo_collection()

### Por que isso aconteceu:

- O Beanie é o ODM que usamos para conectar o MongoDB com o Pydantic
- Na versão 2.0, os desenvolvedores renomearam o método para refletir melhor que retorna uma coleção do PyMongo (não do Motor diretamente)
- O Motor é o driver assíncrono, o PyMongo é a biblioteca base

### Lição aprendida:

Ao atualizar bibliotecas, sempre verificar o **changelog** ou **migration guide** para identificar breaking changes (mudanças que quebram compatibilidade).