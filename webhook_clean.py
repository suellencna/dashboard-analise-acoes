#!/usr/bin/env python3
"""
🛒 SISTEMA DE VENDAS - PONTO ÓTIMO INVEST
========================================

Sistema otimizado para processamento de vendas:
- Webhook Hotmart integrado
- Validação automática de compras
- Email de boas-vindas profissional
- Controle de acesso por token
- Deploy otimizado para Render

Para executar:
    python3 webhook_clean.py

Para deploy no Render:
    Configurar como Web Service
"""

import os
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
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
ph = PasswordHasher()

# Configurações do banco de dados SQLite
DATABASE_PATH = "sistema_vendas.db"

def init_database():
    """Inicializar banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            nome TEXT,
            status_compra TEXT DEFAULT 'pendente',
            token_acesso_app TEXT UNIQUE,
            expiracao_acesso TIMESTAMP,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            nome TEXT,
            senha_hash TEXT,
            status_conta TEXT DEFAULT 'ativo',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_login TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado.")

# Configurações de Email (Gmail SMTP)
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
APP_URL = os.environ.get('APP_URL', 'https://seu-app.onrender.com')
APP_DOWNLOAD_URL = os.environ.get('APP_DOWNLOAD_URL', 'https://seu-app.onrender.com')

# HTML para o email de boas-vindas
EMAIL_BOAS_VINDAS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bem-vindo ao Ponto Ótimo Invest!</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { width: 80%; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; border-bottom: 1px solid #ddd; color: white; }
        .content { padding: 20px 0; }
        .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }
        .footer { margin-top: 20px; font-size: 0.8em; color: #777; text-align: center; }
        .credentials { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🎉 Parabéns! Sua compra foi aprovada!</h2>
        </div>
        <div class="content">
            <p>Olá, <strong>{nome}</strong>!</p>
            <p>Obrigado por adquirir o <strong>Ponto Ótimo Invest</strong>!</p>
            <p>Sua compra foi processada com sucesso e você já pode começar a usar o aplicativo.</p>
            
            <div class="credentials">
                <h3>📱 Como acessar seu app:</h3>
                <p><strong>Link de Acesso:</strong> <a href="{link_acesso}">{link_acesso}</a></p>
                <p><strong>Token de Acesso:</strong> <code>{token_acesso}</code></p>
                <p><strong>Validade:</strong> {data_expiracao}</p>
            </div>
            
            <p style="text-align: center;">
                <a href="{link_acesso}" class="button">📱 Acessar App Agora</a>
            </p>
            
            <h3>🚀 O que você recebeu:</h3>
            <ul>
                <li>✅ Acesso completo ao aplicativo</li>
                <li>✅ Análises de ações em tempo real</li>
                <li>✅ Relatórios personalizados</li>
                <li>✅ Suporte técnico incluído</li>
            </ul>
            
            <h3>📞 Precisa de ajuda?</h3>
            <p>Nossa equipe está pronta para te ajudar:</p>
            <p>📧 Email: pontootimoinvest@gmail.com</p>
            
            <p>Bem-vindo à nossa comunidade de investidores!</p>
            <p>Atenciosamente,</p>
            <p><strong>Equipe Ponto Ótimo Invest</strong></p>
        </div>
        <div class="footer">
            <p>Este é um email automático, por favor, não responda.</p>
            <p>Seu token de acesso: <code>{token_acesso}</code></p>
        </div>
    </div>
</body>
</html>
"""

