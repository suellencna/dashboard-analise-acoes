#!/usr/bin/env python3
"""
🧪 TESTE LOCAL DO SISTEMA
=========================
Este script testa o sistema localmente antes do deploy
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def print_status(message):
    print(f"🔍 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def testar_imports():
    """Testar se todas as dependências estão instaladas"""
    print_status("Testando imports...")
    
    try:
        import streamlit
        import sqlalchemy
        import psycopg2
        import argon2
        import pandas
        import numpy
        import plotly
        import matplotlib
        import yfinance
        import requests
        import smtplib
        import flask
        print_success("Todos os imports funcionaram")
        return True
    except ImportError as e:
        print_error(f"Erro de import: {e}")
        return False

def testar_banco_dados():
    """Testar conexão com banco de dados"""
    print_status("Testando conexão com banco de dados...")
    
    try:
        from webhook_hotmart_unificado import get_db_connection, create_user_table
        
        # Testar conexão
        conn = get_db_connection()
        if conn:
            print_success("Conexão com banco OK")
            
            # Testar criação de tabela
            if create_user_table():
                print_success("Tabela de usuários criada/verificada")
                conn.close()
                return True
            else:
                print_error("Erro ao criar tabela")
                return False
        else:
            print_error("Não foi possível conectar ao banco")
            return False
    except Exception as e:
        print_error(f"Erro no banco de dados: {e}")
        return False

def testar_email():
    """Testar envio de email"""
    print_status("Testando envio de email...")
    
    try:
        from webhook_hotmart_unificado import send_activation_email
        
        # Testar envio de email
        success, result = send_activation_email(
            "teste@exemplo.com", 
            "Cliente Teste", 
            "token_teste_123"
        )
        
        if success:
            print_success("Email enviado com sucesso")
            return True
        else:
            print_error(f"Erro no envio de email: {result}")
            return False
    except Exception as e:
        print_error(f"Erro no teste de email: {e}")
        return False

def testar_webhook_local():
    """Testar webhook localmente"""
    print_status("Testando webhook localmente...")
    
    try:
        from webhook_hotmart_unificado import app
        
        # Testar dados do webhook
        webhook_data = {
            "buyer": {
                "email": "teste@exemplo.com",
                "name": "Cliente Teste"
            },
            "transaction": {
                "id": "TEST123456789"
            },
            "status": "approved"
        }
        
        with app.test_client() as client:
            response = client.post('/webhook/hotmart', json=webhook_data)
            
            if response.status_code == 200:
                print_success("Webhook local funcionando")
                return True
            else:
                print_error(f"Webhook falhou: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Erro no teste de webhook: {e}")
        return False

def testar_app_principal():
    """Testar aplicação principal"""
    print_status("Testando aplicação principal...")
    
    try:
        # Verificar se o arquivo app.py existe e é válido
        if os.path.exists("app.py"):
            print_success("Arquivo app.py encontrado")
            
            # Testar se consegue importar
            import app
            print_success("Aplicação principal importada com sucesso")
            return True
        else:
            print_error("Arquivo app.py não encontrado")
            return False
    except Exception as e:
        print_error(f"Erro na aplicação principal: {e}")
        return False

def main():
    """Executar todos os testes locais"""
    print("🧪 INICIANDO TESTES LOCAIS")
    print("=" * 40)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    resultados = []
    
    # 1. Testar imports
    resultados.append(("Imports", testar_imports()))
    
    # 2. Testar banco de dados
    resultados.append(("Banco de Dados", testar_banco_dados()))
    
    # 3. Testar email
    resultados.append(("Email", testar_email()))
    
    # 4. Testar webhook local
    resultados.append(("Webhook Local", testar_webhook_local()))
    
    # 5. Testar app principal
    resultados.append(("App Principal", testar_app_principal()))
    
    # Resumo dos resultados
    print("\n" + "=" * 40)
    print("📊 RESUMO DOS TESTES LOCAIS")
    print("=" * 40)
    
    sucessos = 0
    total = len(resultados)
    
    for teste, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{teste:20} {status}")
        if sucesso:
            sucessos += 1
    
    print("-" * 40)
    print(f"Total: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("\n🎉 TODOS OS TESTES LOCAIS PASSARAM!")
        print("✅ O sistema está pronto para deploy!")
        print("\n📋 Próximos passos:")
        print("1. Execute: ./deploy_automatico.sh")
        print("2. Configure as variáveis de ambiente")
        print("3. Teste o fluxo completo")
    else:
        print(f"\n⚠️ {total - sucessos} teste(s) falharam")
        print("❌ Corrija os problemas antes de fazer deploy")
        
        if not resultados[0][1]:  # Imports falharam
            print("\n🔧 Para corrigir imports:")
            print("   pip install -r requirements.txt")
        
        if not resultados[1][1]:  # Banco falhou
            print("\n🔧 Para corrigir banco:")
            print("   - Configure DATABASE_URL no .env")
            print("   - Verifique se o NEON está ativo")
        
        if not resultados[2][1]:  # Email falhou
            print("\n🔧 Para corrigir email:")
            print("   - Configure GMAIL_APP_PASSWORD no .env")
            print("   - Ative verificação em duas etapas no Gmail")
    
    return sucessos == total

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
