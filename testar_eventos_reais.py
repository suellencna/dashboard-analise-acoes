#!/usr/bin/env python3
"""
Testar eventos reais da Hotmart
"""

import requests
import json
import time

def testar_purchase_expired():
    """Testar evento PURCHASE_EXPIRED"""
    print("🛒 TESTANDO PURCHASE_EXPIRED")
    print("=" * 50)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # Dados reais do PURCHASE_EXPIRED
    webhook_data = {
        "id": "88934470-b868-45b4-900a-215246872ad0",
        "creation_date": int(time.time() * 1000),
        "event": "PURCHASE_EXPIRED",
        "version": "2.0.0",
        "data": {
            "product": {
                "id": 0,
                "ucode": "fb056612-bcc6-4217-9e6d-2a5d1110ac2f",
                "name": "Produto test postback2"
            },
            "buyer": {
                "email": "testeComprador271101postman15@example.com",
                "name": "Teste Comprador",
                "first_name": "Teste",
                "last_name": "Comprador"
            },
            "purchase": {
                "transaction": "HP16015479281022",
                "status": "EXPIRED"
            }
        }
    }
    
    print(f"📧 Email: {webhook_data['data']['buyer']['email']}")
    print(f"👤 Nome: {webhook_data['data']['buyer']['name']}")
    print(f"🛍️ Produto: {webhook_data['data']['product']['name']}")
    print(f"🔑 Transação: {webhook_data['data']['purchase']['transaction']}")
    print()
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ PURCHASE_EXPIRED processado com sucesso!")
            print(f"Resposta: {result}")
        else:
            print(f"❌ Falhou: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_subscription_cancellation():
    """Testar evento SUBSCRIPTION_CANCELLATION"""
    print("\n🛒 TESTANDO SUBSCRIPTION_CANCELLATION")
    print("=" * 50)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # Dados reais do SUBSCRIPTION_CANCELLATION
    webhook_data = {
        "id": "92c1cb51-775e-416d-8f79-61c046977203",
        "creation_date": int(time.time() * 1000),
        "event": "SUBSCRIPTION_CANCELLATION",
        "version": "2.0.0",
        "data": {
            "product": {
                "id": 788921,
                "name": "Product name com ç e á"
            },
            "subscriber": {
                "code": "0000aaaa",
                "name": "User name",
                "email": "test@hotmart.com"
            }
        }
    }
    
    print(f"📧 Email: {webhook_data['data']['subscriber']['email']}")
    print(f"👤 Nome: {webhook_data['data']['subscriber']['name']}")
    print(f"🛍️ Produto: {webhook_data['data']['product']['name']}")
    print()
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ SUBSCRIPTION_CANCELLATION processado com sucesso!")
            print(f"Resposta: {result}")
        else:
            print(f"❌ Falhou: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 TESTANDO EVENTOS REAIS DA HOTMART")
    print("=" * 60)
    
    # Aguardar deploy
    print("⏳ Aguardando deploy (30 segundos)...")
    time.sleep(30)
    
    # Testar PURCHASE_EXPIRED
    testar_purchase_expired()
    
    # Testar SUBSCRIPTION_CANCELLATION
    testar_subscription_cancellation()
    
    print("\n" + "=" * 60)
    print("🎯 TESTES CONCLUÍDOS!")
    print("✅ Verifique se os eventos foram processados corretamente")
    print("📧 Emails devem ser enviados para os endereços de teste")
