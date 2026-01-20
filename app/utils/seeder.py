import random
from faker import Faker
from beanie import WriteRules

# Importando os Models dos seus colegas
from app.models.produto import Produto
from app.models.cliente import Cliente, Endereco # Endereco é um modelo interno do Cliente
from app.models.pedido import Pedido, ItemPedido

fake = Faker('pt_BR') # Configura para gerar dados do Brasil

CATEGORIAS = ["Eletrônicos", "Livros", "Casa", "Moda", "Brinquedos"]

async def limpar_banco():
    """
    Remove todos os dados do banco.
    """
    print("🗑️  Limpando banco de dados...")
    await Pedido.delete_all()
    await Cliente.delete_all()
    await Produto.delete_all()
    print("✅ Banco limpo!")

async def popular_banco(force: bool = False):
    """
    Verifica se o banco está vazio e popula com dados fictícios.
    Se force=True, limpa o banco e repopula.
    """
    # 1. Se forçar, limpa tudo primeiro
    if force:
        await limpar_banco()
    
    # 2. Verificar se já existem dados para evitar duplicidade
    if await Produto.count() > 0:
        print("⚠️  Banco já contém dados. Pulando o seed.")
        return

    print("🌱 Iniciando o Seeding (População do Banco)...")

    # --- 2. Criar PRODUTOS ---
    produtos_db = []
    print("   -> Criando Produtos...")
    for _ in range(10):
        p = Produto(
            nome=f"{fake.word().capitalize()} {fake.word().capitalize()}",
            descricao=fake.sentence(),
            preco=round(random.uniform(10.0, 500.0), 2),
            categoria=random.choice(CATEGORIAS),
            estoque=random.randint(0, 100)
        )
        await p.insert()
        produtos_db.append(p)
    
    # --- 3. Criar CLIENTES ---
    clientes_db = []
    print("   -> Criando Clientes...")
    for _ in range(10):
        # O Membro 2 definiu 'Endereco' como um schema/model embutido
        end = Endereco(
            rua=fake.street_name(),
            numero=str(fake.building_number()),
            bairro=fake.bairro(),
            cidade=fake.city(),
            estado=fake.estado_sigla(),
            cep=fake.postcode()
        )
        
        c = Cliente(
            nome=fake.name(),
            email=fake.unique.email(),
            cpf=fake.cpf(),
            endereco=end
        )
        await c.insert()
        clientes_db.append(c)

    # --- 4. Criar PEDIDOS ---
    print("   -> Criando Pedidos...")
    for _ in range(15): # Vamos criar 15 pedidos para ter massa de teste
        cliente_random = random.choice(clientes_db)
        
        # Gerar de 1 a 4 itens aleatórios para este pedido
        itens_pedido = []
        valor_total_calculado = 0.0
        
        # Seleciona produtos aleatórios sem repetir no mesmo pedido
        produtos_selecionados = random.sample(produtos_db, k=random.randint(1, 4))
        
        for prod in produtos_selecionados:
            qtd = random.randint(1, 3)
            # ItemPedido (definido pelo Membro 2) congela o preço
            item = ItemPedido(
                produto=prod, # Link automático do Beanie
                quantidade=qtd,
                preco_unitario=prod.preco
            )
            itens_pedido.append(item)
            valor_total_calculado += (prod.preco * qtd)

        # Importante para o Req D/F (Filtro por Data):
        # Geramos datas espalhadas no último ano
        data_retroativa = fake.date_time_between(start_date='-1y', end_date='now')

        pedido = Pedido(
            cliente=cliente_random,
            itens=itens_pedido,
            valor_total=round(valor_total_calculado, 2),
            data_emissao=data_retroativa,
            status=random.choice(["PENDENTE", "PAGO", "ENVIADO", "CANCELADO"])
        )
        
        # WriteRules.WRITE garante que os links sejam salvos corretamente (se necessário)
        await pedido.insert(link_rule=WriteRules.WRITE)

    print("✅ Seeding concluído com sucesso!")