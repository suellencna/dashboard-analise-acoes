#!/usr/bin/env python3
"""
Testar envio de email para todos os provedores
"""

import os
from email_service import testar_envio_email
import time

# Configurar variáveis de ambiente
os.environ['FROM_EMAIL'] = 'noreply@pontootimo.com.br'
os.environ['APP_URL'] = 'https://web-production-e66d.up.railway.app'

emails_teste = [
    ("Gmail 1", "suellencna@gmail.com"),
    ("Yahoo", "suellencna@yahoo.com.br"),
    ("Hotmail", "suellencna@hotmail.com"),
    ("Gmail 2", "aaisuellen@gmail.com"),
    ("Outlook", "jorgehap@outlook.com"),
]

print("=" * 80)
print("📧 TESTE DE ENTREGABILIDADE - TODOS OS PROVEDORES")
print("=" * 80)

resultados = []

for provedor, email in emails_teste:
    print(f"\n📤 Enviando para {provedor} ({email})...")
    
    try:
        sucesso, mensagem = testar_envio_email(email)
        
        if sucesso:
            print(f"   ✅ ENVIADO - {mensagem}")
            resultados.append((provedor, email, "✅ ENVIADO", mensagem))
        else:
            print(f"   ❌ FALHOU - {mensagem}")
            resultados.append((provedor, email, "❌ FALHOU", mensagem))
            
    except Exception as e:
        print(f"   ❌ ERRO - {str(e)}")
        resultados.append((provedor, email, "❌ ERRO", str(e)))
    
    # Aguardar 2 segundos entre envios para evitar rate limit
    if email != emails_teste[-1][1]:
        time.sleep(2)

print("\n" + "=" * 80)
print("📊 RESUMO DOS ENVIOS")
print("=" * 80)
print(f"{'Provedor':<15} {'Email':<30} {'Status':<15}")
print("-" * 80)

for provedor, email, status, msg in resultados:
    print(f"{provedor:<15} {email:<30} {status:<15}")

print("-" * 80)

print("\n📝 INSTRUÇÕES:")
print("1. Aguarde 2-3 minutos")
print("2. Verifique INBOX e SPAM de TODOS os emails")
print("3. Me informe quais emails CHEGARAM")
print("4. Vamos identificar o padrão de bloqueio")

print("\n" + "=" * 80)
