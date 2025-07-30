# Bloco de código NOVO E CORRIGIDO para o início do app.py

import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# --- Configurações da Página e Estilo ---
st.set_page_config(
    page_title="Análise de Carteira",
    page_icon="💼",
    layout="wide"
)
plt.style.use('seaborn-v0_8-darkgrid')

# --- Bloco de Carregamento e Configuração Dinâmica ---

# Bloco de código NOVO E CORRIGIDO

# --- Bloco de Carregamento e Configuração Dinâmica ---
DATA_PATH = "dados"

# Tenta ler a lista de arquivos da pasta de dados
try:
    todos_arquivos = os.listdir(DATA_PATH)

    # A CORREÇÃO ESTÁ AQUI: adicionamos .replace('.csv', '') para remover a extensão do nome de cada arquivo
    disponiveis = [arquivo.replace('.csv', '') for arquivo in todos_arquivos if arquivo.endswith('.SA.csv')]
    disponiveis.sort()

    if not disponiveis:
        st.error("Nenhum arquivo de ação (.SA.csv) encontrado na pasta de dados.")
        st.stop()

except FileNotFoundError:
    st.error(f"Pasta de dados '{DATA_PATH}' não encontrada. Verifique o caminho e a sincronização do Google Drive.")
    st.stop()  # st.stop() é mais limpo que usar exit() em apps Streamlit

# Dicionários de mapeamento e constantes
MAPA_ATIVOS = {
    'ABEV3.SA': {'setor': 'Consumo Não Cíclico'},
    'AZUL4.SA': {'setor': 'Bens Industriais'},
    'B3SA3.SA': {'setor': 'Financeiro'},
    'BBAS3.SA': {'setor': 'Financeiro'},
    'BBDC3.SA': {'setor': 'Financeiro'},
    'BBDC4.SA': {'setor': 'Financeiro'},
    'BBSE3.SA': {'setor': 'Financeiro'},
    'BEEF3.SA': {'setor': 'Consumo Não Cíclico'},
    'BPAC11.SA': {'setor': 'Financeiro'},
    'BRAP4.SA': {'setor': 'Materiais Básicos'},
    'BRFS3.SA': {'setor': 'Consumo Não Cíclico'},
    'BRKM5.SA': {'setor': 'Materiais Básicos'},
    'CCRO3.SA': {'setor': 'Bens Industriais'},
    'CIEL3.SA': {'setor': 'Financeiro'},
    'CMIG4.SA': {'setor': 'Utilidade Pública'},
    'COGN3.SA': {'setor': 'Consumo Cíclico'},
    'CPFE3.SA': {'setor': 'Utilidade Pública'},
    'CRFB3.SA': {'setor': 'Consumo Não Cíclico'},
    'CSAN3.SA': {'setor': 'Petróleo'},
    'CSNA3.SA': {'setor': 'Materiais Básicos'},
    'CVCB3.SA': {'setor': 'Consumo Cíclico'},
    'CYRE3.SA': {'setor': 'Consumo Cíclico'},
    'ECOR3.SA': {'setor': 'Bens Industriais'},
    'EGIE3.SA': {'setor': 'Utilidade Pública'},
    'ELET3.SA': {'setor': 'Utilidade Pública'},
    'ELET6.SA': {'setor': 'Utilidade Pública'},
    'EMBR3.SA': {'setor': 'Bens Industriais'},
    'ENGI11.SA': {'setor': 'Utilidade Pública'},
    'EQTL3.SA': {'setor': 'Utilidade Pública'},
    'FLRY3.SA': {'setor': 'Saúde'},
    'GGBR4.SA': {'setor': 'Materiais Básicos'},
    'GOAU4.SA': {'setor': 'Materiais Básicos'},
    'GOLL4.SA': {'setor': 'Bens Industriais'},
    'HAPV3.SA': {'setor': 'Saúde'},
    'HYPE3.SA': {'setor': 'Saúde'},
    'IRBR3.SA': {'setor': 'Financeiro'},
    'ITSA4.SA': {'setor': 'Financeiro'},
    'ITUB4.SA': {'setor': 'Financeiro'},
    'JBSS3.SA': {'setor': 'Consumo Não Cíclico'},
    'KLBN11.SA': {'setor': 'Materiais Básicos'},
    'LREN3.SA': {'setor': 'Consumo Cíclico'},
    'MGLU3.SA': {'setor': 'Consumo Cíclico'},
    'MRFG3.SA': {'setor': 'Consumo Não Cíclico'},
    'MRVE3.SA': {'setor': 'Consumo Cíclico'},
    'MULT3.SA': {'setor': 'Consumo Cíclico'},
    'NTCO3.SA': {'setor': 'Consumo Não Cíclico'},
    'PCAR3.SA': {'setor': 'Consumo Não Cíclico'},
    'PETR3.SA': {'setor': 'Petróleo'},
    'PETR4.SA': {'setor': 'Petróleo'},
    'PRIO3.SA': {'setor': 'Petróleo'},
    'QUAL3.SA': {'setor': 'Saúde'},
    'RADL3.SA': {'setor': 'Consumo Não Cíclico'},
    'RAIL3.SA': {'setor': 'Bens Industriais'},
    'RENT3.SA': {'setor': 'Consumo Cíclico'},
    'SANB11.SA': {'setor': 'Financeiro'},
    'SBSP3.SA': {'setor': 'Utilidade Pública'},
    'SULA11.SA': {'setor': 'Saúde'},
    'SUZB3.SA': {'setor': 'Materiais Básicos'},
    'TAEE11.SA': {'setor': 'Utilidade Pública'},
    'TIMS3.SA': {'setor': 'Comunicações'},
    'TOTS3.SA': {'setor': 'Tecnologia da Informação'},
    'UGPA3.SA': {'setor': 'Petróleo'},
    'USIM5.SA': {'setor': 'Materiais Básicos'},
    'VALE3.SA': {'setor': 'Materiais Básicos'},
    'VIVT3.SA': {'setor': 'Comunicações'},
    'VVAR3.SA': {'setor': 'Consumo Cíclico'},
    'WEGE3.SA': {'setor': 'Bens Industriais'},
    'YDUQ3.SA': {'setor': 'Consumo Cíclico'}
}

