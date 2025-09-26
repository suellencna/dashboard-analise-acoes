# limpar_usuarios.py - Script para limpar usuários existentes no banco
import os
import sqlalchemy

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

# --- CONFIRMAÇÃO DE SEGURANÇA ---
print("\n⚠️  ATENÇÃO: Esta operação irá DELETAR TODOS os usuários do banco de dados!")
print("Esta ação é IRREVERSÍVEL!")
print("\nUsuários que serão deletados:")
try:
    with engine.connect() as conn:
        query = sqlalchemy.text("SELECT email, nome FROM usuarios")
        result = conn.execute(query)
        usuarios = result.fetchall()
        
        if not usuarios:
            print("Nenhum usuário encontrado no banco de dados.")
            exit()
        
        for usuario in usuarios:
            print(f"  - {usuario[0]} ({usuario[1]})")
        
        print(f"\nTotal de usuários: {len(usuarios)}")
        
except Exception as e:
    print(f"Erro ao listar usuários: {e}")
    exit()

# Confirmação final
confirmacao = input("\nDigite 'CONFIRMAR' para prosseguir com a exclusão: ")
if confirmacao != "CONFIRMAR":
    print("Operação cancelada.")
    exit()

# --- EXECUTAR A LIMPEZA ---
try:
    with engine.connect() as conn:
        # Deletar todos os usuários
        query = sqlalchemy.text("DELETE FROM usuarios")
        result = conn.execute(query)
        conn.commit()
        
        print(f"\n✅ SUCESSO! {result.rowcount} usuário(s) deletado(s) do banco de dados.")
        
        # Verificar se a tabela está vazia
        query_check = sqlalchemy.text("SELECT COUNT(*) FROM usuarios")
        count_result = conn.execute(query_check)
        count = count_result.scalar()
        
        if count == 0:
            print("✅ Confirmação: Tabela de usuários está vazia.")
        else:
            print(f"⚠️  Aviso: Ainda existem {count} usuário(s) na tabela.")
            
except Exception as e:
    print(f"\n❌ ERRO ao tentar limpar os usuários.")
    print(f"Detalhe do erro: {e}")

print("\nOperação concluída.")
