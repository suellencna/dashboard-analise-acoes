#!/usr/bin/env python3
"""
Sistema de gerenciamento de senhas para usuários do Hotmart
"""

import os
import sqlalchemy
from argon2 import PasswordHasher
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações
ph = PasswordHasher()

# Carregar variáveis de ambiente
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

DATABASE_URL = os.environ.get('DATABASE_URL')
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')

def criar_usuario_hotmart(email, nome):
    """Cria usuário do Hotmart com senha temporária e envia por email"""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não configurada")
        return False, "Database not configured"
    
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Verificar se usuário já existe
            query_check = sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email LIMIT 1")
            result = conn.execute(query_check, {"email": email}).first()
            
            if result:
                return False, "User already exists"
            
            # Gerar senha temporária
            temp_password = secrets.token_urlsafe(8)
            hashed_password = ph.hash(temp_password)
            
            # Inserir usuário
            query_insert = sqlalchemy.text("""
                INSERT INTO usuarios (nome, email, senha_hash, status_assinatura) 
                VALUES (:nome, :email, :senha_hash, 'ativo')
            """)
            conn.execute(query_insert, {
                "nome": nome, 
                "email": email, 
                "senha_hash": hashed_password
            })
            conn.commit()
            
            # Enviar email com senha temporária
            if SMTP_USER and SMTP_PASS:
                enviar_senha_por_email(email, nome, temp_password)
                return True, f"User created and password sent to {email}"
            else:
                return True, f"User created with temporary password: {temp_password}"
                
    except Exception as e:
        return False, f"Error: {e}"

def enviar_senha_por_email(email, nome, senha):
    """Envia senha temporária por email"""
    
    if not all([SMTP_USER, SMTP_PASS]):
        print("⚠️  Configurações de email não encontradas")
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg['Subject'] = "Bem-vindo ao Ponto Ótimo Invest - Sua senha de acesso"
        
        # Corpo do email
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">🎉 Bem-vindo ao Ponto Ótimo Invest!</h2>
                
                <p>Olá <strong>{nome}</strong>,</p>
                
                <p>Sua conta foi criada com sucesso! Aqui estão seus dados de acesso:</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">🔑 Dados de Acesso</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Senha temporária:</strong> <code style="background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-family: monospace;">{senha}</code></p>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <h4 style="color: #856404; margin-top: 0;">⚠️ Importante</h4>
                    <p style="margin-bottom: 0;">Esta é uma senha temporária. Recomendamos que você altere sua senha no primeiro acesso para maior segurança.</p>
                </div>
                
                <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8; margin: 20px 0;">
                    <h4 style="color: #0c5460; margin-top: 0;">🚀 Como acessar</h4>
                    <p style="margin-bottom: 0;">1. Acesse a plataforma<br>2. Use seu email e a senha temporária<br>3. Altere sua senha nas configurações</p>
                </div>
                
                <p>Se você tiver alguma dúvida, entre em contato conosco.</p>
                
                <p>Atenciosamente,<br><strong>Equipe Ponto Ótimo Invest</strong></p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Enviar email
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        text = msg.as_string()
        server.sendmail(SMTP_USER, email, text)
        server.quit()
        
        print(f"✅ Email enviado para {email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

def main():
    """Função principal para testar o sistema"""
    print("=== SISTEMA DE SENHAS HOTMART ===")
    
    email = input("Email do usuário: ").strip()
    nome = input("Nome do usuário: ").strip()
    
    if email and nome:
        success, message = criar_usuario_hotmart(email, nome)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    else:
        print("❌ Dados incompletos")

if __name__ == "__main__":
    main()
