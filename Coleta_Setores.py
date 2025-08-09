import pandas as pd

# Caminho do arquivo
caminho_arquivo = "Relatório_Geral_07_08_2025 (português).xlsx"

# Carregar a planilha
df = pd.read_excel(caminho_arquivo, sheet_name="Planilha")

# Visualizar as colunas disponíveis
print(df.columns)

# Filtrar apenas as colunas relevantes, assumindo que sejam "Código de Negociação" e "Subsetor"
df_filtrado = df[['Código de Negociação', 'Subsetor']].dropna()

# Adicionar o sufixo '.SA' ao ticker
df_filtrado['Ticker'] = df_filtrado['Código de Negociação'].astype(str).str.upper() + '.SA'
df_filtrado['Setor'] = df_filtrado['Subsetor'].str.strip()

# Criar o dicionário
mapa_ativos = {
    row['Ticker']: {'setor': row['Setor']} for _, row in df_filtrado.iterrows()
}

# Exemplo de exibição
for i, (k, v) in enumerate(mapa_ativos.items()):
    print(f"'{k}': {v},", end=' ')
    if (i + 1) % 5 == 0:
        print()  # quebra de linha a cada 5 itens

# (Opcional) Salvar em arquivo Python
with open('mapa_ativos.py', 'w', encoding='utf-8') as f:
    f.write("MAPA_ATIVOS = {\n")
    for ticker, info in mapa_ativos.items():
        f.write(f"    '{ticker}': {{'setor': '{info['setor']}'}}," + "\n")
    f.write("}")
