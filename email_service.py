#!/usr/bin/env python3
"""
Serviço de envio de emails via MailerSend
Integração com webhook Hotmart para sistema de ativação
"""

import os
from mailersend import emails
import logging

logger = logging.getLogger(__name__)

# Configurações
MAILERSEND_API_KEY = os.environ.get('MAILERSEND_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@pontootimo.com.br')
APP_URL = os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')

def enviar_email_ativacao(email, nome, token):
    """
    Enviar email de ativação de conta
    
    Args:
        email: Email do usuário
        nome: Nome do usuário
        token: Token de ativação
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        subject = "🔐 Ative sua conta - Ponto Ótimo Invest"
        
        link_ativacao = f"{APP_URL}/ativar/{token}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c3e50; margin: 0;">🎯 Ponto Ótimo Invest</h1>
                        <p style="color: #7f8c8d; margin: 5px 0;">Ferramentas de Análise de Investimentos</p>
                    </div>
                    
                    <h2 style="color: #27ae60; margin-bottom: 20px;">🔐 Ative sua conta</h2>
                    
                    <p>Olá <strong>{nome}</strong>,</p>
                    
                    <p>Seja bem-vindo(a) ao <strong>Ponto Ótimo Invest</strong>! 🚀</p>
                    
                    <p>Para ativar sua conta e começar a usar nossas ferramentas de análise, clique no botão abaixo:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{link_ativacao}" 
                           style="background-color: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            🔓 ATIVAR MINHA CONTA
                        </a>
                    </div>
                    
                    <p><strong>⏰ Importante:</strong> Este link expira em 48 horas.</p>
                    
                    <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">⚠️ AVISO IMPORTANTE</h3>
                        <p style="margin: 0; font-size: 14px; color: #555;">
                            Esta plataforma fornece <strong>FERRAMENTAS ANALÍTICAS</strong> e <strong>DADOS HISTÓRICOS</strong> 
                            para fins educacionais e informativos. <strong>NÃO constitui recomendação de investimento</strong>.
                        </p>
                    </div>
                    
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; font-size: 14px; color: #27ae60;">
                            <strong>📊 O que você terá acesso:</strong><br>
                            • Análise de ativos e setores<br>
                            • Métricas de risco e retorno<br>
                            • Dados históricos e comparativos<br>
                            • Ferramentas educacionais
                        </p>
                    </div>
                    
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        Se você não solicitou esta conta, pode ignorar este email.<br>
                        Este é um email automático, não responda.
                    </p>
                    
                </div>
            </body>
        </html>
        """
        
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
        
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(html_content, mail_body)
        
        response = mailer.send(mail_body)
        
        logger.info(f"Email de ativação enviado para {email}")
        return True, "Email enviado com sucesso"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de ativação: {e}")
        return False, str(e)


def enviar_email_boas_vindas(email, nome):
    """
    Enviar email de boas-vindas após ativação
    
    Args:
        email: Email do usuário
        nome: Nome do usuário
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    try:
        subject = "🎉 Bem-vindo(a) ao Ponto Ótimo Invest!"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c3e50; margin: 0;">🎯 Ponto Ótimo Invest</h1>
                        <p style="color: #7f8c8d; margin: 5px 0;">Ferramentas de Análise de Investimentos</p>
                    </div>
                    
                    <h2 style="color: #27ae60; margin-bottom: 20px;">🎉 Conta ativada com sucesso!</h2>
                    
                    <p>Olá <strong>{nome}</strong>,</p>
                    
                    <p>Sua conta foi ativada com sucesso! Agora você tem acesso completo às nossas ferramentas de análise. 🚀</p>
                    
                    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">📊 O que você pode fazer agora:</h3>
                        <ul style="color: #2c3e50;">
                            <li>Analisar ativos e setores</li>
                            <li>Calcular métricas de risco e retorno</li>
                            <li>Comparar diferentes investimentos</li>
                            <li>Acessar dados históricos</li>
                            <li>Usar ferramentas educacionais</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{APP_URL}" 
                           style="background-color: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            🚀 ACESSAR PLATAFORMA
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">⚠️ LEMBRETE IMPORTANTE</h3>
                        <p style="margin: 0; font-size: 14px; color: #555;">
                            Esta plataforma fornece <strong>FERRAMENTAS ANALÍTICAS</strong> e <strong>DADOS HISTÓRICOS</strong> 
                            para fins educacionais e informativos. <strong>NÃO constitui recomendação de investimento</strong>.
                        </p>
                    </div>
                    
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        Se você tiver dúvidas, entre em contato conosco.<br>
                        Este é um email automático, não responda.
                    </p>
                    
                </div>
            </body>
        </html>
        """
        
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
        
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(html_content, mail_body)
        
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
        subject = "🧪 Teste - MailerSend Configurado!"
        
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
    print("=== Teste de Envio de Email - MailerSend ===")
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

