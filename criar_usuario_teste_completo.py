#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlalchemy
from argon2 import PasswordHasher
import secrets
from datetime import datetime, timedelta

# Carregar variáveis de ambiente
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada")
    exit()

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    ph = PasswordHasher()
    print("✅ Conexão com banco estabelecida")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    exit()

# Dados do usuário de teste
email_teste = "aaisuellen@gmail.com"
nome_teste = "Suellen Teste"

print(f"\n🧪 Criando usuário de teste:")
print(f"📧 Email: {email_teste}")
print(f"👤 Nome: {nome_teste}")

try:
    with engine.connect() as conn:
        # Verificar se usuário já existe
        query_check = sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email")
        result = conn.execute(query_check, {"email": email_teste}).first()
        
        if result:
            print("⚠️ Usuário já existe. Removendo...")
            # Remover usuário existente
            query_delete = sqlalchemy.text("DELETE FROM usuarios WHERE email = :email")
            conn.execute(query_delete, {"email": email_teste})
            conn.commit()
            print("✅ Usuário removido")
        
        # Gerar token de ativação
        token_ativacao = secrets.token_urlsafe(32)
        data_expiracao = datetime.now() + timedelta(hours=48)
        
        print(f"🎫 Token gerado: {token_ativacao}")
        print(f"⏰ Expira em: {data_expiracao}")
        
        # Criar novo usuário
        query_insert = sqlalchemy.text("""
            INSERT INTO usuarios 
            (nome, email, status_assinatura, status_conta, token_ativacao, data_expiracao_token, senha_hash) 
            VALUES 
            (:nome, :email, 'ativo', 'pendente', :token, :expiracao, 'TEMP_PASSWORD_TO_BE_CHANGED')
        """)
        
        conn.execute(query_insert, {
            "nome": nome_teste,
            "email": email_teste,
            "token": token_ativacao,
            "expiracao": data_expiracao
        })
        conn.commit()
        
        print("✅ Usuário criado com sucesso!")
        print(f"📊 Status: pendente (aguardando ativação)")
        
        # Verificar criação
        query_verify = sqlalchemy.text("""
            SELECT nome, email, status_conta, token_ativacao 
            FROM usuarios 
            WHERE email = :email
        """)
        result = conn.execute(query_verify, {"email": email_teste}).first()
        
        if result:
            nome, email, status, token = result
            print(f"\n📋 Verificação:")
            print(f"   Nome: {nome}")
            print(f"   Email: {email}")
            print(f"   Status: {status}")
            print(f"   Token: {token}")
            
            # Salvar token para envio de email
            with open("token_ativacao_teste.txt", "w") as f:
                f.write(f"Token: {token}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Link: https://streamlit-analise-acoes.onrender.com/?token={token}\n")
            
            print(f"\n💾 Token salvo em: token_ativacao_teste.txt")
            print(f"🔗 Link de ativação: https://streamlit-analise-acoes.onrender.com/?token={token}")
            
        else:
            print("❌ Erro: Usuário não foi criado corretamente")

except Exception as e:
    print(f"❌ Erro: {e}")
