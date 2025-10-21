#!/usr/bin/env python3
"""
Teste de email para suellencna@hotmail.com
"""

import os
from email_service import testar_envio_email

# Configurar variáveis de ambiente
os.environ['MAILERSEND_API_KEY'] = input('MAILERSEND_API_KEY: ')
os.environ['FROM_EMAIL'] = 'noreply@pontootimo.com.br'
os.environ['APP_URL'] = 'https://web-production-e66d.up.railway.app'

print("=== TESTE DE EMAIL PARA HOTMAIL ===")
print("📧 Enviando email de teste para suellencna@hotmail.com...")

sucesso, mensagem = testar_envio_email('suellencna@hotmail.com')

if sucesso:
    print("✅ Email enviado com sucesso!")
    print("📬 Verifique a caixa de entrada e spam do Hotmail")
else:
    print("❌ Erro ao enviar email:")
    print(f"   {mensagem}")

