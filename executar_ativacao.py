#!/usr/bin/env python3
"""
Script para executar a página de ativação via Streamlit
"""

import subprocess
import sys
import os

def executar_streamlit():
    """Executar Streamlit com a página de ativação"""
    
    print("=" * 60)
    print("🚀 INICIANDO PÁGINA DE ATIVAÇÃO VIA STREAMLIT")
    print("=" * 60)
    print("📱 URL: http://localhost:8501")
    print("🔗 Página de ativação: http://localhost:8501")
    print("=" * 60)
    print("📝 INSTRUÇÕES:")
    print("1. Abra o navegador em: http://localhost:8501")
    print("2. Teste a página de ativação")
    print("3. Pressione Ctrl+C para parar o servidor")
    print("=" * 60)
    
    try:
        # Executar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ativacao_streamlit.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar_streamlit()
