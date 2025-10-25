#!/usr/bin/env python3
"""
🚀 WEBHOOK RAILWAY - RESPOSTA RÁPIDA
====================================

Sistema otimizado para Railway:
- Resposta instantânea para webhooks
- Sem cold starts
- Processamento em background
- Integração com Render

Para deploy no Railway:
    Configurar como Web Service
"""

import os
import sqlite3
import secrets
import logging
import threading
import smtplib
import ssl
import requests
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

# Configurações do banco de dados
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL não configurada.")
    exit(1)

# Configurações de Email (Gmail SMTP)
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
RENDER_APP_URL = os.environ.get('RENDER_APP_URL', 'https://ponto-otimo-invest.onrender.com')

def init_database():
    """Inicializar banco de dados"""
    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    nome VARCHAR(255),
                    status_compra VARCHAR(50) DEFAULT 'pendente',
                    token_acesso_app VARCHAR(255) UNIQUE,
                    expiracao_acesso TIMESTAMP,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
        logger.info("Banco de dados inicializado.")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")

def enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao):
    """Enviar email de boas-vindas"""
    if not GMAIL_APP_PASSWORD:
        logger.error("GMAIL_APP_PASSWORD não configurada. Email não enviado.")
        return False, "GMAIL_APP_PASSWORD não configurada"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎉 Bem-vindo ao Ponto Ótimo Invest! Sua compra foi aprovada!"
    msg["From"] = GMAIL_EMAIL
    msg["To"] = email

    link_acesso = f"{RENDER_APP_URL}?token={token_acesso}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bem-vindo ao Ponto Ótimo Invest!</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ width: 80%; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; border-bottom: 1px solid #ddd; color: white; }}
            .content {{ padding: 20px 0; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
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
    """Health check para Railway"""
    return "RAILWAY_WEBHOOK_FUNCIONANDO", 200

@app.route('/webhook', methods=['POST'])
def hotmart_webhook():
    """Endpoint para receber webhooks da Hotmart - RESPOSTA RÁPIDA"""
    data = request.json
    logger.info(f"Webhook Hotmart recebido: {data}")

    email = data.get('buyer', {}).get('email')
    nome = data.get('buyer', {}).get('name')
    produto_id = data.get('product', {}).get('id')
    status_compra = data.get('status')

    if not email or not nome:
        logger.error("Dados essenciais (email ou nome) ausentes no webhook.")
        return jsonify({"status": "error", "message": "Dados essenciais ausentes"}), 400

    # Processar em background para resposta rápida
    threading.Thread(target=processar_compra_background, args=(email, nome, produto_id, status_compra)).start()

    # Resposta imediata para Hotmart
    return jsonify({"status": "success", "message": "Webhook recebido e processamento iniciado"}), 200

def processar_compra_background(email, nome, produto_id, status_compra):
    """Processar compra em background"""
    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Verificar se cliente existe
            result = conn.execute(text(
                "SELECT id, status_compra, token_acesso_app, expiracao_acesso FROM clientes WHERE email = :email"
            ), {"email": email}).fetchone()

            if status_compra == 'approved':
                token_acesso = secrets.token_urlsafe(32)
                expiracao_acesso = datetime.now() + timedelta(days=365)
                data_expiracao_str = expiracao_acesso.strftime("%d/%m/%Y %H:%M:%S")

                if result:
                    logger.info(f"Cliente {email} já existe. Atualizando acesso.")
                    conn.execute(text("""
                        UPDATE clientes SET status_compra = 'ativo', token_acesso_app = :token, expiracao_acesso = :expiracao WHERE email = :email
                    """), {"token": token_acesso, "expiracao": expiracao_acesso, "email": email})
                    logger.info(f"Cliente {email} atualizado com nova compra.")
                else:
                    logger.info(f"Novo cliente {email} criado.")
                    conn.execute(text("""
                        INSERT INTO clientes (email, nome, status_compra, token_acesso_app, expiracao_acesso) VALUES (:email, :nome, 'ativo', :token, :expiracao)
                    """), {"email": email, "nome": nome, "token": token_acesso, "expiracao": expiracao_acesso})
                    logger.info(f"Novo cliente {email} criado.")
                
                conn.commit()
                email_success, email_message = enviar_email_boas_vindas(email, nome, token_acesso, data_expiracao_str)
                logger.info(f"Email de boas-vindas para {email}: {email_message}")

            elif status_compra in ['refunded', 'canceled', 'chargeback', 'expired', 'blocked']:
                if result and result[1] == 'ativo':
                    conn.execute(text("""
                        UPDATE clientes SET status_compra = 'inativo', token_acesso_app = NULL, expiracao_acesso = NULL WHERE email = :email
                    """), {"email": email})
                    conn.commit()
                    logger.info(f"Acesso cancelado para {email} devido a {status_compra}.")
                else:
                    logger.info(f"Cliente {email} já estava inativo ou não encontrado para {status_compra}. Nenhuma alteração necessária.")
            else:
                logger.info(f"Status de compra '{status_compra}' para {email} não requer ação de ativação/desativação imediata.")

    except Exception as e:
        logger.error(f"Erro no processamento da compra para {email}: {e}")

@app.route('/api/validar-acesso', methods=['GET'])
def validar_acesso_api():
    """Endpoint API para validar o token de acesso"""
    token_acesso = request.args.get('token')
    logger.info(f"Tentativa de validação de acesso para token: {token_acesso}")

    if not token_acesso:
        return jsonify({"status": "error", "message": "Token de acesso não fornecido."}), 400

    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT email, nome, status_compra, expiracao_acesso FROM clientes WHERE token_acesso_app = :token"
            ), {"token": token_acesso}).fetchone()

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
    """Página inicial do sistema de webhook"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webhook Railway - Ponto Ótimo Invest</title>
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
            <h1>🚀 Webhook Railway - Ponto Ótimo Invest</h1>
            
            <div class="status-box">
                <h2>✔ Sistema de webhook funcionando!</h2>
                <p>
                    Resposta instantânea para Hotmart<br>
                    Processamento em background<br>
                    Integração com Render
                </p>
            </div>
            
            <div class="endpoints">
                <h3>Endpoints do sistema de webhook:</h3>
                <div class="endpoint"><strong>GET /health</strong> - Health check</div>
                <div class="endpoint"><strong>POST /webhook</strong> - Webhook Hotmart (compras)</div>
                <div class="endpoint"><strong>GET /api/validar-acesso?token=XXX</strong> - Validar acesso do cliente</div>
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
    print("🚀 INICIANDO WEBHOOK RAILWAY - PONTO ÓTIMO INVEST")
    print("=" * 60)
    if not GMAIL_APP_PASSWORD:
        print("⚠️  AVISO: GMAIL_APP_PASSWORD não configurada.")
        print("   Configure para envio de emails de boas-vindas.")
        print("   Exemplo: export GMAIL_APP_PASSWORD='sua_senha_app'")
        print()
    
    print(f"📧 Email configurado: {GMAIL_EMAIL}")
    print(f"🌐 URL Render: {RENDER_APP_URL}")
    print(f"💾 Banco de dados: {DATABASE_URL}")
    print()
    print("🔗 Endpoints do sistema de webhook:")
    print("   GET  /health - Health check")
    print("   POST /webhook - Webhook Hotmart (compras)")
    print("   GET  /api/validar-acesso?token=XXX - Validar acesso do cliente")
    print("   POST /test-email - Testar email de boas-vindas")
    print()
    print("🚀 Vantagens do Railway:")
    print("   ✅ Resposta instantânea para webhooks")
    print("   ✅ Sem cold starts")
    print("   ✅ Sempre ativo")
    print("   ✅ Ideal para Hotmart")
    print()
    print("🌐 Acesse: http://localhost:5000")
    print("⏹️  Para parar: Ctrl+C")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Sistema de webhook parado pelo usuário.")
    except Exception as e:
        logger.error(f"\n❌ Erro ao iniciar sistema de webhook: {e}")
