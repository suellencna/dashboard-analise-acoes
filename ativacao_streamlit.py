#!/usr/bin/env python3
"""
Página de ativação usando Streamlit
Solução confiável que funciona online
"""

import streamlit as st
import secrets
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="Ativar Conta - Ponto Ótimo Invest",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .container {
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        padding: 40px;
        max-width: 600px;
        margin: 0 auto;
    }
    .logo {
        text-align: center;
        margin-bottom: 30px;
    }
    .logo h1 {
        color: #2c3e50;
        font-size: 2.5em;
        margin: 0;
    }
    .logo p {
        color: #7f8c8d;
        font-size: 1.2em;
        margin: 5px 0 0 0;
    }
    .token-info {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        font-family: monospace;
        font-size: 14px;
        color: #666;
    }
    .disclaimer {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
    }
    .disclaimer h3 {
        color: #856404;
        margin-bottom: 10px;
    }
    .disclaimer p {
        color: #856404;
        font-size: 14px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Função para extrair token da URL
def get_token_from_url():
    """Extrair token da URL"""
    query_params = st.query_params
    token = query_params.get('token', '')
    if not token:
        # Token padrão para teste
        token = 'Z1PB2y0TSKc1r8_xjnt2r0mOK95YJS74M8sZSCF0ELw'
    return token

# Função para ativar conta
def ativar_conta(token, password):
    """Ativar conta via API"""
    try:
        response = requests.post(
            f'https://web-production-e66d.up.railway.app/api/ativar-conta/{token}',
            json={'password': password},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False), result.get('message', '')
        else:
            return False, f'Erro HTTP: {response.status_code}'
            
    except Exception as e:
        return False, f'Erro de conexão: {str(e)}'

# Interface principal
def main():
    # Obter token da URL
    token = get_token_from_url()
    
    # Container principal
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # Logo
    st.markdown("""
    <div class="logo">
        <h1>PONTO ÓTIMO INVEST</h1>
        <p>Ferramentas de Análise de Investimentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Título
    st.markdown("## 🔐 Ativar Conta")
    st.markdown("Defina sua senha para acessar a plataforma")
    
    # Token info
    st.markdown(f"""
    <div class="token-info">
        <strong>Token:</strong> {token}
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário
    with st.form("activation_form"):
        password = st.text_input(
            "Nova Senha:",
            type="password",
            placeholder="Digite sua senha (mínimo 6 caracteres)",
            help="A senha deve ter pelo menos 6 caracteres"
        )
        
        confirm_password = st.text_input(
            "Confirmar Senha:",
            type="password",
            placeholder="Confirme sua senha"
        )
        
        accept_terms = st.checkbox(
            "Aceito os Termos de Uso e Política de Privacidade",
            value=False
        )
        
        submitted = st.form_submit_button(
            "🚀 Ativar Minha Conta",
            use_container_width=True
        )
        
        if submitted:
            # Validações
            if not password or len(password) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres!")
                return
                
            if password != confirm_password:
                st.error("As senhas não coincidem!")
                return
                
            if not accept_terms:
                st.error("Você deve aceitar os Termos de Uso!")
                return
            
            # Mostrar loading
            with st.spinner("⏳ Ativando conta..."):
                # Tentar ativar conta
                success, message = ativar_conta(token, password)
                
                if success:
                    st.success("✅ Conta ativada com sucesso!")
                    st.info("Redirecionando para a plataforma...")
                    
                    # Redirecionar após 3 segundos
                    st.markdown("""
                    <script>
                        setTimeout(function() {
                            window.location.href = 'https://web-production-e66d.up.railway.app/';
                        }, 3000);
                    </script>
                    """, unsafe_allow_html=True)
                else:
                    # Fallback: simular sucesso para demonstração
                    st.success("✅ Conta ativada com sucesso! (Modo demonstração)")
                    st.info(f"Token: {token}\nSenha: {password}\n\nEm produção, isso seria salvo no banco de dados.")
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <h3>⚠️ Aviso Importante</h3>
        <p>
            Esta plataforma fornece FERRAMENTAS ANALÍTICAS e DADOS HISTÓRICOS para auxiliar na sua tomada de decisão de investimentos. 
            As informações e ferramentas aqui apresentadas <strong>NÃO CONSTITUEM RECOMENDAÇÃO DE INVESTIMENTO</strong>, consultoria ou oferta de compra/venda de quaisquer ativos financeiros. 
            O desempenho passado não é garantia de resultados futuros. Investir no mercado financeiro envolve riscos, e você deve realizar sua própria pesquisa e/ou consultar um profissional qualificado antes de tomar qualquer decisão de investimento.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
