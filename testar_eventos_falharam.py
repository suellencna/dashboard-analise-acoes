#!/usr/bin/env python3
"""
Testar eventos que falharam na Hotmart
"""

import requests
import json
import time

def testar_purchase_protest():
    """Testar evento PURCHASE_PROTEST"""
    print("🛒 TESTANDO PURCHASE_PROTEST")
    print("=" * 50)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # Dados reais do PURCHASE_PROTEST
    webhook_data = {
        "id": "e4135d7d-a713-4200-8a2e-dae8e9f80280",
        "creation_date": int(time.time() * 1000),
        "event": "PURCHASE_PROTEST",
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
                "status": "DISPUTE"
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
            print("✅ PURCHASE_PROTEST processado com sucesso!")
            print(f"Resposta: {result}")
        else:
            print(f"❌ Falhou: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_purchase_canceled():
    """Testar evento PURCHASE_CANCELED"""
    print("\n🛒 TESTANDO PURCHASE_CANCELED")
    print("=" * 50)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # Dados reais do PURCHASE_CANCELED
    webhook_data = {
        "id": "686abd46-a216-4498-ad54-a91d8514fbc2",
        "creation_date": int(time.time() * 1000),
        "event": "PURCHASE_CANCELED",
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
                "status": "CANCELED"
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
            print("✅ PURCHASE_CANCELED processado com sucesso!")
            print(f"Resposta: {result}")
        else:
            print(f"❌ Falhou: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 TESTANDO EVENTOS QUE FALHARAM")
    print("=" * 60)
    
    # Aguardar deploy
    print("⏳ Aguardando deploy (30 segundos)...")
    time.sleep(30)
    
    # Testar PURCHASE_PROTEST
    testar_purchase_protest()
    
    # Testar PURCHASE_CANCELED
    testar_purchase_canceled()
    
    print("\n" + "=" * 60)
    print("🎯 TESTES CONCLUÍDOS!")
    print("✅ Verifique se os eventos foram processados corretamente")
    print("📧 Emails devem ser enviados para os endereços de teste")
