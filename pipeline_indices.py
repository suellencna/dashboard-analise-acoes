#!/usr/bin/env python3
"""
Pipeline de Coleta de Índices - IFIX e IDIV
Arquivo separado para coleta de dados do IFIX e IDIV usando investpy
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import random

# Tentar importar investpy, mas continuar se não estiver disponível
try:
    import investpy
    INVESTPY_AVAILABLE = True
except ImportError:
    print("⚠️ Aviso: investpy não disponível. Instale com: pip install investpy")
    INVESTPY_AVAILABLE = False

# --- CONFIGURAÇÃO ---
PASTA_OUTPUT = "dados"
ANOS_HISTORICO = 10
MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos

print("=" * 80)
print("🚀 PIPELINE DE COLETA DE ÍNDICES - IFIX E IDIV")
print("=" * 80)
print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"📁 Pasta de destino: {PASTA_OUTPUT}/")
print(f"📊 Período: Últimos {ANOS_HISTORICO} anos")
print()

# Criar pasta de destino se não existir
if not os.path.exists(PASTA_OUTPUT):
    os.makedirs(PASTA_OUTPUT)
    print(f"✅ Pasta '{PASTA_OUTPUT}' criada")

# Calcular período
end_date = datetime.now()
start_date = end_date - timedelta(days=ANOS_HISTORICO * 365)

print(f"📅 Período: {start_date.strftime('%d/%m/%Y')} até {end_date.strftime('%d/%m/%Y')}")
print()

def coletar_ifix_idiv():
    """Coleta dados do IFIX e IDIV usando investpy com retry logic"""
    if not INVESTPY_AVAILABLE:
        print("⚠️ investpy não disponível, pulando coleta de IFIX/IDIV...")
        return False
    
    print("🔄 Coletando dados do IFIX e IDIV...")
    
    # Mapear índices do investpy para nossos nomes de arquivo
    indices_config = {
        'BM&FBOVESPA Real Estate IFIX': 'IFIX.SA.csv',
        'Bovespa Dividend': 'IDIV.SA.csv'
    }
    
    # Formatar datas para o investpy (dd/mm/yyyy)
    end_str = end_date.strftime('%d/%m/%Y')
    start_str = start_date.strftime('%d/%m/%Y')
    
    sucessos = 0
    falhas = 0
    
    for index_name, output_filename in indices_config.items():
        print(f"  📊 Coletando {index_name}...")
        
        tentativa = 0
        sucesso_index = False
        
        while tentativa < MAX_RETRIES and not sucesso_index:
            try:
                if tentativa > 0:
                    delay = RETRY_DELAY * 2 + random.uniform(0, 2)  # Delay maior para investpy
                    print(f"    🔄 Tentativa {tentativa + 1}/{MAX_RETRIES} em {delay:.1f}s...")
                    time.sleep(delay)
                
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
                df_limpo['Date'] = df_limpo['Date'].dt.strftime('%Y-%m-%d')
                
                # Caminho completo do arquivo de saída
                caminho_output = os.path.join(PASTA_OUTPUT, output_filename)
                
                # Salvar arquivo CSV
                df_limpo.to_csv(caminho_output, index=False)
                
                print(f"    ✅ {output_filename}: {len(df_limpo)} registros")
                sucessos += 1
                sucesso_index = True
                
            except Exception as e:
                tentativa += 1
                error_msg = str(e)
                
                if "ERR#0015" in error_msg or "error 403" in error_msg:
                    print(f"    ⚠️ {index_name}: Erro 403 - Rate limit do investpy")
                    if tentativa < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * 3)  # Delay ainda maior para 403
                        continue
                    else:
                        print(f"    ❌ {index_name}: Falha após {MAX_RETRIES} tentativas - Rate limit")
                        break
                elif tentativa < MAX_RETRIES:
                    print(f"    ⚠️ {index_name}: Erro na tentativa {tentativa} - {error_msg}")
                    continue
                else:
                    print(f"    ❌ {index_name}: Falha após {MAX_RETRIES} tentativas - {error_msg}")
                    break
        
        if not sucesso_index:
            falhas += 1
    
    print(f"✅ IFIX/IDIV: {sucessos} sucessos, {falhas} falhas")
    return sucessos > 0

def gerar_arquivo_status():
    """Gera arquivo de status da coleta de índices"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'pasta_dados': PASTA_OUTPUT,
        'periodo_inicio': start_date.isoformat(),
        'periodo_fim': end_date.isoformat(),
        'investpy_disponivel': INVESTPY_AVAILABLE,
        'tipo_coleta': 'indices_ifix_idiv',
        'status': 'concluido'
    }
    
    with open(f"{PASTA_OUTPUT}/status_indices.json", 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    
    print("✅ Arquivo de status dos índices gerado")

def main():
    """Função principal do pipeline de índices"""
    print("🚀 Iniciando pipeline de coleta de índices...")
    print()
    
    # Executar coleta de índices
    sucesso = coletar_ifix_idiv()
    
    # Gerar status
    gerar_arquivo_status()
    
    # Resumo final
    print()
    print("=" * 80)
    print("📊 RESUMO DA COLETA DE ÍNDICES")
    print("=" * 80)
    
    status = "✅ SUCESSO" if sucesso else "❌ FALHA"
    print(f"IFIX/IDIV: {status}")
    
    if sucesso:
        print("🎉 Pipeline de índices executado com SUCESSO!")
        return 0
    else:
        print("⚠️ Pipeline de índices executado com ERROS")
        return 1

if __name__ == "__main__":
    sys.exit(main())
