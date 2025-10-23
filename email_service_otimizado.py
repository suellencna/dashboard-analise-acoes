#!/usr/bin/env python3
"""
Serviço de envio de emails via MailerSend OTIMIZADO
Usa templates do MailerSend para melhor entregabilidade
"""

import os
from mailersend import emails
import logging

logger = logging.getLogger(__name__)

# Configurações
MAILERSEND_API_KEY = os.environ.get('MAILERSEND_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@pontootimo.com.br')
APP_URL = os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')

# Template IDs do MailerSend (configure após criar os templates)
TEMPLATE_ATIVACAO_ID = os.environ.get('TEMPLATE_ATIVACAO_ID', '351ndgwyenxlzqx8')  # ID do template de ativação
TEMPLATE_BOAS_VINDAS_ID = os.environ.get('TEMPLATE_BOAS_VINDAS_ID', '')  # ID do template de boas-vindas

def enviar_email_ativacao(email, nome, token):
    """
    Enviar email de ativação usando template do MailerSend
    
    Args:
        email: Email do usuário
        nome: Nome do usuário
        token: Token de ativação
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        link_ativacao = f"{APP_URL}/ativar/{token}"
        
        mailer = emails.NewEmail(MAILERSEND_API_KEY)
        
        mail_body = {}
        mail_from = {
            "name": "Ponto Ótimo Invest",
            "email": FROM_EMAIL,
        }
        recipients = [
            {
                "name": nome,
                "email": email,
            }
        ]
        
        # Se template ID estiver configurado, usar template
        if TEMPLATE_ATIVACAO_ID:
            mailer.set_template(TEMPLATE_ATIVACAO_ID, mail_body)
            mailer.set_personalization([{
                "email": email,
                "data": {
                    "nome": nome,
                    "link_ativacao": link_ativacao
                }
            }], mail_body)
        else:
            # Fallback para HTML customizado (versão otimizada)
            subject = "Ative sua conta - Ponto Ótimo Invest"
            
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
                        
                        <h2 style="color: #2c3e50; margin: 0 0 20px 0;">Ative sua Conta</h2>
                        
                        <p>Olá <strong>{nome}</strong>,</p>
                        
                        <p>Seja bem-vindo(a) ao Ponto Ótimo Invest!</p>
                        
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
                                      display: inline-block;">
                                ATIVAR MINHA CONTA
                            </a>
                        </div>
                        
                        <p><strong>Importante:</strong> Este link expira em 48 horas.</p>
                        
                        <!-- O que você terá -->
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="color: #2c3e50; margin: 0 0 15px 0;">O que você terá acesso:</h3>
                            <ul style="color: #555; margin: 0;">
                                <li>Análise de ativos e setores</li>
                                <li>Métricas de risco e retorno</li>
                                <li>Dados históricos</li>
                                <li>Ferramentas educacionais</li>
                            </ul>
                        </div>
                        
                        <!-- Disclaimer -->
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p style="color: #856404; margin: 0; font-size: 14px;">
                                <strong>Aviso:</strong> Esta plataforma fornece ferramentas analíticas e dados históricos 
                                para fins educacionais. NÃO constitui recomendação de investimento.
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
                        Se o botão não funcionar: {link_ativacao}
                    </p>
                </div>
                
            </body>
            </html>
            """
            
            mailer.set_subject(subject, mail_body)
            mailer.set_html_content(html_content, mail_body)
        
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        
        response = mailer.send(mail_body)
        
        logger.info(f"Email de ativação enviado para {email}")
        return True, "Email enviado com sucesso"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de ativação: {e}")
        return False, str(e)


def enviar_email_boas_vindas(email, nome):
    """
    Enviar email de boas-vindas usando template do MailerSend
    
    Args:
        email: Email do usuário
        nome: Nome do usuário
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        mailer = emails.NewEmail(MAILERSEND_API_KEY)
        
        mail_body = {}
        mail_from = {
            "name": "Ponto Ótimo Invest",
            "email": FROM_EMAIL,
        }
        recipients = [
            {
                "name": nome,
                "email": email,
            }
        ]
        
        # Se template ID estiver configurado, usar template
        if TEMPLATE_BOAS_VINDAS_ID:
            mailer.set_template_id(TEMPLATE_BOAS_VINDAS_ID)
            mailer.set_template_variables({
                "nome": nome,
                "app_url": APP_URL
            })
        else:
            # Fallback para HTML customizado
            subject = "Bem-vindo(a) ao Ponto Ótimo Invest!"
            
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
                                      display: inline-block;">
                                ACESSAR PLATAFORMA
                            </a>
                        </div>
                        
                        <!-- O que você pode fazer -->
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="color: #2c3e50; margin: 0 0 15px 0;">O que você pode fazer agora:</h3>
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
            
            mailer.set_subject(subject, mail_body)
            mailer.set_html_content(html_content, mail_body)
        
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        
        response = mailer.send(mail_body)
        
        logger.info(f"Email de boas-vindas enviado para {email}")
        return True, "Email enviado com sucesso"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas: {e}")
        return False, str(e)


def testar_envio_email(email_teste):
    """
    Função de teste para validar integração MailerSend
    
    Args:
        email_teste: Email para envio de teste
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        subject = "Teste - MailerSend Configurado"
        
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #28a745;">✅ MailerSend Funcionando!</h2>
                <p>Este é um email de teste.</p>
                <p><strong>Se você recebeu isto, a integração está OK!</strong></p>
                <hr>
                <p style="font-size: 12px; color: #888;">Ponto Ótimo Invest - Teste de Integração</p>
            </body>
        </html>
        """
        
        mailer = emails.NewEmail(MAILERSEND_API_KEY)
        
        mail_body = {}
        mail_from = {
            "name": "Ponto Ótimo Invest - Teste",
            "email": FROM_EMAIL,
        }
        recipients = [
            {
                "name": "Teste",
                "email": email_teste,
            }
        ]
        
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(html_content, mail_body)
        
        response = mailer.send(mail_body)
        
        print(f"✅ Email de teste enviado com sucesso!")
        logger.info(f"Email de teste enviado para {email_teste}")
        return True, "Email enviado com sucesso"
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro ao enviar email de teste: {e}")
        return False, str(e)


if __name__ == "__main__":
    # Teste rápido
    print("=== Teste de Envio de Email - MailerSend OTIMIZADO ===")
    email = input("Digite um email para teste: ")
    
    sucesso, mensagem = testar_envio_email(email)
    if sucesso:
        print("\n✅ MailerSend configurado corretamente!")
        print("✅ Você pode enviar até 12.000 emails/mês no plano free!")
        print(f"✅ Mensagem: {mensagem}")
    else:
        print("\n❌ Erro na configuração. Verifique:")
        print("1. MAILERSEND_API_KEY está correta?")
        print("2. FROM_EMAIL está verificado?")
        print("3. Domínio está autenticado?")
        print(f"❌ Erro: {mensagem}")