MAPA_BENCHMARK = {'IBOVESPA': 'IBOV_BVSP.csv', 'IFIX': 'IFIX.SA.csv', 'IDIV': 'IDIV.SA.csv', 'CDI': 'CDI.csv',
                  'IPCA': 'IPCA.csv'}
PREGOES_NO_ANO = 252
TAXA_LIVRE_DE_RISCO = 0.105

# --- TÍTULO ---
st.title('Dashboard de Análise de Carteiras 💼')

# --- O restante do seu código (BARRA LATERAL, LÓGICA PRINCIPAL, etc.) continua daqui... ---

# --- BARRA LATERAL ---
st.sidebar.header('Definição da Carteira')
ativos_selecionados = st.sidebar.multiselect('Selecione os Ativos', disponiveis,
                                             default=['PETR4.SA', 'WEGE3.SA', 'ITUB4.SA'])
st.sidebar.caption("Aviso: Esta ferramenta não constitui recomendação de investimento.")

# --- LÓGICA PRINCIPAL ---
# Bloco NOVO e CORRIGIDO
if len(ativos_selecionados) >= 2:
    # Bloco de código NOVO E CORRIGIDO
    try:
        lista_dfs = []
        for ativo in ativos_selecionados:
            caminho_arquivo = os.path.join(DATA_PATH, f"{ativo}.csv")
            df_ativo = pd.read_csv(caminho_arquivo, index_col='Date', parse_dates=True)
            # Renomeia a coluna 'Close' para o nome do ticker
            df_ativo.rename(columns={'Close': ativo}, inplace=True)
            lista_dfs.append(df_ativo)

        # Concatena todos os DataFrames em um único
        df_portfolio = pd.concat(lista_dfs, axis=1)

        # AQUI ESTÁ A CORREÇÃO: Garante que todos os dados são numéricos
        # errors='coerce' transforma qualquer texto que não seja número em um valor vazio
        df_portfolio = df_portfolio.apply(pd.to_numeric, errors='coerce')
        # Remove linhas que possam ter tido erros de conversão
        df_portfolio.dropna(inplace=True)

    except Exception as e:
        st.error(f"Ocorreu um erro ao ler ou processar os arquivos de dados dos ativos: {e}")
        st.stop()

    except FileNotFoundError:
        st.error(f"Erro: Arquivo não encontrado na pasta '{DATA_PATH}'. Verifique se o Google Drive está sincronizado e o caminho está correto.")
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler os arquivos de dados dos ativos: {e}")
        st.stop()



    # O resto do código continua daqui...
    except FileNotFoundError:
        st.error(
            f"Erro: Arquivo não encontrado na pasta '{DATA_PATH}'. Verifique se o Google Drive está sincronizado e o caminho está correto.")
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler os arquivos de dados: {e}")
        st.stop()

    # Restante da lógica do aplicativo
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

    # Esta linha agora funcionará, pois df_portfolio contém apenas números
    df_portfolio['Carteira'] = (df_portfolio[ativos_selecionados] * pesos).sum(axis=1)

    # --- Seção 1: Análise da Carteira Atual ---
    # ... (O restante do código para exibir os gráficos e a otimização continua o mesmo) ...
    # (Por favor, use a última versão completa que funcionou visualmente para o restante do arquivo)

