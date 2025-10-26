#!/usr/bin/env python3
"""
Script para testar as melhorias de design e responsividade
"""

import streamlit as st
import time
import random

def testar_responsividade():
    """Testa os componentes responsivos"""
    st.header("🧪 Teste de Responsividade")
    
    # Teste de botões lado a lado
    st.subheader("Botões Lado a Lado")
    col1, col2 = st.columns(2)
    
    with col1:
        st.button("Botão 1 - Teste Responsivo", key="btn1")
    
    with col2:
        st.button("Botão 2 - Teste Responsivo", key="btn2")
    
    # Teste de inputs
    st.subheader("Campos de Input")
    email = st.text_input("Email", placeholder="Digite seu email")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
    
    # Teste de selectbox
    st.subheader("Dropdown")
    opcao = st.selectbox("Escolha uma opção", ["Opção 1", "Opção 2", "Opção 3"])
    
    # Teste de radio buttons
    st.subheader("Radio Buttons")
    radio_opcao = st.radio("Escolha uma opção", ["Opção A", "Opção B", "Opção C"])
    
    # Teste de slider
    st.subheader("Slider")
    valor = st.slider("Escolha um valor", 0, 100, 50)
    
    # Teste de checkbox
    st.subheader("Checkbox")
    checkbox = st.checkbox("Aceito os termos")
    
    return {
        "email": email,
        "senha": senha,
        "opcao": opcao,
        "radio_opcao": radio_opcao,
        "valor": valor,
        "checkbox": checkbox
    }

def testar_tema():
    """Testa a compatibilidade com temas"""
    st.header("🎨 Teste de Tema")
    
    # Cards de teste
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("Card de Informação")
        st.write("Este é um card de informação que deve se adaptar ao tema.")
    
    with col2:
        st.success("Card de Sucesso")
        st.write("Este é um card de sucesso com cores adaptáveis.")
    
    with col3:
        st.warning("Card de Aviso")
        st.write("Este é um card de aviso que muda com o tema.")
    
    # Teste de cores
    st.subheader("Teste de Cores")
    st.write("As cores devem se adaptar automaticamente ao tema do sistema:")
    st.write("• Texto principal deve ser legível")
    st.write("• Fundos devem ter contraste adequado")
    st.write("• Bordas devem ser visíveis")

def testar_animações():
    """Testa as animações e transições"""
    st.header("✨ Teste de Animações")
    
    # Botão com animação
    if st.button("Clique para testar animação", key="anim_btn"):
        st.success("Animação funcionando! ✨")
        time.sleep(1)
    
    # Progress bar
    progress_bar = st.progress(0)
    for i in range(100):
        progress_bar.progress(i + 1)
        time.sleep(0.01)
    
    st.success("Progresso concluído!")

def testar_layout():
    """Testa o layout responsivo"""
    st.header("📱 Teste de Layout")
    
    # Grid responsivo
    st.subheader("Grid Responsivo")
    
    # 4 colunas em desktop, 2 em tablet, 1 em mobile
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Métrica 1", "100", "10%")
    
    with col2:
        st.metric("Métrica 2", "200", "-5%")
    
    with col3:
        st.metric("Métrica 3", "300", "15%")
    
    with col4:
        st.metric("Métrica 4", "400", "8%")
    
    # Cards empilhados
    st.subheader("Cards Empilhados")
    
    for i in range(3):
        with st.expander(f"Card {i+1}"):
            st.write(f"Conteúdo do card {i+1}")
            st.write("Este card deve se adaptar ao tamanho da tela.")
            st.write("Em telas pequenas, deve ocupar toda a largura.")
            st.write("Em telas grandes, deve ter largura adequada.")

def main():
    """Função principal do teste"""
    st.set_page_config(
        page_title="Teste de Melhorias de Design",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Teste de Melhorias de Design e Responsividade")
    st.markdown("---")
    
    # Menu de navegação
    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 Responsividade", 
        "🎨 Tema", 
        "✨ Animações", 
        "📐 Layout"
    ])
    
    with tab1:
        resultados = testar_responsividade()
        st.json(resultados)
    
    with tab2:
        testar_tema()
    
    with tab3:
        testar_animações()
    
    with tab4:
        testar_layout()
    
    # Instruções
    st.markdown("---")
    st.info("""
    **Instruções para Teste:**
    
    1. **Teste de Responsividade**: Redimensione a janela do navegador para ver como os elementos se adaptam
    2. **Teste de Tema**: Mude o tema do seu sistema (claro/escuro) para ver a adaptação automática
    3. **Teste de Animações**: Clique nos botões para ver as animações
    4. **Teste de Layout**: Observe como o grid se adapta em diferentes tamanhos de tela
    
    **Breakpoints:**
    - Mobile: < 480px
    - Tablet: 480px - 768px  
    - Desktop: > 768px
    """)

if __name__ == "__main__":
    main()
