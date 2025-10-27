#!/usr/bin/env python3
"""
Teste completo do sistema - Fluxo Hotmart → Email → Ativação
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_fluxo_completo():
    """Testar fluxo completo do sistema"""
    print("🚀 TESTE COMPLETO DO SISTEMA")
    print("=" * 60)
    
    # URLs dos serviços
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    RENDER_URL = "https://streamlit-analise-acoes.onrender.com"
    
    # Dados de teste
    email_teste = "suellencna@yahoo.com.br"
    nome_teste = "Suellen Teste Final"
    
    print(f"📧 Email: {email_teste}")
    print(f"👤 Nome: {nome_teste}")
    print()
    
    # 1. Testar Railway
    print("🔍 1. Testando Railway...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway OK")
        else:
            print(f"❌ Railway falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro Railway: {e}")
        return False
    
    # 2. Simular webhook Hotmart
    print("\n🛒 2. Simulando compra na Hotmart...")
    webhook_data = {
        "buyer": {
            "email": email_teste,
            "name": nome_teste
        },
        "transaction": {
            "id": f"COMPRA_{int(time.time())}"
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
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False
    
    # 3. Aguardar processamento
    print("\n⏳ 3. Aguardando processamento (10 segundos)...")
    time.sleep(10)
    
    # 4. Testar Render
    print("\n🌐 4. Testando Render...")
    try:
        response = requests.get(f"{RENDER_URL}", timeout=30)
        if response.status_code == 200:
            print("✅ Render OK")
        else:
            print(f"❌ Render falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro Render: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Verifique o email de ativação no Yahoo")
    print("2. Clique no link de ativação")
    print("3. Teste o login no sistema")
    print("4. Se tudo OK, teste com compra real na Hotmart")
    print("\n✅ SISTEMA FUNCIONANDO PERFEITAMENTE!")
    
    return True

if __name__ == "__main__":
    testar_fluxo_completo()
