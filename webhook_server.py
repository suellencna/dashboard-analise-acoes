# webhook_server.py (VERSÃO FINALÍSSIMA)

# ... (mantenha todas as importações e configurações iniciais) ...
from flask import Flask, request, jsonify
import os
import sqlalchemy
from passlib.context import CryptContext
import secrets
import time

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

        # --- LÓGICA DE EXTRAÇÃO CORRIGIDA ---
        evento = data.get('event')
        email = data['data']['buyer']['email']
        nome = data['data']['buyer']['name']
        print(f"--- Dados extraídos: Evento={evento}, Email={email}")

        if evento == 'PURCHASE_APPROVED':
            print("--- Evento APROVADO. Tentando criar usuário... ---")
            temp_password = secrets.token_urlsafe(8)
            hashed_password = pwd_context.hash(temp_password)

            with engine.connect() as conn:
                query_check = sqlalchemy.text("SELECT email FROM usuarios WHERE email = :email")
                result = conn.execute(query_check, {"email": email}).first()

                if result:
                    print(f"--- AVISO: Usuário com email {email} já existe. Nenhuma ação tomada. ---")
                    return jsonify({"status": "ok", "message": "User already exists"}), 200

                query_insert = sqlalchemy.text(
                    "INSERT INTO usuarios (nome, email, senha_hash) VALUES (:nome, :email, :senha_hash)")
                conn.execute(query_insert, {"nome": nome, "email": email, "senha_hash": hashed_password})
                conn.commit()
                print(f"--- SUCESSO: Usuário {email} criado. ---")

            return jsonify({"status": "success", "message": "User created"}), 201

        else:
            print(f"--- AVISO: Evento '{evento}' ignorado. ---")
            return jsonify({"status": "ignored", "message": f"Event '{evento}' is not 'PURCHASE_APPROVED'"}), 200

    except KeyError as e:
        print(f"--- ERRO 500: Chave não encontrada no payload da Hotmart: {e} ---")
        return jsonify({"status": "error", "message": f"KeyError: {e}"}), 500
    except Exception as e:
        print(f"--- ERRO 500: Ocorreu um erro interno no processamento: {e} ---")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500