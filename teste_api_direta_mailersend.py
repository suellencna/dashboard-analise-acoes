#!/usr/bin/env python3
"""
Teste direto da API MailerSend - Bypass limitação de emails registrados
Usa a API REST diretamente conforme documentação oficial
"""

import requests
import json
import os
import time

# Configurações
MAILERSEND_API_KEY = os.environ.get('MAILERSEND_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@pontootimo.com.br')
APP_URL = os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')
TEMPLATE_ID = '351ndgwyenxlzqx8'  # Seu template ID

def enviar_email_api_direta(email, nome):
    """
    Enviar email usando API REST direta do MailerSend
    Bypass limitação de emails registrados
    """
    
    try:
        url = "https://api.mailersend.com/v1/email"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {MAILERSEND_API_KEY}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Gerar token de ativação
        import secrets
        token = secrets.token_urlsafe(32)
        link_ativacao = f"{APP_URL}/ativar/{token}"
        
        # Payload conforme documentação oficial
        payload = {
            "from": {
                "email": FROM_EMAIL,
                "name": "Ponto Ótimo Invest"
            },
            "to": [
                {
                    "email": email,
                    "name": nome
                }
            ],
            "subject": "Ative sua conta - Ponto Ótimo Invest",
            "personalization": [
                {
                    "email": email,
                    "data": {
                        "nome": nome,
                        "link_ativacao": link_ativacao
                    }
                }
            ],
            "template_id": TEMPLATE_ID
        }
        
        print(f"📤 Enviando para {nome} ({email})...")
        print(f"🔗 Link: {link_ativacao}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 202:
            print(f"   ✅ ENVIADO - Status: {response.status_code}")
            message_id = response.headers.get('x-message-id', 'N/A')
            print(f"   📧 Message ID: {message_id}")
            return True, message_id, link_ativacao
        else:
            print(f"   ❌ FALHOU - Status: {response.status_code}")
            print(f"   📝 Resposta: {response.text[:200]}")
            return False, response.text, None
            
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        return False, str(e), None

def testar_todos_emails_api_direta():
    """
    Testar envio para todos os provedores usando API direta
    """
    
    emails_teste = [
        ("Gmail 1", "suellencna@gmail.com"),
        ("Yahoo", "suellencna@yahoo.com.br"),
        ("Hotmail", "suellencna@hotmail.com"),
        ("Gmail 2", "aaisuellen@gmail.com"),
        ("Outlook", "jorgehap@outlook.com"),
    ]
    
    print("=" * 80)
    print("📧 TESTE API DIRETA MAILERSEND - BYPASS LIMITAÇÃO")
    print("=" * 80)
    print(f"🔑 API Key: {MAILERSEND_API_KEY[:20]}...")
    print(f"📧 From: {FROM_EMAIL}")
    print(f"🎨 Template ID: {TEMPLATE_ID}")
    print("=" * 80)
    
    resultados = []
    links_gerados = []
    
    for provedor, email in emails_teste:
        print(f"\n📤 {provedor} ({email})")
        
        sucesso, mensagem, link = enviar_email_api_direta(email, provedor)
        
        if sucesso:
            resultados.append((provedor, email, "✅ ENVIADO"))
            if link:
                links_gerados.append((provedor, email, link))
        else:
            resultados.append((provedor, email, "❌ FALHOU"))
        
        # Aguardar entre envios para evitar rate limit
        time.sleep(3)
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS ENVIOS")
    print("=" * 80)
    
    for provedor, email, status in resultados:
        print(f"{status} {provedor:<15} {email}")
    
    # Salvar links gerados
    if links_gerados:
        print("\n🔗 LINKS DE ATIVAÇÃO GERADOS:")
        with open("links_ativacao_api_direta.txt", "w", encoding="utf-8") as f:
            for provedor, email, link in links_gerados:
                print(f"📧 {provedor} ({email}):")
                print(f"   {link}")
                f.write(f"Provedor: {provedor}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Link: {link}\n\n")
    
    print("\n" + "=" * 80)
    print("📝 PRÓXIMOS PASSOS:")
    print("1. Aguarde 2-3 minutos")
    print("2. Verifique TODOS os emails (inbox + spam)")
    print("3. Me informe quais emails CHEGARAM")
    print("4. Teste os links de ativação")
    print("=" * 80)

if __name__ == "__main__":
    if not MAILERSEND_API_KEY:
        print("❌ MAILERSEND_API_KEY não configurada!")
        print("Configure a variável de ambiente:")
        print("export MAILERSEND_API_KEY='sua_api_key_aqui'")
        exit(1)
    
    testar_todos_emails_api_direta()
