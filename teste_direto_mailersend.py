#!/usr/bin/env python3
"""
Teste DIRETO com MailerSend - usando API Key manualmente
"""

import sys

# Solicitar API Key
print("=" * 80)
print("🔑 TESTE DIRETO COM MAILERSEND")
print("=" * 80)
print("\nPara testar, precisamos da MAILERSEND_API_KEY")
print("Você pode encontrá-la em: https://app.mailersend.com/api-tokens")
print("\nCole a API Key abaixo (ou pressione Ctrl+C para cancelar):")
print("-" * 80)

try:
    api_key = input("MAILERSEND_API_KEY: ").strip()
    if not api_key:
        print("❌ API Key não fornecida!")
        sys.exit(1)
except KeyboardInterrupt:
    print("\n❌ Cancelado pelo usuário")
    sys.exit(1)

# Configurar ambiente
import os
os.environ['MAILERSEND_API_KEY'] = api_key
os.environ['FROM_EMAIL'] = 'noreply@pontootimo.com.br'

# Importar serviço de email
from email_service import testar_envio_email

emails_teste = [
    ("Gmail 1", "suellencna@gmail.com"),
    ("Yahoo", "suellencna@yahoo.com.br"),
    ("Hotmail", "suellencna@hotmail.com"),
    ("Gmail 2", "aaisuellen@gmail.com"),
    ("Outlook", "jorgehap@outlook.com"),
]

print("\n" + "=" * 80)
print("📧 ENVIANDO EMAILS DE TESTE")
print("=" * 80)

import time

resultados = []

for provedor, email in emails_teste:
    print(f"\n📤 {provedor} ({email})...")
    
    try:
        sucesso, mensagem = testar_envio_email(email)
        
        if sucesso:
            print(f"   ✅ ENVIADO")
            resultados.append((provedor, email, "✅"))
        else:
            print(f"   ❌ FALHOU: {mensagem}")
            resultados.append((provedor, email, "❌"))
            
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)[:100]}")
        resultados.append((provedor, email, "❌"))
    
    # Aguardar entre envios
    if email != emails_teste[-1][1]:
        time.sleep(2)

print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)

for provedor, email, status in resultados:
    print(f"{status} {provedor:<15} {email}")

print("\n📝 Aguarde 2-3 minutos e verifique TODOS os emails (inbox + spam)")
print("=" * 80)
