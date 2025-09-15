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
st.set_page_config(page_title="Análise de Carteira", page_icon="💼", layout="wide")


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
        return False, "DB_ERROR", None, None, None, None  # Retorna 6 valores

    if user_data:
        (nome_usuario, senha_hash_salva, ultima_carteira, ultimos_pesos,
         data_inicio, data_fim, status_assinatura) = user_data

        if pwd_context.verify(password, senha_hash_salva):
            if status_assinatura == 'ativo':
                # Login bem-sucedido
                return True, nome_usuario, ultima_carteira, ultimos_pesos, data_inicio, data_fim
            else:
                # Senha correta, mas assinatura inativa
                return False, "INACTIVE_SUBSCRIPTION", None, None, None, None

    # Email não encontrado ou senha incorreta
    return False, "INVALID_CREDENTIALS", None, None, None, None


# --- 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if 'resultados_otimizacao' not in st.session_state:
    st.session_state.resultados_otimizacao = None
if 'ativos_otimizados' not in st.session_state:
    st.session_state.ativos_otimizados = []
if 'gerar_analise_ia' not in st.session_state:
    st.session_state.gerar_analise_ia = False

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

    # DADOS INICIAIS E MAPEAMENTOS
    DATA_PATH = "dados"
    MAPA_GERAL_ATIVOS = {**MAPA_ATIVOS, **MAPA_FIIS}
    MAPA_BENCHMARK = {'IBOVESPA': 'IBOV_BVSP.csv', 'IFIX': 'IFIX.SA.csv', 'IDIV': 'IDIV.SA.csv', 'CDI': 'CDI.csv',
                      'IPCA': 'IPCA.csv'}
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

    # Se não houver carteira salva, usa o padrão antigo
    if not default_selection:
        default_selection = [ativo for ativo in ['PETR4.SA', 'WEGE3.SA', 'ITUB4.SA'] if ativo in disponiveis]

    ativos_selecionados = st.sidebar.multiselect('Selecione os Ativos', disponiveis, default=default_selection)

    # Lógica para SALVAR a carteira no banco de dados se houver mudança
    nova_carteira_str = ",".join(ativos_selecionados)
    if nova_carteira_str != carteira_salva_str:
        try:
            with engine.connect() as conn:
                query = sqlalchemy.text("UPDATE usuarios SET ultima_carteira = :carteira WHERE email = :email")
                # Assumindo que o email do usuário logado está em st.session_state
                # Precisamos adicioná-lo ao session_state no login!
                conn.execute(query, {"carteira": nova_carteira_str, "email": st.session_state.email})
                conn.commit()
                st.session_state["ultima_carteira"] = nova_carteira_str  # Atualiza o estado da sessão
        except Exception as e:
            st.sidebar.error(f"Erro ao salvar a carteira: {e}")

    #---- FIM DA DEFINIÇÃO DE CARTEIRA
    if len(ativos_selecionados) >= 2:
        # Bloco de código NOVO E CORRIGIDO

        # Bloco CORRIGIDO para leitura dos ativos
        try:
            lista_dfs = []
            for ativo in ativos_selecionados:
                caminho_arquivo = os.path.join(DATA_PATH, f"{ativo}.csv")
                # Adicionamos skiprows=[1] para pular a linha extra que causa erros
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

        st.sidebar.subheader('Opções de Otimização e Simulação')
        num_carteiras_simuladas = st.sidebar.slider('Simulações de Markowitz', 1000, 10000, 5000, key='sim_markowitz')
        data_minima = df_portfolio_completo.index.min().date()
        data_maxima = df_portfolio_completo.index.max().date()

        # Usa a data salva, ou um padrão se não houver
        data_inicio_salva = st.session_state.get("data_inicio_salva")
        data_fim_salva = st.session_state.get("data_fim_salva")

        data_inicio = st.sidebar.date_input("Data de Início",
                                            value=data_inicio_salva or (data_maxima - timedelta(days=365)),
                                            min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
        data_fim = st.sidebar.date_input("Data de Fim",
                                         value=data_fim_salva or data_maxima,
                                         min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")

        if data_inicio > data_fim:
            st.sidebar.error("A data de início não pode ser posterior à data de fim.")
            st.stop()

        data_inicio = pd.to_datetime(data_inicio)  # ← NOVA LINHA
        data_fim = pd.to_datetime(data_fim)  # ← NOVA LINHA
        df_portfolio = df_portfolio_completo.loc[data_inicio:data_fim]  # ← MODIFICADA

        pesos = []
        st.sidebar.subheader('Pesos da Carteira Atual (%)')
        # Converte a string de pesos salvos em uma lista de números
        pesos_salvos_str = st.session_state.get("ultimos_pesos")
        pesos_salvos = []
        if pesos_salvos_str:
            try:
                pesos_salvos = [float(p) for p in pesos_salvos_str.split(',')]
            except:
                pesos_salvos = []  # Ignora se houver erro na conversão

        for i, ativo in enumerate(ativos_selecionados):
            # Usa o peso salvo se ele existir para este ativo, senão usa o padrão
            valor_padrao = pesos_salvos[i] if i < len(pesos_salvos) else round(100 / len(ativos_selecionados), 2)
            peso = st.sidebar.number_input(f'Peso para {ativo}', min_value=0.0, max_value=100.0,
                                           value=valor_padrao, step=1.0, key=f'peso_{i}')
            pesos.append(peso)

        # Adicione este bloco na barra lateral, após os inputs de peso
        if st.sidebar.button("Salvar Configuração da Carteira"):
            # Formata os pesos para salvar como texto
            pesos_para_salvar = ",".join([str(p) for p in pesos])

            try:
                with engine.connect() as conn:
                    query = sqlalchemy.text(
                        "UPDATE usuarios SET "
                        "ultima_carteira = :carteira, "
                        "ultimos_pesos = :pesos, "
                        "data_inicio_salva = :data_inicio, "
                        "data_fim_salva = :data_fim "
                        "WHERE email = :email"
                    )
                    conn.execute(query, {
                        "carteira": ",".join(ativos_selecionados),
                        "pesos": pesos_para_salvar,
                        "data_inicio": data_inicio,
                        "data_fim": data_fim,
                        "email": st.session_state.email
                    })
                    conn.commit()
                    st.sidebar.success("Configuração salva com sucesso!")
                    # Atualiza o estado da sessão com os novos valores
                    st.session_state["ultima_carteira"] = ",".join(ativos_selecionados)
                    st.session_state["ultimos_pesos"] = pesos_para_salvar
                    st.session_state["data_inicio_salva"] = data_inicio
                    st.session_state["data_fim_salva"] = data_fim
            except Exception as e:
                st.sidebar.error(f"Erro ao salvar: {e}")

        if sum(pesos) > 0:
            pesos = np.array(pesos) / sum(pesos)
        else:
            st.error("A soma dos pesos não pode ser zero.")
            st.stop()

        pesos = np.array(pesos, dtype=float)  # ← isso garante o tipo certo para multiplicação
        # st.write(df_portfolio[ativos_selecionados].dtypes) ## imprime o tipo de dados
        # st.write(pesos)
        df_portfolio['Carteira'] = (df_portfolio[ativos_selecionados] * pesos).sum(axis=1)

        # Centralizado
        st.markdown(
            f"<h3 style='text-align: center;'>Análise da Carteira de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</h3>",
            unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        # Bloco NOVO e CORRIGIDO (com lógica de busca inteligente)

        with col1:
            st.subheader('Composição da Carteira')
            visao_pizza = st.radio("Visualizar por:", ('Ativo', 'Setor'), horizontal=True, key='visao_pizza')

            if visao_pizza == 'Ativo':
                # Ordena ativos por peso (maior para menor)
                ativos_pesos_ordenados = sorted(zip(ativos_selecionados, pesos), key=lambda x: x[1], reverse=True)
                ativos_ordenados = [item[0] for item in ativos_pesos_ordenados]
                pesos_ordenados = [item[1] for item in ativos_pesos_ordenados]
                
                fig_pizza = go.Figure(data=[go.Pie(
                    labels=ativos_ordenados, 
                    values=pesos_ordenados, 
                    hole=.3, 
                    textinfo='label+percent',
                    textfont=dict(size=12, color='white'),
                    marker=dict(
                        colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                    ),
                    sort=False,
                    direction='clockwise'
                )])
                fig_pizza.update_layout(
                    title=dict(text="Composição por Ativo", font=dict(size=16, color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )
            else:  # Lógica para visão por Setor
                pesos_setor = {}
                for ativo, peso in zip(ativos_selecionados, pesos):

                    # --- LÓGICA DE BUSCA INTELIGENTE ---
                    # 1. Tenta encontrar uma correspondência exata primeiro (bom para FIIs e Units como 'BTLG11.SA')
                    info_ativo = MAPA_GERAL_ATIVOS.get(ativo)

                    # 2. Se não encontrar, tenta encontrar pelo radical (ex: 'PETR4.SA' -> 'PETR.SA')
                    if not info_ativo:
                        match = re.search(r'\d', ativo)  # Encontra o primeiro número no nome do ativo
                        if match:
                            indice_do_numero = match.start()
                            ticker_base = ativo[:indice_do_numero] + '.SA'  # Cria o radical, ex: 'PETR.SA'
                            info_ativo = MAPA_GERAL_ATIVOS.get(ticker_base,
                                                               {'setor': 'Outros'})  # Tenta a busca de novo
                        else:
                            info_ativo = {'setor': 'Outros'}  # Se não tiver número, classifica como Outros

                    setor = info_ativo.get('setor', 'Outros')  # Busca segura final
                    # --- FIM DA LÓGICA ---

                    if setor in pesos_setor:
                        pesos_setor[setor] += peso
                    else:
                        pesos_setor[setor] = peso

                # Ordena setores por peso (maior para menor)
                setores_pesos_ordenados = sorted(pesos_setor.items(), key=lambda x: x[1], reverse=True)
                setores_ordenados = [item[0] for item in setores_pesos_ordenados]
                pesos_setores_ordenados = [item[1] for item in setores_pesos_ordenados]

                fig_pizza = go.Figure(data=[go.Pie(
                    labels=setores_ordenados, 
                    values=pesos_setores_ordenados, 
                    hole=.3,
                    textinfo='label+percent',
                    textfont=dict(size=12, color='white'),
                    marker=dict(
                        colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                    ),
                    sort=False,
                    direction='clockwise'
                )])
                fig_pizza.update_layout(
                    title=dict(text="Composição por Setor", font=dict(size=16, color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )

            st.plotly_chart(fig_pizza, use_container_width=True)

        with col2:
            st.subheader('Carteira vs. Benchmark')
            benchmark_selecionado = st.selectbox("Selecione o Benchmark:", list(MAPA_BENCHMARK.keys()))
            caminho_bench = os.path.join(DATA_PATH, MAPA_BENCHMARK[benchmark_selecionado])
            try:
                # Linha NOVA e CORRIGIDA do Benchmark
                df_bench = pd.read_csv(caminho_bench, index_col='Date', parse_dates=True, skiprows=[1])
                df_bench = df_bench.reindex(df_portfolio.index).ffill().dropna()

                retornos_diarios_comp = pd.DataFrame(
                    {'Carteira': df_portfolio['Carteira'], 'Benchmark': df_bench['Close']}).pct_change().dropna()

                if retornos_diarios_comp.empty or len(retornos_diarios_comp) < 2:
                    st.warning(
                        f"Dados insuficientes para o benchmark '{benchmark_selecionado}' no período para gerar o gráfico.")
                else:
                    df_acumulado = (1 + retornos_diarios_comp).cumprod() * 100
                    df_acumulado.iloc[0] = 100
                    fig_desempenho = go.Figure()
                    fig_desempenho.add_trace(
                        go.Scatter(x=df_acumulado.index, y=df_acumulado['Carteira'], mode='lines',
                                   name='Minha Carteira'))
                    fig_desempenho.add_trace(go.Scatter(x=df_acumulado.index, y=df_acumulado['Benchmark'], mode='lines',
                                                        name=benchmark_selecionado))
                    fig_desempenho.update_layout(title_text='Desempenho Comparativo (Base 100)', template='plotly_dark')
                    st.plotly_chart(fig_desempenho, use_container_width=True)
            except Exception as e:
                st.error(
                    f"Não foi possível carregar ou processar os dados do benchmark '{benchmark_selecionado}'. Verifique o arquivo .csv. Erro: {e}")

        st.markdown("---")

        ## ------------------------------------


        # --- Seção 2: Otimização, Guia e Projeções (Tudo em Um) ---
        with st.expander("Clique aqui para Otimização e Projeções", expanded=True):

            # --- CONTROLES UNIFICADOS NA SIDEBAR ---
            #st.sidebar.subheader('Opções de Otimização e Simulação')
            #num_carteiras_simuladas = st.sidebar.slider('Simulações de Markowitz', 1000, 10000, 5000,
            #                                            key='sim_markowitz')
            valor_investimento = st.sidebar.number_input("Valor do Investimento (R$)", min_value=1000.0, value=50000.0,
                                                         step=1000.0, key='val_investimento')
            anos_projecao = st.sidebar.slider("Anos de Projeção (Monte Carlo)", 1, 30, 10, key='anos_projecao')
            num_simulacoes_mc = st.sidebar.select_slider("Simulações de Monte Carlo", options=[100, 250, 500],
                                                         value=250, key='sim_mc')

            # Inicializa o estado da sessão para guardar todos os resultados
            if 'resultados_gerados' not in st.session_state:
                st.session_state.resultados_gerados = None

            if st.button('Otimizar Carteira e Gerar Projeções'):
                with st.spinner('Realizando todos os cálculos... Isso pode levar um momento.'):
                    # 1. CÁLCULO DE MARKOWITZ
                    retornos_diarios = df_portfolio[ativos_selecionados].pct_change().dropna()
                    matriz_covariancia = retornos_diarios.cov() * PREGOES_NO_ANO

                    resultados_retorno, resultados_risco, resultados_sharpe, matriz_pesos = [[] for _ in range(4)]
                    for i in range(num_carteiras_simuladas):
                        pesos_sim = np.random.random(len(ativos_selecionados))
                        pesos_sim /= np.sum(pesos_sim)
                        matriz_pesos.append(pesos_sim)
                        retorno = np.sum(retornos_diarios.mean() * pesos_sim) * PREGOES_NO_ANO
                        risco = np.sqrt(np.dot(pesos_sim.T, np.dot(matriz_covariancia, pesos_sim)))
                        resultados_retorno.append(retorno)
                        resultados_risco.append(risco)
                        resultados_sharpe.append((retorno - TAXA_LIVRE_DE_RISCO) / risco)

                    st.session_state.resultados_otimizacao = {
                        'risco': np.array(resultados_risco), 'retorno': np.array(resultados_retorno),
                        'sharpe': np.array(resultados_sharpe),
                        'pesos': matriz_pesos,
                        'retornos_individuais': retornos_diarios.mean() * PREGOES_NO_ANO,
                        'volatilidades_individuais': retornos_diarios.std() * np.sqrt(PREGOES_NO_ANO)
                    }
                    st.session_state.ativos_otimizados = ativos_selecionados.copy()


                    res_markowitz = {
                        'risco': np.array(resultados_risco), 'retorno': np.array(resultados_retorno),
                        'sharpe': np.array(resultados_sharpe), 'pesos': matriz_pesos,
                        'retornos_individuais': retornos_diarios.mean() * PREGOES_NO_ANO,
                        'volatilidades_individuais': retornos_diarios.std() * np.sqrt(PREGOES_NO_ANO)
                    }
                    indice_max_sharpe = np.argmax(resultados_sharpe)
                    pesos_otimos = matriz_pesos[indice_max_sharpe]

                    # 2. BUSCA DE PREÇOS E GUIA DE INVESTIMENTO (CÓDIGO MOVIDO)
                    res = st.session_state.resultados_otimizacao
                    indice_max_sharpe = res['sharpe'].argmax()
                    pesos_otimos = res['pesos'][indice_max_sharpe]
                    dados_recentes = yf.download(ativos_selecionados, period="5d")['Close']
                    ultimos_precos = dados_recentes.iloc[-1]
                    df_guia = pd.DataFrame({'Ativo': ativos_selecionados, 'Peso (%)': [p * 100 for p in pesos_otimos]})

                    df_guia['Valor a Investir (R$)'] = df_guia['Peso (%)'] / 100 * valor_investimento
                    df_guia['Último Preço (R$)'] = df_guia['Ativo'].map(ultimos_precos)
                    df_guia['Quantidade de Ações'] = (
                                df_guia['Valor a Investir (R$)'] / df_guia['Último Preço (R$)']).astype(int)

                    # 3. CÁLCULO DE MONTE CARLO
                    retorno_anual_esperado = resultados_retorno[indice_max_sharpe]
                    risco_anual_esperado = resultados_risco[indice_max_sharpe]
                    retorno_diario_medio = retorno_anual_esperado / PREGOES_NO_ANO
                    volatilidade_diaria = risco_anual_esperado / np.sqrt(PREGOES_NO_ANO)
                    dias_projecao = anos_projecao * PREGOES_NO_ANO
                    matriz_resultados = np.zeros((dias_projecao, num_simulacoes_mc))
                    for i in range(num_simulacoes_mc):
                        retornos_aleatorios = np.random.normal(retorno_diario_medio, volatilidade_diaria, dias_projecao)
                        caminho_patrimonio = np.zeros(dias_projecao)
                        caminho_patrimonio[0] = valor_investimento * (1 + retornos_aleatorios[0])
                        for j in range(1, dias_projecao):
                            caminho_patrimonio[j] = caminho_patrimonio[j - 1] * (1 + retornos_aleatorios[j])
                        matriz_resultados[:, i] = caminho_patrimonio

                    df_simulacao = pd.DataFrame(matriz_resultados)
                    datas_projecao = pd.bdate_range(start=datetime.now().date(), periods=dias_projecao)
                    df_simulacao.index = datas_projecao
                    fig_mc = go.Figure()
                    simulacoes_a_mostrar = min(num_simulacoes_mc, 500)
                    for i in range(simulacoes_a_mostrar):
                        fig_mc.add_trace(go.Scatter(x=df_simulacao.index, y=df_simulacao.iloc[:, i], mode='lines',
                                                    line=dict(width=1, color='lightblue'), showlegend=False,
                                                    opacity=0.1))
                    fig_mc.add_trace(
                        go.Scatter(x=df_simulacao.index, y=df_simulacao.quantile(0.05, axis=1), mode='lines',
                                   line=dict(color='red', width=2), name='Pior Cenário (5%)'))
                    fig_mc.add_trace(
                        go.Scatter(x=df_simulacao.index, y=df_simulacao.quantile(0.50, axis=1), mode='lines',
                                   line=dict(color='orange', width=3), name='Cenário Mediano (50%)'))
                    fig_mc.add_trace(
                        go.Scatter(x=df_simulacao.index, y=df_simulacao.quantile(0.95, axis=1), mode='lines',
                                   line=dict(color='lightgreen', width=2), name='Melhor Cenário (95%)'))
                    fig_mc.update_layout(title_text=f'Projeção de Patrimônio em {anos_projecao} Anos',
                                         xaxis_title='Data', yaxis_title='Patrimônio (R$)', template='plotly_dark',
                                         showlegend=True)
                    patrimonio_final_mediano = df_simulacao.iloc[-1].median()
                    patrimonio_final_pior_cenario = df_simulacao.iloc[-1].quantile(0.05)
                    patrimonio_final_melhor_cenario = df_simulacao.iloc[-1].quantile(0.95)

                    # 4. SALVAR TUDO EM UM ÚNICO LUGAR
                    st.session_state.resultados_gerados = {
                        "markowitz": res,
                        "guia_investimento": df_guia,
                        "ativos_otimizados": ativos_selecionados.copy(),
                        "monte_carlo_fig": fig_mc,
                        "monte_carlo_text_data": {
                            'investimento': valor_investimento, 'simulacoes': num_simulacoes_mc, 'anos': anos_projecao,
                            'mediano': patrimonio_final_mediano, 'pior': patrimonio_final_pior_cenario,
                            'melhor': patrimonio_final_melhor_cenario
                        }
                    }
                st.rerun()

            # --- BLOCO DE EXIBIÇÃO (SÓ MOSTRA OS RESULTADOS) ---
            if st.session_state.resultados_gerados:
                resultados = st.session_state.resultados_gerados
                res = resultados["markowitz"]
                ativos_otimizados = resultados["ativos_otimizados"]
                indice_max_sharpe = res['sharpe'].argmax()
                pesos_otimos = res['pesos'][indice_max_sharpe]
                indice_min_risco = res['risco'].argmin()

                # EXIBIÇÃO DE MARKOWITZ
                st.subheader('Resultados da Otimização')
                st.info("""
                            #### Entendendo o Gráfico de Markowitz

                            * **O que é?** 
                                Uma teoria vencedora do Prêmio Nobel que provou matematicamente o velho ditado: "não coloque todos os ovos na mesma cesta". A ideia é que, ao combinar ativos diferentes, você pode reduzir o risco geral da sua carteira sem sacrificar muito do seu retorno.

                            * **O que o gráfico significa?**
                                * **Eixo Vertical (Retorno):** Quanto mais alto, melhor.
                                * **Eixo Horizontal (Risco):** Quanto mais para a **esquerda**, melhor.
                                * **Nuvem de Pontos:** Cada ponto é uma carteira possível com uma combinação de pesos diferente. A cor indica a qualidade (relação risco/retorno), sendo amarelo a melhor.
                                * **Estrela Dourada (★):** A carteira "ótima", com o melhor equilíbrio entre risco e retorno.
                                * **"X" Vermelho:** A carteira com o menor risco possível.

                            * **Como usar?** 
                                Compare a posição dos ativos individuais (losangos) com as estrelas. O gráfico te ajuda a visualizar o poder da diversificação: ao combinar os ativos, é possível criar carteiras (as estrelas) que são melhores do que qualquer um dos ativos sozinhos.

                            """)
                col_graf_fronteira, col_graf_pesos = st.columns([0.6, 0.4])
                with col_graf_fronteira:
                    st.markdown("###### Fronteira Eficiente")
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.scatter(res['risco'], res['retorno'], c=res['sharpe'], cmap='viridis', marker='.', s=5,
                               alpha=0.4)

                    cores_ativos = ['#FF4B4B', '#3E6D8E', '#6B4E9A']
                    for i, ticker in enumerate(st.session_state.ativos_otimizados):
                        ax.scatter(res['volatilidades_individuais'][i], res['retornos_individuais'][i], marker='D',
                                   color=cores_ativos[i % len(cores_ativos)], s=150, label=ticker, zorder=5)

                    ax.scatter(res['risco'][indice_min_risco], res['retorno'][indice_min_risco], marker='X',
                               color='red', s=200, label='Carteira Risco Mínimo', zorder=5)
                    ax.scatter(res['risco'][indice_max_sharpe], res['retorno'][indice_max_sharpe], marker='*',
                               color='gold', s=300, label='Carteira Sharpe Máximo', zorder=5)

                    ax.set_title('Otimização de Portfólio', fontsize=12)
                    ax.set_xlabel('Risco (Volatilidade)', fontsize=10)
                    ax.set_ylabel('Retorno Esperado', fontsize=10)
                    ax.legend(loc='upper right', fontsize=8)  # <-- LEGENDA DE VOLTA
                    st.pyplot(fig)

                with col_graf_pesos:
                    st.markdown("###### Composição da Carteira Ótima")
                    df_pesos_otimos = pd.DataFrame(pesos_otimos, index=st.session_state.ativos_otimizados,
                                                   columns=['Peso'])

                    # --- ALTERAÇÃO AQUI: Criando as legendas personalizadas ---
                    legendas_personalizadas = [f"{ativo} ({peso:.2%})" for ativo, peso in
                                               df_pesos_otimos['Peso'].items()]

                    # Ordena a carteira ótima por peso (maior para menor)
                    df_pesos_otimos_ordenado = df_pesos_otimos.sort_values('Peso', ascending=False)
                    legendas_personalizadas_ordenadas = [f"{ativo} ({peso:.2%})" for ativo, peso in df_pesos_otimos_ordenado['Peso'].items()]

                    fig_pie_otima = go.Figure(
                        data=[go.Pie(
                            labels=legendas_personalizadas_ordenadas,
                            values=df_pesos_otimos_ordenado['Peso'],
                            hole=.3,
                            textinfo='label+percent',
                            textfont=dict(size=12, color='white'),
                            marker=dict(
                                colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                            ),
                            sort=False,
                            direction='clockwise'
                        )]
                    )

                    fig_pie_otima.update_layout(
                        title=dict(text="Carteira Ótima", font=dict(size=16, color='white')),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05
                        )
                    )
                    st.plotly_chart(fig_pie_otima, use_container_width=True)

                st.subheader('Métricas dos Ativos para Comparação')
                # ... (seu código da tabela de métricas)
                df_metricas = pd.DataFrame({
                    'Retorno Anual': res['retornos_individuais'],
                    'Volatilidade': res['volatilidades_individuais']
                }).reset_index().rename(columns={'index': 'Ativo'})
                st.dataframe(df_metricas, column_config={
                    "Retorno Anual": st.column_config.ProgressColumn("Retorno Anual", format="%.2f%%", min_value=0),
                    "Volatilidade": st.column_config.ProgressColumn("Volatilidade", format="%.2f%%", min_value=0)
                }, use_container_width=True, hide_index=True)

                # EXIBIÇÃO DO GUIA DE INVESTIMENTO
                st.markdown("---")
                st.subheader("Guia de Investimento para a Carteira Ótima")
                st.dataframe(resultados["guia_investimento"],
                             column_config={
                                 "Peso (%)": st.column_config.ProgressColumn("Peso (%)", format="%.1f%%", min_value=0,
                                                                             max_value=100),
                                 "Valor a Investir (R$)": st.column_config.NumberColumn("Valor a Investir (R$)",
                                                                                        format="R$ %.2f"),
                                 "Último Preço (R$)": st.column_config.NumberColumn("Último Preço (R$)",
                                                                                    format="R$ %.2f"),
                                 "Quantidade de Ações": st.column_config.NumberColumn("Qtde. Ações (aprox.)")
                             },
                             use_container_width=True, hide_index=True)

                # EXIBIÇÃO DE MONTE CARLO
                st.markdown("---")
                st.subheader("Projeção de Patrimônio Futuro (Monte Carlo)")
                res_mc_text = resultados["monte_carlo_text_data"]
                # ... (seu código dos st.metric) ...
                # --- INÍCIO DO CÓDIGO DO RESUMO COM st.metric ---

                # 1. Pega os dados do dicionário e calcula as porcentagens de retorno
                investimento_inicial = res_mc_text['investimento']
                retorno_mediano_pct = (res_mc_text['mediano'] / investimento_inicial - 1) * 100
                retorno_otimista_pct = (res_mc_text['melhor'] / investimento_inicial - 1) * 100
                retorno_pessimista_pct = (res_mc_text['pior'] / investimento_inicial - 1) * 100

                # Calcula a data final da projeção
                data_final_projecao = datetime.now().date() + timedelta(days=res_mc_text['anos'] * 365)

                # 2. Exibe o resumo em 4 colunas com st.metric
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        label=f"Cenário Atual ({datetime.now().strftime('%d %b %Y')})",
                        value=f"R$ {investimento_inicial:,.2f}",
                        delta="0.00%"
                    )
                with col2:
                    st.metric(
                        label=f"Esperado ({data_final_projecao.strftime('%d %b %Y')})",
                        value=f"R$ {res_mc_text['mediano']:,.2f}",
                        delta=f"{retorno_mediano_pct:.2f}%"
                    )
                with col3:
                    st.metric(
                        label=f"Otimista ({data_final_projecao.strftime('%d %b %Y')})",
                        value=f"R$ {res_mc_text['melhor']:,.2f}",
                        delta=f"{retorno_otimista_pct:.2f}%"
                    )
                with col4:
                    st.metric(
                        label=f"Pessimista ({data_final_projecao.strftime('%d %b %Y')})",
                        value=f"R$ {res_mc_text['pior']:,.2f}",
                        delta=f"{retorno_pessimista_pct:.2f}%"
                    )

                # --- FIM DO CÓDIGO DO RESUMO ---

                st.plotly_chart(resultados["monte_carlo_fig"], use_container_width=True)
                st.info(f"""
                            #### 🤔 Como Ler o Gráfico da Simulação?

                            Nós criamos {res_mc_text['simulacoes']} simulações de como sua carteira de investimentos **(R$ {res_mc_text['investimento']:,.2f})** poderia se comportar nos próximos **{res_mc_text['anos']} anos**. Este gráfico resume tudo isso.

                            * **🎯 O Alvo Principal (Linha Laranja):**
                                Esta linha no meio representa o **resultado central** de todas as simulações. É o valor mais provável que seu patrimônio pode atingir, chegando a cerca de **R$ {res_mc_text['mediano']:,.2f}**.

                            * **↔️ A Faixa de Resultados Realista:**
                                Nossa análise mostra uma probabilidade de 90% de que o patrimônio final fique na seguinte faixa:
                                * **Cenário Pessimista:** R$ {res_mc_text['pior']:,.2f}
                                * **Cenário Otimista:** R$ {res_mc_text['melhor']:,.2f}

                            **O que fazer com essa informação?**
                            Use esta projeção para ter uma ideia se o plano de investimentos atual está alinhado com seus sonhos. A faixa de valores te dá uma visão realista do que esperar, ajudando a planejar o futuro com mais segurança e menos surpresas.

                            **Obs.:** Lembrando que, caso deseje alterar, o valor inicial da carteira está na aba lateral!
                            """)

                if st.button("Limpar Análise"):
                    st.session_state.resultados_gerados = None
                    st.rerun()
    else:
        st.warning('Por favor, selecione pelo menos um ativo para a análise.')

else:
    # SE NÃO ESTIVER LOGADO, MOSTRA A TELA DE LOGIN
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("prints/slogan_preto.png", width=500)
        st.warning('Por favor, insira seu usuário e senha para acessar')

    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        is_logged_in, user_name, ultima_carteira, ultimos_pesos, data_inicio, data_fim = check_login(email, password)
        if is_logged_in:
            st.session_state["authentication_status"] = True
            st.session_state["name"] = user_name
            st.session_state["email"] = email
            st.session_state["ultima_carteira"] = ultima_carteira
            st.session_state["ultimos_pesos"] = ultimos_pesos
            st.session_state["data_inicio_salva"] = data_inicio
            st.session_state["data_fim_salva"] = data_fim
            st.rerun()
        else:
            st.session_state["authentication_status"] = False
            if user_name == "INACTIVE_SUBSCRIPTION":
                st.sidebar.error("Sua assinatura não está ativa.")
            else:
                st.sidebar.error("Email ou senha incorreta.")