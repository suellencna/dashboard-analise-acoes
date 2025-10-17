#!/usr/bin/env python3
"""
Serviço de envio de emails via SendGrid
Integração com webhook Hotmart para sistema de ativação
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging

logger = logging.getLogger(__name__)

# Configurações
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@pontootimo.com.br')
APP_URL = os.environ.get('APP_URL', 'https://web-production-e66d.up.railway.app')


def enviar_email_ativacao(email_destino, nome, token_ativacao):
    """
    Envia email de ativação com link para cliente criar senha
    
    Args:
        email_destino: Email do cliente
        nome: Nome do cliente
        token_ativacao: Token único de ativação
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    if not SENDGRID_API_KEY:
        logger.error("SENDGRID_API_KEY não configurada")
        return False, "SendGrid não configurado"
    
    try:
        link_ativacao = f"{APP_URL}/ativar/{token_ativacao}"
        
        # Assunto do email
        subject = "🎉 Ative sua conta - Ponto Ótimo Invest"
        
        # Conteúdo HTML do email
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ative sua conta - Ponto Ótimo Invest</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    
    <!-- Container Principal -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <!-- Card do Email -->
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                    
                    <!-- Header com Gradiente -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="color: white; margin: 0; font-size: 32px; font-weight: bold;">🎯 PONTO ÓTIMO INVEST</h1>
                            <p style="color: #e0e0e0; margin: 15px 0 0 0; font-size: 18px;">Ferramenta Educativa de Análise de Investimentos</p>
                        </td>
                    </tr>
                    
                    <!-- Conteúdo Principal -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            
                            <!-- Saudação -->
                            <h2 style="color: #2c3e50; margin-top: 0; font-size: 24px;">Olá, {nome}! 👋</h2>
                            
                            <p style="font-size: 18px; color: #555; margin-bottom: 20px;">
                                <strong>🎉 Sua compra foi aprovada com sucesso!</strong>
                            </p>
                            
                            <p style="font-size: 16px; color: #666; margin-bottom: 30px;">
                                Estamos felizes em recebê-lo! Seu acesso à nossa plataforma educativa 
                                está quase pronto. Falta apenas um passo: <strong>ativar sua conta</strong>.
                            </p>
                            
                            <!-- Box de Próximo Passo -->
                            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 25px; border-radius: 12px; margin: 30px 0; text-align: center;">
                                <h3 style="color: white; margin: 0 0 15px 0; font-size: 20px;">🚀 Próximo Passo</h3>
                                <p style="color: white; margin-bottom: 20px; font-size: 16px;">
                                    Clique no botão abaixo para ativar sua conta e criar sua senha:
                                </p>
                                <a href="{link_ativacao}" style="display: inline-block; background: white; color: #28a745; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                                    ✨ Ativar Minha Conta
                                </a>
                            </div>
                            
                            <!-- O que vai acontecer -->
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #007bff;">
                                <h4 style="color: #007bff; margin-top: 0; font-size: 18px;">📋 O que acontece na ativação:</h4>
                                <ul style="color: #555; margin: 10px 0; padding-left: 20px;">
                                    <li style="margin-bottom: 8px;">Você <strong>cria sua própria senha</strong> (segura e memorável)</li>
                                    <li style="margin-bottom: 8px;">Lê e aceita os <strong>Termos de Uso</strong></li>
                                    <li style="margin-bottom: 8px;">Sua conta é ativada <strong>instantaneamente</strong></li>
                                    <li style="margin-bottom: 8px;">Você pode fazer <strong>login imediatamente</strong></li>
                                </ul>
                            </div>
                            
                            <!-- Recursos da Plataforma -->
                            <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #17a2b8;">
                                <h4 style="color: #17a2b8; margin-top: 0; font-size: 18px;">💼 O que você poderá fazer (educativo):</h4>
                                <ul style="color: #004085; margin: 10px 0; padding-left: 20px;">
                                    <li style="margin-bottom: 8px;">📊 Analisar <strong>dados históricos</strong> de ações e FIIs</li>
                                    <li style="margin-bottom: 8px;">📈 Calcular <strong>métricas educativas</strong> (Sharpe, Volatilidade)</li>
                                    <li style="margin-bottom: 8px;">🎲 Simular cenários com <strong>Monte Carlo</strong> (hipotético)</li>
                                    <li style="margin-bottom: 8px;">🎯 Estudar <strong>otimização matemática</strong> de carteiras</li>
                                </ul>
                            </div>
                            
                            <!-- DISCLAIMER CVM -->
                            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #ffc107;">
                                <h4 style="color: #856404; margin-top: 0; font-size: 16px;">⚠️ Aviso Legal Importante</h4>
                                <p style="color: #856404; margin: 0; font-size: 14px;">
                                    O <strong>Ponto Ótimo Invest</strong> é uma ferramenta <strong>EDUCATIVA e INFORMATIVA</strong>. 
                                    <strong>NÃO constitui recomendação de investimento</strong> e 
                                    <strong>NÃO substitui</strong> consulta a profissional certificado pela CVM.
                                </p>
                                <p style="color: #856404; margin: 10px 0 0 0; font-size: 14px;">
                                    <strong>Rentabilidade passada NÃO garante rentabilidade futura.</strong> 
                                    Você é responsável por suas decisões de investimento.
                                </p>
                            </div>
                            
                            <!-- Expiração do Link -->
                            <div style="background: #ffe6e6; padding: 15px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #dc3545;">
                                <p style="color: #721c24; margin: 0; font-size: 14px;">
                                    ⏰ <strong>Importante:</strong> Este link de ativação expira em <strong>48 horas</strong>.
                                    Ative sua conta o quanto antes para não perder o acesso.
                                </p>
                            </div>
                            
                            <!-- Link alternativo (caso botão não funcione) -->
                            <p style="font-size: 14px; color: #888; margin: 30px 0;">
                                Se o botão não funcionar, copie e cole este link no navegador:<br>
                                <a href="{link_ativacao}" style="color: #007bff; word-break: break-all;">{link_ativacao}</a>
                            </p>
                            
                            <!-- Mensagem Final -->
                            <div style="text-align: center; margin: 40px 0 20px 0; border-top: 2px solid #e9ecef; padding-top: 25px;">
                                <p style="font-size: 16px; color: #666; margin-bottom: 15px;">
                                    Estamos ansiosos para você explorar nossas ferramentas educativas!
                                </p>
                                <p style="font-size: 14px; color: #888; margin: 0;">
                                    <strong>Equipe Ponto Ótimo Invest</strong><br>
                                    <em>Educação financeira através de dados e tecnologia</em>
                                </p>
                            </div>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                            <p style="margin: 0; font-size: 12px; color: #888;">
                                © 2025 Ponto Ótimo Invest. Todos os direitos reservados.<br>
                                Este é um email automático, não responda a esta mensagem.<br>
                                <a href="https://pontootimo.com.br/termos" style="color: #007bff;">Termos de Uso</a> | 
                                <a href="https://pontootimo.com.br/privacidade" style="color: #007bff;">Política de Privacidade</a>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
    
