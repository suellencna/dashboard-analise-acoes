# app.py
from flask import Flask, request, jsonify
import os
import sqlalchemy
from passlib.context import CryptContext
import secrets

app = Flask(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pega as variáveis de ambiente configuradas na Render
DATABASE_URL = os.environ.get('DATABASE_URL')
HOTMART_HOTTOK = os.environ.get('HOTMART_HOTTOK')

# Cria a "engine" de conexão com o banco de dados
try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
except Exception as e:
    # Se a variável de ambiente não estiver disponível, o app não vai iniciar
    print(f"ERRO: Não foi possível criar a engine do banco de dados. Verifique a variável de ambiente DATABASE_URL. Erro: {e}")
    engine = None


@app.route('/')
def index():
    return "Servidor de Webhook está no ar."

@app.route('/webhook/hotmart', methods=['POST'])
def hotmart_webhook():
    if not engine:
        return jsonify({"status": "error", "message": "Database not configured"}), 500

    hottok = request.headers.get('Hottok')
    if not hottok or hottok != HOTMART_HOTTOK:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.json
    status = data.get('status')
    email = data.get('email')
    nome = data.get('name')

    if status == 'approved':
        try:
            temp_password = secrets.token_urlsafe(8)
            hashed_password = pwd_context.hash(temp_password)

            with engine.connect() as conn:
                # Usamos text() para criar uma query SQL segura
                query = sqlalchemy.text("INSERT INTO usuarios (nome, email, senha_hash) VALUES (:nome, :email, :senha_hash)")
                conn.execute(query, {"nome": nome, "email": email, "senha_hash": hashed_password})
                conn.commit()

            # AQUI você adicionaria a lógica de envio de e-mail com a senha temporária
            print(f"Usuário {email} criado com sucesso. Senha temporária: {temp_password}")

            return jsonify({"status": "success", "message": "User created"}), 201

        except sqlalchemy.exc.IntegrityError:
            return jsonify({"status": "ok", "message": "User already exists"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "ignored"}), 200