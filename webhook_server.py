# webhook_server.py (Versão com Debug de Timeout)
from flask import Flask, request, jsonify
import os
import sqlalchemy
from passlib.context import CryptContext
import secrets
import time # Importamos a biblioteca de tempo

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
    start_time = time.time() # Marca o tempo de início
    print(f"--- Webhook recebido às {start_time} ---")

    if not engine:
        return jsonify({"status": "error", "message": "Database not configured"}), 500

    hottok = request.headers.get('Hottok')
    if not hottok or hottok != HOTMART_HOTTOK:
        print("--- ERRO: Hottok inválido ou ausente. ---")
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    print("--- DEBUG: Hottok validado com sucesso. ---")
    data = request.json
    status = data['purchase']['status'] # Caminho correto para o status
    email = data['buyer']['email']
    nome = data['buyer']['name']
    print(f"--- DEBUG: Dados extraídos - Status: {status}, Email: {email} ---")

    if status == 'APPROVED':
        try:
            print("--- DEBUG: Gerando senha... ---")
            temp_password = secrets.token_urlsafe(8)
            hashed_password = pwd_context.hash(temp_password)

            print("--- DEBUG: Conectando ao banco de dados... ---")
            with engine.connect() as conn:
                print("--- DEBUG: Conexão bem-sucedida. Inserindo usuário... ---")
                query = sqlalchemy.text("INSERT INTO usuarios (nome, email, senha_hash) VALUES (:nome, :email, :senha_hash)")
                conn.execute(query, {"nome": nome, "email": email, "senha_hash": hashed_password})
                conn.commit()
                print("--- DEBUG: Usuário inserido com sucesso. ---")

            # TODO: Adicionar lógica de envio de e-mail com a senha temporária
            print(f"Usuário {email} criado com sucesso. Senha temporária: {temp_password}")

            end_time = time.time()
            print(f"--- Processamento concluído em {end_time - start_time:.2f} segundos. ---")
            return jsonify({"status": "success", "message": "User created"}), 201

        except Exception as e:
            print(f"--- ERRO DURANTE O PROCESSAMENTO: {e} ---")
            return jsonify({"status": "error", "message": str(e)}), 500

    print(f"--- DEBUG: Status '{status}' ignorado. ---")
    return jsonify({"status": "ignored"}), 200