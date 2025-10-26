#!/usr/bin/env python3
"""
Script para diagnosticar problemas de email
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_conexao_gmail():
    """Testar conexão direta com Gmail SMTP"""
    print("🔍 DIAGNÓSTICO DE EMAIL - GMAIL SMTP")
    print("=" * 50)
    
    # Configurações
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
    GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    
    print(f"📧 Email: {GMAIL_EMAIL}")
    print(f"🔑 Senha: {'✅ Configurada' if GMAIL_APP_PASSWORD else '❌ NÃO CONFIGURADA'}")
    print()
    
    if not GMAIL_APP_PASSWORD:
        print("❌ ERRO: GMAIL_APP_PASSWORD não está configurada!")
        print("💡 Configure no arquivo .env:")
        print("   GMAIL_APP_PASSWORD=sua_senha_de_app")
        return False
    
    # Testar conexão SMTP
    print("🔌 Testando conexão SMTP...")
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Criar contexto SSL
        context = ssl.create_default_context()
        
        # Conectar ao servidor
        print(f"   Conectando a {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Iniciar TLS
        print("   Iniciando TLS...")
        server.starttls(context=context)
        
        # Fazer login
        print("   Fazendo login...")
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        
        print("✅ Conexão SMTP OK!")
        
        # Testar envio de email simples
        print("\n📧 Testando envio de email...")
        
        # Criar mensagem de teste
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = "suellencna@yahoo.com.br"
        msg['Subject'] = "Teste de Conexão - Ponto Ótimo Investimentos"
        
        body = """
        <html>
        <body>
            <h2>Teste de Conexão SMTP</h2>
            <p>Este é um email de teste para verificar se a conexão com Gmail está funcionando.</p>
            <p>Se você recebeu este email, a configuração está correta!</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # Enviar email
        server.send_message(msg)
        print("✅ Email de teste enviado com sucesso!")
        
        # Fechar conexão
        server.quit()
        print("✅ Conexão fechada com sucesso!")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ ERRO DE AUTENTICAÇÃO: {e}")
        print("💡 Verifique se:")
        print("   - A senha de app está correta")
        print("   - A verificação em 2 etapas está ativada")
        print("   - A senha de app foi gerada corretamente")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ ERRO DE DESTINATÁRIO: {e}")
        print("💡 Verifique se o email de destino está correto")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ ERRO SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

def verificar_logs_railway():
    """Verificar logs do Railway para erros de email"""
    print("\n🔍 VERIFICANDO LOGS DO RAILWAY...")
    print("=" * 50)
    
    import requests
    
    try:
        # Testar health check
        response = requests.get("https://web-production-040d1.up.railway.app/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway está online")
        else:
            print(f"❌ Railway com problemas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Railway: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO DE EMAIL")
    print("=" * 60)
    
    # Testar conexão Gmail
    gmail_ok = testar_conexao_gmail()
    
    # Verificar Railway
    verificar_logs_railway()
    
    print("\n" + "=" * 60)
    if gmail_ok:
        print("✅ DIAGNÓSTICO CONCLUÍDO: Gmail funcionando!")
        print("💡 O problema pode estar no Railway ou no processamento do webhook")
    else:
        print("❌ DIAGNÓSTICO CONCLUÍDO: Problema na configuração do Gmail")
        print("💡 Verifique as credenciais e tente novamente")
