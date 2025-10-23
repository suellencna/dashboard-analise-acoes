#!/usr/bin/env python3
"""
Teste Gmail SMTP via Railway
Usa os endpoints do Railway para testar
"""

import requests
import json

# URL do Railway
RAILWAY_URL = "https://web-production-e66d.up.railway.app"

def testar_email_simples():
    """Teste simples com um email"""
    
    print("=" * 60)
    print("📧 TESTE GMAIL SMTP VIA RAILWAY")
    print("=" * 60)
    
    email = input("Digite um email para teste: ").strip()
    if not email:
        email = "suellencna@gmail.com"
    
    print(f"\n📤 Testando envio para: {email}")
    print(f"🌐 URL: {RAILWAY_URL}/test-email?email={email}")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/test-email?email={email}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCESSO!")
            print(f"📧 Email: {data.get('email')}")
            print(f"📝 Mensagem: {data.get('message')}")
            print(f"🔧 Serviço: {data.get('email_service')}")
        else:
            print(f"\n❌ ERRO - Status: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

def testar_todos_provedores():
    """Teste completo com todos os provedores"""
    
    print("=" * 60)
    print("📧 TESTE COMPLETO GMAIL SMTP VIA RAILWAY")
    print("=" * 60)
    
    print(f"🌐 URL: {RAILWAY_URL}/test-email-all")
    print("📤 Enviando para todos os provedores...")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/test-email-all", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ TESTE COMPLETO REALIZADO!")
            print(f"📊 Total enviados: {data.get('total_enviados', 0)}")
            print(f"📊 Total falharam: {data.get('total_falharam', 0)}")
            print(f"🔧 Serviço: {data.get('email_service')}")
            
            print(f"\n📋 RESULTADOS:")
            for resultado in data.get('resultados', []):
                status = resultado.get('status', '❓')
                provedor = resultado.get('provedor', 'N/A')
                email = resultado.get('email', 'N/A')
                print(f"  {status} {provedor:<15} {email}")
            
            print(f"\n🔗 LINKS GERADOS:")
            for link_data in data.get('links_gerados', []):
                provedor = link_data.get('provedor', 'N/A')
                email = link_data.get('email', 'N/A')
                link = link_data.get('link', 'N/A')
                print(f"  📧 {provedor} ({email}):")
                print(f"     {link}")
                
        else:
            print(f"\n❌ ERRO - Status: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

if __name__ == "__main__":
    print("Escolha o teste:")
    print("1. Teste simples (um email)")
    print("2. Teste completo (todos os provedores)")
    
    opcao = input("Digite 1 ou 2: ").strip()
    
    if opcao == "1":
        testar_email_simples()
    elif opcao == "2":
        testar_todos_provedores()
    else:
        print("Opção inválida!")