# HTML para validação de acesso
VALIDATION_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Validação de Acesso - Ponto Ótimo Invest</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; }
        .card { background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; max-width: 500px; width: 90%; }
        h1 { color: #333; }
        p { color: #555; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .credentials { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; text-align: left; }
        .credentials p { margin: 5px 0; color: #333; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🔐 Validação de Acesso</h1>
        <div id="message"></div>
        <div id="credentials" class="credentials" style="display:none;">
            <p><strong>Cliente:</strong> <span id="cliente-nome"></span></p>
            <p><strong>Email:</strong> <span id="cliente-email"></span></p>
            <p><strong>Status:</strong> <span id="status-compra"></span></p>
            <p><strong>Expira em:</strong> <span id="data-expiracao"></span></p>
        </div>
        <a href="/" class="button">Voltar ao Início</a>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            const messageDiv = document.getElementById('message');
            const credentialsDiv = document.getElementById('credentials');

            if (!token) {{
                messageDiv.innerHTML = '<p class="error">❌ Token de acesso não fornecido.</p>';
                return;
            }}

            fetch('/api/validar-acesso?token=' + token, {{
                method: 'GET',
                headers: {{
                    'Content-Type': 'application/json'
                }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'success') {{
                    messageDiv.innerHTML = '<p class="success">✅ Acesso autorizado!</p>';
                    document.getElementById('cliente-nome').textContent = data.nome;
                    document.getElementById('cliente-email').textContent = data.email;
                    document.getElementById('status-compra').textContent = data.status_compra;
                    document.getElementById('data-expiracao').textContent = data.data_expiracao;
                    credentialsDiv.style.display = 'block';
                }} else {{
                    messageDiv.innerHTML = '<p class="error">❌ ' + data.message + '</p>';
                }}
            }})
            .catch(error => {{
                console.error('Erro:', error);
                messageDiv.innerHTML = '<p class="error">❌ Erro na validação de acesso.</p>';
            }});
        }});
    </script>
</body>
</html>
"""

def enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao):
    """Enviar email de boas-vindas com link de acesso e token"""
    if not GMAIL_APP_PASSWORD:
        logger.error("GMAIL_APP_PASSWORD não configurada. Email não enviado.")
        return False, "GMAIL_APP_PASSWORD não configurada"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎉 Bem-vindo ao Ponto Ótimo Invest! Sua compra foi aprovada!"
    msg["From"] = GMAIL_EMAIL
    msg["To"] = email

    link_acesso = f"{APP_URL}?token={token_acesso}"
    html_content = EMAIL_BOAS_VINDAS_TEMPLATE.format(
        nome=nome,
        link_acesso=link_acesso,
        token_acesso=token_acesso,
        data_expiracao=data_expiracao
    )

    part1 = MIMEText(html_content, "html")
    msg.attach(part1)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_EMAIL, email, msg.as_string())
        logger.info(f"Email de boas-vindas enviado para {email}")
        return True, "Email enviado com sucesso"
    except Exception as e:
        logger.error(f"Erro ao enviar email para {email}: {e}")
        return False, str(e)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para Render"""
    return "SISTEMA_VENDAS_FUNCIONANDO", 200

@app.route('/webhook', methods=['POST'])
def hotmart_webhook():
    """Endpoint para receber webhooks da Hotmart"""
    data = request.json
    logger.info(f"Webhook Hotmart recebido: {data}")

    email = data.get('buyer', {}).get('email')
    nome = data.get('buyer', {}).get('name')
    produto_id = data.get('product', {}).get('id')
    status_compra = data.get('status')

    if not email or not nome:
        logger.error("Dados essenciais (email ou nome) ausentes no webhook.")
        return jsonify({"status": "error", "message": "Dados essenciais ausentes"}), 400

    threading.Thread(target=processar_compra_background, args=(email, nome, produto_id, status_compra)).start()

    return jsonify({"status": "success", "message": "Webhook recebido e processamento iniciado"}), 200

