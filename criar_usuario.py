# criar_usuario.py (Versão 3 - com argon2)
import os
import sqlalchemy
from argon2 import PasswordHasher

# Configuração para hashear a senha com argon2
ph = PasswordHasher()

# --- CARREGAR VARIÁVEIS DE AMBIENTE ---
# Tentar carregar do arquivo .env se existir
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# --- PEGAR A URL DO BANCO DE DADOS ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Variável de ambiente DATABASE_URL não encontrada.")
    print("Execute primeiro: python configurar_bd.py")
    DATABASE_URL = input("Ou cole aqui a sua URL de conexão completa da Neon:\n")

if not DATABASE_URL:
    print("URL do banco de dados não fornecida. Saindo.")
    exit()

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    print("\nConexão com o banco de dados estabelecida com sucesso!")
except Exception as e:
    print(f"\nERRO: Não foi possível conectar ao banco de dados.")
    print(f"Detalhe do erro: {e}")
    exit()

# --- Coleta dos dados do novo usuário ---
print("\n--- Cadastro do Novo Usuário ---")
nome = input("Nome do usuário: ")
email = input("Email do usuário: ")

print("\n!!! AVISO: Sua senha ficará visível na tela enquanto você digita. !!!")
senha = input("Digite a senha: ")
senha_confirm = input("Confirme a senha: ")

if senha != senha_confirm:
    print("\nAs senhas não conferem. Operação cancelada.")
    exit()

# Hashear a senha com argon2
senha_hash = ph.hash(senha)

# --- Inserir no banco de dados ---
try:
    with engine.connect() as conn:
        query = sqlalchemy.text("INSERT INTO usuarios (nome, email, senha_hash) VALUES (:nome, :email, :senha_hash)")
        conn.execute(query, {"nome": nome, "email": email, "senha_hash": senha_hash})
        conn.commit()
    print(f"\n✅ SUCESSO! Usuário '{email}' criado no banco de dados.")
except Exception as e:
    print(f"\n❌ ERRO ao tentar criar o usuário.")
    print(f"O email '{email}' provavelmente já existe no banco de dados.")
    print(f"Detalhe do erro: {e}")