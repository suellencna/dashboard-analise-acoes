import os

# --- CONFIGURAÇÃO ---
PASTA_DE_DADOS = "dados"
ARQUIVO_MASTER_TICKERS = "lista_tickers.txt"

print("Iniciando validação da base de dados...")

try:
    # 1. Carrega a lista de tickers válidos
    with open(ARQUIVO_MASTER_TICKERS, 'r') as f:
        tickers_validos = {linha.strip() for linha in f if linha.strip()}
    print(f" -> Encontrados {len(tickers_validos)} tickers válidos na lista master.")

    # 2. Carrega a lista de arquivos .csv que temos atualmente
    arquivos_na_pasta = {f for f in os.listdir(PASTA_DE_DADOS) if f.endswith('.csv')}
    print(f" -> Encontrados {len(arquivos_na_pasta)} arquivos .csv na pasta '{PASTA_DE_DADOS}'.")

    # 3. Compara as duas listas para encontrar os arquivos que devem ser apagados
    # Converte a lista de tickers válidos para nomes de arquivos
    arquivos_validos = {ticker.replace('^', 'IBOV_') + '.csv' for ticker in tickers_validos}

    # Adiciona os benchmarks que não estão na lista do Fundamentus
    arquivos_validos.add("CDI.csv")
    arquivos_validos.add("IPCA.csv")

    # Encontra a diferença: arquivos que estão na pasta mas não na lista de válidos
    arquivos_para_apagar = arquivos_na_pasta - arquivos_validos

    if not arquivos_para_apagar:
        print("\nSUCESSO! Sua base de dados já está limpa e alinhada com a lista de tickers válidos.")
    else:
        print(f"\nENCONTRADOS {len(arquivos_para_apagar)} ARQUIVOS OBSOLETOS PARA APAGAR:")
        for arquivo in sorted(list(arquivos_para_apagar)):
            print(f" - {arquivo}")

        # 4. Pede a confirmação do usuário antes de apagar
        resposta = input("\nVocê confirma a exclusão desses arquivos? (s/n): ")

        if resposta.lower() == 's':
            print("\nIniciando limpeza...")
            for arquivo in arquivos_para_apagar:
                os.remove(os.path.join(PASTA_DE_DADOS, arquivo))
                print(f" - Arquivo '{arquivo}' apagado.")
            print("\nLimpeza concluída!")
        else:
            print("\nOperação cancelada pelo usuário.")

except FileNotFoundError:
    print(f"\nERRO: Arquivo '{ARQUIVO_MASTER_TICKERS}' não encontrado. Execute o 'gerador_lista_completa.py' primeiro.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")