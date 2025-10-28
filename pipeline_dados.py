#!/usr/bin/env python3
"""
Pipeline de Coleta de Dados - Dashboard Análise de Ações
Versão melhorada que combina dados reais do BCB com lista completa de tickers
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import yfinance as yf

# Tentar importar bcb, mas continuar se não estiver disponível
try:
    from bcb import sgs
    BCB_AVAILABLE = True
except ImportError:
    print("⚠️ Aviso: python-bcb não disponível. Usando dados simulados para CDI/IPCA.")
    BCB_AVAILABLE = False

# Tentar importar investpy, mas continuar se não estiver disponível
try:
    import investpy
    INVESTPY_AVAILABLE = True
except ImportError:
    print("⚠️ Aviso: investpy não disponível. Pulando coleta de IFIX/IDIV.")
    INVESTPY_AVAILABLE = False

# --- CONFIGURAÇÃO ---
PASTA_OUTPUT = "dados"
ANOS_HISTORICO = 10

print("=" * 80)
print("🚀 PIPELINE DE COLETA DE DADOS - DASHBOARD ANÁLISE DE AÇÕES")
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

def ler_lista_tickers(caminho_arquivo="lista_tickers.txt"):
    """Lê a lista de tickers de um arquivo de texto."""
    print(f"📋 Lendo lista de tickers do arquivo '{caminho_arquivo}'...")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            tickers = [linha.strip() for linha in f if linha.strip()]
        print(f"✅ {len(tickers)} tickers encontrados na lista")
        return tickers
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{caminho_arquivo}' não encontrado")
        return []
    except Exception as e:
        print(f"❌ ERRO ao ler arquivo: {e}")
        return []

def coletar_dados_bcb():
    """Coleta dados reais do Banco Central do Brasil"""
    if not BCB_AVAILABLE:
        print("⚠️ BCB não disponível, usando dados simulados...")
        return coletar_cdi_ipca_simulado()
    
    print("🔄 Coletando dados reais do Banco Central...")
    
    try:
        # Códigos do BCB
        codigos_bcb = {
            'CDI': 12,      # Taxa SELIC diária (proxy do CDI)
            'IPCA': 433     # IPCA mensal
        }
        
        sucessos = 0
        for nome, codigo in codigos_bcb.items():
            print(f"  📊 Coletando {nome}...")
            try:
                dados = sgs.get({nome: codigo}, start=start_date.strftime('%Y-%m-%d'))
                dados.rename(columns={nome: 'Close'}, inplace=True)
                dados.reset_index(inplace=True)
                dados.rename(columns={'index': 'Date'}, inplace=True)
                dados['Date'] = dados['Date'].dt.strftime('%Y-%m-%d')
                
                # Salvar arquivo
                caminho_arquivo = os.path.join(PASTA_OUTPUT, f"{nome}.csv")
                dados.to_csv(caminho_arquivo, index=False)
                print(f"    ✅ {nome}: {len(dados)} registros")
                sucessos += 1
                
            except Exception as e:
                print(f"    ❌ {nome}: Erro - {e}")
        
        print(f"✅ Dados do BCB: {sucessos}/{len(codigos_bcb)} coletados")
        return sucessos > 0
        
    except Exception as e:
        print(f"❌ Erro geral no BCB: {e}")
        return coletar_cdi_ipca_simulado()

def coletar_cdi_ipca_simulado():
    """Coleta dados simulados do CDI e IPCA quando BCB não está disponível"""
    print("🔄 Gerando dados simulados do CDI e IPCA...")
    
    try:
        # Valores históricos aproximados do CDI por ano
        cdi_por_ano = {
            2015: 14.25, 2016: 14.15, 2017: 7.12, 2018: 6.40,
            2019: 5.39, 2020: 2.75, 2021: 5.90, 2022: 13.65,
            2023: 12.15, 2024: 10.45, 2025: 15.25
        }
        
        # Valores históricos aproximados do IPCA por ano
        ipca_por_ano = {
            2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75,
            2019: 4.31, 2020: 4.52, 2021: 10.06, 2022: 5.79,
            2023: 4.62, 2024: 4.18, 2025: 5.13
        }
        
        # Gerar série diária do CDI
        datas = pd.date_range(start=start_date, end=end_date, freq='D')
        cdi_diario = []
        
        for data in datas:
            ano = data.year
            if ano in cdi_por_ano:
                # Adicionar variação aleatória pequena (±0.1%)
                variacao = np.random.normal(0, 0.05)
                taxa_diaria = (cdi_por_ano[ano] / 100) / 365 + variacao / 100
                cdi_diario.append({
                    'Date': data.strftime('%Y-%m-%d'),
                    'Close': taxa_diaria * 100  # Converter para percentual
                })
        
        # Salvar CDI
        df_cdi = pd.DataFrame(cdi_diario)
        df_cdi.to_csv(f"{PASTA_OUTPUT}/CDI.csv", index=False)
        print(f"✅ CDI simulado: {len(df_cdi)} registros")
        
        # Gerar série mensal do IPCA
        datas_mensais = pd.date_range(start=start_date, end=end_date, freq='MS')
        ipca_mensal = []
        
        for data in datas_mensais:
            ano = data.year
            if ano in ipca_por_ano:
                # Adicionar variação aleatória pequena
                variacao = np.random.normal(0, 0.2)
                taxa_mensal = (ipca_por_ano[ano] / 100) / 12 + variacao / 100
                ipca_mensal.append({
                    'Date': data.strftime('%Y-%m-%d'),
                    'Close': taxa_mensal * 100  # Converter para percentual
                })
        
        # Salvar IPCA
        df_ipca = pd.DataFrame(ipca_mensal)
        df_ipca.to_csv(f"{PASTA_OUTPUT}/IPCA.csv", index=False)
        print(f"✅ IPCA simulado: {len(df_ipca)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar dados simulados: {e}")
        return False

def coletar_dados_yfinance(tickers, pasta_destino):
    """Coleta dados do yfinance para lista de tickers"""
    print(f"🔄 Coletando dados do yfinance para {len(tickers)} tickers...")
    
    sucessos = 0
    falhas = 0
    
    for i, ticker in enumerate(tickers, 1):
        print(f"  📈 [{i}/{len(tickers)}] Coletando {ticker}...")
        try:
            dados = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if dados.empty:
                print(f"    ⚠️ {ticker}: Dados vazios")
                falhas += 1
                continue

            # Padronizar formato
            dados.reset_index(inplace=True)
            dados_padronizados = dados[['Date', 'Close']].copy()
            dados_padronizados['Date'] = dados_padronizados['Date'].dt.strftime('%Y-%m-%d')

            # Nome do arquivo
            nome_base = ticker.replace('^', 'IBOV_').replace('.SA', '')
            nome_arquivo = f"{nome_base}.csv"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)

            # Salvar
            dados_padronizados.to_csv(caminho_completo, index=False)
            print(f"    ✅ {ticker}: {len(dados_padronizados)} registros")
            sucessos += 1
            
        except Exception as e:
            print(f"    ❌ {ticker}: Erro - {e}")
            falhas += 1
    
    print(f"✅ yfinance: {sucessos} sucessos, {falhas} falhas")
    return sucessos > 0

def coletar_ifix_idiv():
    """Coleta dados do IFIX e IDIV usando investpy"""
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
            df_limpo['Date'] = df_limpo['Date'].dt.strftime('%Y-%m-%d')
            
            # Caminho completo do arquivo de saída
            caminho_output = os.path.join(PASTA_OUTPUT, output_filename)
            
            # Salvar arquivo CSV
            df_limpo.to_csv(caminho_output, index=False)
            
            print(f"    ✅ {output_filename}: {len(df_limpo)} registros")
            sucessos += 1
            
        except Exception as e:
            print(f"    ❌ {index_name}: Erro - {e}")
            falhas += 1
    
    print(f"✅ IFIX/IDIV: {sucessos} sucessos, {falhas} falhas")
    return sucessos > 0

def gerar_arquivo_status():
    """Gera arquivo de status da coleta"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'pasta_dados': PASTA_OUTPUT,
        'periodo_inicio': start_date.isoformat(),
        'periodo_fim': end_date.isoformat(),
        'bcb_disponivel': BCB_AVAILABLE,
        'investpy_disponivel': INVESTPY_AVAILABLE,
        'status': 'concluido'
    }
    
    with open(f"{PASTA_OUTPUT}/status_coleta.json", 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    
    print("✅ Arquivo de status gerado")

def main():
    """Função principal do pipeline"""
    print("🚀 Iniciando pipeline de coleta de dados...")
    print()
    
    # Executar coletas
    resultados = []
    
    # 1. Ler lista de tickers
    tickers_a_buscar = ler_lista_tickers()
    if not tickers_a_buscar:
        print("⚠️ Lista de tickers vazia, usando lista padrão...")
        # Lista de fallback com principais ativos
        tickers_a_buscar = [
            'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
            'MGLU3.SA', 'WEGE3.SA', 'RENT3.SA', 'LREN3.SA', 'SUZB3.SA'
        ]
    
    # 2. Adicionar benchmarks
    tickers_benchmarks = ["^BVSP"]  # Ibovespa
    todos_tickers = list(set(tickers_a_buscar + tickers_benchmarks))
    
    # 3. Coletar dados do BCB
    resultados.append(("BCB (CDI/IPCA)", coletar_dados_bcb()))
    
    # 4. Coletar dados do yfinance
    resultados.append(("yfinance", coletar_dados_yfinance(todos_tickers, PASTA_OUTPUT)))
    
    # 5. Coletar dados do IFIX/IDIV
    resultados.append(("IFIX/IDIV", coletar_ifix_idiv()))
    
    # 6. Gerar status
    gerar_arquivo_status()
    
    # Resumo final
    print()
    print("=" * 80)
    print("📊 RESUMO DA COLETA")
    print("=" * 80)
    
    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ SUCESSO" if sucesso else "❌ FALHA"
        print(f"{nome:20} : {status}")
        if sucesso:
            sucessos += 1
    
    print(f"\n📈 Taxa de sucesso: {sucessos}/{len(resultados)} ({sucessos/len(resultados)*100:.1f}%)")
    
    if sucessos == len(resultados):
        print("🎉 Pipeline executado com SUCESSO TOTAL!")
        return 0
    else:
        print("⚠️ Pipeline executado com ALGUNS ERROS")
        return 1

if __name__ == "__main__":
    sys.exit(main())