</body>
</html>
        """
        
        # Criar mensagem
        message = Mail(
            from_email=Email(FROM_EMAIL, "Ponto Ótimo Invest"),
            to_emails=To(email_destino),
            subject=subject,
            html_content=Content("text/html", html_content)
        )
        
        # Enviar via SendGrid API
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Email de ativação enviado para {email_destino} - Status: {response.status_code}")
        return True, f"Enviado com sucesso (status {response.status_code})"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de ativação: {e}")
        return False, str(e)


def enviar_email_boas_vindas(email_destino, nome):
    """
    Envia email de boas-vindas após ativação bem-sucedida
    
    Args:
        email_destino: Email do cliente
        nome: Nome do cliente
        
    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    
    if not SENDGRID_API_KEY:
        logger.error("SENDGRID_API_KEY não configurada")
        return False, "SendGrid não configurado"
    
    try:
        subject = "✅ Conta Ativada - Bem-vindo ao Ponto Ótimo Invest!"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bem-vindo - Ponto Ótimo Invest</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="color: white; margin: 0; font-size: 36px;">🎊</h1>
                            <h2 style="color: white; margin: 10px 0; font-size: 28px; font-weight: bold;">Conta Ativada!</h2>
                            <p style="color: #e0e0e0; margin: 10px 0 0 0; font-size: 18px;">Bem-vindo ao Ponto Ótimo Invest</p>
                        </td>
                    </tr>
                    
                    <!-- Conteúdo -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            
                            <h3 style="color: #2c3e50; margin-top: 0; font-size: 22px;">Olá, {nome}! 🎉</h3>
                            
                            <p style="font-size: 16px; color: #555;">
                                Sua conta foi <strong>ativada com sucesso</strong>! Você já pode acessar 
                                todas as ferramentas educativas da plataforma.
                            </p>
                            
                            <!-- Dados de Acesso -->
                            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 12px; border-left: 5px solid #28a745; margin: 30px 0;">
                                <h4 style="color: #28a745; margin-top: 0; font-size: 18px;">🔑 Seus Dados de Acesso</h4>
                                <div style="background: white; padding: 20px; border-radius: 8px; margin: 15px 0;">
                                    <p style="margin: 10px 0; font-size: 16px;">
                                        <strong>📧 Email:</strong> {email_destino}
                                    </p>
                                    <p style="margin: 10px 0; font-size: 16px;">
                                        <strong>🔐 Senha:</strong> A que você acabou de criar
                                    </p>
                                </div>
                            </div>
                            
                            <!-- Botão de Acesso -->
                            <div style="text-align: center; margin: 35px 0;">
                                <a href="{APP_URL}" style="display: inline-block; background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);">
                                    🚀 Acessar Plataforma Agora
                                </a>
                            </div>
                            
                            <!-- Recursos Educativos -->
                            <div style="background: #e7f3ff; padding: 25px; border-radius: 12px; border-left: 5px solid #007bff; margin: 30px 0;">
                                <h4 style="color: #007bff; margin-top: 0; font-size: 18px;">📚 Ferramentas Educativas Disponíveis:</h4>
                                <ul style="color: #004085; margin: 15px 0; padding-left: 20px;">
                                    <li style="margin-bottom: 10px;">
                                        <strong>Análise de Dados Históricos</strong><br>
                                        <span style="font-size: 14px; color: #666;">Visualize e estude preços, retornos e dividendos passados</span>
                                    </li>
                                    <li style="margin-bottom: 10px;">
                                        <strong>Cálculo de Métricas</strong><br>
                                        <span style="font-size: 14px; color: #666;">Sharpe, Volatilidade, Correlação e mais (educativo)</span>
                                    </li>
                                    <li style="margin-bottom: 10px;">
                                        <strong>Simulação Monte Carlo</strong><br>
                                        <span style="font-size: 14px; color: #666;">Explore cenários hipotéticos e entenda riscos</span>
                                    </li>
                                    <li style="margin-bottom: 10px;">
                                        <strong>Otimização Markowitz</strong><br>
                                        <span style="font-size: 14px; color: #666;">Estude alocação matemática de portfólios</span>
                                    </li>
                                </ul>
                            </div>
                            
                            <!-- DISCLAIMER CVM PRINCIPAL -->
                            <div style="background: #fff3cd; padding: 25px; border-radius: 8px; margin: 25px 0; border-left: 5px solid #ffc107;">
                                <h4 style="color: #856404; margin-top: 0; font-size: 16px;">⚠️ AVISO LEGAL - LEIA COM ATENÇÃO</h4>
                                <p style="color: #856404; margin: 0 0 10px 0; font-size: 14px; line-height: 1.6;">
                                    <strong>Esta plataforma tem caráter EDUCATIVO e INFORMATIVO.</strong>
                                </p>
                                <ul style="color: #856404; margin: 10px 0; padding-left: 20px; font-size: 14px;">
                                    <li style="margin-bottom: 8px;">
                                        <strong>NÃO constitui recomendação de investimento</strong>
                                    </li>
                                    <li style="margin-bottom: 8px;">
                                        <strong>NÃO substitui</strong> consulta a analista certificado pela CVM
                                    </li>
                                    <li style="margin-bottom: 8px;">
                                        <strong>Rentabilidade passada NÃO garante</strong> rentabilidade futura
                                    </li>
                                    <li style="margin-bottom: 8px;">
                                        <strong>Simulações são hipotéticas</strong> e podem divergir da realidade
                                    </li>
                                    <li style="margin-bottom: 8px;">
                                        <strong>Você é responsável</strong> por suas decisões de investimento
                                    </li>
                                </ul>
                                <p style="color: #856404; margin: 15px 0 0 0; font-size: 14px;">
                                    💼 <strong>Sempre consulte um profissional certificado antes de investir.</strong>
                                </p>
                            </div>
                            
                            <!-- Suporte -->
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0;">
                                <h4 style="color: #6c757d; margin-top: 0; font-size: 16px;">💬 Precisa de Ajuda?</h4>
                                <p style="color: #6c757d; margin: 0; font-size: 14px;">
                                    Se tiver dúvidas sobre como usar a plataforma, entre em contato conosco.
                                    Estamos aqui para ajudar com questões técnicas e educativas.
                                </p>
                            </div>
                            
                            <!-- Mensagem Final -->
                            <div style="text-align: center; margin: 40px 0 20px 0; border-top: 2px solid #e9ecef; padding-top: 25px;">
                                <p style="font-size: 16px; color: #666; margin-bottom: 15px;">
                                    Boa jornada de aprendizado! 📚
                                </p>
                                <p style="font-size: 14px; color: #888; margin: 0;">
                                    <strong>Equipe Ponto Ótimo Invest</strong><br>
                                    <em>Educação financeira através de dados e tecnologia</em>
                                </p>
                            </div>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                            <p style="margin: 0; font-size: 12px; color: #888; line-height: 1.8;">
                                © 2025 Ponto Ótimo Invest. Todos os direitos reservados.<br>
                                Este é um email automático, não responda a esta mensagem.<br>
                                <a href="https://pontootimo.com.br/termos" style="color: #007bff; text-decoration: none;">Termos de Uso</a> | 
                                <a href="https://pontootimo.com.br/privacidade" style="color: #007bff; text-decoration: none;">Política de Privacidade</a>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
    
