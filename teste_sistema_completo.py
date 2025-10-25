#!/usr/bin/env python3
"""
Script para testar o sistema completo
Hotmart → Railway → Neon → Email → Ativação
"""

import requests
import json
import time

# Configurações
RAILWAY_URL = "https://web-production-040d1.up.railway.app"
TEST_EMAIL = "suellencna@hotmail.com"
TEST_NOME = "Suellen Teste Completo"

def test_health_check():
    """Testar health check"""
    print("🔍 Testando Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health Check: {response.text}")
            return True
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Health Check: {e}")
        return False

def test_email_sending():
    """Testar envio de email"""
    print("\n📧 Testando envio de email...")
    try:
        data = {
            "email": TEST_EMAIL,
            "nome": TEST_NOME
        }
        
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email enviado: {result.get('message')}")
            print(f"📨 Token gerado: {result.get('token', 'N/A')[:20]}...")
            return result.get('token')
        else:
            print(f"❌ Erro ao enviar email: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro no envio de email: {e}")
        return None

def test_webhook_simulation():
    """Simular webhook do Hotmart"""
    print("\n🔄 Simulando webhook do Hotmart...")
    try:
        # Dados simulados do Hotmart
        webhook_data = {
            "event": "PURCHASE_APPROVED",
            "data": {
                "buyer": {
                    "email": TEST_EMAIL,
                    "name": TEST_NOME
                },
                "transaction": {
                    "id": f"TEST_{int(time.time())}"
                }
            }
        }
        
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook processado: {result.get('message')}")
            print(f"👤 Usuário: {result.get('nome')} ({result.get('email')})")
            return True
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False

def test_activation_link(token):
    """Testar link de ativação"""
    if not token:
        print("\n⚠️ Token não disponível para teste de ativação")
        return False
        
    print(f"\n🔗 Testando link de ativação...")
    try:
        response = requests.get(f"{RAILWAY_URL}/ativar/{token}", timeout=10)
        
        if response.status_code == 200:
            print("✅ Link de ativação funcionando!")
            print("📄 Página de ativação carregada com sucesso")
            return True
        else:
            print(f"❌ Erro no link de ativação: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no link de ativação: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA")
    print("=" * 50)
    
    # Teste 1: Health Check
    health_ok = test_health_check()
    if not health_ok:
        print("\n❌ Sistema não está funcionando. Parando testes.")
        return
    
    # Teste 2: Envio de email
    token = test_email_sending()
    
    # Teste 3: Simulação de webhook
    webhook_ok = test_webhook_simulation()
    
    # Teste 4: Link de ativação
    if token:
        activation_ok = test_activation_link(token)
    else:
        activation_ok = False
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES:")
    print(f"✅ Health Check: {'OK' if health_ok else 'FALHOU'}")
    print(f"📧 Email: {'OK' if token else 'FALHOU'}")
    print(f"🔄 Webhook: {'OK' if webhook_ok else 'FALHOU'}")
    print(f"🔗 Ativação: {'OK' if activation_ok else 'FALHOU'}")
    
    if all([health_ok, token, webhook_ok, activation_ok]):
        print("\n🎉 SISTEMA COMPLETO FUNCIONANDO!")
        print("✅ Pronto para receber compras do Hotmart!")
    else:
        print("\n⚠️ SISTEMA COM PROBLEMAS")
        print("❌ Verifique os logs do Railway")

if __name__ == "__main__":
    main()
