#!/usr/bin/env python3
"""
Teste síncrono de email para diagnosticar problema
"""

import os
import smtplib
import ssl
import secrets
import hashlib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def enviar_email_sincrono():
    """Enviar email síncrono para teste"""
    print("📧 ENVIO SÍNCRONO DE EMAIL")
    print("=" * 50)
    
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
    GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not GMAIL_APP_PASSWORD:
        print("❌ GMAIL_APP_PASSWORD não configurada!")
        return False
    
    try:
        # Configurar SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        print(f"🔌 Conectando a {smtp_server}:{smtp_port}...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = f"Ponto Ótimo Investimentos <{GMAIL_EMAIL}>"
            msg['To'] = "suellencna@yahoo.com.br"
            msg['Subject'] = "Ative sua conta - Ponto Ótimo Investimentos"
            msg['Reply-To'] = GMAIL_EMAIL
            msg['X-Mailer'] = "Ponto Ótimo Investimentos System"
            msg['X-Priority'] = "3"
            
            # Gerar token e senha
            token = secrets.token_urlsafe(32)
            temp_password = secrets.token_urlsafe(8)
            
            # Corpo do email
            activation_link = f"https://streamlit-analise-acoes.onrender.com/?token={token}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #f8f9fa; padding: 30px; text-align: center; border: 1px solid #dee2e6;">
                    <h1 style="color: #333; margin: 0;">Bem-vindo ao Ponto Ótimo Investimentos</h1>
                </div>
                
                <div style="padding: 30px; background: white;">
                    <h2 style="color: #333;">Olá, Suellen Pinto!</h2>
                    
                    <p>Sua compra foi aprovada com sucesso! Para ativar sua conta e acessar o sistema, clique no link abaixo:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{activation_link}" 
                           style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Ativar Minha Conta
                        </a>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #dee2e6;">
                        <h3 style="color: #495057; margin-top: 0;">Suas Credenciais Temporárias:</h3>
                        <p><strong>Email:</strong> suellencna@yahoo.com.br</p>
                        <p><strong>Senha Temporária:</strong> <code style="background: #fff; padding: 2px 5px; border-radius: 3px; border: 1px solid #dee2e6;">{temp_password}</code></p>
                        <p style="color: #dc3545; font-size: 14px;"><strong>⚠️ Importante:</strong> Você será obrigado a trocar esta senha no primeiro login.</p>
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #0c5460; margin-top: 0;">🚀 O que você terá acesso:</h3>
                        <ul style="color: #0c5460;">
                            <li>Análise completa de ações brasileiras</li>
                            <li>Otimização de portfólio com Markowitz</li>
                            <li>Simulações Monte Carlo</li>
                            <li>Relatórios detalhados de investimentos</li>
                        </ul>
                    </div>
                    
                    <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                        Se você não fez esta compra, ignore este email.<br>
                        Este é um email automático, não responda diretamente.
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 12px; margin: 0;">
                        © 2025 Ponto Ótimo Investimentos. Todos os direitos reservados.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Enviar email
            print("📧 Enviando email...")
            server.send_message(msg)
            print("✅ Email enviado com sucesso!")
            
            print(f"\n🔗 Link de ativação: {activation_link}")
            print(f"🔑 Senha temporária: {temp_password}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE SÍNCRONO DE EMAIL")
    print("=" * 60)
    
    if enviar_email_sincrono():
        print("\n✅ EMAIL ENVIADO COM SUCESSO!")
        print("📧 Verifique suellencna@yahoo.com.br")
        print("🔗 Clique no link de ativação")
        print("🧪 Teste o login no sistema")
    else:
        print("\n❌ FALHA NO ENVIO DO EMAIL")
        print("💡 Verifique as credenciais do Gmail")
