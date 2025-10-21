#!/usr/bin/env python3
"""
Script para testar o sistema de login após as correções
"""

import os
import sqlalchemy
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

# Configuração
ph = PasswordHasher()

# --- PEGAR A URL DO BANCO DE DADOS ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Variável de ambiente DATABASE_URL não encontrada.")
    DATABASE_URL = input("Por favor, cole aqui a sua URL de conexão completa da Neon:\n")

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

def check_login_test(email, password):
    """Função de teste do login (cópia da função do app.py)"""
    user_data = None
    try:
        with engine.connect() as conn:
            query = sqlalchemy.text(
                "SELECT nome, senha_hash, ultima_carteira, ultimos_pesos, "
                "data_inicio_salva, data_fim_salva, status_assinatura "
                "FROM usuarios WHERE email = :email"
            )
            result = conn.execute(query, {"email": email}).first()
            if result:
                user_data = result
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False, "DB_ERROR", None, None, None, None

    if user_data:
        (nome_usuario, senha_hash_salva, ultima_carteira, ultimos_pesos,
         data_inicio, data_fim, status_assinatura) = user_data

        try:
            ph.verify(senha_hash_salva, password)
            if status_assinatura == 'ativo':
                # Login bem-sucedido
                return True, nome_usuario, ultima_carteira, ultimos_pesos, data_inicio, data_fim
            else:
                # Senha correta, mas assinatura inativa
                return False, "INACTIVE_SUBSCRIPTION", None, None, None, None
        except VerifyMismatchError:
            # Senha incorreta
            pass
        except InvalidHashError:
            # Hash inválido - usuário precisa redefinir senha
            return False, "INVALID_HASH", None, None, None, None

    # Email não encontrado ou senha incorreta
    return False, "INVALID_CREDENTIALS", None, None, None, None

def update_password_test(email, new_password):
    """Função de teste para atualizar senha"""
    try:
        with engine.connect() as conn:
            # Gerar novo hash da senha
            new_hash = ph.hash(new_password)
            
            # Atualizar no banco
            query = sqlalchemy.text("UPDATE usuarios SET senha_hash = :new_hash WHERE email = :email")
            result = conn.execute(query, {"new_hash": new_hash, "email": email})
            conn.commit()
            
            if result.rowcount > 0:
                return True, "Senha atualizada com sucesso"
            else:
                return False, "Usuário não encontrado"
    except Exception as e:
        return False, f"Erro ao atualizar senha: {e}"

def main():
    print("=== TESTE DO SISTEMA DE LOGIN ===")
    
    # 1. Verificar se existem usuários no banco
    try:
        with engine.connect() as conn:
            query = sqlalchemy.text("SELECT email, nome FROM usuarios")
            result = conn.execute(query)
            usuarios = result.fetchall()
            
            if not usuarios:
                print("❌ Nenhum usuário encontrado no banco de dados.")
                print("Execute primeiro o script 'criar_usuario.py' para criar um usuário de teste.")
                return
            
            print(f"✅ Encontrados {len(usuarios)} usuário(s) no banco:")
            for usuario in usuarios:
                print(f"  - {usuario[0]} ({usuario[1]})")
                
    except Exception as e:
        print(f"❌ Erro ao consultar usuários: {e}")
        return
    
    # 2. Teste de login
    print("\n=== TESTE DE LOGIN ===")
    email = input("Digite o email para testar: ")
    password = input("Digite a senha para testar: ")
    
    is_logged_in, user_name, ultima_carteira, ultimos_pesos, data_inicio, data_fim = check_login_test(email, password)
    
    if is_logged_in:
        print("✅ Login bem-sucedido!")
        print(f"  Nome: {user_name}")
        print(f"  Carteira: {ultima_carteira}")
        print(f"  Pesos: {ultimos_pesos}")
    elif user_name == "INVALID_HASH":
        print("⚠️ Hash inválido - usuário precisa redefinir senha")
        
        # Teste de redefinição de senha
        print("\n=== TESTE DE REDEFINIÇÃO DE SENHA ===")
        new_password = input("Digite uma nova senha: ")
        confirm_password = input("Confirme a nova senha: ")
        
        if new_password == confirm_password:
            success, message = update_password_test(email, new_password)
            if success:
                print(f"✅ {message}")
                
                # Teste de login com nova senha
                print("\n=== TESTE DE LOGIN COM NOVA SENHA ===")
                is_logged_in, user_name, _, _, _, _ = check_login_test(email, new_password)
                if is_logged_in:
                    print("✅ Login com nova senha bem-sucedido!")
                else:
                    print(f"❌ Erro no login com nova senha: {user_name}")
            else:
                print(f"❌ Erro ao atualizar senha: {message}")
        else:
            print("❌ Senhas não coincidem.")
            
    elif user_name == "INACTIVE_SUBSCRIPTION":
        print("⚠️ Assinatura inativa")
    else:
        print(f"❌ Login falhou: {user_name}")

if __name__ == "__main__":
    main()
