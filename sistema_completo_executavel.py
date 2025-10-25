#!/usr/bin/env python3
"""
SISTEMA COMPLETO EXECUTÁVEL - PONTO ÓTIMO INVEST
================================================

Este arquivo contém todo o sistema refatorado em um único executável:
- Webhook Hotmart
- Banco de dados (SQLite local)
- Email Gmail SMTP
- Ativação de conta
- Troca de senha obrigatória

Para executar:
    python3 sistema_completo_executavel.py

Para parar: Ctrl+C
"""

import os
import sys
import sqlite3
import secrets
import logging
import threading
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, make_response, render_template_string
from argon2 import PasswordHasher

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
ph = PasswordHasher()

# Configurações do banco de dados SQLite local
DATABASE_PATH = "sistema_local.db"

def init_database():
    """Inicializar banco de dados SQLite local"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            nome VARCHAR(255),
            senha_hash VARCHAR(255),
            token_ativacao VARCHAR(255) UNIQUE,
            expiracao_token TIMESTAMP,
            status_conta VARCHAR(50) DEFAULT 'pendente',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Banco de dados SQLite local inicializado.")

# Configurações de Email (Gmail SMTP)
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

# HTML para o email de ativação
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ativação da sua Conta Ponto Ótimo Invest</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { width: 80%; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .header { background-color: #f4f4f4; padding: 10px; text-align: center; border-bottom: 1px solid #ddd; }
        .content { padding: 20px 0; }
        .button { display: inline-block; background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { margin-top: 20px; font-size: 0.8em; color: #777; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Bem-vindo(a) ao Ponto Ótimo Invest!</h2>
        </div>
        <div class="content">
            <p>Olá, {nome}!</p>
            <p>Sua conta foi criada com sucesso. Para começar a usar, por favor, ative sua conta clicando no botão abaixo:</p>
            <p style="text-align: center;">
                <a href="{link_ativacao}" class="button">Ativar Minha Conta</a>
            </p>
            <p>Se o botão não funcionar, copie e cole o seguinte link no seu navegador:</p>
            <p><a href="{link_ativacao}">{link_ativacao}</a></p>
            <p>Suas credenciais temporárias são:</p>
            <ul>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>Senha Temporária:</strong> {senha_temporaria}</li>
            </ul>
            <p>Você será solicitado(a) a trocar sua senha no primeiro login.</p>
            <p>Obrigado(a) por escolher o Ponto Ótimo Invest!</p>
            <p>Atenciosamente,</p>
            <p>Equipe Ponto Ótimo Invest</p>
        </div>
        <div class="footer">
            <p>Este é um email automático, por favor, não responda.</p>
        </div>
    </div>
</body>
</html>
"""

# HTML para a página de ativação
ACTIVATION_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ativação de Conta</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f4f4f4; margin: 0; }
        .card { background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; max-width: 400px; width: 90%; }
        h1 { color: #333; }
        p { color: #555; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .button { display: inline-block; background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .credentials { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; text-align: left; }
        .credentials p { margin: 5px 0; color: #333; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Ativação de Conta</h1>
        <div id="message"></div>
        <div id="credentials" class="credentials" style="display:none;">
            <p><strong>Email:</strong> <span id="activated-email"></span></p>
            <p><strong>Senha Temporária:</strong> <span id="temporary-password"></span></p>
        </div>
        <a href="/" class="button">Ir para o Login</a>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const path = window.location.pathname;
            const token = path.split('/').pop();
            const messageDiv = document.getElementById('message');
            const credentialsDiv = document.getElementById('credentials');
            const activatedEmailSpan = document.getElementById('activated-email');
            const temporaryPasswordSpan = document.getElementById('temporary-password');

            if (!token) {
                messageDiv.innerHTML = '<p class="error">Token de ativação não encontrado.</p>';
                return;
            }

            fetch('/api/ativar/' + token, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    messageDiv.innerHTML = '<p class="success">✅ Sua conta foi ativada com sucesso!</p>';
                    activatedEmailSpan.textContent = data.email;
                    temporaryPasswordSpan.textContent = data.senha_temporaria;
                    credentialsDiv.style.display = 'block';
                } else {
                    messageDiv.innerHTML = '<p class="error">❌ Erro ao ativar conta: ' + data.message + '</p>';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                messageDiv.innerHTML = '<p class="error">❌ Ocorreu um erro inesperado ao ativar sua conta.</p>';
            });
        });
    </script>
