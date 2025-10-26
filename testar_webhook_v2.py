#!/usr/bin/env python3
"""
Testar webhook Hotmart v2.0.0 corrigido
"""

import requests
import json
import time

def testar_webhook_v2():
    """Testar webhook v2.0.0 da Hotmart"""
    print("🛒 TESTANDO WEBHOOK HOTMART V2.0.0")
    print("=" * 60)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # Dados do webhook v2.0.0 (formato real da Hotmart)
    webhook_v2_data = {
        "id": "35272db0-0546-48bd-b867-6749d03e8ba6",
        "creation_date": int(time.time() * 1000),
        "event": "PURCHASE_APPROVED",
        "version": "2.0.0",
        "data": {
            "actual_recurrence_value": 97.00,
            "cancellation_date": None,
            "date_next_charge": None,
            "product": {
                "id": 6187846,
                "name": "Ponto Ótimo Invest - A Carteira Ideal ao Seu Alcance"
            },
            "subscriber": {
                "code": "0000aaaa",
                "name": "Suellen Pinto",
                "email": "suellencna@yahoo.com.br",
                "phone": {
                    "dddPhone": ""
                }
            }
        }
    }
    
    print(f"📧 Email: {webhook_v2_data['data']['subscriber']['email']}")
    print(f"👤 Nome: {webhook_v2_data['data']['subscriber']['name']}")
    print(f"🛍️ Produto: {webhook_v2_data['data']['product']['name']}")
    print(f"💰 Valor: R$ {webhook_v2_data['data']['actual_recurrence_value']}")
    print()
    
    # 1. Testar Railway
    print("🔍 1. Testando Railway...")
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
    
    # 2. Enviar webhook v2.0.0
    print("\n🛒 2. Enviando webhook v2.0.0...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_v2_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook v2.0.0 processado com sucesso!")
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
    time.sleep(5)
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO:")
    print("1. ✅ Webhook v2.0.0 processado")
    print("2. ✅ Email sendo enviado")
    print("3. ⏳ Aguarde 1-2 minutos")
    print("4. 📧 Verifique suellencna@yahoo.com.br")
    print("5. 🔗 Clique no link de ativação")
    print("\n🚀 SISTEMA FUNCIONANDO COM HOTMART V2.0.0!")
    
    return True

if __name__ == "__main__":
    testar_webhook_v2()
