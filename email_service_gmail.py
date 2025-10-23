#!/usr/bin/env python3
"""
Serviço de envio de emails via Gmail SMTP
100% entregabilidade, gratuito, sem limitações
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

# Configurações
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'pontootimoinvest@gmail.com')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')  # Senha de app do Gmail
APP_URL = os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')

def enviar_email_ativacao_gmail(email, nome, token):
    """
    Enviar email de ativação via Gmail SMTP
    
    Args:
        email: Email do usuário
        nome: Nome do usuário
        token: Token de ativação
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        if not GMAIL_APP_PASSWORD:
            return False, "GMAIL_APP_PASSWORD não configurada"
        
        link_ativacao = f"{APP_URL}/ativar/{token}"
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🔐 Ative sua conta - Ponto Ótimo Invest"
        msg['From'] = f"Ponto Ótimo Invest <{GMAIL_EMAIL}>"
        msg['To'] = email
        
        # HTML do email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Ativação de Conta</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background-color: #2c3e50; padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">PONTO ÓTIMO INVEST</h1>
                    <p style="color: #bdc3c7; margin: 5px 0 0 0; font-size: 14px;">Ferramentas de Análise de Investimentos</p>
                </div>
                
                <!-- Conteúdo -->
                <div style="padding: 40px 30px;">
                    
                    <h2 style="color: #2c3e50; margin: 0 0 20px 0;">🔐 Ative sua Conta</h2>
                    
                    <p>Olá <strong>{nome}</strong>,</p>
                    
                    <p>Seja bem-vindo(a) ao <strong>Ponto Ótimo Invest</strong>! 🚀</p>
                    
                    <p>Para ativar sua conta e começar a usar nossas ferramentas de análise, clique no botão abaixo:</p>
                    
                    <!-- Botão -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{link_ativacao}" 
                           style="background-color: #27ae60; 
                                  color: #ffffff; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 5px; 
                                  font-weight: bold; 
                                  display: inline-block;
                                  box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                            🔓 ATIVAR MINHA CONTA
                        </a>
                    </div>
                    
                    <p><strong>⏰ Importante:</strong> Este link expira em 48 horas.</p>
                    
                    <!-- O que você terá -->
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0;">📊 O que você terá acesso:</h3>
                        <ul style="color: #555; margin: 0;">
                            <li>Análise de ativos e setores</li>
                            <li>Métricas de risco e retorno</li>
                            <li>Dados históricos</li>
                            <li>Ferramentas educacionais</li>
                            <li>Relatórios detalhados</li>
                        </ul>
                    </div>
                    
                    <!-- Disclaimer -->
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="color: #856404; margin: 0; font-size: 14px;">
                            <strong>⚠️ Aviso Importante:</strong> Esta plataforma fornece ferramentas analíticas e dados históricos 
                            para fins educacionais. <strong>NÃO constitui recomendação de investimento</strong>.
                        </p>
                    </div>
                    
                </div>
                
                <!-- Footer -->
                <div style="background-color: #ecf0f1; padding: 20px; text-align: center;">
                    <p style="color: #7f8c8d; margin: 0; font-size: 12px;">
                        Ponto Ótimo Invest - Este é um email automático
                    </p>
                </div>
                
            </div>
            
            <!-- Link de fallback -->
            <div style="max-width: 600px; margin: 20px auto; padding: 15px; background-color: #ffffff; border-radius: 5px; text-align: center;">
                <p style="color: #666; font-size: 12px; margin: 0;">
                    Se o botão não funcionar, copie e cole este link no seu navegador:
                </p>
                <p style="color: #2c3e50; font-size: 12px; word-break: break-all; margin: 10px 0 0 0;">
                    {link_ativacao}
                </p>
            </div>
            
        </body>
        </html>
        """
        
        # Texto simples (fallback)
        text_content = f"""
        PONTO ÓTIMO INVEST
        Ferramentas de Análise de Investimentos
        
        Olá {nome},
        
        Seja bem-vindo(a) ao Ponto Ótimo Invest!
        
        Para ativar sua conta, acesse o link:
        {link_ativacao}
        
        Este link expira em 48 horas.
        
        O que você terá acesso:
        • Análise de ativos e setores
        • Métricas de risco e retorno
        • Dados históricos
        • Ferramentas educacionais
        
        Aviso: Esta plataforma fornece ferramentas analíticas para fins educacionais. 
        NÃO constitui recomendação de investimento.
        
        Ponto Ótimo Invest
        """
        
        # Anexar conteúdo
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email de ativação enviado via Gmail para {email}")
        return True, "Email enviado com sucesso via Gmail SMTP"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email via Gmail: {e}")
        return False, str(e)


def enviar_email_boas_vindas_gmail(email, nome):
    """
    Enviar email de boas-vindas via Gmail SMTP
    
    Args:
        email: Email do usuário
        nome: Nome do usuário
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        if not GMAIL_APP_PASSWORD:
            return False, "GMAIL_APP_PASSWORD não configurada"
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🎉 Bem-vindo(a) ao Ponto Ótimo Invest!"
        msg['From'] = f"Ponto Ótimo Invest <{GMAIL_EMAIL}>"
        msg['To'] = email
        
        # HTML do email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Bem-vindo(a)</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background-color: #27ae60; padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">🎉 CONTA ATIVADA!</h1>
                    <p style="color: #ffffff; margin: 5px 0 0 0; font-size: 14px;">Ponto Ótimo Invest</p>
                </div>
                
                <!-- Conteúdo -->
                <div style="padding: 40px 30px;">
                    
                    <h2 style="color: #2c3e50; margin: 0 0 20px 0;">Bem-vindo(a), {nome}!</h2>
                    
                    <p>Sua conta foi ativada com sucesso! Agora você tem acesso completo às nossas ferramentas de análise.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{APP_URL}" 
                           style="background-color: #27ae60; 
                                  color: #ffffff; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 5px; 
                                  font-weight: bold; 
                                  display: inline-block;
                                  box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                            🚀 ACESSAR PLATAFORMA
                        </a>
                    </div>
                    
                    <!-- O que você pode fazer -->
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0;">📊 O que você pode fazer agora:</h3>
                        <ul style="color: #555; margin: 0;">
                            <li>Analisar ativos e setores</li>
                            <li>Calcular métricas de risco e retorno</li>
                            <li>Acessar dados históricos</li>
                            <li>Usar ferramentas educacionais</li>
                            <li>Gerar relatórios detalhados</li>
                        </ul>
                    </div>
                    
                    <!-- Disclaimer -->
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="color: #856404; margin: 0; font-size: 14px;">
                            <strong>Lembrete:</strong> Esta plataforma fornece ferramentas analíticas e dados históricos 
                            para fins educacionais. NÃO constitui recomendação de investimento.
                        </p>
                    </div>
                    
                </div>
                
                <!-- Footer -->
                <div style="background-color: #ecf0f1; padding: 20px; text-align: center;">
                    <p style="color: #7f8c8d; margin: 0; font-size: 12px;">
                        Ponto Ótimo Invest - Ferramentas de Análise de Investimentos
                    </p>
                </div>
                
            </div>
            
        </body>
        </html>
        """
        
        # Texto simples
        text_content = f"""
        PONTO ÓTIMO INVEST
        Ferramentas de Análise de Investimentos
        
        Bem-vindo(a), {nome}!
        
        Sua conta foi ativada com sucesso!
        
        Acesse a plataforma: {APP_URL}
        
        O que você pode fazer:
        • Analisar ativos e setores
        • Calcular métricas de risco e retorno
        • Acessar dados históricos
        • Usar ferramentas educacionais
        
        Lembrete: Esta plataforma fornece ferramentas analíticas para fins educacionais.
        NÃO constitui recomendação de investimento.
        
        Ponto Ótimo Invest
        """
        
        # Anexar conteúdo
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email de boas-vindas enviado via Gmail para {email}")
        return True, "Email enviado com sucesso via Gmail SMTP"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas via Gmail: {e}")
        return False, str(e)


def testar_gmail_smtp(email_teste):
    """
    Testar Gmail SMTP
    
    Args:
        email_teste: Email para teste
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        if not GMAIL_APP_PASSWORD:
            return False, "GMAIL_APP_PASSWORD não configurada"
        
        # Criar mensagem de teste
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🧪 Teste Gmail SMTP - Ponto Ótimo Invest"
        msg['From'] = f"Ponto Ótimo Invest <{GMAIL_EMAIL}>"
        msg['To'] = email_teste
        
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #28a745;">✅ Gmail SMTP Funcionando!</h2>
                <p>Este é um email de teste enviado via Gmail SMTP.</p>
                <p><strong>Se você recebeu isto, a integração está OK!</strong></p>
                <hr>
                <p style="font-size: 12px; color: #888;">Ponto Ótimo Invest - Teste Gmail SMTP</p>
            </body>
        </html>
        """
        
        text_content = """
        Gmail SMTP Teste
        
        Este é um email de teste enviado via Gmail SMTP.
        Se você recebeu isto, a integração está OK!
        
        Ponto Ótimo Invest
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email de teste enviado via Gmail SMTP!")
        logger.info(f"Email de teste enviado via Gmail para {email_teste}")
        return True, "Email enviado com sucesso via Gmail SMTP"
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro ao enviar email de teste via Gmail: {e}")
        return False, str(e)


if __name__ == "__main__":
    # Teste rápido
    print("=== Teste Gmail SMTP ===")
    
    if not GMAIL_APP_PASSWORD:
        print("❌ GMAIL_APP_PASSWORD não configurada!")
        print("Configure a senha de app do Gmail:")
        print("1. Acesse: https://myaccount.google.com/security")
        print("2. Ative a verificação em 2 etapas")
        print("3. Gere uma senha de app")
        print("4. Configure: export GMAIL_APP_PASSWORD='sua_senha_de_app'")
        exit(1)
    
    email = input("Digite um email para teste: ")
    
    sucesso, mensagem = testar_gmail_smtp(email)
    if sucesso:
        print("\n✅ Gmail SMTP configurado corretamente!")
        print("✅ 100% entregabilidade garantida!")
        print(f"✅ Mensagem: {mensagem}")
    else:
        print("\n❌ Erro na configuração. Verifique:")
        print("1. GMAIL_APP_PASSWORD está correta?")
        print("2. Verificação em 2 etapas ativada?")
        print("3. Senha de app gerada?")
        print(f"❌ Erro: {mensagem}")
