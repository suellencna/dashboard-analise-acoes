import pandas as pd
import requests


def gerar_lista_final():
    """
    Busca todos os tickers de Ações e FIIs do Fundamentus e salva em um
    único arquivo de texto chamado 'lista_tickers.txt'.
    """
    lista_final = []

    # Busca Ações
    print("Buscando a lista de tickers de AÇÕES...")
    try:
        url_acoes = 'https://www.fundamentus.com.br/resultado.php'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response_acoes = requests.get(url_acoes, headers=headers)
        df_acoes = pd.read_html(response_acoes.text, decimal=',', thousands='.')[0]
        lista_final.extend([f"{ticker}.SA" for ticker in df_acoes['Papel'].tolist()])
        print(f" -> {len(df_acoes)} tickers de ações encontrados.")
    except Exception as e:
        print(f" -> FALHA ao buscar tickers de ações. Erro: {e}")

    # Busca FIIs
    print("\nBuscando a lista de tickers de FIIs...")
    try:
        url_fiis = 'https://www.fundamentus.com.br/fii_resultado.php'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response_fiis = requests.get(url_fiis, headers=headers)
        df_fiis = pd.read_html(response_fiis.text, decimal=',', thousands='.')[0]
        lista_final.extend([f"{ticker}.SA" for ticker in df_fiis['Papel'].tolist()])
        print(f" -> {len(df_fiis)} tickers de FIIs encontrados.")
    except Exception as e:
        print(f" -> FALHA ao buscar tickers de FIIs. Erro: {e}")

    # Salva a lista final em um arquivo de texto
    if lista_final:
        print(f"\nGerando o arquivo 'lista_tickers.txt' com {len(lista_final)} ativos no total...")
        with open('lista_tickers.txt', 'w', encoding='utf-8') as f:
            for ticker in sorted(list(set(lista_final))):  # Ordena e remove duplicatas
                f.write(f"{ticker}\n")
        print(" -> SUCESSO! Arquivo 'lista_tickers.txt' criado.")
    else:
        print(" -> NENHUM TICKER ENCONTRADO. O arquivo não foi gerado.")


if __name__ == '__main__':
    gerar_lista_final()