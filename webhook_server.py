# webhook_server.py (VERSÃO FINAL E ROBUSTA)

# ... (importações e configurações iniciais) ...
from flask import Flask, request, jsonify
import os
import sqlalchemy
from passlib.context import CryptContext
import secrets

app = Flask(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = os.environ.get('DATABASE_URL')
HOTMART_HOTTOK = os.environ.get('HOTMART_HOTTOK')
engine = sqlalchemy.create_engine(DATABASE_URL) if DATABASE_URL else None


@app.route('/')
def index():
    return "Servidor de Webhook está no ar."


@app.route('/webhook/hotmart', methods=['POST'])
def hotmart_webhook():
    print("--- NOVO WEBHOOK RECEBIDO ---")

    # 1. Validação de Segurança
    hottok_from_request = request.headers.get('X-Hotmart-Hottok')
    if not hottok_from_request or hottok_from_request != HOTMART_HOTTOK:
        print("=> RESULTADO: FALHA NA AUTENTICAÇÃO.")
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    print("=> RESULTADO: AUTENTICAÇÃO BEM-SUCEDIDA!")

    # 2. Extração de Dados e Criação do Usuário
    try:
        data = request.json

        # --- LÓGICA DE EXTRAÇÃO SEGURA E CORRIGIDA ---
        evento = data.get('event')
        # Acessa os dados de forma segura, evitando KeyErrors
        dados_principais = data.get('data', {})
        comprador = dados_principais.get('buyer', {})

        email = comprador.get('email')
        nome = comprador.get('name')

        # Se não encontrar o email, não há o que fazer
        if not email:
            print(f"--- AVISO: Evento '{evento}' recebido sem email de comprador. Ignorando. ---")
            return jsonify({"status": "ignored", "message": "No buyer email found"}), 200

        print(f"--- Dados extraídos: Evento={evento}, Email={email}")

        if evento == 'PURCHASE_APPROVED':
            print("--- Evento APROVADO. Tentando criar usuário... ---")
            temp_password = secrets.token_urlsafe(8)
            hashed_password = pwd_context.hash(temp_password)

            with engine.connect() as conn:
                query_check = sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email")
                result = conn.execute(query_check, {"email": email}).first()

                if result:
                    # Se o usuário já existe, apenas garante que a assinatura está ativa
                    query_update = sqlalchemy.text(
                        "UPDATE usuarios SET status_assinatura = 'ativo' WHERE email = :email")
                    conn.execute(query_update, {"email": email})
                    conn.commit()
                    print(f"--- AVISO: Usuário {email} já existe. Assinatura reativada. ---")
                    return jsonify({"status": "ok", "message": "User already exists, subscription reactivated"}), 200

                # Se não existe, insere o novo usuário
                query_insert = sqlalchemy.text(
                    "INSERT INTO usuarios (nome, email, senha_hash, status_assinatura) VALUES (:nome, :email, :senha_hash, 'ativo')")
                conn.execute(query_insert, {"nome": nome, "email": email, "senha_hash": hashed_password})
                conn.commit()
                print(f"--- SUCESSO: Usuário {email} criado. ---")

            return jsonify({"status": "success", "message": "User created"}), 201

        else:  # Para todos os outros eventos (cancelamento, chargeback, etc.)
            novo_status = 'inativo'
            if evento in ['SUBSCRIPTION_ACTIVATED']:
                novo_status = 'ativo'

            with engine.connect() as conn:
                query = sqlalchemy.text("UPDATE usuarios SET status_assinatura = :status WHERE email = :email")
                conn.execute(query, {"status": novo_status, "email": email})
                conn.commit()
                print(f"--- SUCESSO: Status do usuário {email} atualizado para '{novo_status}'. ---")

            return jsonify({"status": "success", "message": f"User status updated to {novo_status}"}), 200

    except Exception as e:
        print(f"--- ERRO 500: Ocorreu um erro interno no processamento: {e} ---")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500