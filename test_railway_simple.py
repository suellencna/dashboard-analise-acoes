#!/usr/bin/env python3
"""
Teste simples para Railway
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        "status": "success",
        "message": "Railway funcionando!",
        "database_url": "DATABASE_URL" in os.environ,
        "gmail_email": "GMAIL_EMAIL" in os.environ,
        "gmail_password": "GMAIL_APP_PASSWORD" in os.environ
    })

@app.route('/')
def home():
    return jsonify({
        "message": "Railway Webhook funcionando!",
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
