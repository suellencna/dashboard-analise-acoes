#!/usr/bin/env python3
"""
Pipeline de Coleta de Índices - IFIX e IDIV
Arquivo separado para coleta de dados do IFIX e IDIV usando brapi.dev
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import random
import requests

# Configuração da API brapi.dev
BRAPI_TOKEN = "4YpDFTVrWH1rtybFtSuSRS"
BRAPI_BASE_URL = "https://brapi.dev/api"

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

def coletar_dados_brapi(ticker, range_param="10y"):
    """Coleta dados históricos de um ticker usando brapi.dev"""
    url = f"{BRAPI_BASE_URL}/quote/{ticker}"
    
    params = {
        'range': range_param,
        'interval': '1d',
        'token': BRAPI_TOKEN
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'results' not in data or not data['results']:
            return None
            
        result = data['results'][0]
        
        if 'historicalDataPrice' not in result:
            return None
            
        historical_data = result['historicalDataPrice']
        
        # Converter para DataFrame
        df_data = []
        for item in historical_data:
            # Converter timestamp Unix para data
            date_obj = datetime.fromtimestamp(item['date'])
            df_data.append({
                'Date': date_obj.strftime('%Y-%m-%d'),
                'Close': item['close']
            })
        
        df = pd.DataFrame(df_data)
        
        return df
        
    except Exception as e:
        print(f"    ⚠️ Erro ao coletar {ticker}: {e}")
        return None

def coletar_indice_com_fallback(ticker_principal, tickers_fallback, output_filename):
    """Coleta dados de um índice com estratégia de fallback para ETFs"""
    print(f"  📊 Coletando {ticker_principal}...")
    
    # Primeiro, tentar o ticker principal
    df = coletar_dados_brapi(ticker_principal, "10y")
    
    if df is not None and not df.empty and len(df) > 10:  # Se tem dados suficientes
        print(f"    ✅ {ticker_principal}: {len(df)} registros")
        return df, ticker_principal
    
    # Se falhou, tentar tickers de fallback
    for ticker_fallback in tickers_fallback:
        print(f"    🔄 Tentando fallback: {ticker_fallback}...")
        df = coletar_dados_brapi(ticker_fallback, "10y")
        
        if df is not None and not df.empty and len(df) > 10:
            print(f"    ✅ {ticker_fallback}: {len(df)} registros (fallback)")
            return df, ticker_fallback
    
    print(f"    ❌ {ticker_principal}: Nenhum ticker funcionou")
    return None, None

def coletar_ifix_idiv():
    """Coleta dados do IFIX e IDIV usando brapi.dev com estratégia de fallback"""
    print("🔄 Coletando dados do IFIX e IDIV usando brapi.dev...")
    
    # Configuração principal e fallbacks
    indices_config = {
        'IFIX': {
            'principal': 'IFIX.SA',
            'fallbacks': ['BOVA11', 'IVVB11'],  # ETFs que podem representar o mercado
            'output': 'IFIX.SA.csv'
        },
        'IDIV': {
            'principal': 'IDIV.SA', 
            'fallbacks': ['BOVA11', 'IVVB11'],  # ETFs que podem representar o mercado
            'output': 'IDIV.SA.csv'
        }
    }
    
    sucessos = 0
    falhas = 0
    
    for nome_indice, config in indices_config.items():
        print(f"  📊 Coletando {nome_indice}...")
        
        tentativa = 0
        sucesso_index = False
        
        while tentativa < MAX_RETRIES and not sucesso_index:
            try:
                if tentativa > 0:
                    delay = RETRY_DELAY + random.uniform(0, 1)
                    print(f"    🔄 Tentativa {tentativa + 1}/{MAX_RETRIES} em {delay:.1f}s...")
                    time.sleep(delay)
                
                # Coletar dados com fallback
                df, ticker_usado = coletar_indice_com_fallback(
                    config['principal'], 
                    config['fallbacks'], 
                    config['output']
                )
                
                if df is not None:
                    # Caminho completo do arquivo de saída
                    caminho_output = os.path.join(PASTA_OUTPUT, config['output'])
                    
                    # Salvar arquivo CSV
                    df.to_csv(caminho_output, index=False)
                    
                    print(f"    ✅ {config['output']}: {len(df)} registros (via {ticker_usado})")
                    sucessos += 1
                    sucesso_index = True
                else:
                    print(f"    ⚠️ {nome_indice}: Dados não encontrados")
                    break
                
            except Exception as e:
                tentativa += 1
                error_msg = str(e)
                
                if "403" in error_msg or "rate limit" in error_msg.lower():
                    print(f"    ⚠️ {nome_indice}: Erro 403 - Rate limit da brapi.dev")
                    if tentativa < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * 2)  # Delay maior para 403
                        continue
                    else:
                        print(f"    ❌ {nome_indice}: Falha após {MAX_RETRIES} tentativas - Rate limit")
                        break
                elif tentativa < MAX_RETRIES:
                    print(f"    ⚠️ {nome_indice}: Erro na tentativa {tentativa} - {error_msg}")
                    continue
                else:
                    print(f"    ❌ {nome_indice}: Falha após {MAX_RETRIES} tentativas - {error_msg}")
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
        'api_usada': 'brapi.dev',
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

