#!/usr/bin/env python3
"""
SISTEMA DE VENDAS COM VALIDAÇÃO - PONTO ÓTIMO INVEST
===================================================

Este sistema permite vender seu app com validação de compra:
- Cliente compra → Recebe email com link do app
- Validação ativa → Só funciona se compra válida
- Controle de expiração → Para de funcionar se cancelar
- Sistema de boas-vindas → Email profissional

Para executar:
    python3 sistema_vendas_executavel.py

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
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
ph = PasswordHasher()

# Configurações do banco de dados SQLite local
DATABASE_PATH = "sistema_vendas.db"

def init_database():
    """Inicializar banco de dados SQLite local para vendas"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            nome VARCHAR(255),
            status_compra VARCHAR(50) DEFAULT 'pendente',
            data_compra TIMESTAMP,
            data_expiracao TIMESTAMP,
            produto_id VARCHAR(100),
            valor_pago DECIMAL(10,2),
            token_acesso VARCHAR(255) UNIQUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acesso TIMESTAMP,
            acessos_totais INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Banco de dados de vendas inicializado.")

# Configurações de Email (Gmail SMTP)
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
APP_DOWNLOAD_URL = os.environ.get('APP_DOWNLOAD_URL', 'https://seu-app.com/download')

# HTML para o email de boas-vindas
EMAIL_BOAS_VINDAS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bem-vindo ao Ponto Ótimo Invest!</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ width: 80%; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; border-bottom: 1px solid #ddd; }}
        .content {{ padding: 20px 0; }}
        .button {{ display: inline-block; background-color: #007bff; color: #ffffff; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
        .footer {{ margin-top: 20px; font-size: 0.8em; color: #777; text-align: center; }}
        .credentials {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
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
                <p><strong>Link de Download:</strong> <a href="{link_download}">{link_download}</a></p>
                <p><strong>Token de Acesso:</strong> <code>{token_acesso}</code></p>
                <p><strong>Validade:</strong> {data_expiracao}</p>
            </div>
            
            <p style="text-align: center;">
                <a href="{link_download}" class="button">📱 Baixar App Agora</a>
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
            <p>💬 WhatsApp: (11) 99999-9999</p>
            
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
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f4f4f4; margin: 0; }
        .card { background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; max-width: 500px; width: 90%; }
        h1 { color: #333; }
        p { color: #555; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .warning { color: #ffc107; font-weight: bold; }
        .button { display: inline-block; background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
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
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            const messageDiv = document.getElementById('message');
            const credentialsDiv = document.getElementById('credentials');

            if (!token) {
                messageDiv.innerHTML = '<p class="error">❌ Token de acesso não fornecido.</p>';
                return;
            }

            fetch('/api/validar-acesso?token=' + token, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    messageDiv.innerHTML = '<p class="success">✅ Acesso autorizado!</p>';
                    document.getElementById('cliente-nome').textContent = data.nome;
                    document.getElementById('cliente-email').textContent = data.email;
                    document.getElementById('status-compra').textContent = data.status_compra;
                    document.getElementById('data-expiracao').textContent = data.data_expiracao;
                    credentialsDiv.style.display = 'block';
                } else {
                    messageDiv.innerHTML = '<p class="error">❌ ' + data.message + '</p>';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                messageDiv.innerHTML = '<p class="error">❌ Erro na validação de acesso.</p>';
            });
        });
    </script>
</body>
</html>
"""

def enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao):
    """Enviar email de boas-vindas com link do app"""
    if not GMAIL_APP_PASSWORD:
        logger.error("GMAIL_APP_PASSWORD não configurada. Email não enviado.")
        return False, "GMAIL_APP_PASSWORD não configurada"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎉 Bem-vindo ao Ponto Ótimo Invest! Sua compra foi aprovada!"
    msg["From"] = GMAIL_EMAIL
    msg["To"] = email

    html_content = EMAIL_BOAS_VINDAS_TEMPLATE.format(
        nome=nome,
        link_download=APP_DOWNLOAD_URL,
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
    """Health check simples"""
    return "SISTEMA_VENDAS_FUNCIONANDO", 200

@app.route('/api/validar-acesso', methods=['GET'])
def validar_acesso():
    """Validar acesso do cliente"""
    token = request.args.get('token')
    if not token:
        return jsonify({"status": "error", "message": "Token não fornecido"}), 400
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Buscar cliente pelo token
        cursor.execute(
            "SELECT nome, email, status_compra, data_expiracao, ultimo_acesso, acessos_totais FROM clientes WHERE token_acesso = ?",
            (token,)
        )
        result = cursor.fetchone()

        if not result:
            return jsonify({"status": "error", "message": "Token inválido"}), 400

        nome, email, status_compra, data_expiracao, ultimo_acesso, acessos_totais = result

        # Verificar se compra está ativa
        if status_compra != 'ativo':
            return jsonify({"status": "error", "message": "Compra não está ativa"}), 400

        # Verificar se não expirou
        if data_expiracao and datetime.now() > datetime.fromisoformat(data_expiracao):
            return jsonify({"status": "error", "message": "Acesso expirado"}), 400

        # Atualizar último acesso e contador
        cursor.execute(
            "UPDATE clientes SET ultimo_acesso = ?, acessos_totais = ? WHERE token_acesso = ?",
            (datetime.now().isoformat(), acessos_totais + 1, token)
        )
        conn.commit()

        return jsonify({
            "status": "success",
            "nome": nome,
            "email": email,
            "status_compra": status_compra,
            "data_expiracao": data_expiracao,
            "acessos_totais": acessos_totais + 1
        }), 200
    except Exception as e:
        logger.error(f"Erro ao validar acesso: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/validar', methods=['GET'])
def validar_page():
    """Página de validação de acesso"""
    return make_response(render_template_string(VALIDATION_PAGE_TEMPLATE), 200, {'Content-Type': 'text/html'})

@app.route('/webhook', methods=['POST'])
def hotmart_webhook():
    """Endpoint para receber webhooks da Hotmart"""
    data = request.json
    logger.info(f"Webhook Hotmart recebido: {data}")

    # Dados da compra
    email = data.get('buyer', {}).get('email')
    nome = data.get('buyer', {}).get('name')
    produto_id = data.get('product', {}).get('id')
    status_compra = data.get('status')
    valor = data.get('purchase', {}).get('price', 0)

    if not email or not nome:
        logger.error("Dados essenciais (email ou nome) ausentes no webhook.")
        return jsonify({"status": "error", "message": "Dados essenciais ausentes"}), 400

    # Processamento em background
    threading.Thread(target=processar_compra_background, args=(email, nome, produto_id, status_compra, valor)).start()

    return jsonify({"status": "success", "message": "Webhook recebido e processamento iniciado"}), 200

def processar_compra_background(email, nome, produto_id, status_compra, valor):
    """Processar compra em background"""
    logger.info(f"Processando compra para {email} (Status: {status_compra})")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        if status_compra == 'approved':
            # Gerar token de acesso único
            token_acesso = secrets.token_urlsafe(32)
            data_compra = datetime.now()
            data_expiracao = data_compra + timedelta(days=365)  # 1 ano de acesso
            
            # Verificar se cliente já existe
            cursor.execute("SELECT id FROM clientes WHERE email = ?", (email,))
            cliente_existente = cursor.fetchone()
            
            if cliente_existente:
                # Atualizar cliente existente
                cursor.execute("""
                    UPDATE clientes SET 
                        status_compra = 'ativo',
                        data_compra = ?,
                        data_expiracao = ?,
                        produto_id = ?,
                        valor_pago = ?,
                        token_acesso = ?
                    WHERE email = ?
                """, (data_compra.isoformat(), data_expiracao.isoformat(), produto_id, valor, token_acesso, email))
                logger.info(f"Cliente {email} atualizado com nova compra.")
            else:
                # Criar novo cliente
                cursor.execute("""
                    INSERT INTO clientes (email, nome, status_compra, data_compra, data_expiracao, produto_id, valor_pago, token_acesso)
                    VALUES (?, ?, 'ativo', ?, ?, ?, ?, ?)
                """, (email, nome, data_compra.isoformat(), data_expiracao.isoformat(), produto_id, valor, token_acesso))
                logger.info(f"Novo cliente {email} criado.")
            
            conn.commit()
            
            # Enviar email de boas-vindas
            email_success, email_message = enviar_email_boas_vindas(
                email, nome, token_acesso, data_expiracao.strftime("%d/%m/%Y")
            )
            logger.info(f"Email de boas-vindas para {email}: {email_message}")
            
        elif status_compra in ['refunded', 'canceled']:
            # Desativar acesso
            cursor.execute("UPDATE clientes SET status_compra = 'cancelado' WHERE email = ?", (email,))
            conn.commit()
            logger.info(f"Acesso cancelado para {email} devido a {status_compra}.")

    except Exception as e:
        logger.error(f"Erro no processamento da compra para {email}: {e}")
    finally:
        conn.close()

@app.route('/test-email', methods=['POST'])
def test_email_route():
    """Testar envio de email de boas-vindas"""
    data = request.json
    email = data.get('email', 'teste@example.com')
    nome = data.get('nome', 'Cliente Teste')
    token_acesso = secrets.token_urlsafe(32)
    data_expiracao = (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")

    logger.info(f"Testando email de boas-vindas para {email}")
    success, message = enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao)

    if success:
        return jsonify({"status": "success", "message": "Email de boas-vindas enviado!", "details": message}), 200
    else:
        return jsonify({"status": "error", "message": "Falha ao enviar email", "details": message}), 500

@app.route('/test-email-get', methods=['GET'])
def test_email_get():
    """Testar envio de email via GET (para facilitar testes no navegador)"""
    email = request.args.get('email', 'teste@example.com')
    nome = request.args.get('nome', 'Cliente Teste')
    token_acesso = secrets.token_urlsafe(32)
    data_expiracao = (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y")

    logger.info(f"Testando email de boas-vindas para {email}")
    success, message = enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao)

    if success:
        return f"""
        <html>
        <head><title>Teste de Email - Sucesso</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2>✅ Email de Boas-vindas Enviado!</h2>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Nome:</strong> {nome}</p>
                <p><strong>Token:</strong> {token_acesso}</p>
                <p><strong>Status:</strong> {message}</p>
                <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar ao Início</a>
            </div>
        </body>
        </html>
        """, 200
    else:
        return f"""
        <html>
        <head><title>Teste de Email - Erro</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2>❌ Erro ao Enviar Email</h2>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Nome:</strong> {nome}</p>
                <p><strong>Erro:</strong> {message}</p>
                <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar ao Início</a>
            </div>
        </body>
        </html>
        """, 500

@app.route('/')
def home():
    """Página inicial do sistema de vendas"""
    return """
    <html>
    <head>
        <title>Sistema de Vendas - Ponto Ótimo Invest</title>
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
            <h1>🛒 Sistema de Vendas - Ponto Ótimo Invest</h1>
            <div class="status">
                <strong>✅ Sistema de vendas funcionando!</strong><br>
                Validação de compra ativa<br>
                Controle de acesso implementado<br>
                Email de boas-vindas configurado
            </div>
            
            <div class="endpoints">
                <h3>Endpoints do sistema de vendas:</h3>
                <div class="endpoint"><strong>GET /health</strong> - Health check</div>
                <div class="endpoint"><strong>POST /webhook</strong> - Webhook Hotmart (compras)</div>
                <div class="endpoint"><strong>GET /validar?token=XXX</strong> - Validar acesso do cliente</div>
                <div class="endpoint"><strong>POST /test-email</strong> - Testar email de boas-vindas (API)</div>
                <div class="endpoint"><strong>GET /test-email-get</strong> - Testar email de boas-vindas (Navegador)</div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/health" class="button">Testar Health Check</a>
                <a href="/test-email-get" class="button">Testar Email</a>
            </div>
        </div>
    </body>
    </html>
    """

def main():
    """Função principal"""
    print("🛒 INICIANDO SISTEMA DE VENDAS - PONTO ÓTIMO INVEST")
    print("=" * 60)
    
    # Inicializar banco de dados
    init_database()
    
    # Verificar configurações
    if not GMAIL_APP_PASSWORD:
        print("⚠️  AVISO: GMAIL_APP_PASSWORD não configurada.")
        print("   Configure para envio de emails de boas-vindas.")
        print("   Exemplo: export GMAIL_APP_PASSWORD='sua_senha_app'")
        print()
    
    print(f"📧 Email configurado: {GMAIL_EMAIL}")
    print(f"🌐 URL base: {APP_URL}")
    print(f"📱 Link do app: {APP_DOWNLOAD_URL}")
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
    print("🌐 Acesse: http://localhost:5001")
    print("⏹️  Para parar: Ctrl+C")
    print("=" * 60)
    
    # Iniciar servidor
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Sistema de vendas parado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar sistema de vendas: {e}")

if __name__ == '__main__':
    main()
