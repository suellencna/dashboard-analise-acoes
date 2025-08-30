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
            query = sqlalchemy.text("SELECT nome, senha_hash FROM usuarios WHERE email = :email")
            result = conn.execute(query, {"email": email}).first()
            if result:
                user_data = result
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        return False, None

    if user_data:
        nome_usuario, senha_hash_salva = user_data
        if pwd_context.verify(password, senha_hash_salva):
            return True, nome_usuario

    return False, None

# --- 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None

# --- 5. LÓGICA DA INTERFACE ---
if st.session_state.get("authentication_status"):
    # SE ESTIVER LOGADO, MOSTRA O DASHBOARD COMPLETO
    # (TODO O SEU CÓDIGO DO DASHBOARD VAI AQUI DENTRO)
    plt.style.use('seaborn-v0_8-darkgrid')
    # --- DADOS INICIAIS E MAPEAMENTOS ---
    DATA_PATH = "dados"

    MAPA_GERAL_ATIVOS = {**MAPA_ATIVOS, **MAPA_FIIS}  # Mapa dos setores

    # --- LÓGICA DINÂMICA PARA ENCONTRAR OS ATIVOS DISPONÍVEIS  E COMPATIVEL COM SETORES---
    try:
        # 1. Lê o nome de todos os arquivos na pasta de dados
        todos_arquivos = os.listdir(DATA_PATH)
        # 2. Filtra a lista para pegar apenas os arquivos de AÇÕES e FIIs (que terminam com .SA.csv)
        disponiveis = [arquivo.replace('.csv', '') for arquivo in todos_arquivos if arquivo.endswith('.SA.csv')]
        disponiveis.sort()  # Ordena a lista em ordem alfabética

        if not disponiveis:
            st.error(f"Nenhum arquivo de ativo (.SA.csv) encontrado na pasta '{DATA_PATH}'. Verifique os arquivos.")
            st.stop()  # Para a execução se não encontrar arquivos

    except FileNotFoundError:
        st.error(f"Pasta de dados '{DATA_PATH}' não encontrada. Verifique o caminho no código.")
        disponiveis = []  # Define uma lista vazia para evitar mais erros
        st.stop()

    MAPA_BENCHMARK = {'IBOVESPA': 'IBOV_BVSP.csv', 'IFIX': 'IFIX.SA.csv', 'IDIV': 'IDIV.SA.csv', 'CDI': 'CDI.csv',
                      'IPCA': 'IPCA.csv'}
    PREGOES_NO_ANO = 252
    TAXA_LIVRE_DE_RISCO = 0.105

    st.title('Dashboard de Análise de Carteiras 💼')

    st.sidebar.header('Definição da Carteira')

    # Cria uma lista padrão segura, pegando os 3 primeiros ativos da lista de disponíveis
    default_selection = disponiveis[:3] if len(disponiveis) >= 3 else disponiveis

    ativos_selecionados = st.sidebar.multiselect('Selecione os Ativos', disponiveis,
                                                 default=default_selection)
    st.sidebar.caption("Aviso: Esta ferramenta não constitui recomendação de investimento.")

    if 'resultados_otimizacao' not in st.session_state:
        st.session_state.resultados_otimizacao = None
    if 'ativos_otimizados' not in st.session_state:
        st.session_state.ativos_otimizados = []
    if 'gerar_analise_ia' not in st.session_state:
        st.session_state.gerar_analise_ia = False

    if sorted(st.session_state.ativos_otimizados) != sorted(ativos_selecionados):
        st.session_state.resultados_otimizacao = None
        st.session_state.gerar_analise_ia = False

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

        st.sidebar.subheader("Período de Análise")
        data_minima = df_portfolio_completo.index.min().date()
        data_maxima = df_portfolio_completo.index.max().date()
        data_inicio_default = data_maxima - timedelta(days=365)
        if data_inicio_default < data_minima:
            data_inicio_default = data_minima
        data_inicio = st.sidebar.date_input("Data de Início", value=data_inicio_default, min_value=data_minima,
                                            max_value=data_maxima, format="DD/MM/YYYY")
        data_fim = st.sidebar.date_input("Data de Fim", value=data_maxima, min_value=data_minima, max_value=data_maxima,
                                         format="DD/MM/YYYY")

        if data_inicio > data_fim:
            st.sidebar.error("A data de início não pode ser posterior à data de fim.")
            st.stop()

        data_inicio = pd.to_datetime(data_inicio)  # ← NOVA LINHA
        data_fim = pd.to_datetime(data_fim)  # ← NOVA LINHA
        df_portfolio = df_portfolio_completo.loc[data_inicio:data_fim]  # ← MODIFICADA

        pesos = []
        st.sidebar.subheader('Pesos da Carteira Atual (%)')
        for i, ativo in enumerate(ativos_selecionados):
            peso = st.sidebar.number_input(f'Peso para {ativo}', min_value=0.0, max_value=100.0,
                                           value=round(100 / len(ativos_selecionados), 2), step=1.0, key=f'peso_{i}')
            pesos.append(peso)

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
                fig_pizza = go.Figure(
                    data=[go.Pie(labels=ativos_selecionados, values=pesos, hole=.3, textinfo='label+percent')])
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

                fig_pizza = go.Figure(data=[
                    go.Pie(labels=list(pesos_setor.keys()), values=list(pesos_setor.values()), hole=.3,
                           textinfo='label+percent')])

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

        # --- Seção 2: Otimização de Markowitz ---
        with st.expander("Clique aqui para Otimização de Risco e Retorno (Markowitz)"):
            st.sidebar.subheader('Opções de Otimização')
            num_carteiras_simuladas = st.sidebar.slider('Número de Simulações', 1000, 20000, 5000, key='num_carteiras')

            if st.button('Otimizar Carteira'):
                st.session_state.gerar_analise_ia = False
                with st.spinner('Calculando milhares de portfólios... Por favor, aguarde.'):
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

            if 'resultados_otimizacao' in st.session_state and st.session_state.resultados_otimizacao is not None:
                if sorted(st.session_state.ativos_otimizados) == sorted(ativos_selecionados):
                    res = st.session_state.resultados_otimizacao
                    indice_max_sharpe = res['sharpe'].argmax()
                    pesos_otimos = res['pesos'][indice_max_sharpe]
                    indice_min_risco = res['risco'].argmin()

                    st.subheader('Resultados da Otimização')
                    # Bloco de código para ADICIONAR

                    # --- INÍCIO DO TEXTO EXPLICATIVO ---
                    st.info("""
                                    #### Entendendo o Gráfico de Markowitz

                                    * **O que é?** Uma teoria vencedora do Prêmio Nobel que provou matematicamente o velho ditado: "não coloque todos os ovos na mesma cesta". A ideia é que, ao combinar ativos diferentes, você pode reduzir o risco geral da sua carteira sem sacrificar muito do seu retorno.

                                    * **O que o gráfico significa?**
                                        * **Eixo Vertical (Retorno):** Quanto mais alto, melhor.
                                        * **Eixo Horizontal (Risco):** Quanto mais para a **esquerda**, melhor.
                                        * **Nuvem de Pontos:** Cada ponto é uma carteira possível com uma combinação de pesos diferente. A cor indica a qualidade (relação risco/retorno), sendo amarelo a melhor.
                                        * **Estrela Dourada (★):** A carteira "ótima", com o melhor equilíbrio entre risco e retorno.
                                        * **"X" Vermelho:** A carteira com o menor risco possível.

                                    * **Como usar?** Compare a posição dos ativos individuais (losangos) com as estrelas. O gráfico te ajuda a visualizar o poder da diversificação: ao combinar os ativos, é possível criar carteiras (as estrelas) que são melhores do que qualquer um dos ativos sozinhos.
                                    """)
                    # --- FIM DO TEXTO EXPLICATIVO ---
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
                        fig_pesos, ax_pesos = plt.subplots(figsize=(8, 5))
                        barras = ax_pesos.barh(df_pesos_otimos.index, df_pesos_otimos['Peso'],
                                               color=cores_ativos[:len(st.session_state.ativos_otimizados)])
                        ax_pesos.set_xlabel('Percentual (%)')
                        ax_pesos.set_title('Alocação por Ativo')
                        rotulos = [f'{p * 100:.1f}%' for p in df_pesos_otimos['Peso']]
                        ax_pesos.bar_label(barras, labels=rotulos, padding=3, fontsize=10)
                        ax_pesos.set_xlim(right=df_pesos_otimos['Peso'].max() * 1.25)
                        st.pyplot(fig_pesos)

                    st.markdown("---")
                    st.subheader('Métricas dos Ativos para Comparação')
                    df_metricas = pd.DataFrame({
                        'Retorno Anual': res['retornos_individuais'],
                        'Volatilidade': res['volatilidades_individuais']
                    }).reset_index().rename(columns={'index': 'Ativo'})
                    st.dataframe(df_metricas, column_config={
                        "Retorno Anual": st.column_config.ProgressColumn("Retorno Anual", format="%.2f%%", min_value=0),
                        "Volatilidade": st.column_config.ProgressColumn("Volatilidade", format="%.2f%%", min_value=0)
                    }, use_container_width=True, hide_index=True)

                    if st.button('Gerar Análise da Carteira com IA', key='ia_btn'):
                        st.session_state.gerar_analise_ia = True

                    if st.session_state.gerar_analise_ia:
                        with st.spinner('A IA do Gemini está analisando a carteira...'):
                            pesos_str = ", ".join([f"{t.replace('.SA', '')}: {p:.1%}" for t, p in
                                                   zip(st.session_state.ativos_otimizados, pesos_otimos)])
                            st.info('**Análise Qualitativa da Carteira Ótima (gerada por IA)**')
                            st.write(
                                f"A otimização matemática, buscando o maior retorno ajustado ao risco, sugeriu a alocação: **{pesos_str}**. Esta combinação busca o maior retorno ajustado ao risco, com base nos dados históricos. Ativos com maior peso provavelmente tiveram uma performance superior, enquanto os outros foram incluídos para otimizar a diversificação e reduzir o risco geral do portfólio.")
                else:
                    st.info(
                        "A seleção de ativos mudou. Por favor, clique em 'Otimizar Carteira' novamente para recalcular.")
    else:
        st.warning('Por favor, selecione pelo menos um ativo para a análise.')

else:
    # SE NÃO ESTIVER LOGADO, MOSTRA A TELA DE LOGIN
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Senha", type="password")

    st.warning('Por favor, insira seu usuário e senha para acessar')

    if st.sidebar.button("Entrar"):
        is_logged_in, user_name = check_login(email, password)
        if is_logged_in:
            st.session_state["authentication_status"] = True
            st.session_state["name"] = user_name
            st.rerun()
        else:
            st.session_state["authentication_status"] = False
            st.rerun()

    if st.session_state["authentication_status"] is False:
        st.sidebar.error("Email ou senha incorreta.")

