#!/usr/bin/env python3
"""
🚀 WEBHOOK HOTMART UNIFICADO - SISTEMA COMPLETO
===============================================

Sistema otimizado para receber webhooks da Hotmart e processar compras:
- Recebe webhook da Hotmart
- Cadastra usuário no banco NEON
- Envia email de ativação via Gmail
- Redireciona para sistema no RENDER

Para deploy no Railway:
    Configurar como Web Service
"""

import os
import json
import secrets
import hashlib
import smtplib
import ssl
import logging
import threading
import requests
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor
import argon2
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurar hash de senha
password_hasher = argon2.PasswordHasher()

# Configurações
DATABASE_URL = os.environ.get('DATABASE_URL')
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
RENDER_APP_URL = os.environ.get('RENDER_APP_URL', 'https://ponto-otimo-invest.onrender.com')
RAILWAY_APP_URL = os.environ.get('RAILWAY_APP_URL', 'https://web-production-040d1.up.railway.app')

# Rate limiting para evitar bloqueios do Gmail
EMAIL_SEND_LOCK = threading.Lock()
LAST_EMAIL_TIME = 0
EMAIL_DELAY = 2  # 2 segundos entre emails

def get_db_connection():
    """Conectar ao banco de dados Neon"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
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
                    hotmart_transaction_id VARCHAR(255),
                    status_assinatura VARCHAR(50) DEFAULT 'ativo'
                )
            """)
            conn.commit()
            logger.info("Tabela de usuários criada/verificada com sucesso")
            return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela: {e}")
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
    """Enviar email de ativação via Gmail SMTP com rate limiting"""
    global LAST_EMAIL_TIME
    
    # Rate limiting para evitar bloqueios do Gmail
    with EMAIL_SEND_LOCK:
        current_time = time.time()
        time_since_last = current_time - LAST_EMAIL_TIME
        
        if time_since_last < EMAIL_DELAY:
            sleep_time = EMAIL_DELAY - time_since_last
            logger.info(f"⏳ Rate limiting: aguardando {sleep_time:.1f}s antes de enviar email")
            time.sleep(sleep_time)
        
        LAST_EMAIL_TIME = time.time()
    
    try:
        # Configurar SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = f"Ponto Ótimo Investimentos <{GMAIL_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = "Ative sua conta - Ponto Ótimo Investimentos"
        msg['Reply-To'] = GMAIL_EMAIL
        msg['X-Mailer'] = "Ponto Ótimo Investimentos System"
        msg['X-Priority'] = "3"
        
        # Corpo do email
        activation_link = f"{RAILWAY_APP_URL}/ativar/{token}"
        temp_password = secrets.token_urlsafe(8)
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f8f9fa; padding: 30px; text-align: center; border: 1px solid #dee2e6;">
                <h1 style="color: #333; margin: 0;">Bem-vindo ao Ponto Ótimo Investimentos</h1>
            </div>
            
            <div style="padding: 30px; background: white;">
                <h2 style="color: #333;">Olá, {nome}!</h2>
                
                <p>Sua compra foi aprovada com sucesso! Para ativar sua conta e acessar o sistema, clique no link abaixo:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{activation_link}" 
                       style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Ativar Minha Conta
                    </a>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #dee2e6;">
                    <h3 style="color: #495057; margin-top: 0;">Suas Credenciais Temporárias:</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Senha Temporária:</strong> <code style="background: #fff; padding: 2px 5px; border-radius: 3px; border: 1px solid #dee2e6;">{temp_password}</code></p>
                    <p style="color: #dc3545; font-size: 14px;"><strong>⚠️ Importante:</strong> Você será obrigado a trocar esta senha no primeiro login.</p>
                </div>
                
                <div style="background: #d1ecf1; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #0c5460; margin-top: 0;">🚀 O que você terá acesso:</h3>
                    <ul style="color: #0c5460; margin: 0;">
                        <li>Análise de carteira com Markowitz</li>
                        <li>Simulações Monte Carlo</li>
                        <li>Métricas de risco e retorno</li>
                        <li>Comparação com benchmarks</li>
                        <li>Relatórios detalhados</li>
                    </ul>
                </div>
                
                <p>Se o botão não funcionar, copie e cole este link no seu navegador:</p>
                <p style="word-break: break-all; color: #007bff;">{activation_link}</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                
                <p style="color: #6c757d; font-size: 14px;">
                    Este email foi enviado automaticamente. Se você não fez esta compra, entre em contato conosco.
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
        
        logger.info(f"✅ Email de ativação enviado com sucesso para {email}")
        return True, temp_password
        
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
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
                # Atualizar usuário existente
                cur.execute("""
                    UPDATE usuarios 
                    SET nome = %s, 
                        senha_hash = %s, 
                        status_conta = 'pendente', 
                        token_ativacao = %s, 
                        hotmart_transaction_id = %s,
                        status_assinatura = 'ativo',
                        data_criacao = CURRENT_TIMESTAMP
                    WHERE email = %s
                """, (nome, password_hash, token, hotmart_transaction_id, email))
                logger.info(f"Usuário {email} atualizado com nova compra")
            else:
                # Inserir novo usuário
                cur.execute("""
                    INSERT INTO usuarios (email, nome, senha_hash, status_conta, token_ativacao, hotmart_transaction_id, status_assinatura)
                    VALUES (%s, %s, %s, 'pendente', %s, %s, 'ativo')
                """, (email, nome, password_hash, token, hotmart_transaction_id))
                logger.info(f"Novo usuário {email} criado")
            
            conn.commit()
            return True, token
            
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        return False, str(e)
    finally:
        conn.close()

