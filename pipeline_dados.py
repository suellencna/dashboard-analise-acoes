import yfinance as yf
import pandas as pd
import os
import requests
from bcb import sgs
from io import StringIO  # Usado para ler texto como se fosse um arquivo

# --- CONFIGURAÇÃO ---
DATA_PATH = "dados"


# --- FUNÇÃO ROBUSTA PARA OBTER TICKERS (AÇÕES OU FIIs) ---
def obter_tickers_fundamentus(tipo='acoes'):
    subdominio = 'resultado' if tipo == 'acoes' else 'fii_resultado'
    print(f"Buscando a lista de tickers de {tipo}...")
    try:
        url = f'https://www.fundamentus.com.br/{subdominio}.php'

        # Cabeçalhos que imitam um navegador comum
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Usamos uma sessão para a requisição
        with requests.Session() as s:
            response = s.get(url, headers=headers)
            response.raise_for_status()  # Lança um erro se a requisição falhar (ex: 404, 500)

            # Usamos StringIO para garantir que o pandas leia o texto corretamente
            tabela = pd.read_html(StringIO(response.text), decimal=',', thousands='.')[0]

        tickers = [f"{ticker}.SA" for ticker in tabela['Papel'].tolist()]
        print(f" -> SUCESSO! {len(tickers)} tickers de {tipo} encontrados.")
        return tickers
    except Exception as e:
        print(f" -> FALHA ao buscar tickers de {tipo}. Erro: {e}")
        return []


# --- FUNÇÃO PARA COLETAR DADOS DO YFINANCE ---
def coletar_dados_yfinance(tickers, pasta_destino):
    for ticker in tickers:
        print(f"Buscando yfinance para: {ticker}...")
        try:
            dados = yf.download(ticker, start='2020-01-01', progress=False)
            if dados.empty:
                print(f" -> Alerta: Nenhum dado retornado para {ticker}. Pulando.")
                continue

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

    tickers_acoes = obter_tickers_fundamentus(tipo='acoes')
    tickers_fiis = obter_tickers_fundamentus(tipo='fiis')

    if not tickers_acoes and not tickers_fiis:
        raise RuntimeError("Não foi possível obter a lista de tickers de ações e FIIs. Processo interrompido.")

    tickers_benchmarks_yf = ["^BVSP", "IFIX.SA", "IDIV.SA"]
    todos_tickers_yf = list(set(tickers_acoes + tickers_fiis + tickers_benchmarks_yf))

    coletar_dados_yfinance(todos_tickers_yf, DATA_PATH)
    coletar_dados_bcb(DATA_PATH)

    print("\nPipeline de dados finalizado!")