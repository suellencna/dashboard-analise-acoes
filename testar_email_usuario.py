#!/usr/bin/env python3
"""
Script para testar envio de email para usuário existente
"""

import os
import sys
import requests
import json
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URLs dos serviços
RAILWAY_URL = os.environ.get('RAILWAY_APP_URL', 'https://web-production-040d1.up.railway.app')

def testar_envio_email_usuario():
    """Testar envio de email para usuário específico"""
    print("🧪 TESTE DE ENVIO DE EMAIL PARA USUÁRIO EXISTENTE")
    print("=" * 60)
    
    # Dados do usuário de teste
    email_teste = "suellencna@yahoo.com.br"
    nome_teste = "Suellen Teste"
    
    print(f"📧 Email de destino: {email_teste}")
    print(f"👤 Nome: {nome_teste}")
    print()
    
    # 1. Testar Health Check
    print("🔍 1. Testando Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health Check OK")
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Health Check: {e}")
        return False
    
    # 2. Simular webhook da Hotmart
    print("\n🛒 2. Simulando webhook da Hotmart...")
    webhook_data = {
        "buyer": {
            "email": email_teste,
            "name": nome_teste
        },
        "transaction": {
            "id": f"TEST_{int(time.time())}"
        },
        "status": "approved"
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook processado com sucesso")
            print(f"   Resposta: {result}")
        else:
            print(f"❌ Webhook falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False
    
    # 3. Aguardar processamento
    print("\n⏳ 3. Aguardando processamento do email...")
    time.sleep(5)
    
    # 4. Testar endpoint de teste de email
    print("\n📧 4. Testando endpoint de teste de email...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json={"email": email_teste, "nome": nome_teste},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email de teste enviado com sucesso")
            print(f"   Resposta: {result}")
        else:
            print(f"❌ Email de teste falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no email de teste: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique sua caixa de entrada (suellencna@yahoo.com.br)")
    print("2. Procure por email do 'Ponto Ótimo Investimentos'")
    print("3. Clique no link de ativação")
    print("4. Teste o login no sistema")
    print("5. Se tudo OK, teste com compra real na Hotmart")
    
    return True

if __name__ == "__main__":
    testar_envio_email_usuario()
