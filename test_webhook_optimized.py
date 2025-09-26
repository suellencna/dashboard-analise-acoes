#!/usr/bin/env python3
"""
Script para testar o webhook otimizado
"""

import requests
import json
import time

# URL do webhook (ajuste conforme necessário)
WEBHOOK_URL = "https://analise-acoes-api-webhook.onrender.com"  # URL de produção
# WEBHOOK_URL = "http://localhost:5000"  # Para teste local

def test_webhook_performance():
    """Testa a performance do webhook"""
    print("=== TESTE DE PERFORMANCE DO WEBHOOK ===")
    
    # Dados de teste
    test_data = {
        "event": "PURCHASE_APPROVED",
        "data": {
            "buyer": {
                "email": "teste@exemplo.com",
                "name": "Usuário Teste"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Hotmart-Hottok": "test-token"  # Token de teste
    }
    
    # Teste de performance
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{WEBHOOK_URL}/webhook/hotmart",
            json=test_data,
            headers=headers,
            timeout=10  # Timeout de 10 segundos
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"✅ Resposta recebida em {response_time:.2f}s")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response_time > 5:
            print("⚠️  AVISO: Resposta demorou mais de 5 segundos!")
        else:
            print("✅ Performance OK!")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Webhook não respondeu em 10 segundos")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_health_check():
    """Testa o health check"""
    print("\n=== TESTE DE HEALTH CHECK ===")
    
    try:
        response = requests.get(f"{WEBHOOK_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")

def test_basic_endpoints():
    """Testa endpoints básicos"""
    print("\n=== TESTE DE ENDPOINTS BÁSICOS ===")
    
    try:
        response = requests.get(f"{WEBHOOK_URL}/", timeout=5)
        print(f"GET / - Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro no endpoint raiz: {e}")
    
    try:
        response = requests.get(f"{WEBHOOK_URL}/test", timeout=5)
        print(f"GET /test - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Erro no endpoint test: {e}")

if __name__ == "__main__":
    print("Iniciando testes do webhook otimizado...")
    test_health_check()
    test_basic_endpoints()
    test_webhook_performance()
    print("\nTestes concluídos!")
