#!/usr/bin/env python3
"""
TESTE DO SISTEMA DE VENDAS - PONTO ÓTIMO INVEST
==============================================

Este script testa o sistema de vendas com validação de compra.
Execute após iniciar o sistema_vendas_executavel.py
"""

import requests
import json
import time

# Configurações
LOCAL_URL = "http://localhost:5000"
TEST_EMAIL = "cliente@teste.com"
TEST_NAME = "Cliente Teste"
TEST_PRODUTO_ID = "PROD123"
TEST_VALOR = 99.90

print("🛒 TESTE DO SISTEMA DE VENDAS")
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

def test_email_boas_vindas():
    """Testar email de boas-vindas"""
    print("\n📧 Testando Email de Boas-vindas...")
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
            print("✅ Email de boas-vindas enviado!")
            return True
        else:
            print(f"❌ Email falhou: {data.get('details')}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de email: {e}")
        return False

def simulate_compra_aprovada():
    """Simular compra aprovada"""
    print("\n💰 Simulando Compra Aprovada...")
    payload = {
        "id": "EV12345678",
        "event": "PURCHASE_APPROVED",
        "status": "approved",
        "product": {
            "id": TEST_PRODUTO_ID,
            "name": "Ponto Ótimo Invest - Análise de Ações"
        },
        "buyer": {
            "email": TEST_EMAIL,
            "name": TEST_NAME,
            "checkout_phone": "5511987654321"
        },
        "purchase": {
            "price": TEST_VALOR,
            "currency": "BRL"
        }
    }
    try:
        response = requests.post(f"{LOCAL_URL}/webhook", json=payload, timeout=30)
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Mensagem: {data.get('message')}")
        if response.status_code == 200 and data.get('status') == 'success':
            print("✅ Compra aprovada processada!")
            print("📧 Email de boas-vindas deve ter sido enviado")
            print("🎫 Token de acesso deve ter sido gerado")
            return True
        else:
            print(f"❌ Processamento da compra falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na simulação de compra: {e}")
        return False

def simulate_compra_cancelada():
    """Simular compra cancelada"""
    print("\n❌ Simulando Compra Cancelada...")
    payload = {
        "id": "EV12345679",
        "event": "PURCHASE_CANCELED",
        "status": "canceled",
        "product": {
            "id": TEST_PRODUTO_ID,
            "name": "Ponto Ótimo Invest - Análise de Ações"
        },
        "buyer": {
            "email": TEST_EMAIL,
            "name": TEST_NAME
        },
        "purchase": {
            "price": TEST_VALOR,
            "currency": "BRL"
        }
    }
    try:
        response = requests.post(f"{LOCAL_URL}/webhook", json=payload, timeout=30)
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Mensagem: {data.get('message')}")
        if response.status_code == 200 and data.get('status') == 'success':
            print("✅ Compra cancelada processada!")
            print("🚫 Acesso deve ter sido revogado")
            return True
        else:
            print(f"❌ Processamento do cancelamento falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na simulação de cancelamento: {e}")
        return False

def test_validacao_acesso():
    """Testar validação de acesso"""
    print("\n🔐 Testando Validação de Acesso...")
    # Simular token de acesso (em um sistema real, viria do banco)
    token_teste = "token_teste_123"
    
    try:
        response = requests.get(f"{LOCAL_URL}/validar?token={token_teste}", timeout=10)
        if response.status_code == 200:
            print("✅ Página de validação carregada!")
            print("📄 Verifique no navegador: http://localhost:5000/validar?token=token_teste_123")
            return True
        else:
            print(f"❌ Página de validação falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na validação de acesso: {e}")
        return False

def main():
    """Função principal de teste"""
    print("Aguardando sistema de vendas iniciar...")
    time.sleep(2)
    
    # Testar health check
    if not test_health_check():
        print("\n❌ Sistema não está funcionando. Verifique se o sistema_vendas_executavel.py está rodando.")
        return
    
    # Testar email de boas-vindas
    test_email_boas_vindas()
    
    # Simular compra aprovada
    simulate_compra_aprovada()
    
    # Aguardar processamento
    print("\n⏳ Aguardando processamento da compra...")
    time.sleep(3)
    
    # Simular compra cancelada
    simulate_compra_cancelada()
    
    # Testar validação de acesso
    test_validacao_acesso()
    
    print("\n🎉 Teste do sistema de vendas concluído!")
    print("📝 Verifique os logs do sistema para mais detalhes.")
    print("📧 Verifique o email para o link de boas-vindas.")
    print("🌐 Acesse: http://localhost:5000 para ver o sistema funcionando.")

if __name__ == "__main__":
    main()
