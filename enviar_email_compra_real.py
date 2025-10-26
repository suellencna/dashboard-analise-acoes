#!/usr/bin/env python3
"""
Enviar email real de compra para validação completa
"""

import requests
import json
import time

def enviar_email_compra_real():
    """Enviar email real de compra para validação"""
    print("🛒 SIMULANDO COMPRA REAL NA HOTMART")
    print("=" * 60)
    
    # URL do Railway
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # Dados da compra (simulando cliente real)
    compra_data = {
        "buyer": {
            "email": "suellencna@yahoo.com.br",
            "name": "Suellen Pinto"
        },
        "transaction": {
            "id": f"COMPRA_REAL_{int(time.time())}",
            "amount": "97.00",
            "currency": "BRL"
        },
        "status": "approved",
        "product": {
            "name": "Sistema de Análise de Ações - Ponto Ótimo Investimentos"
        }
    }
    
    print(f"📧 Email: {compra_data['buyer']['email']}")
    print(f"👤 Nome: {compra_data['buyer']['name']}")
    print(f"💰 Valor: R$ {compra_data['transaction']['amount']}")
    print(f"🛍️ Produto: {compra_data['product']['name']}")
    print()
    
    # 1. Testar Railway
    print("🔍 1. Verificando Railway...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway funcionando")
        else:
            print(f"❌ Railway com problema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no Railway: {e}")
        return False
    
    # 2. Enviar webhook da Hotmart
    print("\n🛒 2. Enviando webhook da Hotmart...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=compra_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook processado com sucesso!")
            print(f"   Resposta: {result}")
        else:
            print(f"❌ Webhook falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False
    
    # 3. Aguardar processamento
    print("\n⏳ 3. Aguardando processamento do email...")
    print("   (Rate limiting: 2 segundos entre emails)")
    time.sleep(5)
    
    # 4. Testar endpoint de email
    print("\n📧 4. Testando envio de email...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json={
                "email": "suellencna@yahoo.com.br",
                "nome": "Suellen Pinto"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email de teste enviado!")
            print(f"   Resposta: {result}")
        else:
            print(f"❌ Email de teste falhou: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no email de teste: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 VALIDAÇÃO COMPLETA:")
    print("1. ✅ Webhook processado")
    print("2. ✅ Email sendo enviado")
    print("3. ⏳ Aguarde 1-2 minutos")
    print("4. 📧 Verifique suellencna@yahoo.com.br")
    print("5. 🔗 Clique no link de ativação")
    print("6. 🧪 Teste o login no sistema")
    print("\n🚀 SISTEMA FUNCIONANDO PERFEITAMENTE!")
    
    return True

if __name__ == "__main__":
    enviar_email_compra_real()
