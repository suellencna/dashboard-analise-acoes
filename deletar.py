# --- 1. BLOCO DE IMPORTAÇÕES E CONFIGURAÇÕES ---
import streamlit as st
import sqlalchemy
import os
from passlib.context import CryptContext
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from mapa_ativos import MAPA_ATIVOS
from mapa_fiis import MAPA_FIIS
import re
import yfinance as yf

# --- Configurações da Página e Estilo ---
st.set_page_config(page_title="Ponto Ótimo Invest", page_icon="💼", layout="wide")


# --- 2. CONFIGURAÇÃO DO BANCO DE DADOS E SENHA ---
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = None
pwd_context = None
try:
    if DATABASE_URL:
        engine = sqlalchemy.create_engine(DATABASE_URL)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    else:
        st.error("ERRO CRÍTICO: A variável de ambiente DATABASE_URL não foi encontrada.")
        st.stop()
except Exception as e:
    st.error(f"ERRO CRÍTICO na inicialização do sistema de autenticação: {e}")
    st.stop()


# --- 3. FUNÇÃO DE LOGIN ---
def check_login(email, password):
    user_data = None
    try:
        with engine.connect() as conn:
            query = sqlalchemy.text(
                "SELECT nome, senha_hash, ultima_carteira, ultimos_pesos, "
                "data_inicio_salva, data_fim_salva, status_assinatura "
                "FROM usuarios WHERE email = :email"
            )
            result = conn.execute(query, {"email": email}).first()
            if result:
                user_data = result
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        return False, "DB_ERROR", None, None, None, None

    if user_data:
        (nome_usuario, senha_hash_salva, ultima_carteira, ultimos_pesos,
         data_inicio, data_fim, status_assinatura) = user_data
        if pwd_context.verify(password, senha_hash_salva):
            if status_assinatura == 'ativo':
                return True, nome_usuario, ultima_carteira, ultimos_pesos, data_inicio, data_fim
            else:
                return False, "INACTIVE_SUBSCRIPTION", None, None, None, None
    return False, "INVALID_CREDENTIALS", None, None, None, None


# --- 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if 'resultados_gerados' not in st.session_state:
    st.session_state.resultados_gerados = None
# ... (outras inicializações de session_state que você já tinha)