def processar_compra_background(email, nome, transaction_id, status_compra):
    """Processar compra em background para resposta rápida"""
    try:
        if status_compra == 'approved':
            # Criar usuário no banco
            success, result = create_user(email, nome, transaction_id)
            
            if not success:
                logger.error(f"Erro ao criar usuário {email}: {result}")
                return
            
            # Enviar email de ativação
            email_sent, temp_password = send_activation_email(email, nome, result)
            
            if not email_sent:
                logger.error(f"Email falhou para {email}: {temp_password}")
            else:
                logger.info(f"Processamento completo para {email}")
        else:
            logger.info(f"Status {status_compra} para {email} - não processado")
            
    except Exception as e:
        logger.error(f"Erro no processamento background para {email}: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para Railway"""
    return "HOTMART_WEBHOOK_FUNCIONANDO", 200

@app.route('/webhook/hotmart', methods=['POST'])
def webhook_hotmart():
    """Receber webhook do Hotmart - RESPOSTA RÁPIDA"""
    try:
        data = request.get_json()
        logger.info(f"Webhook Hotmart recebido: {data}")
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        # Extrair dados do webhook da Hotmart (suporta v1.0 e v2.0)
        logger.info(f"Webhook recebido - Versão: {data.get('version', '1.0')}")
        
        # Verificar se é webhook v2.0
        if data.get('version') == '2.0.0':
            # Formato v2.0 - Suportar diferentes tipos de eventos
            event_data = data.get('data', {})
            event_type = data.get('event')
            
            # Extrair dados baseado no tipo de evento
            if event_type in ['PURCHASE_APPROVED', 'PURCHASE_EXPIRED', 'PURCHASE_CANCELLED', 'PURCHASE_CANCELED', 'PURCHASE_DELAYED', 'PURCHASE_REFUNDED', 'PURCHASE_CHARGEBACK', 'PURCHASE_PROTEST']:
                # Eventos de compra - usar buyer
                buyer = event_data.get('buyer', {})
                email = buyer.get('email')
                nome = buyer.get('name')
                purchase = event_data.get('purchase', {})
                transaction_id = purchase.get('transaction') or data.get('id')
                status_compra = 'approved' if event_type == 'PURCHASE_APPROVED' else 'pending'
                
            elif event_type in ['SUBSCRIPTION_CANCELLATION', 'SUBSCRIPTION_APPROVED']:
                # Eventos de assinatura - usar subscriber
                subscriber = event_data.get('subscriber', {})
                email = subscriber.get('email')
                nome = subscriber.get('name')
                transaction_id = subscriber.get('code') or data.get('id')
                status_compra = 'approved' if event_type == 'SUBSCRIPTION_APPROVED' else 'pending'
                
            else:
                # Evento não suportado
                logger.warning(f"Evento não suportado: {event_type}")
                return jsonify({"error": f"Evento {event_type} não suportado"}), 400
            
            logger.info(f"Webhook v2.0 - Evento: {event_type}, Email: {email}, Nome: {nome}")
        else:
            # Formato v1.0 (antigo)
            buyer = data.get('buyer', {})
            email = buyer.get('email')
            nome = buyer.get('name')
            transaction = data.get('transaction', {})
            transaction_id = transaction.get('id')
            status_compra = data.get('status')
            
            logger.info(f"Webhook v1.0 - Email: {email}, Nome: {nome}")
        
        if not email or not nome:
            logger.error("Email ou nome não encontrado no webhook")
            return jsonify({"error": "Email ou nome não encontrado"}), 400
        
        # Processar em background para resposta rápida
        threading.Thread(
            target=processar_compra_background, 
            args=(email, nome, transaction_id, status_compra)
        ).start()
        
        # Resposta imediata para Hotmart
        return jsonify({
            "status": "success", 
            "message": "Webhook recebido e processamento iniciado",
            "email": email,
            "transaction_id": transaction_id
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
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
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        max-width: 600px; 
                        margin: 50px auto; 
                        padding: 20px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        text-align: center;
                    }}
                    .success {{ 
                        background: #d4edda; 
                        border: 1px solid #c3e6cb; 
                        color: #155724; 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin-bottom: 30px;
                    }}
                    .info {{ 
                        background: #e9ecef; 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin: 20px 0; 
                        text-align: left;
                    }}
                    .button {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 10px;
                        transition: transform 0.3s ease;
                    }}
                    .button:hover {{
                        transform: translateY(-2px);
                    }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #667eea; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success">
                        <h1>🎉 Conta Ativada com Sucesso!</h1>
                        <p>Olá, <strong>{user[2]}</strong>! Sua conta foi ativada com sucesso.</p>
                    </div>
                    
                    <div class="info">
                        <h2>📋 Próximos Passos:</h2>
                        <ol>
                            <li>Acesse o sistema: <strong>Ponto Ótimo Investimentos</strong></li>
                            <li>Faça login com seu email: <strong>{user[1]}</strong></li>
                            <li>Use a senha temporária que foi enviada por email</li>
                            <li><strong>Importante:</strong> Você será obrigado a trocar a senha no primeiro login</li>
                        </ol>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <a href="{RENDER_APP_URL}" class="button">
                            🚀 Acessar Sistema Agora
                        </a>
                    </div>
                    
                    <div style="margin-top: 20px; font-size: 14px; color: #666;">
                        <p>Se você tiver problemas para acessar, entre em contato conosco:</p>
                        <p><strong>Email:</strong> pontootimoinvest@gmail.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html, 200
            
    except Exception as e:
        logger.error(f"Erro ao ativar conta: {e}")
        return "Erro interno do servidor", 500
    finally:
        conn.close()

@app.route('/test-email', methods=['POST'])
def test_email():
    """Endpoint para testar envio de email - SÍNCRONO"""
    try:
        data = request.get_json()
        email = data.get('email', 'suellencna@hotmail.com')
        nome = data.get('nome', 'Teste')
        
        # Enviar email diretamente (síncrono)
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

def processar_teste_email_background(email, nome):
    """Processar teste de email em background"""
    try:
        token = generate_activation_token()
        success, result = send_activation_email(email, nome, token)
        
        if success:
            logger.info(f"✅ Email de teste enviado com sucesso para {email}")
        else:
            logger.error(f"❌ Email de teste falhou para {email}: {result}")
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de email para {email}: {e}")

@app.route('/')
def home():
    """Página inicial do webhook"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webhook Hotmart - Ponto Ótimo Invest</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                margin: 0; 
            }
            .card { 
                background-color: #ffffff; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); 
                text-align: center; 
                max-width: 600px; 
                width: 90%; 
            }
            h1 { color: #333; margin-bottom: 20px; }
            .status-box { 
                background-color: #d4edda; 
                color: #155724; 
                border: 1px solid #c3e6cb; 
                border-radius: 10px; 
                padding: 20px; 
                margin-bottom: 20px; 
            }
            .endpoints { text-align: left; margin-bottom: 20px; }
            .endpoints h3 { color: #333; margin-bottom: 10px; }
            .endpoint { 
                background-color: #f8f9fa; 
                border: 1px solid #e2e3e5; 
                border-radius: 5px; 
                padding: 10px; 
                margin-bottom: 8px; 
                font-family: 'Courier New', monospace; 
            }
            .button { 
                display: inline-block; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: #ffffff; 
                padding: 12px 24px; 
                text-decoration: none; 
                border-radius: 25px; 
                margin: 5px; 
                font-weight: bold;
                transition: transform 0.3s ease;
            }
            .button:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 Webhook Hotmart - Ponto Ótimo Invest</h1>
            
            <div class="status-box">
                <h2>✔ Sistema de webhook funcionando!</h2>
                <p>
                    Recebe compras da Hotmart<br>
                    Cadastra usuários no NEON<br>
                    Envia emails de ativação<br>
                    Integra com RENDER
                </p>
            </div>
            
            <div class="endpoints">
                <h3>Endpoints do sistema:</h3>
                <div class="endpoint"><strong>GET /health</strong> - Health check</div>
                <div class="endpoint"><strong>POST /webhook/hotmart</strong> - Webhook Hotmart (compras)</div>
                <div class="endpoint"><strong>GET /ativar/&lt;token&gt;</strong> - Ativar conta do usuário</div>
                <div class="endpoint"><strong>POST /test-email</strong> - Testar envio de email</div>
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
    # Criar tabela ao iniciar
    create_user_table()
    
    logger.info("🚀 INICIANDO WEBHOOK HOTMART UNIFICADO - PONTO ÓTIMO INVEST")
    logger.info("=" * 70)
    
    if not GMAIL_APP_PASSWORD:
        logger.warning("⚠️  AVISO: GMAIL_APP_PASSWORD não configurada.")
        logger.warning("   Configure para envio de emails de ativação.")
    
    logger.info(f"📧 Email configurado: {GMAIL_EMAIL}")
    logger.info(f"🌐 URL Render: {RENDER_APP_URL}")
    logger.info(f"🌐 URL Railway: {RAILWAY_APP_URL}")
    logger.info(f"💾 Banco de dados: {DATABASE_URL}")
    logger.info("")
    logger.info("🔗 Endpoints do sistema:")
    logger.info("   GET  /health - Health check")
    logger.info("   POST /webhook/hotmart - Webhook Hotmart (compras)")
    logger.info("   GET  /ativar/<token> - Ativar conta do usuário")
    logger.info("   POST /test-email - Testar envio de email")
    logger.info("")
    logger.info("🚀 Vantagens do sistema unificado:")
    logger.info("   ✅ Resposta instantânea para webhooks")
    logger.info("   ✅ Processamento em background")
    logger.info("   ✅ Integração completa Hotmart → NEON → Gmail → RENDER")
    logger.info("   ✅ Sistema robusto e confiável")
    logger.info("")
    # Obter porta do Railway ou usar 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"🌐 Acesse: http://localhost:{port}")
    logger.info("⏹️  Para parar: Ctrl+C")
    logger.info("=" * 70)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("\n🛑 Sistema de webhook parado pelo usuário.")
    except Exception as e:
        logger.error(f"\n❌ Erro ao iniciar sistema de webhook: {e}")
