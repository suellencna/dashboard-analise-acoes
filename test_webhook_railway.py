#!/usr/bin/env python3
"""
Script de teste para o webhook da Hotmart na Railway
"""

import requests
import json
import sys
import os
from datetime import datetime

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")


def test_health_check(base_url):
    """Testa o endpoint de health check"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print_info("Testando Health Check...")
    
    try:
        start_time = datetime.now()
        response = requests.get(f"{base_url}/health", timeout=10)
        end_time = datetime.now()
        
        elapsed = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tempo de resposta: {elapsed:.2f}s")
        print(f"📡 Status Code: {response.status_code}")
        print(f"📦 Resposta: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print_success(f"Health check OK! ({elapsed:.2f}s)")
                return True
            else:
                print_error("Status não é 'healthy'")
                return False
        else:
            print_error(f"Status code inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro no health check: {e}")
        return False


def test_root_endpoint(base_url):
    """Testa o endpoint raiz"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print_info("Testando Endpoint Raiz (/)...")
    
    try:
        response = requests.get(base_url, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            print_success("Endpoint raiz OK!")
            return True
        else:
            print_error(f"Status code inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro no endpoint raiz: {e}")
        return False


def test_webhook_unauthorized(base_url):
    """Testa webhook sem autenticação (deve retornar 401)"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print_info("Testando Webhook SEM Autenticação (deve falhar)...")
    
    try:
        payload = {
            "event": "TEST",
            "data": {
                "buyer": {
                    "email": "teste@exemplo.com",
                    "name": "Teste"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/webhook/hotmart",
            json=payload,
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Autenticação funcionando! (retornou 401 como esperado)")
            return True
        else:
            print_warning(f"Esperava 401, recebeu {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def test_webhook_purchase(base_url, hottok):
    """Testa webhook de compra aprovada"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print_info("Testando Webhook - Compra Aprovada...")
    
    if not hottok:
        print_warning("HOTMART_HOTTOK não fornecido. Pulando teste autenticado.")
        return None
    
    try:
        payload = {
            "event": "PURCHASE_APPROVED",
            "data": {
                "buyer": {
                    "email": f"teste_{datetime.now().timestamp()}@exemplo.com",
                    "name": "Usuario Teste Railway"
                },
                "product": {
                    "name": "Teste"
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Hotmart-Hottok": hottok
        }
        
        start_time = datetime.now()
        response = requests.post(
            f"{base_url}/webhook/hotmart",
            json=payload,
            headers=headers,
            timeout=30
        )
        end_time = datetime.now()
        
        elapsed = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tempo de resposta: {elapsed:.2f}s")
        print(f"📡 Status Code: {response.status_code}")
        print(f"📦 Resposta: {response.json()}")
        
        if response.status_code in [200, 201]:
            if elapsed < 5:
                print_success(f"Webhook respondeu rápido! ({elapsed:.2f}s < 5s) ✨")
            elif elapsed < 15:
                print_warning(f"Webhook um pouco lento ({elapsed:.2f}s) mas OK")
            else:
                print_error(f"Webhook muito lento! ({elapsed:.2f}s) - Risco de timeout")
            return True
        else:
            print_error(f"Status code inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("TIMEOUT! Webhook não respondeu a tempo (>30s)")
        return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False


def run_all_tests(base_url, hottok=None):
    """Executa todos os testes"""
    print(f"\n{BLUE}{'='*60}")
    print(f"🧪 TESTES DO WEBHOOK RAILWAY")
    print(f"{'='*60}{RESET}")
    print(f"🌐 URL Base: {base_url}")
    print(f"🔑 HOTTOK: {'Fornecido ✅' if hottok else 'Não fornecido ⚠️'}")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    results = {}
    
    # Teste 1: Health Check
    results['health'] = test_health_check(base_url)
    
    # Teste 2: Endpoint Raiz
    results['root'] = test_root_endpoint(base_url)
    
    # Teste 3: Webhook sem auth
    results['webhook_unauth'] = test_webhook_unauthorized(base_url)
    
    # Teste 4: Webhook com compra (se tiver HOTTOK)
    if hottok:
        results['webhook_purchase'] = test_webhook_purchase(base_url, hottok)
    
    # Resumo
    print(f"\n{BLUE}{'='*60}")
    print(f"📊 RESUMO DOS TESTES")
    print(f"{'='*60}{RESET}")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASSOU")
        elif result is False:
            print_error(f"{test_name}: FALHOU")
        else:
            print_warning(f"{test_name}: PULADO")
    
    print(f"\n{BLUE}Total: {total} | ", end='')
    print(f"{GREEN}Passou: {passed} | ", end='')
    print(f"{RED}Falhou: {failed} | ", end='')
    print(f"{YELLOW}Pulado: {skipped}{RESET}")
    
    if failed == 0 and passed > 0:
        print(f"\n{GREEN}{'='*60}")
        print("✨ TODOS OS TESTES PASSARAM! ✨")
        print(f"{'='*60}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'='*60}")
        print("❌ ALGUNS TESTES FALHARAM")
        print(f"{'='*60}{RESET}\n")
        return 1


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚂 Script de Teste - Webhook Railway")
    print("="*60 + "\n")
    
    # Obter URL da linha de comando ou usar padrão
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Digite a URL da Railway (ex: https://seu-app.railway.app): ").strip()
    
    # Remover trailing slash
    url = url.rstrip('/')
    
    # Obter HOTTOK do ambiente ou linha de comando
    hottok = os.environ.get('HOTMART_HOTTOK')
    
    if len(sys.argv) > 2:
        hottok = sys.argv[2]
    elif not hottok:
        hottok_input = input("Digite o HOTMART_HOTTOK (ou deixe vazio para pular testes autenticados): ").strip()
        if hottok_input:
            hottok = hottok_input
    
    # Executar testes
    exit_code = run_all_tests(url, hottok)
    sys.exit(exit_code)

