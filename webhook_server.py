# webhook_server.py (Versão de Depuração Detalhada)
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

        # --- LÓGICA CORRIGIDA E ROBUSTA PARA PEGAR O STATUS ---
        status = data.get('status')  # Tenta pegar do nível principal (comum em testes)
        if not status and 'purchase' in data:
            status = data['purchase'].get('status')  # Tenta pegar de dentro de 'purchase' (comum em produção)

        email = data['buyer']['email']
        nome = data['buyer']['name']
        print(f"--- Dados extraídos: Status={status}, Email={email}")

        if status == 'approved' or status == 'APPROVED':  # Aceita 'approved' ou 'APPROVED'
            print("--- Status APROVADO. Tentando criar usuário... ---")
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
            print(f"--- AVISO: Status '{status}' ignorado. ---")
            return jsonify({"status": "ignored"}), 200

    except Exception as e:
        print(f"--- ERRO 500: Ocorreu um erro interno no processamento: {e} ---")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
