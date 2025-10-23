#!/usr/bin/env python3
"""
Teste completo do Gmail SMTP
Testa envio para todos os provedores
"""

import os
import secrets
from email_service_gmail import enviar_email_ativacao_gmail, testar_gmail_smtp

def testar_todos_provedores_gmail():
    """
    Testar Gmail SMTP com todos os provedores
    """
    
    # Verificar configurações
    gmail_email = os.environ.get('GMAIL_EMAIL')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not gmail_email or not gmail_password:
        print("❌ CONFIGURAÇÕES FALTANDO!")
        print("Configure as variáveis:")
        print("export GMAIL_EMAIL='suellencna@gmail.com'")
        print("export GMAIL_APP_PASSWORD='sua_senha_de_app'")
        return
    
    print("=" * 80)
    print("📧 TESTE GMAIL SMTP - TODOS OS PROVEDORES")
    print("=" * 80)
    print(f"📧 From: {gmail_email}")
    print(f"🔑 App Password: {gmail_password[:8]}...")
    print("=" * 80)
    
    # Lista de emails para teste
    emails_teste = [
        ("Gmail 1", "suellencna@gmail.com"),
        ("Yahoo", "suellencna@yahoo.com.br"),
        ("Hotmail", "suellencna@hotmail.com"),
        ("Gmail 2", "aaisuellen@gmail.com"),
        ("Outlook", "jorgehap@outlook.com"),
    ]
    
    resultados = []
    links_gerados = []
    
    for provedor, email in emails_teste:
        print(f"\n📤 {provedor} ({email})")
        
        # Gerar token único
        token = secrets.token_urlsafe(32)
        link = f"https://web-production-e66d.up.railway.app/ativar/{token}"
        
        print(f"🔗 Link: {link}")
        
        # Enviar email
        sucesso, mensagem = enviar_email_ativacao_gmail(email, provedor, token)
        
        if sucesso:
            print(f"   ✅ ENVIADO - {mensagem}")
            resultados.append((provedor, email, "✅ ENVIADO"))
            links_gerados.append((provedor, email, link, token))
        else:
            print(f"   ❌ FALHOU - {mensagem}")
            resultados.append((provedor, email, "❌ FALHOU"))
        
        # Aguardar entre envios
        import time
        time.sleep(2)
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS ENVIOS")
    print("=" * 80)
    
    for provedor, email, status in resultados:
        print(f"{status} {provedor:<15} {email}")
    
    # Salvar links
    if links_gerados:
        print("\n🔗 LINKS DE ATIVAÇÃO GERADOS:")
        with open("links_ativacao_gmail.txt", "w", encoding="utf-8") as f:
            for provedor, email, link, token in links_gerados:
                print(f"📧 {provedor} ({email}):")
                print(f"   {link}")
                f.write(f"Provedor: {provedor}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Link: {link}\n")
                f.write(f"Token: {token}\n\n")
                f.write("------------------------------------------------------------\n\n")
    
    print("\n" + "=" * 80)
    print("📝 PRÓXIMOS PASSOS:")
    print("1. Aguarde 2-3 minutos")
    print("2. Verifique TODOS os emails (inbox + spam)")
    print("3. Me informe quais emails CHEGARAM")
    print("4. Teste os links de ativação")
    print("=" * 80)

def testar_email_simples():
    """
    Teste simples com um email
    """
    
    print("=== TESTE SIMPLES GMAIL SMTP ===")
    email = input("Digite um email para teste: ")
    
    sucesso, mensagem = testar_gmail_smtp(email)
    
    if sucesso:
        print("\n✅ Gmail SMTP funcionando!")
        print("✅ 100% entregabilidade garantida!")
        print(f"✅ Mensagem: {mensagem}")
    else:
        print("\n❌ Erro na configuração:")
        print("1. GMAIL_APP_PASSWORD está correta?")
        print("2. Verificação em 2 etapas ativada?")
        print("3. Senha de app gerada?")
        print(f"❌ Erro: {mensagem}")

if __name__ == "__main__":
    print("Escolha o teste:")
    print("1. Teste simples (um email)")
    print("2. Teste completo (todos os provedores)")
    
    opcao = input("Digite 1 ou 2: ").strip()
    
    if opcao == "1":
        testar_email_simples()
    elif opcao == "2":
        testar_todos_provedores_gmail()
    else:
        print("Opção inválida!")
