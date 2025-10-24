#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import secrets

def testar_envio_email():
    """Testar envio de email com credenciais"""
    
    # Configurações Gmail SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_remetente = "pontootimoinvest@gmail.com"
    senha_app = os.getenv("GMAIL_APP_PASSWORD", "snbo xxle cero dloe")
    
    if not senha_app:
        print("❌ GMAIL_APP_PASSWORD não encontrada")
        return False
    
    # Ler credenciais do arquivo
    try:
        with open("credenciais_corrigidas.txt", "r") as f:
            lines = f.readlines()
            email_destino = lines[0].split(": ")[1].strip()
            senha_temporaria = lines[1].split(": ")[1].strip()
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    # Conteúdo do email
    assunto = "🔑 Suas Credenciais de Acesso - Ponto Ótimo Invest"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Credenciais de Acesso</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🎯 Ponto Ótimo Invest</h1>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Suas credenciais de acesso</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h2 style="color: #333; margin-top: 0;">🔑 Suas Credenciais de Acesso</h2>
            <p>Olá! Aqui estão suas credenciais para acessar o sistema:</p>
            
            <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p style="margin: 5px 0; font-family: monospace; font-size: 16px;">
                        <strong>Email:</strong> {email_destino}
                    </p>
                    <p style="margin: 5px 0; font-family: monospace; font-size: 16px;">
                        <strong>Senha temporária:</strong> {senha_temporaria}
                    </p>
                </div>
                <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">
                    ⚠️ <strong>Importante:</strong> Na primeira vez que fizer login, você será obrigado a alterar esta senha por segurança.
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://streamlit-analise-acoes.onrender.com/" 
                   style="background: linear-gradient(135deg, #667eea, #764ba2); 
                          color: white; 
                          padding: 15px 30px; 
                          text-decoration: none; 
                          border-radius: 50px; 
                          font-weight: bold; 
                          font-size: 16px;
                          display: inline-block;">
                    🚀 Acessar Dashboard
                </a>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px; border-top: 1px solid #eee;">
            <p style="margin: 0; color: #666; font-size: 14px;">
                <strong>Ponto Ótimo Invest</strong><br>
                Seu dashboard de análise de ações<br>
                <a href="mailto:pontootimoinvest@gmail.com" style="color: #667eea;">pontootimoinvest@gmail.com</a>
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
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        # Conectar ao servidor SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_remetente, senha_app)
            
            # Enviar email
            server.sendmail(email_remetente, email_destino, msg.as_string())
            
        print("✅ Email de credenciais enviado com sucesso!")
        print(f"📧 Para: {email_destino}")
        print(f"🔑 Senha: {senha_temporaria}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando Envio de Email - Credenciais Corrigidas")
    print("=" * 50)
    
    testar_envio_email()
