#!/usr/bin/env python3
"""
Teste simples de email para Hotmail
"""

import os
import sys
from email_service import testar_envio_email

# Configurar variáveis de ambiente
print("=== CONFIGURAÇÃO DE TESTE ===")
print("Digite a MAILERSEND_API_KEY (ou pressione Enter para usar a do Railway):")

try:
    api_key = input()
    if api_key.strip():
        os.environ['MAILERSEND_API_KEY'] = api_key
    else:
        print("Usando variável de ambiente do Railway...")
except:
    print("Usando variável de ambiente do Railway...")

os.environ['FROM_EMAIL'] = 'noreply@pontootimo.com.br'
os.environ['APP_URL'] = 'https://web-production-e66d.up.railway.app'

print("\n=== TESTE DE EMAIL PARA HOTMAIL ===")
print("📧 Enviando email de teste para suellencna@hotmail.com...")

try:
    sucesso, mensagem = testar_envio_email('suellencna@hotmail.com')
    
    if sucesso:
        print("✅ Email enviado com sucesso!")
        print("📬 Verifique a caixa de entrada e spam do Hotmail")
        print(f"📝 Mensagem: {mensagem}")
    else:
        print("❌ Erro ao enviar email:")
        print(f"   {mensagem}")
        
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    sys.exit(1)

