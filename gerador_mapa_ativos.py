import pandas as pd
import requests


def gerar_mapa_ativos_completo():
    """
    Acessa o site Fundamentus para obter a lista de todos os tickers da B3
    e seus respectivos setores, e então gera o código de um dicionário Python.
    """
    print("Buscando a lista completa de tickers e setores no site Fundamentus...")
    try:
        url = 'https://www.fundamentus.com.br/resultado.php'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)

        # O pandas lê a tabela HTML diretamente da página
        # Os parâmetros decimal e thousands são importantes para a leitura correta dos números
        tabelas = pd.read_html(response.text, decimal=',', thousands='.')
        df_tickers = tabelas[0]

        # --- LINHA DE DIAGNÓSTICO ---
        print("Colunas encontradas na tabela:", df_tickers.columns.tolist())
        # ---------------------------

        # Seleciona apenas as colunas que nos interessam
        df_mapa = df_tickers[['Papel', 'Setor']].copy()

        print(f" -> SUCESSO! {len(df_mapa)} ativos e setores encontrados.")
        print("\nGerando o código do dicionário MAPA_ATIVOS...")

        # --- GERADOR DE CÓDIGO PARA O app.py ---
        print("\n" + "=" * 50)
        print("COPIE E COLE O BLOCO DE CÓDIGO ABAIXO NO SEU app.py")
        print("=" * 50 + "\n")

        print("MAPA_ATIVOS = {")
        for index, row in df_mapa.iterrows():
            ticker = row['Papel']
            setor = row['Setor']
            # Adiciona o sufixo '.SA' e escapa aspas simples, se houver
            setor_escaped = setor.replace("'", "\\'")
            print(f"    '{ticker}.SA': {{'setor': '{setor_escaped}'}},")
        print("}")

        print("\n" + "=" * 50)
        print("CÓDIGO GERADO COM SUCESSO!")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f" -> FALHA ao gerar o mapa de ativos. Erro: {e}")


# Executa a função
if __name__ == '__main__':
    gerar_mapa_ativos_completo()