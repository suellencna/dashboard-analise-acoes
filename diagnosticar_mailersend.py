#!/usr/bin/env python3
"""
Diagnóstico completo do MailerSend
"""

import os
import sys

print("=" * 80)
print("🔍 DIAGNÓSTICO MAILERSEND")
print("=" * 80)

# 1. Verificar variáveis de ambiente
print("\n1️⃣ VERIFICANDO VARIÁVEIS DE AMBIENTE:")
print("-" * 80)

MAILERSEND_API_KEY = os.environ.get('MAILERSEND_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@pontootimo.com.br')
APP_URL = os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')

if MAILERSEND_API_KEY:
    print(f"✅ MAILERSEND_API_KEY: Configurada ({MAILERSEND_API_KEY[:20]}...)")
else:
    print("❌ MAILERSEND_API_KEY: NÃO CONFIGURADA")
    
print(f"✅ FROM_EMAIL: {FROM_EMAIL}")
print(f"✅ APP_URL: {APP_URL}")

# 2. Testar importação do MailerSend
print("\n2️⃣ TESTANDO IMPORTAÇÃO MAILERSEND:")
print("-" * 80)

try:
    from mailersend import emails
    print("✅ Biblioteca 'mailersend' importada com sucesso")
except ImportError as e:
    print(f"❌ ERRO ao importar 'mailersend': {e}")
    print("   Execute: pip install mailersend==0.5.8")
    sys.exit(1)

# 3. Testar conexão com API
print("\n3️⃣ TESTANDO CONEXÃO COM API MAILERSEND:")
print("-" * 80)

if not MAILERSEND_API_KEY:
    print("❌ Impossível testar - API Key não configurada")
    sys.exit(1)

try:
    mailer = emails.NewEmail(MAILERSEND_API_KEY)
    print("✅ Objeto MailerSend criado com sucesso")
    
    # Tentar criar um email de teste (sem enviar)
    mail_body = {}
    mail_from = {
        "name": "Teste Diagnóstico",
        "email": FROM_EMAIL,
    }
    recipients = [
        {
            "name": "Teste",
            "email": "teste@exemplo.com",
        }
    ]
    
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Teste", mail_body)
    mailer.set_html_content("<p>Teste</p>", mail_body)
    
    print("✅ Email de teste montado com sucesso")
    print("✅ Estrutura do email válida")
    
except Exception as e:
    print(f"❌ ERRO ao criar email: {e}")
    sys.exit(1)

# 4. Tentar envio REAL
print("\n4️⃣ TENTANDO ENVIO REAL:")
print("-" * 80)
print("📧 Enviando para: suellencna@gmail.com")

try:
    mailer = emails.NewEmail(MAILERSEND_API_KEY)
    
    mail_body = {}
    mail_from = {
        "name": "Diagnóstico MailerSend",
        "email": FROM_EMAIL,
    }
    recipients = [
        {
            "name": "Suellen",
            "email": "suellencna@gmail.com",
        }
    ]
    
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("🔧 DIAGNÓSTICO - MailerSend Test", mail_body)
    mailer.set_html_content("""
        <html>
            <body>
                <h1>TESTE DE DIAGNÓSTICO</h1>
                <p>Se você recebeu este email, o MailerSend está funcionando!</p>
                <p><strong>Hora do envio:</strong> """ + str(os.popen('date').read()) + """</p>
            </body>
        </html>
    """, mail_body)
    
    print("\n📤 Enviando email...")
    response = mailer.send(mail_body)
    
    print("\n✅ RESPOSTA DO MAILERSEND:")
    print(f"   Response: {response}")
    print("\n✅ EMAIL ENVIADO COM SUCESSO!")
    print("   Aguarde 1-2 minutos e verifique a caixa de entrada do Gmail")
    
except Exception as e:
    print(f"\n❌ ERRO AO ENVIAR EMAIL:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")
    
    # Detalhes adicionais do erro
    import traceback
    print("\n📋 STACK TRACE COMPLETO:")
    print("-" * 80)
    traceback.print_exc()

print("\n" + "=" * 80)
print("🏁 DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)
