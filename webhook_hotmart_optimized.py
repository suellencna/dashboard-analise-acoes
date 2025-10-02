# webhook_hotmart_optimized.py - VERSÃO OTIMIZADA PARA CORRIGIR ERRO 408

from flask import Flask, request, jsonify
import os
import sqlalchemy
from argon2 import PasswordHasher
import secrets
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração otimizada do Argon2 para ser mais rápido
ph = PasswordHasher(
    time_cost=1,        # Reduzido de 3 para 1 (mais rápido)
    memory_cost=65536,  # Mantido
    parallelism=2       # Reduzido de 4 para 2
)

DATABASE_URL = os.environ.get('DATABASE_URL')
HOTMART_HOTTOK = os.environ.get('HOTMART_HOTTOK')

# Configurações ULTRA otimizadas para Neon
if DATABASE_URL:
    engine = sqlalchemy.create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=180,  # Reduzido para 3 minutos
        pool_timeout=5,    # Timeout de 5 segundos
        pool_size=3,       # Pool menor
        max_overflow=2,    # Overflow menor
        connect_args={
            "connect_timeout": 5,  # Timeout reduzido
            "application_name": "hotmart_webhook_optimized",
            "options": "-c statement_timeout=10000"  # 10 segundos max por query
        }
    )
else:
    engine = None

# Thread pool para operações assíncronas
executor = ThreadPoolExecutor(max_workers=2)


@app.route('/')
def index():
    return "Webhook Hotmart OTIMIZADO está funcionando!"


@app.route('/health', methods=['GET'])
def health_check():
    """Health check otimizado"""
    try:
        if not engine:
            return jsonify({"status": "unhealthy", "database": "no_engine"}), 503
            
        # Teste rápido de conexão
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "neon_connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route('/webhook/hotmart', methods=['POST'])
def hotmart_webhook():
    start_time = time.time()
    logger.info("=== WEBHOOK OTIMIZADO RECEBIDO ===")
    
    try:
        # 1. VALIDAÇÃO RÁPIDA
        hottok_from_request = request.headers.get('X-Hotmart-Hottok')
        if not hottok_from_request or hottok_from_request != HOTMART_HOTTOK:
            logger.warning("=> FALHA NA AUTENTICAÇÃO")
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        logger.info("=> AUTENTICAÇÃO OK!")

        # 2. PROCESSAR DADOS RAPIDAMENTE
        if not request.is_json:
            return jsonify({"status": "ignored", "message": "Not JSON"}), 200
            
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "ignored", "message": "No data"}), 200

        # Extrair dados essenciais
        evento = data.get('event')
        dados_principais = data.get('data', {})
        comprador = dados_principais.get('buyer', {})

        email = comprador.get('email')
        nome = comprador.get('name', 'Usuário')

        if not email:
            logger.info(f"--- Evento '{evento}' sem email. Ignorando ---")
            return jsonify({"status": "ignored", "message": "No email"}), 200

        logger.info(f"--- Processando: Evento={evento}, Email={email}")

        # 3. RESPOSTA IMEDIATA PARA HOTMART (antes de processar banco)
        response_data = {"status": "processing", "message": "Request received"}
        
        # 4. PROCESSAR EM BACKGROUND (não bloquear resposta)
        if evento == 'PURCHASE_APPROVED':
            executor.submit(processar_compra_background, email, nome)
            response_data["message"] = "Purchase processing started"
        else:
            novo_status = 'ativo' if evento in ['SUBSCRIPTION_ACTIVATED'] else 'inativo'
            executor.submit(atualizar_status_background, email, novo_status)
            response_data["message"] = "Status update started"

        # 5. RESPOSTA RÁPIDA (dentro de 2 segundos)
        processing_time = time.time() - start_time
        logger.info(f"--- RESPOSTA ENVIADA EM: {processing_time:.2f}s ---")
        
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"--- ERRO GERAL: {e} ---")
        return jsonify({"status": "error", "message": "Internal error"}), 500


def processar_compra_background(email, nome):
    """Processa compra em background"""
    try:
        logger.info(f"--- BACKGROUND: Processando compra para {email} ---")
        
        with engine.connect() as conn:
            # Verificação rápida
            query_check = sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email LIMIT 1")
            result = conn.execute(query_check, {"email": email}).first()

            if result:
                # Usuário existe - reativar
                query_update = sqlalchemy.text(
                    "UPDATE usuarios SET status_assinatura = 'ativo' WHERE email = :email")
                conn.execute(query_update, {"email": email})
                conn.commit()
                logger.info(f"--- BACKGROUND: Usuário {email} reativado ---")

            else:
                # Criar novo usuário com senha mais simples
                temp_password = secrets.token_urlsafe(6)  # Senha mais curta
                hashed_password = ph.hash(temp_password)
                
                query_insert = sqlalchemy.text(
                    "INSERT INTO usuarios (nome, email, senha_hash, status_assinatura) VALUES (:nome, :email, :senha_hash, 'ativo')")
                conn.execute(query_insert, {
                    "nome": nome, 
                    "email": email, 
                    "senha_hash": hashed_password
                })
                conn.commit()
                logger.info(f"--- BACKGROUND: Usuário {email} criado ---")
                
    except Exception as e:
        logger.error(f"--- BACKGROUND ERRO: {e} ---")


def atualizar_status_background(email, novo_status):
    """Atualiza status em background"""
    try:
        logger.info(f"--- BACKGROUND: Atualizando status {email} para {novo_status} ---")
        
        with engine.connect() as conn:
            query = sqlalchemy.text(
                "UPDATE usuarios SET status_assinatura = :status WHERE email = :email")
            result = conn.execute(query, {"status": novo_status, "email": email})
            conn.commit()
            
            if result.rowcount > 0:
                logger.info(f"--- BACKGROUND: Status {email} atualizado para {novo_status} ---")
            else:
                logger.warning(f"--- BACKGROUND: Usuário {email} não encontrado ---")
                
    except Exception as e:
        logger.error(f"--- BACKGROUND ERRO: {e} ---")


# Configurações Flask otimizadas
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False

@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