</body>
</html>
        """
        
        message = Mail(
            from_email=Email(FROM_EMAIL, "Ponto Ótimo Invest"),
            to_emails=To(email_destino),
            subject=subject,
            html_content=Content("text/html", html_content)
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Email de boas-vindas enviado para {email_destino} - Status: {response.status_code}")
        return True, f"Enviado com sucesso (status {response.status_code})"
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas: {e}")
        return False, str(e)


def testar_envio_email(email_teste):
    """
    Função de teste para validar integração SendGrid
    
    Args:
        email_teste: Email para envio de teste
        
    Returns:
        bool: True se enviou com sucesso
    """
    
    try:
        subject = "🧪 Teste - SendGrid Configurado!"
        
        html_content = """
        <html>
            <body>
                <h2>✅ SendGrid Funcionando!</h2>
                <p>Este é um email de teste.</p>
                <p>Se você recebeu isto, a integração está OK!</p>
            </body>
        </html>
        """
        
        message = Mail(
            from_email=Email(FROM_EMAIL, "Ponto Ótimo Invest"),
            to_emails=To(email_teste),
            subject=subject,
            html_content=Content("text/html", html_content)
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"✅ Email de teste enviado! Status: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    # Teste rápido
    print("=== Teste de Envio de Email ===")
    email = input("Digite um email para teste: ")
    
    if testar_envio_email(email):
        print("\n✅ SendGrid configurado corretamente!")
    else:
        print("\n❌ Erro na configuração. Verifique:")
        print("1. SENDGRID_API_KEY está correta?")
        print("2. FROM_EMAIL está verificado?")
        print("3. Domínio está autenticado?")