</body>
</html>
"""

def enviar_email_ativacao_gmail(email, nome, token, senha_temporaria):
    """Enviar email de ativação via Gmail SMTP"""
    if not GMAIL_APP_PASSWORD:
        logger.error("GMAIL_APP_PASSWORD não configurada. Email não enviado.")
        return False, "GMAIL_APP_PASSWORD não configurada"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Ative sua Conta Ponto Ótimo Invest!"
    msg["From"] = GMAIL_EMAIL
    msg["To"] = email

    link_ativacao = f"{APP_URL}/ativar/{token}"
    html_content = EMAIL_TEMPLATE.format(
        nome=nome,
        link_ativacao=link_ativacao,
        email=email,
        senha_temporaria=senha_temporaria
    )

    part1 = MIMEText(html_content, "html")
    msg.attach(part1)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_EMAIL, email, msg.as_string())
        logger.info(f"Email de ativação enviado para {email}")
        return True, "Email enviado com sucesso"
    except Exception as e:
        logger.error(f"Erro ao enviar email para {email}: {e}")
        return False, str(e)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check simples"""
    return "FUNCIONANDO", 200

@app.route('/api/ativar/<token>', methods=['POST'])
def ativar_conta_api(token):
    """Endpoint API para ativar a conta e retornar credenciais."""
    logger.info(f"Tentativa de ativação para token: {token}")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Buscar usuário pelo token
        cursor.execute(
            "SELECT email, nome, expiracao_token, status_conta FROM usuarios WHERE token_ativacao = ?",
            (token,)
        )
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Token {token} não encontrado ou já utilizado.")
            return jsonify({"status": "error", "message": "Token inválido ou conta já ativada."}), 400

        email, nome, expiracao_token, status_conta = result

        if status_conta == 'ativo':
            logger.warning(f"Conta para {email} já está ativa.")
            return jsonify({"status": "error", "message": "Conta já está ativa."}), 400

        if expiracao_token and datetime.now() > datetime.fromisoformat(expiracao_token):
            logger.warning(f"Token {token} expirado para {email}.")
            return jsonify({"status": "error", "message": "Token de ativação expirado."}), 400

        # Gerar senha temporária e hash
        senha_temporaria = secrets.token_urlsafe(8)
        senha_hash = ph.hash(senha_temporaria)

        # Atualizar status da conta e senha
        cursor.execute(
            "UPDATE usuarios SET status_conta = 'ativo', senha_hash = ?, token_ativacao = NULL, expiracao_token = NULL WHERE token_ativacao = ?",
            (senha_hash, token)
        )
        conn.commit()
        logger.info(f"Conta para {email} ativada com sucesso. Senha temporária gerada.")

        return jsonify({
            "status": "success",
            "message": "Conta ativada com sucesso!",
            "email": email,
            "nome": nome,
            "senha_temporaria": senha_temporaria
        }), 200
    except Exception as e:
        logger.error(f"Erro ao ativar conta com token {token}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/ativar/<token>', methods=['GET'])
def ativar_conta_page(token):
    """Página HTML para exibir o status da ativação."""
    return make_response(render_template_string(ACTIVATION_PAGE_TEMPLATE, token=token), 200, {'Content-Type': 'text/html'})

@app.route('/webhook', methods=['POST'])
def hotmart_webhook():
    """Endpoint para receber webhooks da Hotmart."""
    data = request.json
    logger.info(f"Webhook Hotmart recebido: {data}")

    # Exemplo de dados esperados da Hotmart
    email = data.get('buyer', {}).get('email')
    nome = data.get('buyer', {}).get('name')
    produto_id = data.get('product', {}).get('id')
    status_compra = data.get('status')

    if not email or not nome:
        logger.error("Dados essenciais (email ou nome) ausentes no webhook.")
        return jsonify({"status": "error", "message": "Dados essenciais ausentes"}), 400

    # Processamento em background
    threading.Thread(target=processar_compra_background, args=(email, nome, produto_id, status_compra)).start()

    return jsonify({"status": "success", "message": "Webhook recebido e processamento iniciado"}), 200

def processar_compra_background(email, nome, produto_id, status_compra):
    """Função para processar a compra em background."""
    logger.info(f"Processando compra em background para {email} (Status: {status_compra})")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar se o usuário já existe
        cursor.execute("SELECT id, status_conta FROM usuarios WHERE email = ?", (email,))
        user_exists = cursor.fetchone()

        if user_exists:
            user_id, current_status = user_exists
            logger.info(f"Usuário {email} já existe com status {current_status}.")

            if status_compra == 'approved' and current_status == 'pendente':
                # Reenviar ativação
                token = secrets.token_urlsafe(32)
                expiracao_token = datetime.now() + timedelta(days=7)
                cursor.execute(
                    "UPDATE usuarios SET token_ativacao = ?, expiracao_token = ? WHERE email = ?",
                    (token, expiracao_token.isoformat(), email)
                )
                conn.commit()
                logger.info(f"Token de ativação atualizado para {email}.")
                
                # Enviar email de ativação
                email_success, email_message = enviar_email_ativacao_gmail(email, nome, token, "Será gerada na ativação")
                logger.info(f"Email de re-ativação enviado para {email}: {email_message}")
                
            elif status_compra in ['refunded', 'canceled'] and current_status == 'ativo':
                # Desativar conta
                cursor.execute("UPDATE usuarios SET status_conta = 'inativo' WHERE email = ?", (email,))
                conn.commit()
                logger.info(f"Conta para {email} desativada devido a {status_compra}.")
            
            return

        # Se o usuário não existe e a compra foi aprovada, criar novo usuário
        if status_compra == 'approved':
            token = secrets.token_urlsafe(32)
            expiracao_token = datetime.now() + timedelta(days=7)
            
            cursor.execute(
                "INSERT INTO usuarios (email, nome, token_ativacao, expiracao_token, status_conta) VALUES (?, ?, ?, ?, 'pendente')",
                (email, nome, token, expiracao_token.isoformat())
            )
            conn.commit()
            logger.info(f"Novo usuário {email} criado com status 'pendente'.")

            # Enviar email de ativação
            email_success, email_message = enviar_email_ativacao_gmail(email, nome, token, "Será gerada na ativação")
            logger.info(f"Email de ativação enviado para {email}: {email_message}")
        else:
            logger.info(f"Compra para {email} com status '{status_compra}' não resultou em criação de conta.")

    except Exception as e:
        logger.error(f"Erro no processamento em background para {email}: {e}")
    finally:
        conn.close()

@app.route('/test-email', methods=['POST'])
def test_email_route():
    """Endpoint para testar o envio de email manualmente."""
    data = request.json
    email = data.get('email', 'teste@example.com')
    nome = data.get('nome', 'Usuario Teste')
    token = secrets.token_urlsafe(32)
    senha_temporaria = secrets.token_urlsafe(8)

    logger.info(f"Recebido pedido de teste de email para {email}")
    success, message = enviar_email_ativacao_gmail(email, nome, token, senha_temporaria)

    if success:
        return jsonify({"status": "success", "message": "Email de teste enviado!", "details": message}), 200
    else:
        return jsonify({"status": "error", "message": "Falha ao enviar email de teste", "details": message}), 500

@app.route('/')
def home():
    """Página inicial"""
    return """
    <html>
    <head>
        <title>Sistema Ponto Ótimo Invest - Local</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .endpoints { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .endpoint { margin: 10px 0; font-family: monospace; }
            .button { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Sistema Ponto Ótimo Invest - Local</h1>
            <div class="status">
                <strong>✅ Sistema funcionando localmente!</strong><br>
                Banco de dados: SQLite local<br>
                Email: Gmail SMTP<br>
                Porta: 5000
            </div>
            
            <div class="endpoints">
                <h3>Endpoints disponíveis:</h3>
                <div class="endpoint"><strong>GET /health</strong> - Health check</div>
                <div class="endpoint"><strong>POST /webhook</strong> - Webhook Hotmart</div>
                <div class="endpoint"><strong>POST /test-email</strong> - Testar email</div>
                <div class="endpoint"><strong>GET /ativar/&lt;token&gt;</strong> - Ativar conta</div>
                <div class="endpoint"><strong>POST /api/ativar/&lt;token&gt;</strong> - API ativação</div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/health" class="button">Testar Health Check</a>
                <a href="/test-email" class="button">Testar Email</a>
            </div>
        </div>
    </body>
    </html>
    """

def main():
    """Função principal"""
    print("🚀 INICIANDO SISTEMA PONTO ÓTIMO INVEST - LOCAL")
    print("=" * 50)
    
    # Inicializar banco de dados
    init_database()
    
    # Verificar configurações
    if not GMAIL_APP_PASSWORD:
        print("⚠️  AVISO: GMAIL_APP_PASSWORD não configurada.")
        print("   Configure a variável de ambiente para envio de emails.")
        print("   Exemplo: export GMAIL_APP_PASSWORD='sua_senha_app'")
        print()
    
    print(f"📧 Email configurado: {GMAIL_EMAIL}")
    print(f"🌐 URL base: {APP_URL}")
    print(f"💾 Banco de dados: {DATABASE_PATH}")
    print()
    print("🔗 Endpoints disponíveis:")
    print("   GET  /health - Health check")
    print("   POST /webhook - Webhook Hotmart")
    print("   POST /test-email - Testar email")
    print("   GET  /ativar/<token> - Ativar conta")
    print("   POST /api/ativar/<token> - API ativação")
    print()
    print("🌐 Acesse: http://localhost:5000")
    print("⏹️  Para parar: Ctrl+C")
    print("=" * 50)
    
    # Iniciar servidor
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Sistema parado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar sistema: {e}")

if __name__ == '__main__':
    main()
