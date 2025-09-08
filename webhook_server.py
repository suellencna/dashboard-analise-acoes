# webhook_server.py (Versão de Depuração Detalhada)
from flask import Flask, request, jsonify
import os
import sqlalchemy
from passlib.context import CryptContext
import secrets
import time

app = Flask(__name__)
# ... (o resto do seu código até a função do webhook) ...
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

    # --- INÍCIO DO NOVO BLOCO DE DEBUG ---
    print("1. VERIFICANDO A CHAVE SALVA NA RENDER:")
    hotmart_hottok_from_env = os.environ.get('HOTMART_HOTTOK')
    if hotmart_hottok_from_env:
        # Mostra apenas os primeiros e últimos caracteres por segurança
        print(
            f"   - Chave encontrada. Inicia com '{hotmart_hottok_from_env[:4]}' e termina com '{hotmart_hottok_from_env[-4:]}'")
    else:
        print("   - ERRO: A variável de ambiente HOTMART_HOTTOK não foi encontrada pelo script!")

    print("\n2. VERIFICANDO A CHAVE RECEBIDA DA HOTMART:")
    print("   - Cabeçalhos completos recebidos:")
    print(f"   - {request.headers}")

    hottok_from_request = request.headers.get('X-Hotmart-Hottok')

    if hottok_from_request:
        print(
            f"   - Chave 'Hottok' encontrada no cabeçalho. Inicia com '{hottok_from_request[:4]}' e termina com '{hottok_from_request[-4:]}'")
    else:
        print("   - ERRO: Nenhuma chave 'Hottok' ou 'hottok' foi encontrada nos cabeçalhos da Hotmart!")
    # --- FIM DO NOVO BLOCO DE DEBUG ---

    # Lógica de validação original
    if not hottok_from_request or hottok_from_request != hotmart_hottok_from_env:
        print("\n=> RESULTADO: FALHA NA AUTENTICAÇÃO. As chaves não batem ou uma delas está ausente.\n")
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    print("\n=> RESULTADO: AUTENTICAÇÃO BEM-SUCEDIDA!")
    # ... (resto do seu código para criar o usuário) ...
    # ... (coloque o resto da sua função aqui, a partir da extração dos dados)
    data = request.json
    status = data['purchase']['status']
    email = data['buyer']['email']
    nome = data['buyer']['name']

    if status == 'APPROVED':
        # etc...
        pass  # Apenas para o exemplo, cole seu código aqui

    return jsonify({"status": "success"}), 200