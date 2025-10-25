#!/usr/bin/env python3
"""
🎯 SISTEMA DE ANÁLISE DE AÇÕES - PONTO ÓTIMO INVEST
==================================================

Sistema limpo e otimizado para análise de carteira de investimentos.
- Interface moderna e responsiva
- Análise completa de ações e FIIs
- Sistema de autenticação integrado
- Deploy otimizado para Render

Para executar:
    streamlit run app_clean.py

Para deploy no Render:
    Configurar como Web Service
"""

import streamlit as st
import sqlalchemy
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import requests
import json

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(
    page_title="Ponto Ótimo Invest - Análise de Carteira",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./usuarios.db")
engine = sqlalchemy.create_engine(DATABASE_URL)
ph = PasswordHasher()

# --- CONFIGURAÇÕES DO SISTEMA HÍBRIDO ---
RAILWAY_WEBHOOK_URL = os.environ.get('RAILWAY_WEBHOOK_URL', 'https://web-production-040d1.up.railway.app')

# --- MAPAS DE ATIVOS ---
MAPA_ATIVOS = {
    "Ações": {
        "VALE3": "Vale S.A.",
        "PETR4": "Petrobras",
        "ITUB4": "Itaú Unibanco",
        "BBDC4": "Bradesco",
        "ABEV3": "Ambev",
        "WEGE3": "WEG",
        "MGLU3": "Magazine Luiza",
        "SUZB3": "Suzano",
        "JBSS3": "JBS",
        "RENT3": "Localiza"
    },
    "FIIs": {
        "HGLG11": "CSHG Logística",
        "XPML11": "XP Malls",
        "VISC11": "Vinci Shopping Centers",
        "BCFF11": "Banco do Brasil FII",
        "RBRR11": "RBR Rendimento High Grade"
    }
}

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
<style>
    /* Tema moderno e responsivo */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def init_database():
    """Inicializar banco de dados se não existir"""
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    nome VARCHAR(255),
                    senha_hash VARCHAR(255),
                    status_conta VARCHAR(50) DEFAULT 'ativo',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login TIMESTAMP
                );
            """))
            conn.commit()
    except Exception as e:
        st.error(f"Erro ao inicializar banco de dados: {e}")

def verificar_autenticacao():
    """Verificar se usuário está autenticado"""
    # Verificar token na URL (sistema híbrido)
    token = st.query_params.get('token')
    if token:
        return validar_token_acesso(token)
    return st.session_state.get('autenticado', False)

def validar_token_acesso(token):
    """Validar token de acesso via Railway"""
    try:
        response = requests.get(f"{RAILWAY_WEBHOOK_URL}/api/validar-acesso?token={token}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                st.session_state['autenticado'] = True
                st.session_state['email'] = data.get('email')
                st.session_state['nome'] = data.get('nome')
                st.session_state['token_acesso'] = token
                return True
    except Exception as e:
        st.error(f"Erro ao validar token: {e}")
    return False

def fazer_login(email, senha):
    """Fazer login do usuário"""
    try:
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(
                "SELECT senha_hash, nome FROM usuarios WHERE email = :email AND status_conta = 'ativo'"
            ), {"email": email}).fetchone()
            
            if result:
                senha_hash, nome = result
                try:
                    ph.verify(senha_hash, senha)
                    st.session_state['autenticado'] = True
                    st.session_state['email'] = email
                    st.session_state['nome'] = nome
                    return True
                except (VerifyMismatchError, InvalidHashError):
                    return False
            return False
    except Exception as e:
        st.error(f"Erro no login: {e}")
        return False

def obter_dados_acao(ticker, periodo="1y"):
    """Obter dados de uma ação"""
    try:
        acao = yf.Ticker(f"{ticker}.SA")
        dados = acao.history(period=periodo)
        return dados
    except Exception as e:
        st.error(f"Erro ao obter dados de {ticker}: {e}")
        return None

def calcular_metricas(dados):
    """Calcular métricas de performance"""
    if dados.empty:
        return None
    
    retorno_total = ((dados['Close'].iloc[-1] / dados['Close'].iloc[0]) - 1) * 100
    volatilidade = dados['Close'].pct_change().std() * np.sqrt(252) * 100
    max_drawdown = ((dados['Close'].cummax() - dados['Close']) / dados['Close'].cummax()).max() * 100
    
    return {
        'retorno_total': retorno_total,
        'volatilidade': volatilidade,
        'max_drawdown': max_drawdown
    }

def criar_grafico_preco(dados, ticker):
    """Criar gráfico de preço"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dados.index,
        y=dados['Close'],
        mode='lines',
        name='Preço',
        line=dict(color='#667eea', width=2)
    ))
    
    fig.update_layout(
        title=f"Evolução do Preço - {ticker}",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        template="plotly_white",
        height=400
    )
    
    return fig

