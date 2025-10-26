#!/usr/bin/env python3
"""
Script para testar configuração DNS de email
"""

import dns.resolver
import sys

def testar_spf(dominio):
    """Testar registro SPF"""
    print(f"🔍 Testando SPF para {dominio}...")
    try:
        respostas = dns.resolver.resolve(dominio, 'TXT')
        for resposta in respostas:
            txt = str(resposta).strip('"')
            if txt.startswith('v=spf1'):
                print(f"✅ SPF encontrado: {txt}")
                return True
        print("❌ SPF não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar SPF: {e}")
        return False

def testar_dkim(dominio):
    """Testar registro DKIM"""
    print(f"🔍 Testando DKIM para {dominio}...")
    try:
        dkim_dominio = f"google._domainkey.{dominio}"
        respostas = dns.resolver.resolve(dkim_dominio, 'TXT')
        for resposta in respostas:
            txt = str(resposta).strip('"')
            if 'v=DKIM1' in txt:
                print(f"✅ DKIM encontrado: {txt[:50]}...")
                return True
        print("❌ DKIM não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar DKIM: {e}")
        return False

def testar_dmarc(dominio):
    """Testar registro DMARC"""
    print(f"🔍 Testando DMARC para {dominio}...")
    try:
        dmarc_dominio = f"_dmarc.{dominio}"
        respostas = dns.resolver.resolve(dmarc_dominio, 'TXT')
        for resposta in respostas:
            txt = str(resposta).strip('"')
            if txt.startswith('v=DMARC1'):
                print(f"✅ DMARC encontrado: {txt}")
                return True
        print("❌ DMARC não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar DMARC: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python testar_dns_email.py <dominio>")
        print("Exemplo: python testar_dns_email.py pontootimoinvest.com")
        sys.exit(1)
    
    dominio = sys.argv[1]
    print(f"🧪 TESTANDO CONFIGURAÇÃO DNS PARA: {dominio}")
    print("=" * 50)
    
    spf_ok = testar_spf(dominio)
    dkim_ok = testar_dkim(dominio)
    dmarc_ok = testar_dmarc(dominio)
    
    print("\n📊 RESUMO:")
    print(f"SPF:   {'✅' if spf_ok else '❌'}")
    print(f"DKIM:  {'✅' if dkim_ok else '❌'}")
    print(f"DMARC: {'✅' if dmarc_ok else '❌'}")
    
    if spf_ok and dkim_ok and dmarc_ok:
        print("\n🎉 CONFIGURAÇÃO DNS COMPLETA!")
        print("Seus emails devem ser entregues corretamente.")
    else:
        print("\n⚠️  CONFIGURAÇÃO INCOMPLETA")
        print("Configure os registros DNS faltantes.")

if __name__ == "__main__":
    main()