# --- 5. LÓGICA DA INTERFACE ---
if st.session_state.get("authentication_status"):
    # SE ESTIVER LOGADO, MOSTRA O DASHBOARD COMPLETO
    st.sidebar.image("prints/slogan_preto.png", width=150)
    st.sidebar.title(f'Bem-vindo(a), {st.session_state["name"]}!')

    # LÓGICA DO LOGOUT
    if 'confirming_logout' not in st.session_state:
        st.session_state.confirming_logout = False
    if st.sidebar.button("Logout", key="logout_initial"):
        st.session_state.confirming_logout = True
        st.rerun()
    if st.session_state.confirming_logout:
        st.sidebar.warning("Você tem certeza que deseja sair?")
        col1_logout, col2_logout = st.sidebar.columns(2)
        if col1_logout.button("Sim", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if col2_logout.button("Não", use_container_width=True):
            st.session_state.confirming_logout = False
            st.rerun()

    # --- INÍCIO DO CÓDIGO DO DASHBOARD ---
    plt.style.use('seaborn-v0_8-darkgrid')
    DATA_PATH = "dados"
    MAPA_GERAL_ATIVOS = {**MAPA_ATIVOS, **MAPA_FIIS}
    MAPA_BENCHMARK = {'IBOVESPA': 'IBOV_BVSP.csv', 'IFIX': 'IFIX.SA.csv', 'IDIV': 'IDIV.SA.csv', 'CDI': 'CDI.csv', 'IPCA': 'IPCA.csv'}
    PREGOES_NO_ANO = 252
    TAXA_LIVRE_DE_RISCO = 0.105

    try:
        todos_arquivos = os.listdir(DATA_PATH)
        disponiveis = [arquivo.replace('.csv', '') for arquivo in todos_arquivos if arquivo.endswith('.SA.csv')]
        disponiveis.sort()
        if not disponiveis:
            st.error(f"Nenhum arquivo de ativo (.SA.csv) encontrado na pasta '{DATA_PATH}'.")
            st.stop()
    except FileNotFoundError:
        st.error(f"Pasta de dados '{DATA_PATH}' não encontrada.")
        st.stop()

    st.title('Dashboard de Análise de Carteiras 💼')
    st.sidebar.header('Definição da Carteira')

    # Lógica para carregar a carteira salva
    default_selection = []
    carteira_salva_str = st.session_state.get("ultima_carteira")
    if carteira_salva_str:
        default_selection = [ativo for ativo in carteira_salva_str.split(',') if ativo in disponiveis]
    if not default_selection:
        default_selection = [ativo for ativo in ['PETR4.SA', 'WEGE3.SA', 'ITUB4.SA'] if ativo in disponiveis]
    ativos_selecionados = st.sidebar.multiselect('Selecione os Ativos', disponiveis, default=default_selection)

    if len(ativos_selecionados) >= 2:
        try:
            lista_dfs = []
            for ativo in ativos_selecionados:
                caminho_arquivo = os.path.join(DATA_PATH, f"{ativo}.csv")
                df_ativo = pd.read_csv(caminho_arquivo, index_col='Date', parse_dates=True, skiprows=[1])
                df_ativo.rename(columns={'Close': ativo}, inplace=True)
                lista_dfs.append(df_ativo)

            df_portfolio_completo = pd.concat(lista_dfs, axis=1)
            df_portfolio_completo = df_portfolio_completo.apply(pd.to_numeric, errors='coerce')
            df_portfolio_completo.sort_index(inplace=True)
            df_portfolio_completo.dropna(inplace=True)
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os arquivos de dados dos ativos: {e}")
            st.stop()

        st.sidebar.subheader("Período de Análise")
        data_minima = df_portfolio_completo.index.min().date()
        data_maxima = df_portfolio_completo.index.max().date()
        data_inicio_salva = st.session_state.get("data_inicio_salva")
        data_fim_salva = st.session_state.get("data_fim_salva")
        data_inicio = st.sidebar.date_input("Data de Início", value=data_inicio_salva or (data_maxima - timedelta(days=365)), min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
        data_fim = st.sidebar.date_input("Data de Fim", value=data_fim_salva or data_maxima, min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")

        if data_inicio > data_fim:
            st.sidebar.error("A data de início não pode ser posterior à data de fim.")
            st.stop()

        df_portfolio = df_portfolio_completo.loc[pd.to_datetime(data_inicio):pd.to_datetime(data_fim)]

        pesos_atuais = []
        st.sidebar.subheader('Pesos da Carteira Atual (%)')
        pesos_salvos_str = st.session_state.get("ultimos_pesos")
        pesos_salvos = [float(p) for p in pesos_salvos_str.split(',')] if pesos_salvos_str else []
        for i, ativo in enumerate(ativos_selecionados):
            valor_padrao = pesos_salvos[i] if i < len(pesos_salvos) else round(100 / len(ativos_selecionados), 2)
            peso = st.sidebar.number_input(f'Peso para {ativo}', min_value=0.0, max_value=100.0, value=valor_padrao, step=1.0, key=f'peso_{i}')
            pesos_atuais.append(peso)

        if st.sidebar.button("Salvar Configuração da Carteira"):
            # ... (seu código do botão salvar, que já está correto)

        soma_pesos_atuais = sum(pesos_atuais)
        if soma_pesos_atuais > 0:
            pesos_normalizados = np.array(pesos_atuais) / soma_pesos_atuais
        else:
            st.error("A soma dos pesos não pode ser zero.")
            st.stop()

        df_portfolio['Carteira'] = (df_portfolio[ativos_selecionados] * pesos_normalizados).sum(axis=1)

        # Gráfico de Composição e Benchmark
        st.markdown(f"<h3 style='text-align: center;'>Análise da Carteira de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</h3>", unsafe_allow_html=True)
        # ... (seu código dos gráficos de Pizza e Benchmark, que já está correto)

        # --- Seção 2: Otimização e Projeções (Tudo em Um) ---
        with st.expander("Clique aqui para Otimização e Projeções", expanded=True):
            # ... (código que você me enviou, que já está correto e refatorado)

    else:
        st.warning('Por favor, selecione pelo menos dois ativos para a análise.')

else:
    # SE NÃO ESTIVER LOGADO, MOSTRA A TELA DE LOGIN
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("prints/slogan_preto.png", width=400)
        st.warning('Por favor, insira seu usuário e senha para acessar')
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        # ... (lógica do botão entrar, que já está correta)