# --- INTERFACE PRINCIPAL ---
def main():
    # Inicializar banco de dados
    init_database()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📈 Ponto Ótimo Invest</h1>
        <p>Análise Profissional de Carteira de Investimentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar autenticação
    if not verificar_autenticacao():
        mostrar_tela_login()
    else:
        mostrar_dashboard()

def mostrar_tela_login():
    """Mostrar tela de login"""
    st.markdown("### 🔐 Acesso ao Sistema")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="seu@email.com")
        senha = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                if email and senha:
                    if fazer_login(email, senha):
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Email ou senha incorretos!")
                else:
                    st.warning("⚠️ Preencha todos os campos!")
        
        with col2:
            if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                st.info("💡 Entre em contato para criar sua conta: pontootimoinvest@gmail.com")

def mostrar_dashboard():
    """Mostrar dashboard principal"""
    # Sidebar com informações do usuário
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.get('nome', 'Usuário')}!")
        st.markdown(f"📧 {st.session_state.get('email', '')}")
        
        if st.button("🚪 Sair"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Menu principal
    tab1, tab2, tab3 = st.tabs(["📊 Análise de Ações", "🏢 Análise de FIIs", "📈 Carteira Completa"])
    
    with tab1:
        analisar_acoes()
    
    with tab2:
        analisar_fiis()
    
    with tab3:
        analisar_carteira()

def analisar_acoes():
    """Análise de ações"""
    st.markdown("### 📊 Análise de Ações")
    
    # Seleção de ações
    acoes_disponiveis = list(MAPA_ATIVOS["Ações"].keys())
    acoes_selecionadas = st.multiselect(
        "Selecione as ações para análise:",
        acoes_disponiveis,
        default=acoes_disponiveis[:5]
    )
    
    if acoes_selecionadas:
        # Período de análise
        periodo = st.selectbox(
            "Período de análise:",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        
        # Análise das ações selecionadas
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de evolução
            fig = go.Figure()
            
            for ticker in acoes_selecionadas:
                dados = obter_dados_acao(ticker, periodo)
                if dados is not None and not dados.empty:
                    fig.add_trace(go.Scatter(
                        x=dados.index,
                        y=dados['Close'],
                        mode='lines',
                        name=f"{ticker} - {MAPA_ATIVOS['Ações'][ticker]}",
                        line=dict(width=2)
                    ))
            
            fig.update_layout(
                title="Evolução dos Preços",
                xaxis_title="Data",
                yaxis_title="Preço (R$)",
                template="plotly_white",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Métricas de performance
            st.markdown("### 📈 Métricas de Performance")
            
            for ticker in acoes_selecionadas:
                dados = obter_dados_acao(ticker, periodo)
                if dados is not None and not dados.empty:
                    metricas = calcular_metricas(dados)
                    if metricas:
                        st.markdown(f"**{ticker} - {MAPA_ATIVOS['Ações'][ticker]}**")
                        
                        col_met1, col_met2 = st.columns(2)
                        
                        with col_met1:
                            st.metric(
                                "Retorno Total",
                                f"{metricas['retorno_total']:.2f}%",
                                delta=f"{metricas['retorno_total']:.2f}%"
                            )
                        
                        with col_met2:
                            st.metric(
                                "Volatilidade",
                                f"{metricas['volatilidade']:.2f}%"
                            )
                        
                        st.metric(
                            "Max Drawdown",
                            f"{metricas['max_drawdown']:.2f}%"
                        )
                        
                        st.markdown("---")

def analisar_fiis():
    """Análise de FIIs"""
    st.markdown("### 🏢 Análise de Fundos Imobiliários")
    
    # Seleção de FIIs
    fiis_disponiveis = list(MAPA_ATIVOS["FIIs"].keys())
    fiis_selecionados = st.multiselect(
        "Selecione os FIIs para análise:",
        fiis_disponiveis,
        default=fiis_disponiveis[:3]
    )
    
    if fiis_selecionados:
        # Período de análise
        periodo = st.selectbox(
            "Período de análise:",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        
        # Análise dos FIIs selecionados
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de evolução
            fig = go.Figure()
            
            for ticker in fiis_selecionados:
                dados = obter_dados_acao(ticker, periodo)
                if dados is not None and not dados.empty:
                    fig.add_trace(go.Scatter(
                        x=dados.index,
                        y=dados['Close'],
                        mode='lines',
                        name=f"{ticker} - {MAPA_ATIVOS['FIIs'][ticker]}",
                        line=dict(width=2)
                    ))
            
            fig.update_layout(
                title="Evolução dos Preços dos FIIs",
                xaxis_title="Data",
                yaxis_title="Preço (R$)",
                template="plotly_white",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Métricas de performance
            st.markdown("### 📈 Métricas de Performance")
            
            for ticker in fiis_selecionados:
                dados = obter_dados_acao(ticker, periodo)
                if dados is not None and not dados.empty:
                    metricas = calcular_metricas(dados)
                    if metricas:
                        st.markdown(f"**{ticker} - {MAPA_ATIVOS['FIIs'][ticker]}**")
                        
                        col_met1, col_met2 = st.columns(2)
                        
                        with col_met1:
                            st.metric(
                                "Retorno Total",
                                f"{metricas['retorno_total']:.2f}%",
                                delta=f"{metricas['retorno_total']:.2f}%"
                            )
                        
                        with col_met2:
                            st.metric(
                                "Volatilidade",
                                f"{metricas['volatilidade']:.2f}%"
                            )
                        
                        st.metric(
                            "Max Drawdown",
                            f"{metricas['max_drawdown']:.2f}%"
                        )
                        
                        st.markdown("---")

def analisar_carteira():
    """Análise de carteira completa"""
    st.markdown("### 📈 Análise de Carteira Completa")
    
    # Configuração da carteira
    st.markdown("#### 🎯 Configuração da Carteira")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Ações:**")
        acoes_carteira = {}
        for ticker, nome in MAPA_ATIVOS["Ações"].items():
            peso = st.slider(f"{ticker} - {nome}", 0.0, 1.0, 0.1, 0.1)
            if peso > 0:
                acoes_carteira[ticker] = peso
    
    with col2:
        st.markdown("**FIIs:**")
        fiis_carteira = {}
        for ticker, nome in MAPA_ATIVOS["FIIs"].items():
            peso = st.slider(f"{ticker} - {nome}", 0.0, 1.0, 0.1, 0.1)
            if peso > 0:
                fiis_carteira[ticker] = peso
    
    # Normalizar pesos
    total_peso = sum(acoes_carteira.values()) + sum(fiis_carteira.values())
    if total_peso > 0:
        acoes_carteira = {k: v/total_peso for k, v in acoes_carteira.items()}
        fiis_carteira = {k: v/total_peso for k, v in fiis_carteira.items()}
        
        # Análise da carteira
        st.markdown("#### 📊 Análise da Carteira")
        
        # Gráfico de composição
        fig_pizza = go.Figure(data=[go.Pie(
            labels=list(acoes_carteira.keys()) + list(fiis_carteira.keys()),
            values=list(acoes_carteira.values()) + list(fiis_carteira.values()),
            hole=0.3
        )])
        
        fig_pizza.update_layout(
            title="Composição da Carteira",
            height=400
        )
        
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        # Métricas da carteira
        st.markdown("#### 📈 Métricas da Carteira")
        
        col_met1, col_met2, col_met3 = st.columns(3)
        
        with col_met1:
            st.metric("Total de Ativos", len(acoes_carteira) + len(fiis_carteira))
        
        with col_met2:
            st.metric("Ações", len(acoes_carteira))
        
        with col_met3:
            st.metric("FIIs", len(fiis_carteira))

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    main()
