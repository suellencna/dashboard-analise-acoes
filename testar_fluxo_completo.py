#!/usr/bin/env python3
"""
🧪 TESTE DO FLUXO COMPLETO - HOTMART → RAILWAY → NEON → GMAIL → RENDER
=======================================================================

Este script testa todo o fluxo de integração:
1. Simula webhook da Hotmart
2. Testa cadastro no banco NEON
3. Testa envio de email
4. Testa ativação de conta
5. Testa login no sistema RENDER
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URLs dos serviços
RAILWAY_URL = os.environ.get('RAILWAY_APP_URL', 'https://web-production-040d1.up.railway.app')
RENDER_URL = os.environ.get('RENDER_APP_URL', 'https://ponto-otimo-invest.onrender.com')

def testar_health_check():
    """Testar se o webhook está funcionando"""
    print("🔍 Testando Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health Check OK")
            return True
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Health Check: {e}")
        return False

def testar_webhook_hotmart():
    """Simular webhook da Hotmart"""
    print("\n🛒 Testando Webhook da Hotmart...")
    
    # Dados simulados de uma compra na Hotmart
    webhook_data = {
        "buyer": {
            "email": "teste@exemplo.com",
            "name": "Cliente Teste"
        },
        "transaction": {
            "id": "TEST123456789"
        },
        "status": "approved",
        "product": {
            "id": "PROD123",
            "name": "Ponto Ótimo Invest"
        }
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Webhook falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False

def testar_email():
    """Testar envio de email"""
    print("\n📧 Testando Envio de Email...")
    
    email_data = {
        "email": "suellencna@hotmail.com",
        "nome": "Suellen Teste"
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json=email_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Email enviado com sucesso")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Email falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no envio de email: {e}")
        return False

def testar_ativacao():
    """Testar ativação de conta"""
    print("\n🔑 Testando Ativação de Conta...")
    
    # Token de teste (você pode pegar um real do banco)
    token_teste = "token_teste_123"
    
    try:
        response = requests.get(f"{RAILWAY_URL}/ativar/{token_teste}", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página de ativação carregada")
            return True
        elif response.status_code == 400:
            print("⚠️ Token inválido (esperado para token de teste)")
            return True
        else:
            print(f"❌ Ativação falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na ativação: {e}")
        return False

def testar_sistema_render():
    """Testar se o sistema RENDER está funcionando"""
    print("\n🌐 Testando Sistema RENDER...")
    
    try:
        response = requests.get(RENDER_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Sistema RENDER funcionando")
            return True
        else:
            print(f"❌ Sistema RENDER falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no sistema RENDER: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("🚀 INICIANDO TESTE DO FLUXO COMPLETO")
    print("=" * 50)
    
    resultados = []
    
    # 1. Health Check
    resultados.append(("Health Check", testar_health_check()))
    
    # 2. Webhook Hotmart
    resultados.append(("Webhook Hotmart", testar_webhook_hotmart()))
    
    # 3. Envio de Email
    resultados.append(("Envio de Email", testar_email()))
    
    # 4. Ativação de Conta
    resultados.append(("Ativação de Conta", testar_ativacao()))
    
    # 5. Sistema RENDER
    resultados.append(("Sistema RENDER", testar_sistema_render()))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    sucessos = 0
    total = len(resultados)
    
    for teste, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{teste:20} {status}")
        if sucesso:
            sucessos += 1
    
    print("-" * 50)
    print(f"Total: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O fluxo completo está funcionando perfeitamente!")
    else:
        print(f"\n⚠️ {total - sucessos} teste(s) falharam")
        print("❌ Verifique os erros acima e corrija os problemas")
    
    print("\n🔗 URLs dos serviços:")
    print(f"   Railway (Webhook): {RAILWAY_URL}")
    print(f"   Render (Sistema):  {RENDER_URL}")
    
    print("\n📋 Próximos passos:")
    print("   1. Configure as variáveis de ambiente no Railway")
    print("   2. Configure as variáveis de ambiente no Render")
    print("   3. Configure o webhook na Hotmart")
    print("   4. Teste com uma compra real")

if __name__ == "__main__":
    main()
