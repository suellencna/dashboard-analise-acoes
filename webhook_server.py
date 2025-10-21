# webhook_server.py (VERSÃO CORRIGIDA PARA ERRO 408)

from flask import Flask, request, jsonify
import os
import sqlalchemy
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
ph = PasswordHasher()

DATABASE_URL = os.environ.get('DATABASE_URL')
HOTMART_HOTTOK = os.environ.get('HOTMART_HOTTOK')

# Configurações de conexão otimizadas para evitar timeout
if DATABASE_URL:
    engine = sqlalchemy.create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexões antes de usar
        pool_recycle=300,    # Recicla conexões a cada 5 minutos
        connect_args={
            "connect_timeout": 10,  # Timeout de conexão de 10 segundos
            "application_name": "hotmart_webhook"
        }
    )
else:
    engine = None


@app.route('/')
def index():
    return "Servidor de Webhook está no ar."


@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """Endpoint para testar o webhook"""
    if request.method == 'GET':
        return jsonify({
            "status": "ok",
            "message": "Webhook server is running",
            "timestamp": time.time()
        }), 200
    
    # Para POST, simular um webhook de teste
    try:
        data = request.get_json(silent=True) or {}
        return jsonify({
            "status": "received",
            "data": data,
            "headers": dict(request.headers),
            "timestamp": time.time()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": time.time()
        }), 400


@app.route('/webhook/hotmart', methods=['POST'])
def hotmart_webhook():
    start_time = time.time()
    logger.info("--- NOVO WEBHOOK RECEBIDO ---")

    # 1. Validação de Segurança RÁPIDA
    hottok_from_request = request.headers.get('X-Hotmart-Hottok')
    if not hottok_from_request or hottok_from_request != HOTMART_HOTTOK:
        logger.warning("=> RESULTADO: FALHA NA AUTENTICAÇÃO.")
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    logger.info("=> RESULTADO: AUTENTICAÇÃO BEM-SUCEDIDA!")

    # 2. Verificação rápida do engine
    if not engine:
        logger.error("=> ERRO: Engine de banco não disponível.")
        return jsonify({"status": "error", "message": "Database not available"}), 500

    # 3. Extração de Dados e Processamento OTIMIZADO
    try:
        # Verificar se o request tem JSON válido
        if not request.is_json:
            logger.warning("=> AVISO: Request não é JSON válido.")
            return jsonify({"status": "ignored", "message": "Not a JSON request"}), 200
            
        data = request.get_json(silent=True)
        
        if not data:
            logger.warning("=> AVISO: Request sem JSON válido ou vazio.")
            return jsonify({"status": "ignored", "message": "No valid JSON"}), 200

        # Extração segura e rápida
        evento = data.get('event')
        dados_principais = data.get('data', {})
        comprador = dados_principais.get('buyer', {})

        email = comprador.get('email')
        nome = comprador.get('name', 'Usuário')

        # Validação rápida
        if not email:
            logger.info(f"--- AVISO: Evento '{evento}' sem email. Ignorando. ---")
            return jsonify({"status": "ignored", "message": "No buyer email found"}), 200

        logger.info(f"--- Processando: Evento={evento}, Email={email}")

        # 4. Processamento com timeout controlado
        try:
            if evento == 'PURCHASE_APPROVED':
                # Processar compra aprovada
                resultado = processar_compra_aprovada(email, nome)
                logger.info(f"--- COMPRA APROVADA: {resultado} ---")
                return jsonify({"status": "success", "message": resultado}), 201

            else:
                # Processar outros eventos
                novo_status = 'ativo' if evento in ['SUBSCRIPTION_ACTIVATED'] else 'inativo'
                resultado = atualizar_status_usuario(email, novo_status)
                logger.info(f"--- STATUS ATUALIZADO: {resultado} ---")
                return jsonify({"status": "success", "message": resultado}), 200

        except sqlalchemy.exc.TimeoutError:
            logger.error("--- ERRO: Timeout no banco de dados ---")
            return jsonify({"status": "error", "message": "Database timeout"}), 408
        except Exception as db_error:
            logger.error(f"--- ERRO DE BANCO: {db_error} ---")
            return jsonify({"status": "error", "message": "Database error"}), 500

    except Exception as e:
        logger.error(f"--- ERRO GERAL: {e} ---")
        # Se for um erro de parsing JSON, retornar 400
        if "JSON" in str(e) or "decode" in str(e).lower():
            return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
    
    finally:
        # Log do tempo de processamento
        processing_time = time.time() - start_time
        logger.info(f"--- TEMPO DE PROCESSAMENTO: {processing_time:.2f}s ---")


def processar_compra_aprovada(email, nome):
    """Processa uma compra aprovada de forma otimizada"""
    with engine.connect() as conn:
        # Verificação rápida se usuário existe
        query_check = sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email LIMIT 1")
        result = conn.execute(query_check, {"email": email}).first()

        if result:
            # Usuário existe - apenas reativar assinatura
            query_update = sqlalchemy.text(
                "UPDATE usuarios SET status_assinatura = 'ativo' WHERE email = :email")
            conn.execute(query_update, {"email": email})
            conn.commit()
            return "User already exists, subscription reactivated"

        else:
            # Usuário não existe - criar novo
            temp_password = secrets.token_urlsafe(8)
            hashed_password = ph.hash(temp_password)
            
            query_insert = sqlalchemy.text(
                "INSERT INTO usuarios (nome, email, senha_hash, status_assinatura) VALUES (:nome, :email, :senha_hash, 'ativo')")
            conn.execute(query_insert, {
                "nome": nome, 
                "email": email, 
                "senha_hash": hashed_password
            })
            conn.commit()
            return "User created successfully"


def atualizar_status_usuario(email, novo_status):
    """Atualiza status do usuário de forma otimizada"""
    with engine.connect() as conn:
        query = sqlalchemy.text(
            "UPDATE usuarios SET status_assinatura = :status WHERE email = :email")
        result = conn.execute(query, {"status": novo_status, "email": email})
        conn.commit()
        
        if result.rowcount > 0:
            return f"User status updated to {novo_status}"
        else:
            return f"User not found: {email}"


# Configurações adicionais para o Flask
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False

# Middleware para adicionar headers de resposta
@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        if engine:
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        else:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 503
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)