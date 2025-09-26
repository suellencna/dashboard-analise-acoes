#!/usr/bin/env python3
"""
Script para consultar senhas temporárias de usuários
"""

import os
import sqlalchemy
from datetime import datetime, timedelta

# Carregar variáveis de ambiente
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL não configurada")
    exit()

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    print("✅ Conexão com banco estabelecida")
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
    exit()

def listar_usuarios():
    """Lista todos os usuários do sistema"""
    try:
        with engine.connect() as conn:
            query = sqlalchemy.text("""
                SELECT nome, email, status_assinatura, created_at 
                FROM usuarios 
                ORDER BY created_at DESC
            """)
            result = conn.execute(query)
            usuarios = result.fetchall()
            
            if usuarios:
                print(f"\n📊 Total de usuários: {len(usuarios)}")
                print("\n" + "="*80)
                print(f"{'Nome':<30} {'Email':<35} {'Status':<15} {'Criado em'}")
                print("="*80)
                
                for usuario in usuarios:
                    nome, email, status, created_at = usuario
                    status_icon = "✅" if status == 'ativo' else "❌"
                    print(f"{nome:<30} {email:<35} {status_icon} {status:<12} {created_at}")
                
                print("="*80)
            else:
                print("❌ Nenhum usuário encontrado")
                
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")

def consultar_usuario_especifico():
    """Consulta dados de um usuário específico"""
    email = input("\nDigite o email do usuário: ").strip()
    
    if not email:
        print("❌ Email não fornecido")
        return
    
    try:
        with engine.connect() as conn:
            query = sqlalchemy.text("""
                SELECT nome, email, status_assinatura, created_at, ultima_carteira, ultimos_pesos
                FROM usuarios 
                WHERE email = :email
            """)
            result = conn.execute(query, {"email": email}).first()
            
            if result:
                nome, email, status, created_at, carteira, pesos = result
                
                print(f"\n👤 Dados do Usuário:")
                print(f"   Nome: {nome}")
                print(f"   Email: {email}")
                print(f"   Status: {'✅ Ativo' if status == 'ativo' else '❌ Inativo'}")
                print(f"   Criado em: {created_at}")
                print(f"   Carteira salva: {carteira or 'Nenhuma'}")
                print(f"   Pesos salvos: {pesos or 'Nenhum'}")
                
                print(f"\n⚠️  IMPORTANTE:")
                print(f"   A senha não pode ser recuperada por segurança.")
                print(f"   O usuário deve usar a funcionalidade 'Esqueci minha senha' na tela de login.")
                print(f"   Ou você pode criar uma nova senha temporária usando o script sistema_senhas_hotmart.py")
                
            else:
                print(f"❌ Usuário com email '{email}' não encontrado")
                
    except Exception as e:
        print(f"❌ Erro ao consultar usuário: {e}")

def main():
    """Menu principal"""
    while True:
        print("\n" + "="*50)
        print("🔍 CONSULTA DE USUÁRIOS - PONTO ÓTIMO INVEST")
        print("="*50)
        print("1. Listar todos os usuários")
        print("2. Consultar usuário específico")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            listar_usuarios()
        elif opcao == "2":
            consultar_usuario_especifico()
        elif opcao == "3":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
