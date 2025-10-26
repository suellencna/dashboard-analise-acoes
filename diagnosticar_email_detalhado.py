#!/usr/bin/env python3
"""
Diagnóstico detalhado do problema de email
"""

import os
import smtplib
import ssl
import requests
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_gmail_direto():
    """Testar Gmail diretamente"""
    print("🔍 TESTE DIRETO DO GMAIL")
    print("=" * 50)
    
    GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
    GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    
    print(f"📧 Email: {GMAIL_EMAIL}")
    print(f"🔑 Senha: {'✅ Configurada' if GMAIL_APP_PASSWORD else '❌ NÃO CONFIGURADA'}")
    
    if not GMAIL_APP_PASSWORD:
        print("❌ ERRO: GMAIL_APP_PASSWORD não configurada!")
        return False
    
    try:
        # Testar conexão
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        print(f"\n🔌 Conectando a {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        print("✅ Login Gmail OK!")
        
        # Enviar email de teste
        print("\n📧 Enviando email de teste...")
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = "suellencna@yahoo.com.br"
        msg['Subject'] = "TESTE DIRETO - Ponto Ótimo Investimentos"
        
        body = """
        <html>
        <body>
            <h2>Teste Direto do Gmail</h2>
            <p>Este é um teste direto para verificar se o Gmail está funcionando.</p>
            <p>Se você recebeu este email, o Gmail está OK!</p>
            <p>Timestamp: """ + str(time.time()) + """</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        server.send_message(msg)
        print("✅ Email de teste enviado com sucesso!")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Erro no Gmail: {e}")
        return False

def testar_railway_logs():
    """Testar Railway e verificar logs"""
    print("\n🔍 TESTANDO RAILWAY")
    print("=" * 50)
    
    RAILWAY_URL = "https://web-production-040d1.up.railway.app"
    
    # 1. Health check
    print("1. Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"   Status: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ FALHOU'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Testar webhook
    print("\n2. Testando webhook...")
    webhook_data = {
        "buyer": {
            "email": "suellencna@yahoo.com.br",
            "name": "Teste Diagnóstico"
        },
        "transaction": {
            "id": f"DIAG_{int(time.time())}"
        },
        "status": "approved"
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/webhook/hotmart",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ FALHOU'}")
        if response.status_code == 200:
            print(f"   Resposta: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Aguardar e testar email
    print("\n3. Aguardando processamento...")
    time.sleep(3)
    
    print("\n4. Testando endpoint de email...")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json={"email": "suellencna@yahoo.com.br", "nome": "Teste Diagnóstico"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ FALHOU'}")
        if response.status_code == 200:
            print(f"   Resposta: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def verificar_credenciais():
    """Verificar se as credenciais estão corretas"""
    print("\n🔍 VERIFICANDO CREDENCIAIS")
    print("=" * 50)
    
    # Verificar arquivo .env
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
        with open('.env', 'r') as f:
            content = f.read()
            if 'GMAIL_APP_PASSWORD' in content:
                print("✅ GMAIL_APP_PASSWORD encontrada no .env")
            else:
                print("❌ GMAIL_APP_PASSWORD NÃO encontrada no .env")
    else:
        print("❌ Arquivo .env NÃO encontrado")
    
    # Verificar variáveis de ambiente
    gmail_email = os.environ.get('GMAIL_EMAIL')
    gmail_pass = os.environ.get('GMAIL_APP_PASSWORD')
    
    print(f"\n📧 GMAIL_EMAIL: {gmail_email}")
    print(f"🔑 GMAIL_APP_PASSWORD: {'✅ Configurada' if gmail_pass else '❌ NÃO CONFIGURADA'}")
    
    if gmail_pass:
        print(f"   Tamanho da senha: {len(gmail_pass)} caracteres")
        print(f"   Primeiros 4 caracteres: {gmail_pass[:4]}...")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO COMPLETO DO PROBLEMA DE EMAIL")
    print("=" * 60)
    
    # 1. Verificar credenciais
    verificar_credenciais()
    
    # 2. Testar Gmail direto
    gmail_ok = testar_gmail_direto()
    
    # 3. Testar Railway
    testar_railway_logs()
    
    print("\n" + "=" * 60)
    if gmail_ok:
        print("✅ GMAIL FUNCIONANDO - Problema pode estar no Railway")
    else:
        print("❌ PROBLEMA NO GMAIL - Verifique credenciais")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Verifique se o email de teste direto chegou")
    print("2. Se não chegou, problema é no Gmail")
    print("3. Se chegou, problema é no Railway")
    print("4. Verifique logs do Railway para mais detalhes")
