#!/usr/bin/env python3
"""
TESTE DO SISTEMA EXECUTÁVEL - PONTO ÓTIMO INVEST
===============================================

Este script testa o sistema executável local.
Execute após iniciar o sistema_completo_executavel.py
"""

import requests
import json
import time

# Configurações
LOCAL_URL = "http://localhost:5000"
TEST_EMAIL = "suellencna@hotmail.com"
TEST_NAME = "Suellen Teste Local"

print("🧪 TESTE DO SISTEMA EXECUTÁVEL")
print("=" * 40)

def test_health_check():
    """Testar health check"""
    print("\n🔍 Testando Health Check...")
    try:
        response = requests.get(f"{LOCAL_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health Check OK: {response.text}")
            return True
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Health Check: {e}")
        return False

def test_email_sending():
    """Testar envio de email"""
    print("\n📧 Testando Envio de Email...")
    payload = {
        "email": TEST_EMAIL,
        "nome": TEST_NAME
    }
    try:
        response = requests.post(f"{LOCAL_URL}/test-email", json=payload, timeout=30)
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Mensagem: {data.get('message')}")
        if data.get('status') == 'success':
            print("✅ Teste de email bem-sucedido!")
            return True
        else:
            print(f"❌ Teste de email falhou: {data.get('details')}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de email: {e}")
        return False

def simulate_hotmart_webhook():
    """Simular webhook Hotmart"""
    print("\n🔄 Simulando Webhook Hotmart...")
    payload = {
        "id": "EV12345678",
        "event": "PURCHASE_APPROVED",
        "status": "approved",
        "product": {
            "id": 12345,
            "name": "Produto Teste Ponto Ótimo"
        },
        "buyer": {
            "email": TEST_EMAIL,
            "name": TEST_NAME,
            "checkout_phone": "5511987654321"
        },
        "purchase": {
            "price": 99.90,
            "currency": "BRL"
        }
    }
    try:
        response = requests.post(f"{LOCAL_URL}/webhook", json=payload, timeout=30)
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Mensagem: {data.get('message')}")
        if response.status_code == 200 and data.get('status') == 'success':
            print("✅ Simulação de webhook bem-sucedida!")
            return True
        else:
            print(f"❌ Simulação de webhook falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na simulação de webhook: {e}")
        return False

def main():
    """Função principal de teste"""
    print("Aguardando sistema iniciar...")
    time.sleep(2)
    
    # Testar health check
    if not test_health_check():
        print("\n❌ Sistema não está funcionando. Verifique se o sistema_completo_executavel.py está rodando.")
        return
    
    # Testar envio de email
    test_email_sending()
    
    # Simular webhook
    simulate_hotmart_webhook()
    
    print("\n🎉 Teste concluído!")
    print("📝 Verifique os logs do sistema para mais detalhes.")
    print("📧 Verifique o email para o link de ativação.")

if __name__ == "__main__":
    main()
