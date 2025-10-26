#!/usr/bin/env python3
"""
Script para corrigir CSS do login
"""

def criar_css_corrigido():
    """Criar CSS corrigido para o login"""
    css_corrigido = """
    <style>
    /* CSS CORRIGIDO PARA LOGIN */
    
    /* Reset básico para campos de input */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
        color: #333 !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    /* Labels dos campos */
    .stTextInput label {
        color: #333 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0 !important;
        padding: 20px !important;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #667eea !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        width: 100% !important;
        font-size: 16px !important;
    }
    
    .stButton > button:hover {
        background-color: #5a6fd8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Remover estilos problemáticos */
    .stTextInput > div {
        background: transparent !important;
    }
    
    /* Garantir que os campos sejam visíveis */
    .stTextInput {
        margin-bottom: 20px !important;
    }
    
    /* Cards principais */
    .card {
        background: white !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 20px !important;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #333 !important;
    }
    
    /* Texto geral */
    .stMarkdown {
        color: #333 !important;
    }
    </style>
    """
    
    return css_corrigido

if __name__ == "__main__":
    css = criar_css_corrigido()
    print("CSS corrigido criado!")
    print("Aplicando correção no app.py...")
    
    # Ler o arquivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar e substituir o CSS existente
    import re
    
    # Padrão para encontrar o CSS existente
    pattern = r'<style>.*?</style>'
    
    # Substituir o CSS
    new_content = re.sub(pattern, css, content, flags=re.DOTALL)
    
    # Salvar o arquivo corrigido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ CSS corrigido aplicado no app.py!")
    print("🚀 Faça commit e deploy para corrigir a página!")