#else:
    #st.warning('Por favor, selecione pelo menos dois ativos para a análise.')

    # --- Seção 1: Análise da Carteira Atual ---
    st.header("Análise da Carteira Definida pelo Usuário")
    col1, col2 = st.columns(2)
    # Bloco de código NOVO E CORRIGIDO

    with col1:
        st.subheader('Composição da Carteira')
        visao_pizza = st.radio("Visualizar por:", ('Ativo', 'Setor'), horizontal=True, key='visao_pizza')

        if visao_pizza == 'Ativo':
            fig_pizza = go.Figure(
                data=[go.Pie(labels=ativos_selecionados, values=pesos, hole=.3, textinfo='label+percent')])
        else:  # Lógica para visão por Setor
            pesos_setor = {}
            for ativo, peso in zip(ativos_selecionados, pesos):
                # --- AQUI ESTÁ A CORREÇÃO ---
                # Usamos .get() para uma busca segura no dicionário.
                # Se o 'ativo' não for encontrado no MAPA_ATIVOS, ele retorna um valor padrão: {'setor': 'Outros'}.
                info_ativo = MAPA_ATIVOS.get(ativo, {'setor': 'Outros'})
                setor = info_ativo['setor']

                # O resto da lógica para somar os pesos continua igual
                if setor in pesos_setor:
                    pesos_setor[setor] += peso
                else:
                    pesos_setor[setor] = peso

            fig_pizza = go.Figure(data=[
                go.Pie(labels=list(pesos_setor.keys()), values=list(pesos_setor.values()), hole=.3,
                       textinfo='label+percent')])

        st.plotly_chart(fig_pizza, use_container_width=True)

    # Bloco NOVO e CORRIGIDO (à prova de falhas)

    with col2:
        st.subheader('Carteira vs. Benchmark')
        benchmark_selecionado = st.selectbox("Selecione o Benchmark:", list(MAPA_BENCHMARK.keys()))
        caminho_bench = os.path.join(DATA_PATH, MAPA_BENCHMARK[benchmark_selecionado])

        try:
            df_bench = pd.read_csv(caminho_bench, index_col='Date', parse_dates=True, skiprows=[1])
            df_bench = df_bench.reindex(df_portfolio.index).ffill().dropna()

            # Cria um DataFrame com os valores da carteira e do benchmark
            df_comparativo = pd.DataFrame({
                'Carteira': df_portfolio['Carteira'],
                'Benchmark': df_bench['Close']
            })

            # Calcula o retorno diário de cada um
            retornos_diarios = df_comparativo.pct_change().dropna()

            # --- NOVA VERIFICAÇÃO DE SEGURANÇA ---
            # Se, após todos os tratamentos, não houver dados suficientes para calcular o retorno, avisa o usuário
            if retornos_diarios.empty or len(retornos_diarios) < 2:
                st.warning(
                    f"Dados insuficientes para o benchmark '{benchmark_selecionado}' no período selecionado para gerar o gráfico.")
            else:
                # Calcula o retorno acumulado, começando de uma base 100
                df_acumulado = (1 + retornos_diarios).cumprod() * 100
                df_acumulado.iloc[0] = 100  # Garante que o primeiro valor é exatamente 100

                # Cria o gráfico com os dados acumulados
                fig_desempenho = go.Figure()
                fig_desempenho.add_trace(
                    go.Scatter(x=df_acumulado.index, y=df_acumulado['Carteira'], mode='lines', name='Minha Carteira'))
                fig_desempenho.add_trace(go.Scatter(x=df_acumulado.index, y=df_acumulado['Benchmark'], mode='lines',
                                                    name=benchmark_selecionado))
                fig_desempenho.update_layout(title_text='Desempenho Comparativo (Retorno Acumulado)',
                                             template='plotly_dark')
                st.plotly_chart(fig_desempenho, use_container_width=True)

        except Exception as e:
            st.error(
                f"Não foi possível carregar ou processar os dados do benchmark '{benchmark_selecionado}'. Verifique o arquivo .csv. Erro: {e}")

    st.markdown("---")

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