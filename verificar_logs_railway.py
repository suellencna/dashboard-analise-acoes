#!/usr/bin/env python3
"""
Verificar logs e status do Railway
"""

import requests
import time

def verificar_railway_detalhado():
    """Verificação detalhada do Railway"""
    print("🔍 VERIFICAÇÃO DETALHADA DO RAILWAY")
    print("=" * 50)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # 1. Health check
    print("1. Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Testar página inicial
    print("\n2. Página inicial...")
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Página inicial OK")
        else:
            print(f"   ❌ Página inicial falhou: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar webhook com dados específicos
    print("\n3. Testando webhook específico...")
    webhook_data = {
        "buyer": {
            "email": "suellencna@yahoo.com.br",
            "name": "Teste Logs"
        },
        "transaction": {
            "id": f"LOGS_{int(time.time())}"
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
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Webhook OK: {result}")
        else:
            print(f"   ❌ Webhook falhou: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Aguardar e testar email
    print("\n4. Aguardando processamento (5 segundos)...")
    time.sleep(5)
    
    print("\n5. Testando email...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json={"email": "suellencna@yahoo.com.br", "nome": "Teste Logs"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Email OK: {result}")
        else:
            print(f"   ❌ Email falhou: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    verificar_railway_detalhado()
