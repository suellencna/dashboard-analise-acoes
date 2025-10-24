#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlalchemy
from argon2 import PasswordHasher

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
senha_teste = "Lt57o8BB7Q4"

print(f"\n🔍 Verificando senha atual:")
print(f"📧 Email: {email_teste}")
print(f"🔑 Senha: {senha_teste}")

try:
    with engine.connect() as conn:
        # Verificar dados do usuário
        query_status = sqlalchemy.text("""
            SELECT nome, email, status_conta, status_assinatura, senha_hash
            FROM usuarios 
            WHERE email = :email
        """)
        result = conn.execute(query_status, {"email": email_teste}).first()
        
        if result:
            nome, email, status_conta, status_assinatura, senha_hash = result
            print(f"\n📊 Dados do usuário:")
            print(f"   Nome: {nome}")
            print(f"   Email: {email}")
            print(f"   Status conta: {status_conta}")
            print(f"   Status assinatura: {status_assinatura}")
            print(f"   Senha hash: {senha_hash[:50]}...")
            
            # Testar senha atual
            print(f"\n🧪 Testando senha:")
            try:
                ph.verify(senha_hash, senha_teste)
                print(f"✅ Senha '{senha_teste}' está CORRETA!")
                print(f"✅ Login deve funcionar!")
            except Exception as e:
                print(f"❌ Senha '{senha_teste}' está INCORRETA: {e}")
                
                # Gerar nova senha simples
                import secrets
                nova_senha = "123456"  # Senha simples para teste
                nova_senha_hash = ph.hash(nova_senha)
                
                print(f"\n🔧 Gerando nova senha simples: {nova_senha}")
                
                # Atualizar senha
                query_update = sqlalchemy.text("""
                    UPDATE usuarios 
                    SET senha_hash = :senha_hash 
                    WHERE email = :email
                """)
                conn.execute(query_update, {
                    "senha_hash": nova_senha_hash,
                    "email": email_teste
                })
                conn.commit()
                
                print(f"✅ Nova senha atualizada: {nova_senha}")
                
                # Salvar credenciais
                with open("credenciais_simples.txt", "w") as f:
                    f.write(f"Email: {email}\n")
                    f.write(f"Senha: {nova_senha}\n")
                    f.write(f"Link: https://streamlit-analise-acoes.onrender.com/\n")
                
                print(f"💾 Credenciais salvas em: credenciais_simples.txt")
                
        else:
            print("❌ Usuário não encontrado no banco")

except Exception as e:
    print(f"❌ Erro: {e}")
