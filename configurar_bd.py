#!/usr/bin/env python3
"""
Script para configurar a conexão com o banco de dados
"""

import os
import sqlalchemy
from argon2 import PasswordHasher

print("=== CONFIGURAÇÃO DO BANCO DE DADOS ===")

# Verificar se já existe um arquivo .env
env_file = ".env"
if os.path.exists(env_file):
    print("✅ Arquivo .env encontrado")
    with open(env_file, 'r') as f:
        content = f.read()
        if 'DATABASE_URL' in content:
            print("✅ DATABASE_URL já configurada no .env")
        else:
            print("⚠️  DATABASE_URL não encontrada no .env")
else:
    print("⚠️  Arquivo .env não encontrado")

# Solicitar URL do banco
print("\nPor favor, forneça a URL de conexão com o banco de dados Neon:")
print("Exemplo: postgresql://usuario:senha@host:porta/database")
print("(A senha será mascarada por segurança)")

DATABASE_URL = input("\nURL do banco de dados: ").strip()

if not DATABASE_URL:
    print("❌ URL não fornecida. Saindo.")
    exit()

# Testar a conexão
print("\n🔍 Testando conexão...")
try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1 as test"))
        test_value = result.scalar()
        print("✅ Conexão bem-sucedida!")
        
        # Verificar se a tabela usuarios existe
        result = conn.execute(sqlalchemy.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'usuarios'
        """))
        table_exists = result.fetchone()
        
        if not table_exists:
            print("⚠️  Tabela 'usuarios' não encontrada. Criando...")
            
            # Criar a tabela
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                status_assinatura VARCHAR(50) DEFAULT 'ativo',
                ultima_carteira TEXT,
                ultimos_pesos TEXT,
                data_inicio_salva DATE,
                data_fim_salva DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            conn.execute(sqlalchemy.text(create_table_sql))
            conn.commit()
            print("✅ Tabela 'usuarios' criada com sucesso!")
        else:
            print("✅ Tabela 'usuarios' já existe")
            
        # Contar usuários
        result = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM usuarios"))
        count = result.scalar()
        print(f"📊 Total de usuários: {count}")
        
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
    exit()

# Salvar no arquivo .env
print("\n💾 Salvando configuração...")
try:
    with open(env_file, 'w') as f:
        f.write(f"DATABASE_URL={DATABASE_URL}\n")
    print("✅ Configuração salva em .env")
except Exception as e:
    print(f"⚠️  Erro ao salvar .env: {e}")

# Criar um usuário de teste
print("\n👤 Deseja criar um usuário de teste? (s/n)")
criar_usuario = input().strip().lower()

if criar_usuario in ['s', 'sim', 'y', 'yes']:
    print("\n--- Criando Usuário de Teste ---")
    nome = input("Nome: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()
    
    if nome and email and senha:
        try:
            ph = PasswordHasher()
            senha_hash = ph.hash(senha)
            
            with engine.connect() as conn:
                query = sqlalchemy.text("""
                    INSERT INTO usuarios (nome, email, senha_hash, status_assinatura) 
                    VALUES (:nome, :email, :senha_hash, 'ativo')
                """)
                conn.execute(query, {
                    "nome": nome, 
                    "email": email, 
                    "senha_hash": senha_hash
                })
                conn.commit()
                
            print("✅ Usuário criado com sucesso!")
            
            # Testar login
            print("\n🔐 Testando login...")
            with engine.connect() as conn:
                query = sqlalchemy.text("SELECT senha_hash FROM usuarios WHERE email = :email")
                result = conn.execute(query, {"email": email}).first()
                
                if result:
                    stored_hash = result[0]
                    try:
                        ph.verify(stored_hash, senha)
                        print("✅ Login testado com sucesso!")
                    except Exception as e:
                        print(f"❌ Erro no teste de login: {e}")
                else:
                    print("❌ Usuário não encontrado")
                    
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
    else:
        print("❌ Dados incompletos")

print("\n✅ Configuração concluída!")
print("\nPróximos passos:")
print("1. Execute: python criar_usuario.py")
print("2. Execute: python test_login.py")
print("3. Execute: streamlit run app.py")
