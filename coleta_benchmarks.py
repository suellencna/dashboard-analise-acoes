# coleta_benchmarks.py
from bcb import sgs
import os
import pandas as pd

print("Iniciando coleta de dados do Banco Central do Brasil...")

DATA_PATH = "G:/Meu Drive/DADOS_ACOES" # Use o mesmo caminho do seu app.py

# Dicionário com os códigos de cada indicador no sistema do BCB
codigos_bcb = {
    'CDI': 12,    # Taxa SELIC diária, usada como proxy do CDI
    'IPCA': 433   # IPCA mensal
}

for nome, codigo in codigos_bcb.items():
    print(f"Buscando dados para: {nome}...")
    try:
        # Busca a série temporal no BCB a partir de 2020
        dados = sgs.get({'codigo': codigo}, start='2020-01-01')

        # Renomeia a coluna de valor para 'Close' para manter nosso padrão
        dados.rename(columns={'codigo': 'Close'}, inplace=True)

        caminho_arquivo = os.path.join(DATA_PATH, f"{nome}.csv")
        dados.to_csv(caminho_arquivo)
        print(f" -> SUCESSO! Arquivo '{nome}.csv' salvo em '{DATA_PATH}'")

    except Exception as e:
        print(f" -> FALHA ao buscar dados para {nome}. Erro: {e}")

print("\nColeta de benchmarks finalizada!")