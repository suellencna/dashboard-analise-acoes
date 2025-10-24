#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def enviar_email_ativacao_teste():
    """Enviar email de ativação para usuário de teste"""
    
    # Configurações Gmail SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_remetente = "pontootimoinvest@gmail.com"
    senha_app = os.getenv("GMAIL_APP_PASSWORD", "snbo xxle cero dloe")
    
    if not senha_app:
        print("❌ GMAIL_APP_PASSWORD não encontrada")
        return False
    
    # Ler token do arquivo
    try:
        with open("token_ativacao_teste.txt", "r") as f:
            lines = f.readlines()
            token = lines[0].split(": ")[1].strip()
            email_destino = lines[1].split(": ")[1].strip()
            link_ativacao = lines[2].split(": ")[1].strip()
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    # Conteúdo do email
    assunto = "🎯 Ativação de Conta - Ponto Ótimo Invest"
    
    # Gerar senha temporária para o email
    import secrets
    senha_temporaria = secrets.token_urlsafe(8)
    
    # Atualizar senha no banco de dados
    try:
        import sqlalchemy
        from argon2 import PasswordHasher
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            engine = sqlalchemy.create_engine(DATABASE_URL)
            ph = PasswordHasher()
            
            with engine.connect() as conn:
                # Atualizar senha no banco
                query_update = sqlalchemy.text("""
                    UPDATE usuarios 
                    SET senha_hash = :senha_hash 
                    WHERE email = :email
                """)
                senha_hash = ph.hash(senha_temporaria)
                conn.execute(query_update, {
                    "senha_hash": senha_hash,
                    "email": email_destino
                })
                conn.commit()
                print(f"✅ Senha atualizada no banco: {senha_temporaria}")
        else:
            print("⚠️ DATABASE_URL não encontrada - senha não atualizada no banco")
    except Exception as e:
        print(f"⚠️ Erro ao atualizar senha no banco: {e}")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Bem-vindo ao Ponto Ótimo Invest</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🎯 Ponto Ótimo Invest</h1>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Seu dashboard de análise de ações</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h2 style="color: #333; margin-top: 0;">🎉 Bem-vindo(a) ao Ponto Ótimo Invest!</h2>
            <p>Olá! Sua conta foi criada com sucesso e já está ativa.</p>
            <p>Para começar a usar o sistema, use suas credenciais de acesso:</p>
            
            <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <h3 style="color: #2e7d32; margin-top: 0;">🔑 Suas Credenciais de Acesso</h3>
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
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <h3 style="color: #1976d2; margin-top: 0;">📋 Como Fazer Login</h3>
            <ol style="margin: 0; padding-left: 20px;">
                <li>Acesse: <a href="https://streamlit-analise-acoes.onrender.com/" style="color: #1976d2;">streamlit-analise-acoes.onrender.com</a></li>
                <li>Digite seu email: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{email_destino}</code></li>
                <li>Digite a senha temporária: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{senha_temporaria}</code></li>
                <li>Clique em "🚀 Entrar"</li>
                <li>Altere sua senha quando solicitado</li>
            </ol>
        </div>
        
        <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
            <h3 style="color: #f57c00; margin-top: 0;">🆘 Precisa de Ajuda?</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Se não conseguir fazer login, entre em contato conosco</li>
                <li>Se perder suas credenciais, podemos reenviar</li>
                <li>Suporte disponível em: <a href="mailto:suellencna@gmail.com" style="color: #f57c00;">suellencna@gmail.com</a></li>
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
            
        print("✅ Email de ativação enviado com sucesso!")
        print(f"📧 Para: {email_destino}")
        print(f"🔗 Link: {link_ativacao}")
        print(f"🎫 Token: {token}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Enviando Email de Ativação - Teste Completo")
    print("=" * 50)
    
    enviar_email_ativacao_teste()
