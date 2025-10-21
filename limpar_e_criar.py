#!/usr/bin/env python3
"""
Script para limpar o banco e criar um usuário correto
"""

import os
import sqlalchemy
from argon2 import PasswordHasher

print("=== LIMPEZA E CRIAÇÃO DE USUÁRIO ===")

# Solicitar URL do banco
print("Cole aqui a URL de conexão com o banco de dados Neon:")
print("Exemplo: postgresql://usuario:senha@host:porta/database")
DATABASE_URL = input("\nURL: ").strip()

if not DATABASE_URL:
    print("❌ URL não fornecida.")
    exit()

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    ph = PasswordHasher()
    
    with engine.connect() as conn:
        print("\n🔍 Verificando usuários existentes...")
        
        # Listar usuários existentes
        query = sqlalchemy.text("SELECT email, nome FROM usuarios")
        result = conn.execute(query)
        usuarios = result.fetchall()
        
        if usuarios:
            print("Usuários encontrados:")
            for usuario in usuarios:
                print(f"  - {usuario[0]} ({usuario[1]})")
            
            # Deletar todos os usuários
            print("\n🗑️  Deletando usuários...")
            query = sqlalchemy.text("DELETE FROM usuarios")
            result = conn.execute(query)
            conn.commit()
            print(f"✅ {result.rowcount} usuário(s) deletado(s)!")
        else:
            print("✅ Banco já está vazio.")
        
        # Criar novo usuário
        print("\n👤 Criando novo usuário...")
        nome = input("Nome: ").strip()
        email = input("Email: ").strip()
        senha = input("Senha: ").strip()
        
        if nome and email and senha:
            # Hashear a senha
            senha_hash = ph.hash(senha)
            
            # Inserir no banco
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
            
            print(f"✅ Usuário '{email}' criado com sucesso!")
            
            # Testar login
            print("\n🔐 Testando login...")
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
        else:
            print("❌ Dados incompletos")
            
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n✅ Processo concluído!")
