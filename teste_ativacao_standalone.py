#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
from datetime import datetime, timedelta

def enviar_email_ativacao_standalone():
    """Enviar email de ativação com HTML standalone"""
    
    # Configurações Gmail SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_remetente = "pontootimoinvest@gmail.com"
    senha_app = os.getenv("GMAIL_APP_PASSWORD", "snbo xxle cero dloe")
    
    if not senha_app:
        print("❌ GMAIL_APP_PASSWORD não encontrada nas variáveis de ambiente")
        return False
    
    # Email de destino
    email_destino = "suellencna@gmail.com"
    
    # Gerar token de ativação
    token = str(uuid.uuid4()).replace('-', '')
    
    # Ler o HTML standalone
    try:
        with open('ativacao_standalone_final.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("❌ Arquivo ativacao_standalone_final.html não encontrado")
        return False
    
    # Substituir token no HTML
    html_content = html_content.replace('?token=SEU_TOKEN', f'?token={token}')
    
    # Conteúdo do email
    assunto = "🎯 Ativação de Conta - Ponto Ótimo Invest"
    
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ativação de Conta</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🎯 Ponto Ótimo Invest</h1>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Seu dashboard de análise de ações</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h2 style="color: #333; margin-top: 0;">✅ Conta Criada com Sucesso!</h2>
            <p>Olá! Sua conta no <strong>Ponto Ótimo Invest</strong> foi criada com sucesso.</p>
            <p>Para começar a usar o sistema, você precisa ativar sua conta clicando no botão abaixo:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="data:text/html;base64,{html_content.encode('utf-8').hex()}" 
                   style="background: linear-gradient(135deg, #667eea, #764ba2); 
                          color: white; 
                          padding: 15px 30px; 
                          text-decoration: none; 
                          border-radius: 50px; 
                          font-weight: bold; 
                          font-size: 16px;
                          display: inline-block;">
                    🚀 Ativar Minha Conta
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666;">
                <strong>Token de ativação:</strong> {token}
            </p>
        </div>
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <h3 style="color: #1976d2; margin-top: 0;">🔗 Link Alternativo</h3>
            <p>Se o botão não funcionar, copie e cole este link no seu navegador:</p>
            <p style="word-break: break-all; background: white; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px;">
                data:text/html;base64,{html_content.encode('utf-8').hex()}
            </p>
        </div>
        
        <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <h3 style="color: #f57c00; margin-top: 0;">⚠️ Importante</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Este link é válido por 24 horas</li>
                <li>Após a ativação, você poderá fazer login no sistema</li>
                <li>Se não conseguir ativar, entre em contato conosco</li>
            </ul>
        </div>
        
        <div style="text-align: center; padding: 20px; border-top: 1px solid #eee;">
            <p style="margin: 0; color: #666; font-size: 14px;">
                <strong>Ponto Ótimo Invest</strong><br>
                Seu dashboard de análise de ações<br>
                <a href="mailto:suellencna@gmail.com" style="color: #667eea;">suellencna@gmail.com</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    # Criar mensagem
    msg = MIMEMultipart("alternative")
    msg["From"] = email_remetente
    msg["To"] = email_destino
    msg["Subject"] = assunto
    
    # Adicionar conteúdo HTML
    html_part = MIMEText(email_html, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        # Conectar ao servidor SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_remetente, senha_app)
            
            # Enviar email
            server.sendmail(email_remetente, email_destino, msg.as_string())
            
        print("✅ Email de ativação enviado com sucesso!")
        print(f"📧 Para: {email_destino}")
        print(f"🎫 Token: {token}")
        print("🔗 Link: HTML standalone embarcado no email")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Email de Ativação - Standalone")
    print("=" * 50)
    
    enviar_email_ativacao_standalone()
