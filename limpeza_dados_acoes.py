# limpeza_dados.py
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
# Caminho para a pasta com os 516 arquivos baixados pelo Colab
DATA_PATH = "G:/Meu Drive/DADOS_ACOES"

print(f"Iniciando limpeza e padronização dos arquivos em '{DATA_PATH}'...")

try:
    # Pega a lista de todos os arquivos na pasta
    todos_os_arquivos = os.listdir(DATA_PATH)
    # Filtra para processar apenas os arquivos CSV
    arquivos_csv = [f for f in todos_os_arquivos if f.endswith('.csv')]

    arquivos_processados = 0
    arquivos_com_erro = 0

    # Loop para processar cada arquivo CSV
    for nome_arquivo in arquivos_csv:
        caminho_completo = os.path.join(DATA_PATH, nome_arquivo)
        try:
            # --- O CORAÇÃO DA LIMPEZA ---
            # 1. Lê o arquivo, usando a primeira linha como cabeçalho (header=0)
            # 2. E o mais importante: pula a segunda linha (skiprows=[1]), que é a nossa "linha fantasma"
            df = pd.read_csv(caminho_completo, header=0, skiprows=[1])

            # 3. Garante que a primeira coluna se chame 'Date'
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

            # 4. Salva o arquivo limpo, sobrescrevendo o antigo
            df.to_csv(caminho_completo, index=False)

            print(f" -> Arquivo '{nome_arquivo}' limpo e salvo com sucesso.")
            arquivos_processados += 1

        except Exception as e:
            print(f" -> ERRO ao processar o arquivo '{nome_arquivo}'. Detalhe: {e}")
            arquivos_com_erro += 1

    print("\n--- Processo de Limpeza Finalizado ---")
    print(f"Total de arquivos processados: {arquivos_processados}")
    print(f"Total de arquivos com erro: {arquivos_com_erro}")

except FileNotFoundError:
    print(f"\nERRO: A pasta '{DATA_PATH}' não foi encontrada. Verifique o caminho.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")