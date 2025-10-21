# webhook_hotmart_optimized.py - VERSÃO OTIMIZADA PARA CORRIGIR ERRO 408

from flask import Flask, request, jsonify, render_template
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
            "application_name": "hotmart_webhook_optimized"
            # Nota: statement_timeout removido pois Neon pooled connection não suporta
        }
    )
else:
    engine = None

# Thread pool para operações assíncronas
executor = ThreadPoolExecutor(max_workers=2)


@app.route('/')
def index():
    return "Webhook Hotmart OTIMIZADO está funcionando!"


@app.route('/test')
def test():
    return "Test endpoint funcionando!"


@app.route('/health', methods=['GET'])
def health_check():
    """Health check otimizado"""
    try:
        if not engine:
            return jsonify({"status": "unhealthy", "database": "no_engine"}), 503
            
        # Teste rápido de conexão
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return jsonify({
            "status": "healthy", 
            "database": "neon_connected",
            "email_test": {
                "mailersend_api_key": "SIM" if os.environ.get('MAILERSEND_API_KEY') else "NÃO",
                "from_email": os.environ.get('FROM_EMAIL', 'NÃO DEFINIDO'),
                "app_url": os.environ.get('APP_URL', 'NÃO DEFINIDO')
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route('/criar-usuario-teste', methods=['POST'])
def criar_usuario_teste():
    """Criar usuário de teste e enviar email de ativação"""
    try:
        data = request.get_json()
        email = data.get('email')
        nome = data.get('nome', 'Usuário Teste')
        
        if not email:
            return jsonify({"status": "error", "message": "Email é obrigatório"}), 400
        
        from datetime import datetime, timedelta
        
        # Gerar token
        token = secrets.token_urlsafe(32)
        expiracao = datetime.now() + timedelta(hours=48)
        
        with engine.connect() as conn:
            # Verificar se usuário já existe
            result = conn.execute(
                sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email"),
                {"email": email}
            )
            existe = result.fetchone()
            
            if existe:
                # Atualizar usuário existente
                conn.execute(
                    sqlalchemy.text("""
                        UPDATE usuarios
                        SET status_conta = 'pendente',
                            token_ativacao = :token,
                            data_expiracao_token = :expiracao,
                            senha_hash = NULL,
                            data_ativacao = NULL,
                            data_aceite_termos = NULL,
                            nome = :nome
                        WHERE email = :email
                    """),
                    {"token": token, "expiracao": expiracao, "email": email, "nome": nome}
                )
                acao = "atualizado"
            else:
                # Criar novo usuário
                conn.execute(
                    sqlalchemy.text("""
                        INSERT INTO usuarios 
                        (nome, email, status_assinatura, status_conta, token_ativacao, data_expiracao_token)
                        VALUES 
                        (:nome, :email, 'ativo', 'pendente', :token, :expiracao)
                    """),
                    {"nome": nome, "email": email, "token": token, "expiracao": expiracao}
                )
                acao = "criado"
            
            conn.commit()
        
        # Enviar email de ativação
        try:
            from email_service import enviar_email_ativacao
            sucesso, mensagem = enviar_email_ativacao(email, nome, token)
            email_enviado = sucesso
            email_mensagem = mensagem
        except Exception as e:
            email_enviado = False
            email_mensagem = str(e)
        
        link_ativacao = f"{os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')}/ativar/{token}"
        
        return jsonify({
            "status": "success",
            "message": f"Usuário {acao} com sucesso",
            "email": email,
            "nome": nome,
            "token": token,
            "link_ativacao": link_ativacao,
            "email_enviado": email_enviado,
            "email_mensagem": email_mensagem,
            "expira_em": expiracao.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao criar usuário de teste: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/test-email', methods=['GET'])
def test_email():
    """Endpoint para testar envio de email"""
    try:
        # Verificar se email_service está disponível
        try:
            from email_service import testar_envio_email
            email_service_ok = True
        except ImportError:
            email_service_ok = False
            
        # Teste real de envio de email
        email_teste = request.args.get('email', 'suellencna@gmail.com')
        
        if email_service_ok:
            # Tentar enviar email real
            try:
                sucesso, mensagem = testar_envio_email(email_teste)
                return jsonify({
                    "status": "success" if sucesso else "error", 
                    "message": f"Email {'enviado' if sucesso else 'falhou'}: {mensagem}",
                    "email_destino": email_teste,
                    "email_service_available": email_service_ok,
                    "mailersend_api_key": "SIM" if os.environ.get('MAILERSEND_API_KEY') else "NÃO",
                    "from_email": os.environ.get('FROM_EMAIL', 'NÃO DEFINIDO'),
                    "app_url": os.environ.get('APP_URL', 'NÃO DEFINIDO')
                }), 200
            except Exception as email_error:
                return jsonify({
                    "status": "error", 
                    "message": f"Erro ao enviar email: {str(email_error)}",
                    "email_service_available": email_service_ok,
                    "mailersend_api_key": "SIM" if os.environ.get('MAILERSEND_API_KEY') else "NÃO"
                }), 500
        else:
            return jsonify({
                "status": "error", 
                "message": "Email service não disponível",
                "email_service_available": email_service_ok
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500


@app.route('/ativar/<token>')
def ativar_conta_page(token):
    """Página de ativação de conta"""
    # Por enquanto, vamos servir uma página estática
    with open('ativacao_estatica.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    from flask import Response
    return Response(html_content, mimetype='text/html')


@app.route('/api/verificar-token/<token>', methods=['GET'])
def verificar_token(token):
    """Verifica se o token é válido e retorna informações do usuário"""
    try:
        with engine.connect() as conn:
            # Buscar usuário pelo token
            result = conn.execute(
                sqlalchemy.text("""
                    SELECT nome, email, data_expiracao_token 
                    FROM usuarios 
                    WHERE token_ativacao = :token 
                    AND status_conta = 'pendente'
                """),
                {"token": token}
            )
            user = result.fetchone()
            
            if not user:
                return jsonify({"valid": False, "message": "Token inválido ou já utilizado"}), 404
            
            # Verificar se o token expirou (48 horas)
            from datetime import datetime
            if user[2] and datetime.now() > user[2]:
                return jsonify({"valid": False, "message": "Token expirado"}), 400
            
            return jsonify({
                "valid": True,
                "nome": user[0],
                "email": user[1]
            }), 200
            
    except Exception as e:
        logger.error(f"Erro ao verificar token: {e}")
        return jsonify({"valid": False, "message": "Erro ao verificar token"}), 500


@app.route('/api/ativar-conta/<token>', methods=['POST'])
def ativar_conta_api(token):
    """API para ativar conta e definir senha"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({"message": "Senha é obrigatória"}), 400
        
        # Hash da senha
        senha_hash = ph.hash(password)
        
        with engine.connect() as conn:
            # Buscar usuário
            result = conn.execute(
                sqlalchemy.text("""
                    SELECT id, email, nome 
                    FROM usuarios 
                    WHERE token_ativacao = :token 
                    AND status_conta = 'pendente'
                """),
                {"token": token}
            )
            user = result.fetchone()
            
            if not user:
                return jsonify({"message": "Token inválido ou já utilizado"}), 404
            
            # Atualizar usuário
            from datetime import datetime
            conn.execute(
                sqlalchemy.text("""
                    UPDATE usuarios 
                    SET senha_hash = :senha_hash,
                        status_conta = 'ativo',
                        token_ativacao = NULL,
                        data_expiracao_token = NULL,
                        data_aceite_termos = :data_aceite,
                        data_ativacao = :data_ativacao
                    WHERE token_ativacao = :token
                """),
                {
                    "senha_hash": senha_hash,
                    "token": token,
                    "data_aceite": datetime.now(),
                    "data_ativacao": datetime.now()
                }
            )
            conn.commit()
            
            # Enviar email de boas-vindas
            try:
                from email_service import enviar_email_boas_vindas
                enviar_email_boas_vindas(user[1], user[2])
            except Exception as email_error:
                logger.warning(f"Erro ao enviar email de boas-vindas: {email_error}")
            
            logger.info(f"Conta ativada com sucesso: {user[1]}")
            
            return jsonify({
                "message": "Conta ativada com sucesso!",
                "redirect_url": os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')
            }), 200
            
    except Exception as e:
        logger.error(f"Erro ao ativar conta: {e}")
        return jsonify({"message": "Erro ao ativar conta"}), 500


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
    """Processa compra em background com sistema de ativação"""
    try:
        logger.info(f"--- BACKGROUND: Processando compra para {email} ---")
        
        from datetime import datetime, timedelta
        
        with engine.connect() as conn:
            # Verificação rápida
            query_check = sqlalchemy.text("SELECT email, status_conta FROM usuarios WHERE email = :email LIMIT 1")
            result = conn.execute(query_check, {"email": email}).first()

            if result:
                # Usuário existe - reativar
                query_update = sqlalchemy.text(
                    "UPDATE usuarios SET status_assinatura = 'ativo', status_conta = 'ativo' WHERE email = :email")
                conn.execute(query_update, {"email": email})
                conn.commit()
                logger.info(f"--- BACKGROUND: Usuário {email} reativado ---")

            else:
                # Criar novo usuário com token de ativação
                token_ativacao = secrets.token_urlsafe(32)
                data_expiracao = datetime.now() + timedelta(hours=48)
                
                query_insert = sqlalchemy.text("""
                    INSERT INTO usuarios 
                    (nome, email, status_assinatura, status_conta, token_ativacao, data_expiracao_token) 
                    VALUES 
                    (:nome, :email, 'ativo', 'pendente', :token, :expiracao)
                """)
                conn.execute(query_insert, {
                    "nome": nome, 
                    "email": email,
                    "token": token_ativacao,
                    "expiracao": data_expiracao
                })
                conn.commit()
                
                # Enviar email de ativação
                try:
                    from email_service import enviar_email_ativacao
                    sucesso, mensagem = enviar_email_ativacao(email, nome, token_ativacao)
                    if sucesso:
                        logger.info(f"--- BACKGROUND: Email de ativação enviado para {email} ---")
                    else:
                        logger.error(f"--- BACKGROUND: Falha ao enviar email: {mensagem} ---")
                except Exception as email_error:
                    logger.error(f"--- BACKGROUND: Erro ao enviar email: {email_error} ---")
                
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
