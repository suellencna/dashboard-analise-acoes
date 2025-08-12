import yfinance as yf
import pandas as pd
import os
import requests
from bcb import sgs

# --- CONFIGURAÇÃO ---
# No ambiente do GitHub, os dados são salvos na pasta 'dados' do projeto
DATA_PATH = "dados"


# --- FUNÇÃO PARA OBTER TICKERS (AÇÕES OU FIIs) ---
def obter_tickers_fundamentus(tipo='acoes'):
    """
    Busca a lista de tickers de ações ou FIIs do site Fundamentus.
    """
    subdominio = 'resultado' if tipo == 'acoes' else 'fii_resultado'
    print(f"Buscando a lista de tickers de {tipo}...")
    try:
        url = f'https://www.fundamentus.com.br/{subdominio}.php'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        df_tickers = pd.read_html(response.text, decimal=',', thousands='.')[0]
        tickers = [f"{ticker}.SA" for ticker in df_tickers['Papel'].tolist()]
        print(f" -> {len(tickers)} tickers de {tipo} encontrados.")
        return tickers
    except Exception as e:
        print(f" -> FALHA ao buscar tickers de {tipo}. Erro: {e}")
        return []


# --- FUNÇÃO PARA COLETAR DADOS DO YFINANCE ---
def coletar_dados_yfinance(tickers, pasta_destino):
    """
    Baixa o histórico de uma lista de tickers e salva em formato padronizado.
    """
    for ticker in tickers:
        print(f"Buscando yfinance para: {ticker}...")
        try:
            dados = yf.download(ticker, start='2020-01-01', progress=False)
            if dados.empty: continue

            dados.reset_index(inplace=True)
            dados_padronizados = dados[['Date', 'Close']]

            nome_base = ticker.replace('^', 'IBOV_')
            nome_arquivo = f"{nome_base}.csv"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)

            dados_padronizados.to_csv(caminho_completo, index=False)
            print(f" -> SUCESSO! Dados de {ticker} salvos.")
        except Exception as e:
            print(f" -> FALHA ao buscar dados para {ticker}. Erro: {e}")


# --- FUNÇÃO PARA COLETAR DADOS DO BANCO CENTRAL ---
def coletar_dados_bcb(pasta_destino):
    """
    Busca dados de CDI e IPCA do Banco Central do Brasil.
    """
    codigos_bcb = {'CDI': 12, 'IPCA': 1178.94}
    for nome, codigo in codigos_bcb.items():
        print(f"Buscando BCB para: {nome}...")
        try:
            dados = sgs.get({nome: codigo}, start='2020-01-01')
            dados.rename(columns={nome: 'Close'}, inplace=True)
            dados.reset_index(inplace=True)
            dados.rename(columns={'index': 'Date'}, inplace=True)
            dados.to_csv(os.path.join(pasta_destino, f"{nome}.csv"), index=False)
            print(f" -> SUCESSO! Dados de {nome} salvos.")
        except Exception as e:
            print(f" -> FALHA ao buscar dados para {nome}. Erro: {e}")


# --- EXECUÇÃO PRINCIPAL DO PIPELINE ---
if __name__ == '__main__':
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    # Coleta de Tickers
    tickers_acoes = obter_tickers_fundamentus(tipo='acoes')
    tickers_fiis = obter_tickers_fundamentus(tipo='fiis')
    tickers_benchmarks_yf = ["^BVSP", "IFIX.SA", "IDIV.SA"]
    todos_tickers_yf = list(set(tickers_acoes + tickers_fiis + tickers_benchmarks_yf))

    # Coleta de Dados Históricos
    coletar_dados_yfinance(todos_tickers_yf, DATA_PATH)

    # Coleta de Indicadores do BCB
    coletar_dados_bcb(DATA_PATH)

    print("\nPipeline de dados finalizado!")