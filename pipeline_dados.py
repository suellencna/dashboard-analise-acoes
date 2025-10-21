import yfinance as yf
import pandas as pd
import os
from bcb import sgs

DATA_PATH = "dados"

def ler_lista_tickers(caminho_arquivo="lista_tickers.txt"):
    """Lê a lista de tickers de um arquivo de texto."""
    print(f"Lendo a lista de tickers do arquivo '{caminho_arquivo}'...")
    try:
        with open(caminho_arquivo, 'r') as f:
            tickers = [linha.strip() for linha in f if linha.strip()]
        print(f" -> {len(tickers)} tickers encontrados na lista.")
        return tickers
    except FileNotFoundError:
        print(f" -> ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
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

    tickers_a_buscar = ler_lista_tickers()
    if not tickers_a_buscar:
        raise RuntimeError("Lista de tickers está vazia. Processo interrompido.")

    tickers_benchmarks_yf = ["^BVSP"]
    todos_tickers_yf = list(set(tickers_a_buscar + tickers_benchmarks_yf))

    coletar_dados_yfinance(todos_tickers_yf, DATA_PATH)
    coletar_dados_bcb(DATA_PATH)

    print("\nPipeline de dados finalizado!")