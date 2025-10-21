#!/usr/bin/env python3
"""
Script para testar o webhook localmente
"""

import requests
import json
import os

# URL base do webhook (ajuste conforme necessário)
BASE_URL = "http://localhost:5000"  # Para teste local
# BASE_URL = "https://analise-acoes-api-webhook.onrender.com"  # Para teste em produção

def test_basic_endpoints():
    """Testa os endpoints básicos"""
    print("=== Testando Endpoints Básicos ===")
    
    # Teste do endpoint raiz
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / - Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro no GET /: {e}")
    
    # Teste do endpoint de health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro no GET /health: {e}")
    
    # Teste do endpoint de teste
    try:
        response = requests.get(f"{BASE_URL}/test")
        print(f"GET /test - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro no GET /test: {e}")

def test_webhook_endpoint():
    """Testa o endpoint do webhook"""
    print("\n=== Testando Webhook Endpoint ===")
    
    # Dados de teste para o webhook
    test_data = {
        "event": "PURCHASE_APPROVED",
        "data": {
            "buyer": {
                "email": "teste@exemplo.com",
                "name": "Usuário Teste"
            }
        }
    }
    
    # Headers de teste (sem o HOTTOK real)
    headers = {
        "Content-Type": "application/json",
        "X-Hotmart-Hottok": "test-token"  # Token de teste
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/hotmart",
            json=test_data,
            headers=headers
        )
        print(f"POST /webhook/hotmart - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro no POST /webhook/hotmart: {e}")

def test_invalid_json():
    """Testa requisições com JSON inválido"""
    print("\n=== Testando JSON Inválido ===")
    
    headers = {
        "Content-Type": "application/json",
        "X-Hotmart-Hottok": "test-token"
    }
    
    # Teste com JSON malformado
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/hotmart",
            data="{'invalid': json}",  # JSON inválido
            headers=headers
        )
        print(f"POST com JSON inválido - Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro no teste de JSON inválido: {e}")

if __name__ == "__main__":
    print("Iniciando testes do webhook...")
    test_basic_endpoints()
    test_webhook_endpoint()
    test_invalid_json()
    print("\nTestes concluídos!")

