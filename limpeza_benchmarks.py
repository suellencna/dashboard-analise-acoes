# limpeza_benchmarks.py
import pandas as pd
import os

# --- CONFIGURAÇÃO ---

# Pasta onde você coloca os arquivos baixados do Investing.com
PASTA_INPUT = "downloads_brutos"

# Pasta de destino dos arquivos limpos (a mesma que o app.py usa)
PASTA_OUTPUT = "dados"

# Dicionário para mapear o nome do arquivo baixado para o nosso nome padrão
# Se o nome do arquivo baixado for diferente, apenas ajuste aqui.
MAPEAMENTO_ARQUIVOS = {
    "IFIX.csv": "IFIX.SA.csv",
    "IDIV.csv": "IDIV.SA.csv"
    # Adicione mais arquivos aqui se precisar no futuro
}

print("Iniciando processo de limpeza e padronização de dados...")

# --- LÓGICA DE LIMPEZA ---

# Verifica se a pasta de destino existe, se não, cria
if not os.path.exists(PASTA_OUTPUT):
    os.makedirs(PASTA_OUTPUT)

# Loop para processar cada arquivo no nosso mapeamento
for nome_arquivo_bruto, nome_arquivo_limpo in MAPEAMENTO_ARQUIVOS.items():

    caminho_input = os.path.join(PASTA_INPUT, nome_arquivo_bruto)
    caminho_output = os.path.join(PASTA_OUTPUT, nome_arquivo_limpo)

    print(f"\nProcessando o arquivo: {nome_arquivo_bruto}...")

    try:
        # 1. Carrega o arquivo CSV "sujo"
        df = pd.read_csv(caminho_input)

        # 2. Seleciona apenas as colunas que nos interessam
        df_limpo = df[['Data', 'Último']]

        # 3. Renomeia as colunas para o nosso padrão ("Date" e "Close")
        df_limpo = df_limpo.rename(columns={'Data': 'Date', 'Último': 'Close'})

        # 4. Converte a coluna de data para o formato correto (Ano-Mês-Dia)
        # O format='%d.%m.%Y' ensina o pandas a ler datas como "25.07.2025"
        df_limpo['Date'] = pd.to_datetime(df_limpo['Date'], format='%d.%m.%Y')

        # 5. Limpa e converte a coluna de preços para o formato numérico correto
        # Remove o separador de milhares '.'
        df_limpo['Close'] = df_limpo['Close'].str.replace('.', '', regex=False)
        # Substitui a vírgula decimal por um ponto decimal
        df_limpo['Close'] = df_limpo['Close'].str.replace(',', '.', regex=False)
        # Converte a coluna de texto para número (float)
        df_limpo['Close'] = df_limpo['Close'].astype(float)

        # 6. Salva o novo arquivo limpo e padronizado na pasta de destino
        df_limpo.to_csv(caminho_output, index=False)

        print(f" -> SUCESSO! Arquivo '{nome_arquivo_limpo}' salvo em '{PASTA_OUTPUT}'")

    except FileNotFoundError:
        print(f" -> ERRO: Arquivo '{nome_arquivo_bruto}' não encontrado na pasta '{PASTA_INPUT}'.")
    except Exception as e:
        print(f" -> ERRO ao processar o arquivo. Detalhe: {e}")

print("\nLimpeza de dados finalizada!")