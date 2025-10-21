#!/usr/bin/env python3
"""
Testar emails através do endpoint /test-email do Railway
"""

import requests
import time

RAILWAY_URL = "https://web-production-e66d.up.railway.app"

emails_teste = [
    ("Gmail 1", "suellencna@gmail.com"),
    ("Yahoo", "suellencna@yahoo.com.br"),
    ("Hotmail", "suellencna@hotmail.com"),
    ("Gmail 2", "aaisuellen@gmail.com"),
    ("Outlook", "jorgehap@outlook.com"),
]

print("=" * 80)
print("📧 TESTE DE EMAILS VIA RAILWAY (API KEY CONFIGURADA)")
print("=" * 80)

resultados = []

for provedor, email in emails_teste:
    print(f"\n📤 Enviando para {provedor} ({email})...")
    
    try:
        # Chamar endpoint /test-email do Railway
        response = requests.post(
            f"{RAILWAY_URL}/test-email",
            json={"email": email},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCESSO - {data.get('message', 'Email enviado')}")
            resultados.append((provedor, email, "✅ ENVIADO", "OK"))
        else:
            print(f"   ❌ FALHOU - Status {response.status_code}")
            print(f"      Resposta: {response.text[:200]}")
            resultados.append((provedor, email, "❌ FALHOU", f"HTTP {response.status_code}"))
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT - Servidor demorou muito")
        resultados.append((provedor, email, "⏰ TIMEOUT", "Timeout"))
        
    except Exception as e:
        print(f"   ❌ ERRO - {str(e)}")
        resultados.append((provedor, email, "❌ ERRO", str(e)))
    
    # Aguardar 2 segundos entre envios
    if email != emails_teste[-1][1]:
        time.sleep(2)

print("\n" + "=" * 80)
print("📊 RESUMO DOS ENVIOS VIA RAILWAY")
print("=" * 80)
print(f"{'Provedor':<15} {'Email':<30} {'Status':<15}")
print("-" * 80)

for provedor, email, status, msg in resultados:
    print(f"{provedor:<15} {email:<30} {status:<15}")

print("-" * 80)

# Contar sucessos
sucessos = sum(1 for _, _, status, _ in resultados if "✅" in status)
total = len(resultados)

print(f"\n📈 Taxa de sucesso: {sucessos}/{total} ({100*sucessos/total:.0f}%)")

print("\n📝 PRÓXIMOS PASSOS:")
print("1. Aguarde 2-3 minutos")
print("2. Verifique INBOX e SPAM de todos os emails")
print("3. Me informe quais emails CHEGARAM")

print("\n" + "=" * 80)
