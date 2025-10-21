#!/usr/bin/env python3
"""
Script para coletar dados históricos do IFIX e IDIV automaticamente
Substitui o download manual do Investing.com
"""

import investpy
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO ---
PASTA_OUTPUT = "dados"
ANOS_HISTORICO = 10

# Mapear índices do investpy para nossos nomes de arquivo
INDICES_CONFIG = {
    'BM&FBOVESPA Real Estate IFIX': 'IFIX.SA.csv',
    'Bovespa Dividend': 'IDIV.SA.csv'
}

print("=" * 70)
print("📊 COLETA AUTOMÁTICA DE DADOS - IFIX E IDIV")
print("=" * 70)
print(f"Período: Últimos {ANOS_HISTORICO} anos")
print(f"Destino: {PASTA_OUTPUT}/")
print()

# Criar pasta de destino se não existir
if not os.path.exists(PASTA_OUTPUT):
    os.makedirs(PASTA_OUTPUT)
    print(f"✅ Pasta '{PASTA_OUTPUT}' criada")

# Calcular datas
end_date = datetime.now()
start_date = end_date - timedelta(days=ANOS_HISTORICO * 365)

# Formatar datas para o investpy (dd/mm/yyyy)
end_str = end_date.strftime('%d/%m/%Y')
start_str = start_date.strftime('%d/%m/%Y')

print(f"📅 Período de coleta: {start_str} até {end_str}")
print()

# Processar cada índice
for index_name, output_filename in INDICES_CONFIG.items():
    print(f"🔄 Processando: {index_name}...")
    
    try:
        # Baixar dados históricos
        df = investpy.get_index_historical_data(
            index=index_name,
            country='brazil',
            from_date=start_str,
            to_date=end_str
        )
        
        # Resetar o índice para transformar Date em coluna
        df = df.reset_index()
        
        # Selecionar apenas as colunas necessárias (Date e Close)
        df_limpo = df[['Date', 'Close']].copy()
        
        # Garantir que a data está no formato correto
        df_limpo['Date'] = pd.to_datetime(df_limpo['Date'])
        
        # Caminho completo do arquivo de saída
        caminho_output = os.path.join(PASTA_OUTPUT, output_filename)
        
        # Salvar arquivo CSV
        df_limpo.to_csv(caminho_output, index=False)
        
        print(f"   ✅ {output_filename}")
        print(f"      📊 {len(df_limpo)} registros salvos")
        print(f"      📅 De {df_limpo['Date'].min().strftime('%d/%m/%Y')} até {df_limpo['Date'].max().strftime('%d/%m/%Y')}")
        print(f"      💰 Último fechamento: R$ {df_limpo['Close'].iloc[-1]:.2f}")
        print()
        
    except Exception as e:
        print(f"   ❌ ERRO ao processar {index_name}")
        print(f"      Detalhe: {e}")
        print()

print("=" * 70)
print("🎉 COLETA FINALIZADA!")
print("=" * 70)
print()
print("ℹ️  Os arquivos foram salvos em:", os.path.abspath(PASTA_OUTPUT))
print("ℹ️  Você pode deletar a pasta 'downloads_brutos' se desejar")
print()
print("💡 DICA: Agende este script para rodar automaticamente:")
print("   - No Mac/Linux: use cron")
print("   - No Windows: use Agendador de Tarefas")
print("   - No Render: adicione como job periódico no render.yaml")

