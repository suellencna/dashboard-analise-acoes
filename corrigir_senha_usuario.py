#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlalchemy
from argon2 import PasswordHasher
import secrets

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

email_teste = "aaisuellen@gmail.com"

print(f"\n🔧 Corrigindo senha do usuário:")
print(f"📧 Email: {email_teste}")

try:
    with engine.connect() as conn:
        # Gerar nova senha temporária
        senha_temporaria = secrets.token_urlsafe(8)
        senha_hash = ph.hash(senha_temporaria)
        
        print(f"🔑 Nova senha temporária: {senha_temporaria}")
        
        # Atualizar senha no banco
        query_update = sqlalchemy.text("""
            UPDATE usuarios 
            SET senha_hash = :senha_hash 
            WHERE email = :email
        """)
        
        result = conn.execute(query_update, {
            "senha_hash": senha_hash,
            "email": email_teste
        })
        conn.commit()
        
        if result.rowcount > 0:
            print("✅ Senha atualizada com sucesso!")
            
            # Verificar atualização
            query_verify = sqlalchemy.text("""
                SELECT nome, email, status_conta, senha_hash
                FROM usuarios 
                WHERE email = :email
            """)
            result = conn.execute(query_verify, {"email": email_teste}).first()
            
            if result:
                nome, email, status, senha_hash_db = result
                print(f"\n📊 Verificação:")
                print(f"   Nome: {nome}")
                print(f"   Email: {email}")
                print(f"   Status: {status}")
                print(f"   Senha hash: {senha_hash_db[:20]}...")
                
                # Salvar credenciais para teste
                with open("credenciais_teste.txt", "w") as f:
                    f.write(f"Email: {email}\n")
                    f.write(f"Senha: {senha_temporaria}\n")
                    f.write(f"Link: https://streamlit-analise-acoes.onrender.com/\n")
                
                print(f"\n💾 Credenciais salvas em: credenciais_teste.txt")
                print(f"🔑 Email: {email}")
                print(f"🔑 Senha: {senha_temporaria}")
                
        else:
            print("❌ Nenhuma linha foi atualizada")

except Exception as e:
    print(f"❌ Erro: {e}")
