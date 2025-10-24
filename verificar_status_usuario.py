#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlalchemy

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
    print("✅ Conexão com banco estabelecida")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    exit()

email_teste = "aaisuellen@gmail.com"
token_teste = "TvO7L66q7sHgBUpq-y4oKgWqzQ3sKg0lMSp08031wqM"

print(f"\n🔍 Verificando status do usuário:")
print(f"📧 Email: {email_teste}")
print(f"🎫 Token: {token_teste}")

try:
    with engine.connect() as conn:
        # Verificar status atual do usuário
        query_status = sqlalchemy.text("""
            SELECT nome, email, status_conta, status_assinatura, token_ativacao, data_expiracao_token
            FROM usuarios 
            WHERE email = :email
        """)
        result = conn.execute(query_status, {"email": email_teste}).first()
        
        if result:
            nome, email, status_conta, status_assinatura, token, expiracao = result
            print(f"\n📊 Status atual:")
            print(f"   Nome: {nome}")
            print(f"   Email: {email}")
            print(f"   Status conta: {status_conta}")
            print(f"   Status assinatura: {status_assinatura}")
            print(f"   Token: {token}")
            print(f"   Expiração: {expiracao}")
            
            # Verificar se o token ainda existe
            if token:
                print(f"\n⚠️ PROBLEMA: Token ainda existe no banco!")
                print(f"   Isso significa que a ativação não foi processada corretamente.")
            else:
                print(f"\n✅ Token foi removido (ativação processada)")
                
        else:
            print("❌ Usuário não encontrado no banco")
            
        # Verificar se há usuários com status pendente
        query_pendentes = sqlalchemy.text("""
            SELECT email, status_conta, token_ativacao
            FROM usuarios 
            WHERE status_conta = 'pendente'
        """)
        pendentes = conn.execute(query_pendentes).fetchall()
        
        if pendentes:
            print(f"\n📋 Usuários pendentes ({len(pendentes)}):")
            for p in pendentes:
                print(f"   - {p[0]} (token: {p[2][:20]}...)")
        else:
            print(f"\n✅ Nenhum usuário pendente encontrado")

except Exception as e:
    print(f"❌ Erro: {e}")
