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
    # ... (a parte de validação do Hottok continua igual)
    hottok_from_request = request.headers.get('X-Hotmart-Hottok')
    if not hottok_from_request or hottok_from_request != HOTMART_HOTTOK:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        data = request.json
        evento = data.get('event')
        email = data['data']['buyer']['email']
        print(f"--- Webhook recebido: Evento={evento}, Email={email} ---")

        novo_status = None
        # Mapeia eventos da Hotmart para o status no nosso sistema
        if evento in ['PURCHASE_APPROVED', 'SUBSCRIPTION_ACTIVATED']:
            novo_status = 'ativo'
        elif evento in ['SUBSCRIPTION_CANCELED', 'SUBSCRIPTION_EXPIRED', 'CHARGEBACK']:
            novo_status = 'inativo'

        # Se o evento for de criação de usuário
        if evento == 'PURCHASE_APPROVED':
            # ... (código para CRIAR um novo usuário, como já tínhamos)
            # ... (garanta que ao criar, o status_assinatura seja 'ativo')
            pass  # Mantenha a lógica de criação que já funciona aqui

        # Se for um evento para ATUALIZAR o status
        if novo_status:
            with engine.connect() as conn:
                query = sqlalchemy.text("UPDATE usuarios SET status_assinatura = :status WHERE email = :email")
                conn.execute(query, {"status": novo_status, "email": email})
                conn.commit()
                print(f"--- SUCESSO: Status do usuário {email} atualizado para '{novo_status}'. ---")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"--- ERRO 500 no processamento do webhook: {e} ---")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500