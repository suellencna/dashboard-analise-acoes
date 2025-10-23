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
                            senha_hash = 'TEMP_PASSWORD_TO_BE_CHANGED',
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
                        (nome, email, status_assinatura, status_conta, token_ativacao, data_expiracao_token, senha_hash)
                        VALUES 
                        (:nome, :email, 'ativo', 'pendente', :token, :expiracao, 'TEMP_PASSWORD_TO_BE_CHANGED')
                    """),
                    {"nome": nome, "email": email, "token": token, "expiracao": expiracao}
                )
                acao = "criado"
            
            conn.commit()
        
        # Enviar email de ativação via Gmail SMTP
        try:
            from email_service_gmail import enviar_email_ativacao_gmail
            sucesso, mensagem = enviar_email_ativacao_gmail(email, nome, token)
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
    """Página de ativação de conta - versão inline funcional"""
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ativar Conta - Ponto Ótimo Invest</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
            text-align: center;
        }}
        
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .logo h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin: 0;
        }}
        
        .logo p {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin: 5px 0 0 0;
        }}
        
        h2 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        
        .subtitle {{
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        
        .token-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            font-family: monospace;
            font-size: 14px;
            color: #666;
        }}
        
        .form-group {{
            margin-bottom: 20px;
            text-align: left;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
        }}
        
        input[type="password"] {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        
        input[type="password"]:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .checkbox-group {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            text-align: left;
        }}
        
        .checkbox-group input[type="checkbox"] {{
            margin-right: 10px;
            transform: scale(1.2);
        }}
        
        .checkbox-group label {{
            margin-bottom: 0;
            font-weight: normal;
            color: #555;
        }}
        
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            width: 100%;
            margin-bottom: 20px;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        
        .disclaimer {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            text-align: left;
        }}
        
        .disclaimer h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        
        .disclaimer p {{
            color: #856404;
            font-size: 14px;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>PONTO ÓTIMO INVEST</h1>
            <p>Ferramentas de Análise de Investimentos</p>
        </div>
        
        <h2>🔐 Ativar Conta</h2>
        <p class="subtitle">Defina sua senha para acessar a plataforma</p>
        
        <div class="token-info">
            <strong>Token:</strong> {token}
        </div>
        
        <form id="activationForm">
            <div class="form-group">
                <label for="password">Nova Senha:</label>
                <input type="password" id="password" name="password" required minlength="6" placeholder="Digite sua senha (mínimo 6 caracteres)">
            </div>
            
            <div class="form-group">
                <label for="confirmPassword">Confirmar Senha:</label>
                <input type="password" id="confirmPassword" name="confirmPassword" required minlength="6" placeholder="Confirme sua senha">
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="acceptTerms" name="acceptTerms" required>
                <label for="acceptTerms">Aceito os <a href="#" style="color: #667eea;">Termos de Uso</a> e <a href="#" style="color: #667eea;">Política de Privacidade</a></label>
            </div>
            
            <button type="submit" class="btn" id="submitBtn">
                🚀 Ativar Minha Conta
            </button>
        </form>
        
        <div class="disclaimer">
            <h3>⚠️ Aviso Importante</h3>
            <p>
                Esta plataforma fornece FERRAMENTAS ANALÍTICAS e DADOS HISTÓRICOS para auxiliar na sua tomada de decisão de investimentos. 
                As informações e ferramentas aqui apresentadas <strong>NÃO CONSTITUEM RECOMENDAÇÃO DE INVESTIMENTO</strong>, consultoria ou oferta de compra/venda de quaisquer ativos financeiros. 
                O desempenho passado não é garantia de resultados futuros. Investir no mercado financeiro envolve riscos, e você deve realizar sua própria pesquisa e/ou consultar um profissional qualificado antes de tomar qualquer decisão de investimento.
            </p>
        </div>
    </div>

    <script>
        document.getElementById('activationForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const acceptTerms = document.getElementById('acceptTerms').checked;
            
            if (password !== confirmPassword) {{
                alert('As senhas não coincidem!');
                return;
            }}
            
            if (password.length < 6) {{
                alert('A senha deve ter pelo menos 6 caracteres!');
                return;
            }}
            
            if (!acceptTerms) {{
                alert('Você deve aceitar os Termos de Uso!');
                return;
            }}
            
            try {{
                const response = await fetch(`/api/ativar-conta/{token}`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        password: password
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    alert('✅ Conta ativada com sucesso!');
                    window.location.href = '/';
                }} else {{
                    alert('❌ Erro: ' + result.message);
                }}
                
            }} catch (error) {{
                console.error('Erro:', error);
                alert('❌ Erro ao ativar conta. Tente novamente.');
            }}
        }});
    </script>
</body>
</html>
    """
    
    from flask import Response
    return Response(html_content, mimetype='text/html; charset=utf-8')


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
                    (nome, email, status_assinatura, status_conta, token_ativacao, data_expiracao_token, senha_hash) 
                    VALUES 
                    (:nome, :email, 'ativo', 'pendente', :token, :expiracao, 'TEMP_PASSWORD_TO_BE_CHANGED')
                """)
                conn.execute(query_insert, {
                    "nome": nome, 
                    "email": email,
                    "token": token_ativacao,
                    "expiracao": data_expiracao
                })
                conn.commit()
                
                # Enviar email de ativação via Gmail SMTP
                try:
                    from email_service_gmail import enviar_email_ativacao_gmail
                    sucesso, mensagem = enviar_email_ativacao_gmail(email, nome, token_ativacao)
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