def processar_compra_background(email, nome, produto_id, status_compra):
    """Processar compra em background"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, status_compra, token_acesso_app, expiracao_acesso FROM clientes WHERE email = ?", (email,))
        cliente_existente = cursor.fetchone()

        if status_compra == 'approved':
            token_acesso = secrets.token_urlsafe(32)
            expiracao_acesso = datetime.now() + timedelta(days=365)
            data_expiracao_str = expiracao_acesso.strftime("%d/%m/%Y %H:%M:%S")

            if cliente_existente:
                logger.info(f"Cliente {email} já existe. Atualizando acesso.")
                cursor.execute("""
                    UPDATE clientes SET status_compra = 'ativo', token_acesso_app = ?, expiracao_acesso = ? WHERE email = ?
                """, (token_acesso, expiracao_acesso, email))
                logger.info(f"Cliente {email} atualizado com nova compra.")
            else:
                logger.info(f"Novo cliente {email} criado.")
                cursor.execute("""
                    INSERT INTO clientes (email, nome, status_compra, token_acesso_app, expiracao_acesso) VALUES (?, ?, 'ativo', ?, ?)
                """, (email, nome, token_acesso, expiracao_acesso))
                logger.info(f"Novo cliente {email} criado.")
            
            conn.commit()
            email_success, email_message = enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao_str)
            logger.info(f"Email de boas-vindas para {email}: {email_message}")

        elif status_compra in ['refunded', 'canceled', 'chargeback', 'expired', 'blocked']:
            if cliente_existente and cliente_existente[1] == 'ativo':
                cursor.execute("""
                    UPDATE clientes SET status_compra = 'inativo', token_acesso_app = NULL, expiracao_acesso = NULL WHERE email = ?
                """, (email,))
                conn.commit()
                logger.info(f"Acesso cancelado para {email} devido a {status_compra}.")
            else:
                logger.info(f"Cliente {email} já estava inativo ou não encontrado para {status_compra}. Nenhuma alteração necessária.")
        else:
            logger.info(f"Status de compra '{status_compra}' para {email} não requer ação de ativação/desativação imediata.")

    except Exception as e:
        logger.error(f"Erro no processamento da compra para {email}: {e}")
    finally:
        if conn:
            conn.close()

@app.route('/api/validar-acesso', methods=['GET'])
def validar_acesso_api():
    """Endpoint API para validar o token de acesso ao app"""
    token_acesso = request.args.get('token')
    logger.info(f"Tentativa de validação de acesso para token: {token_acesso}")

    if not token_acesso:
        return jsonify({"status": "error", "message": "Token de acesso não fornecido."}), 400

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT email, nome, status_compra, expiracao_acesso FROM clientes WHERE token_acesso_app = ?",
            (token_acesso,)
        )
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Token de acesso {token_acesso} não encontrado.")
            return jsonify({"status": "error", "message": "Token de acesso inválido."}), 401

        email, nome, status_compra, expiracao_acesso_str = result
        expiracao_acesso = datetime.strptime(expiracao_acesso_str, "%Y-%m-%d %H:%M:%S.%f") if expiracao_acesso_str else None

        if status_compra != 'ativo':
            logger.warning(f"Acesso negado para {email}. Status da compra: {status_compra}.")
            return jsonify({"status": "error", "message": "Sua conta não está ativa. Por favor, verifique o status da sua compra."}), 403

        if expiracao_acesso and datetime.now() > expiracao_acesso:
            logger.warning(f"Acesso negado para {email}. Token expirado em {expiracao_acesso}.")
            return jsonify({"status": "error", "message": "Seu token de acesso expirou. Por favor, renove sua assinatura."}), 403

        logger.info(f"Acesso concedido para {email} com token {token_acesso}.")
        return jsonify({
            "status": "success",
            "message": "Acesso concedido!",
            "email": email,
            "nome": nome,
            "status_compra": status_compra,
            "data_expiracao": expiracao_acesso.strftime("%d/%m/%Y %H:%M:%S") if expiracao_acesso else "N/A"
        }), 200
    except Exception as e:
        logger.error(f"Erro ao validar acesso com token {token_acesso}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/validar', methods=['GET'])
def validar_acesso_page():
    """Página HTML para exibir o status da validação de acesso"""
    return make_response(render_template_string(VALIDATION_PAGE_TEMPLATE), 200, {'Content-Type': 'text/html'})

@app.route('/test-email', methods=['POST'])
def test_email_route():
    """Testar envio de email de boas-vindas"""
    data = request.json
    email = data.get('email', 'cliente@teste.com')
    nome = data.get('nome', 'Cliente Teste')
    token_acesso = secrets.token_urlsafe(32)
    data_expiracao = (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y %H:%M:%S")

    logger.info(f"Testando email de boas-vindas para {email}")
    success, message = enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao)

    if success:
        return jsonify({"status": "success", "message": "Email de boas-vindas enviado!", "details": message}), 200
    else:
        return jsonify({"status": "error", "message": "Falha ao enviar email", "details": message}), 500

@app.route('/')
def home():
    """Página inicial do sistema de vendas"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Vendas - Ponto Ótimo Invest</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; }
            .card { background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; max-width: 600px; width: 90%; }
            h1 { color: #333; margin-bottom: 20px; }
            .status-box { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
            .status-box h2 { margin-top: 0; color: #155724; }
            .endpoints { text-align: left; margin-bottom: 20px; }
            .endpoints h3 { color: #333; margin-bottom: 10px; }
            .endpoint { background-color: #f8f9fa; border: 1px solid #e2e3e5; border-radius: 4px; padding: 10px; margin-bottom: 8px; font-family: 'Courier New', monospace; }
            .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛒 Sistema de Vendas - Ponto Ótimo Invest</h1>
            
            <div class="status-box">
                <h2>✔ Sistema de vendas funcionando!</h2>
                <p>
                    Validação de compra ativa<br>
                    Controle de acesso implementado<br>
                    Email de boas-vindas configurado
                </p>
            </div>
            
            <div class="endpoints">
                <h3>Endpoints do sistema de vendas:</h3>
                <div class="endpoint"><strong>GET /health</strong> - Health check</div>
                <div class="endpoint"><strong>POST /webhook</strong> - Webhook Hotmart (compras)</div>
                <div class="endpoint"><strong>GET /validar?token=XXX</strong> - Validar acesso do cliente</div>
                <div class="endpoint"><strong>POST /test-email</strong> - Testar email de boas-vindas</div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/health" class="button">Testar Health Check</a>
                <a href="/test-email" class="button">Testar Email</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    init_database()
    print("🛒 INICIANDO SISTEMA DE VENDAS - PONTO ÓTIMO INVEST")
    print("=" * 60)
    if not GMAIL_APP_PASSWORD:
        print("⚠️  AVISO: GMAIL_APP_PASSWORD não configurada.")
        print("   Configure para envio de emails de boas-vindas.")
        print("   Exemplo: export GMAIL_APP_PASSWORD='sua_senha_app'")
        print()
    
    print(f"📧 Email configurado: {GMAIL_EMAIL}")
    print(f"🌐 URL base: {APP_URL}")
    print(f"💾 Banco de dados: {DATABASE_PATH}")
    print()
    print("🔗 Endpoints do sistema de vendas:")
    print("   GET  /health - Health check")
    print("   POST /webhook - Webhook Hotmart (compras)")
    print("   GET  /validar?token=XXX - Validar acesso do cliente")
    print("   POST /test-email - Testar email de boas-vindas")
    print()
    print("🛒 Fluxo de vendas:")
    print("   1. Cliente compra → Webhook recebido")
    print("   2. Sistema valida → Cria/atualiza cliente")
    print("   3. Email enviado → Link do app + token de acesso")
    print("   4. Cliente acessa → Validação automática")
    print("   5. Controle ativo → Expiração automática")
    print()
    print("🌐 Acesse: http://localhost:5000")
    print("⏹️  Para parar: Ctrl+C")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Sistema de vendas parado pelo usuário.")
    except Exception as e:
        logger.error(f"\n❌ Erro ao iniciar sistema de vendas: {e}")
