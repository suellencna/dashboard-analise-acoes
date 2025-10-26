#!/usr/bin/env python3
"""
Script para verificar logs e status do Railway
"""

import requests
import json
import time

def verificar_status_railway():
    """Verificar status completo do Railway"""
    print("🔍 VERIFICANDO STATUS DO RAILWAY")
    print("=" * 50)
    
    base_url = "https://web-production-040d1.up.railway.app"
    
    # 1. Health Check
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health Check OK")
        else:
            print(f"   ❌ Health Check falhou: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Testar webhook com dados simples
    print("\n2. Testando webhook...")
    webhook_data = {
        "buyer": {
            "email": "teste@exemplo.com",
            "name": "Teste Usuario"
        },
        "transaction": {
            "id": f"TEST_{int(time.time())}"
        },
        "status": "approved"
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/hotmart",
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
        print(f"   ❌ Erro no webhook: {e}")
    
    # 3. Testar endpoint de teste de email
    print("\n3. Testando endpoint de email...")
    try:
        response = requests.post(
            f"{base_url}/test-email",
            json={"email": "teste@exemplo.com", "nome": "Teste"},
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
        print(f"   ❌ Erro no email: {e}")

if __name__ == "__main__":
    verificar_status_railway()
