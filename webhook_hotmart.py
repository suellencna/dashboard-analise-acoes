#!/usr/bin/env python3
"""
Webhook Hotmart - Sistema Completo
Recebe notificações do Hotmart, cria usuário no Neon, envia email de ativação
"""

import os
import json
import secrets
import hashlib
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import argon2

app = Flask(__name__)

# Configurações
DATABASE_URL = os.environ.get('DATABASE_URL')
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
APP_URL = os.environ.get('APP_URL', 'https://web-production-040d1.up.railway.app')

# Configurar hash de senha
password_hasher = argon2.PasswordHasher()

def get_db_connection():
    """Conectar ao banco de dados Neon"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def create_user_table():
    """Criar tabela de usuários se não existir"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    nome VARCHAR(255) NOT NULL,
                    senha_hash VARCHAR(255) NOT NULL,
                    status_conta VARCHAR(50) DEFAULT 'pendente',
                    token_ativacao VARCHAR(255),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_ativacao TIMESTAMP,
                    hotmart_transaction_id VARCHAR(255)
                )
            """)
            conn.commit()
            return True
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        return False
    finally:
        conn.close()

def generate_activation_token():
    """Gerar token de ativação seguro"""
    return secrets.token_urlsafe(32)

def hash_password(password):
    """Hash da senha com Argon2"""
    return password_hasher.hash(password)

def send_activation_email(email, nome, token):
    """Enviar email de ativação via Gmail SMTP"""
    try:
        # Configurar SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = email
        msg['Subject'] = "🎉 Ative sua conta - Ponto Ótimo Investimentos"
        
        # Corpo do email
        activation_link = f"{APP_URL}/ativar/{token}"
        temp_password = secrets.token_urlsafe(8)
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎉 Bem-vindo ao Ponto Ótimo!</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Olá, {nome}!</h2>
                
                <p>Sua conta foi criada com sucesso! Para ativá-la, clique no botão abaixo:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{activation_link}" 
                       style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        ✅ Ativar Minha Conta
                    </a>
                </div>
                
                <div style="background: #e9ecef; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #495057; margin-top: 0;">📋 Suas Credenciais Temporárias:</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Senha Temporária:</strong> <code style="background: #fff; padding: 2px 5px; border-radius: 3px;">{temp_password}</code></p>
                    <p style="color: #dc3545; font-size: 14px;"><strong>⚠️ Importante:</strong> Você será obrigado a trocar esta senha no primeiro login.</p>
                </div>
                
                <p>Se o botão não funcionar, copie e cole este link no seu navegador:</p>
                <p style="word-break: break-all; color: #007bff;">{activation_link}</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                
                <p style="color: #6c757d; font-size: 14px;">
                    Este email foi enviado automaticamente. Se você não solicitou uma conta, pode ignorar este email.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # Conectar e enviar
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        return True, temp_password
        
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False, str(e)

def create_user(email, nome, hotmart_transaction_id):
    """Criar usuário no banco de dados"""
    conn = get_db_connection()
    if not conn:
        return False, "Erro de conexão com banco"
    
    try:
        # Gerar token e senha temporária
        token = generate_activation_token()
        temp_password = secrets.token_urlsafe(8)
        password_hash = hash_password(temp_password)
        
        with conn.cursor() as cur:
            # Verificar se usuário já existe
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cur.fetchone():
                return False, "Usuário já existe"
            
            # Inserir novo usuário
            cur.execute("""
                INSERT INTO usuarios (email, nome, senha_hash, status_conta, token_ativacao, hotmart_transaction_id)
                VALUES (%s, %s, %s, 'pendente', %s, %s)
            """, (email, nome, password_hash, token, hotmart_transaction_id))
            
            conn.commit()
            return True, token
            
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False, str(e)
    finally:
        conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para Railway"""
    return "FUNCIONANDO", 200

@app.route('/webhook/hotmart', methods=['POST'])
def webhook_hotmart():
    """Receber webhook do Hotmart"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        # Verificar se é uma compra aprovada
        if data.get('event') == 'PURCHASE_APPROVED':
            # Extrair dados do comprador
            buyer = data.get('data', {}).get('buyer', {})
            email = buyer.get('email')
            nome = buyer.get('name')
            transaction_id = data.get('data', {}).get('transaction', {}).get('id')
            
            if not email or not nome:
                return jsonify({"error": "Email ou nome não encontrado"}), 400
            
            # Criar usuário no banco
            success, result = create_user(email, nome, transaction_id)
            
            if not success:
                return jsonify({"error": f"Erro ao criar usuário: {result}"}), 500
            
            # Enviar email de ativação
            email_sent, temp_password = send_activation_email(email, nome, result)
            
            if not email_sent:
                return jsonify({
                    "error": f"Usuário criado mas email falhou: {temp_password}",
                    "user_created": True,
                    "activation_token": result
                }), 500
            
            return jsonify({
                "success": True,
                "message": "Usuário criado e email enviado com sucesso",
                "email": email,
                "nome": nome,
                "transaction_id": transaction_id
            }), 200
        
        return jsonify({"message": "Evento não processado"}), 200
        
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/ativar/<token>', methods=['GET'])
def activate_account(token):
    """Ativar conta do usuário"""
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão com banco", 500
    
    try:
        with conn.cursor() as cur:
            # Buscar usuário pelo token
            cur.execute("""
                SELECT id, email, nome, status_conta FROM usuarios 
                WHERE token_ativacao = %s AND status_conta = 'pendente'
            """, (token,))
            
            user = cur.fetchone()
            if not user:
                return "Token inválido ou conta já ativada", 400
            
            # Ativar conta
            cur.execute("""
                UPDATE usuarios 
                SET status_conta = 'ativo', 
                    token_ativacao = NULL,
                    data_ativacao = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (user[0],))
            
            conn.commit()
            
            # Página de sucesso
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Conta Ativada - Ponto Ótimo Investimentos</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                    .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 5px; }}
                    .info {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="success">
                    <h1>🎉 Conta Ativada com Sucesso!</h1>
                    <p>Olá, <strong>{user[2]}</strong>! Sua conta foi ativada com sucesso.</p>
                </div>
                
                <div class="info">
                    <h3>📋 Próximos Passos:</h3>
                    <ol>
                        <li>Acesse o sistema: <a href="{APP_URL}" target="_blank">Ponto Ótimo Investimentos</a></li>
                        <li>Faça login com seu email: <strong>{user[1]}</strong></li>
                        <li>Use a senha temporária que foi enviada por email</li>
                        <li><strong>Importante:</strong> Você será obrigado a trocar a senha no primeiro login</li>
                    </ol>
                </div>
                
                <p style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                        🚀 Acessar Sistema
                    </a>
                </p>
            </body>
            </html>
            """
            
            return html, 200
            
    except Exception as e:
        print(f"Erro ao ativar conta: {e}")
        return "Erro interno do servidor", 500
    finally:
        conn.close()

@app.route('/test-email', methods=['POST'])
def test_email():
    """Endpoint para testar envio de email"""
    try:
        data = request.get_json()
        email = data.get('email', 'suellencna@hotmail.com')
        nome = data.get('nome', 'Teste')
        
        token = generate_activation_token()
        success, result = send_activation_email(email, nome, token)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Email enviado com sucesso",
                "email": email,
                "token": token
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Criar tabela ao iniciar
    create_user_table()
    app.run(host='0.0.0.0', port=5000, debug=True)
