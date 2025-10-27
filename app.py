# --- 1. BLOCO DE IMPORTAÇÕES E CONFIGURAÇÕES ---
import streamlit as st
import sqlalchemy
import os
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from mapa_ativos import MAPA_ATIVOS
from mapa_fiis import MAPA_FIIS
import re
import yfinance as yf

# --- Configurações da Página e Estilo ---
st.set_page_config(page_title="Análise de Carteira", layout="wide")

# Tema responsivo e adaptável ao sistema do usuário
st.markdown("""
    <style>
    /* ===== SISTEMA DE CORES UNIFORME - CORES DO LOGO ===== */
    :root {
        /* Cores do logo - Azul claro e dourado */
        --primary-color: #87CEEB;  /* Azul claro do logo */
        --primary-hover: #6BB6FF;  /* Azul mais escuro */
        --secondary-color: #FFD700; /* Dourado do logo */
        --accent-color: #e74c3c;   /* Vermelho para compra */
        --logo-blue: #87CEEB;      /* Azul claro do logo */
        --logo-gold: #FFD700;      /* Dourado do logo */
        
        /* TEMA UNIFORME - TUDO PRETO */
        --bg-primary: #1a1a1a;
        --bg-secondary: #2d2d2d;
        --bg-card: #2d2d2d;
        --bg-sidebar: #2d2d2d;
        
        /* Cores de texto uniformes */
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
        --text-muted: #808080;
        --text-white: #ffffff;
        
        /* Cores de borda uniformes */
        --border-color: #404040;
        --border-focus: var(--primary-color);
        --border-strong: #505050;
        
        /* Sombras uniformes para tema preto */
        --shadow-light: rgba(255, 255, 255, 0.1);
        --shadow-medium: rgba(255, 255, 255, 0.15);
        --shadow-heavy: rgba(255, 255, 255, 0.25);
        
        /* Transições suaves */
        --transition-fast: 0.2s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.5s ease;
    }
    
    /* ===== RESET E BASE ===== */
    * {
        box-sizing: border-box;
    }
    
    /* ===== LAYOUT RESPONSIVO ===== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* ===== SIDEBAR UNIFORME ===== */
    .stSidebar {
        background-color: var(--bg-sidebar) !important;
        border-right: 2px solid var(--border-strong) !important;
        padding: 1.5rem !important;
        color: var(--text-primary) !important;
    }
    
    /* Garantir que todo texto na sidebar seja visível */
    .stSidebar * {
        color: var(--text-primary) !important;
    }
    
    .stSidebar label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    .stSidebar .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
        color: var(--text-primary) !important;
    }
    
    @media (max-width: 768px) {
        .stSidebar {
            padding: 1rem !important;
        }
    }
    
    /* ===== CAMPOS DE INPUT UNIFORMES ===== */
    .stTextInput > div > div > input {
        background-color: var(--bg-card) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        font-size: 16px !important;
        color: var(--text-primary) !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all var(--transition-normal) !important;
        min-height: 48px !important;
    }
    
    /* ===== CORRIGIR CONTAINERS BRANCOS ===== */
    /* Forçar tema escuro em todos os containers */
    .stContainer, .stDataFrame, .stTable, .stMetric, .stColumns > div {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    /* Containers específicos que estavam brancos */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--primary-color) !important;
    }
    
    /* Container "Precisa de ajuda" */
    .stMarkdown:contains("Precisa de ajuda"),
    .stMarkdown:contains("contato"),
    .stMarkdown:contains("gmail") {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: 16px !important;
        border-radius: 12px !important;
        border: 2px solid var(--primary-color) !important;
    }
    
    /* Cards de funcionalidades */
    .stMarkdown:contains("Análise Markowitz"),
    .stMarkdown:contains("Simulação Monte Carlo"),
    .stMarkdown:contains("Métricas em Tempo Real") {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        border: 2px solid var(--primary-color) !important;
        margin: 10px 0 !important;
    }
    
    /* Containers de gráficos */
    .stPlotlyChart, .stPyplot, .stAltair {
        background-color: var(--bg-card) !important;
    }
    
    /* Tabelas e dataframes */
    .stDataFrame table, .stTable table {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stDataFrame th, .stDataFrame td, .stTable th, .stTable td {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }
    
    /* ===== BORDAS NOS CAMPOS DE NÚMEROS ===== */
    .stNumberInput > div > div > input {
        background-color: var(--bg-card) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 16px !important;
        color: var(--text-primary) !important;
        text-align: center !important;
        min-width: 80px !important;
        transition: all var(--transition-normal) !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.1) !important;
        outline: none !important;
    }
    
    /* ===== BORDAS NOS ATIVOS SELECIONADOS ===== */
    .stMultiSelect > div > div > div {
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        background-color: var(--bg-card) !important;
        min-height: 48px !important;
    }
    
    .stMultiSelect > div > div > div:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.1) !important;
    }
    
    /* Tags dos ativos selecionados */
    .stMultiSelect > div > div > div > div[data-baseweb="tag"] {
        background-color: var(--primary-color) !important;
        color: #2c3e50 !important;
        border: 1px solid var(--primary-hover) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        margin: 2px !important;
    }
    
    .stMultiSelect > div > div > div > div[data-baseweb="tag"]:hover {
        background-color: var(--primary-hover) !important;
    }
    
    /* Garantir que placeholder seja visível */
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.8 !important;
    }
    
    /* Garantir que texto digitado seja sempre visível */
    .stTextInput > div > div > input:not(:placeholder-shown) {
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.7 !important;
    }
    
    /* Labels dos campos */
    .stTextInput label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        display: block !important;
    }
    
    /* Container dos inputs */
    .stTextInput > div {
        background: transparent !important;
    }
    
    .stTextInput {
        margin-bottom: 1.5rem !important;
    }
    
    /* ===== BOTÕES COM CORES DO LOGO ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--logo-blue) 0%, var(--logo-gold) 100%) !important;
        color: #1a1a1a !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 14px 24px !important;
        width: 100% !important;
        font-size: 16px !important;
        min-height: 48px !important;
        transition: all var(--transition-normal) !important;
        box-shadow: 0 4px 12px rgba(135, 206, 235, 0.3) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        line-height: 1.2 !important;
    }
    
    /* Botões que PRECISAM de quebra de linha */
    .stButton > button:contains("Salvar Configuração"),
    .stButton > button:contains("Salvar configuração"),
    .stButton > button:contains("Otimização e Projeções"),
    .stButton > button:contains("Clique aqui para") {
        white-space: normal !important;
        line-height: 1.3 !important;
        padding: 16px 24px !important;
        min-height: 60px !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    
    /* Botões que NÃO precisam de quebra (texto curto) */
    .stButton > button:contains("Entrar"),
    .stButton > button:contains("Login"),
    .stButton > button:contains("Logout"),
    .stButton > button:contains("Fechar"),
    .stButton > button:contains("Verificar") {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Garantir que texto dos botões seja sempre visível e centralizado */
    .stButton > button * {
        color: #2c3e50 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    
    .stButton > button span {
        color: #2c3e50 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    /* Centralização específica para ícones e texto */
    .stButton > button .stButtonIcon {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-right: 8px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-hover) 0%, #d4ac0d 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(243, 156, 18, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3) !important;
    }
    
    /* ===== BOTÃO COMPRAR AGORA ESPECIAL ===== */
    .stButton > button:contains("Comprar Agora"),
    .stButton > button:contains("Comprar"),
    .stButton > button[data-testid*="comprar"] {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3) !important;
    }
    
    .stButton > button:contains("Comprar Agora"):hover,
    .stButton > button:contains("Comprar"):hover,
    .stButton > button[data-testid*="comprar"]:hover {
        background: linear-gradient(135deg, #c0392b 0%, #a93226 100%) !important;
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.5) !important;
    }
    
    /* Estilo para botões de compra/venda */
    .stButton > button[style*="red"],
    .stButton > button[style*="crimson"] {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3) !important;
    }
    
    /* Botões pequenos para telas pequenas */
    @media (max-width: 480px) {
        .stButton > button {
            font-size: 14px !important;
            padding: 12px 16px !important;
            min-height: 44px !important;
        }
    }
    
    /* ===== BOTÕES LADO A LADO RESPONSIVOS ===== */
    .button-group {
        display: flex !important;
        gap: 12px !important;
        width: 100% !important;
        flex-wrap: wrap !important;
    }
    
    .button-group .stButton {
        flex: 1 !important;
        min-width: 140px !important;
    }
    
    /* Layout específico para botões verificar email e fechar */
    .button-group-vertical {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
        width: 100% !important;
    }
    
    .button-group-vertical .stButton {
        flex: none !important;
        min-width: auto !important;
    }
    
    /* Botões específicos para "Esqueci minha senha" */
    .stButton > button:contains("Esqueci"),
    .stButton > button:contains("Verificar"),
    .stButton > button:contains("Fechar") {
        white-space: nowrap !important;
        line-height: 1.2 !important;
        min-width: 120px !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
    }
    
    @media (max-width: 768px) {
        .button-group {
            flex-direction: column !important;
            gap: 8px !important;
        }
        
        .button-group .stButton {
            flex: none !important;
            min-width: auto !important;
        }
        
        .stButton > button:contains("Esqueci"),
        .stButton > button:contains("Verificar"),
        .stButton > button:contains("Fechar") {
            font-size: 13px !important;
            padding: 10px 12px !important;
            min-width: 100px !important;
        }
    }
    
    @media (max-width: 480px) {
        .button-group .stButton > button {
            font-size: 12px !important;
            padding: 8px 10px !important;
        }
        
        .stButton > button:contains("Esqueci"),
        .stButton > button:contains("Verificar"),
        .stButton > button:contains("Fechar") {
            font-size: 11px !important;
            padding: 8px 10px !important;
            min-width: 90px !important;
        }
    }
    
    /* ===== CARDS RESPONSIVOS ===== */
    .card {
        background: var(--bg-card) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px var(--shadow-light) !important;
        margin-bottom: 24px !important;
        border: 1px solid var(--border-color) !important;
        transition: all var(--transition-normal) !important;
    }
    
    .card:hover {
        box-shadow: 0 8px 24px var(--shadow-medium) !important;
        transform: translateY(-2px) !important;
    }
    
    @media (max-width: 768px) {
        .card {
            padding: 16px !important;
            margin-bottom: 16px !important;
        }
    }
    
    /* ===== TÍTULOS RESPONSIVOS ===== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
        line-height: 1.3 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        h2 {
            font-size: 1.75rem !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
        }
    }
    
    /* ===== TEXTO GERAL UNIFORME ===== */
    .stMarkdown {
        color: var(--text-primary) !important;
        line-height: 1.6 !important;
    }
    
    p {
        color: var(--text-primary) !important;
        margin-bottom: 1rem !important;
    }
    
    /* Garantir que todos os textos sejam visíveis */
    body, .main, .block-container {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Forçar visibilidade de todos os elementos de texto */
    div, span, p, h1, h2, h3, h4, h5, h6, label, a, button {
        color: inherit !important;
    }
    
    /* Garantir que links sejam visíveis */
    a {
        color: var(--primary-color) !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: var(--primary-hover) !important;
        text-decoration: underline !important;
    }
    
    /* ===== CORREÇÃO DE QUEBRA DE TEXTO DO EMAIL ===== */
    .stMarkdown a[href*="@"] {
        word-break: break-all !important;
        word-wrap: break-word !important;
        white-space: normal !important;
        display: inline-block !important;
        max-width: 100% !important;
    }
    
    /* Quebrar especificamente no @ para emails */
    .stMarkdown a[href*="mailto:"] {
        word-break: break-all !important;
        word-wrap: break-word !important;
        white-space: normal !important;
    }
    
    /* Texto de ajuda com quebra controlada */
    .stMarkdown p:contains("@") {
        word-break: break-all !important;
        word-wrap: break-word !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }
    
    /* Atualizar cores de foco para amarelo */
    .stButton > button:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }
    
    /* ===== GRID RESPONSIVO ===== */
    .stColumns {
        gap: 1rem !important;
    }
    
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column !important;
        }
        
        .stColumns > div {
            width: 100% !important;
        }
    }
    
    /* ===== SLIDERS E CONTROLES ===== */
    .stSlider > div > div > div > div {
        background: var(--primary-color) !important;
    }
    
    .stSlider label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* ===== SELECTBOX E DROPDOWN ===== */
    .stSelectbox > div > div > div {
        background-color: var(--bg-card) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div > div:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stSelectbox label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* ===== RADIO BUTTONS ===== */
    .stRadio > div {
        gap: 12px !important;
    }
    
    .stRadio > div > label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        transition: all var(--transition-fast) !important;
    }
    
    .stRadio > div > label:hover {
        background-color: rgba(102, 126, 234, 0.1) !important;
    }
    
    /* ===== CHECKBOX ===== */
    .stCheckbox > div > label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* ===== MENSAGENS DE ERRO E SUCESSO DESTACADAS ===== */
    .stAlert {
        border-radius: 12px !important;
        border: 2px solid var(--primary-color) !important;
        box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4) !important;
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        animation: pulse 2s infinite !important;
    }
    
    /* Alertas de erro */
    .stAlert[data-testid="stAlert"]:has(.alert-danger),
    .stAlert:contains("erro"),
    .stAlert:contains("Erro") {
        border-color: #e74c3c !important;
        background-color: rgba(231, 76, 60, 0.1) !important;
        color: #e74c3c !important;
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4) !important;
    }
    
    /* Alertas de sucesso */
    .stAlert:contains("sucesso"),
    .stAlert:contains("Sucesso"),
    .stAlert:contains("concluído") {
        border-color: #27ae60 !important;
        background-color: rgba(39, 174, 96, 0.1) !important;
        color: #27ae60 !important;
        box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4) !important;
    }
    
    /* Animação de destaque */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* ===== SCROLLBAR PERSONALIZADA ===== */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-hover);
    }
    
    /* ===== ANIMAÇÕES ===== */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* ===== MELHORIAS DE ACESSIBILIDADE ===== */
    .stButton > button:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }
    
    /* ===== CORREÇÃO DE GRÁFICOS E LEGENDAS ===== */
    /* Forçar tema escuro nos gráficos Plotly */
    .stPlotlyChart {
        background-color: var(--bg-card) !important;
    }
    
    /* Corrigir legendas dos gráficos - TORNAR VISÍVEL */
    .stPlotlyChart .legend {
        color: var(--text-primary) !important;
        background-color: var(--bg-card) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* Forçar tema escuro nos gráficos */
    .js-plotly-plot .plotly {
        background-color: var(--bg-card) !important;
    }
    
    /* Corrigir textos dos eixos */
    .js-plotly-plot .plotly .xtick, .js-plotly-plot .plotly .ytick {
        color: var(--text-primary) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }
    
    /* Corrigir títulos dos gráficos */
    .js-plotly-plot .plotly .gtitle {
        color: var(--text-primary) !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    
    /* Forçar fundo escuro nos gráficos */
    .stPlotlyChart .plotly .plotly {
        background-color: var(--bg-card) !important;
    }
    
    /* Corrigir legenda do gráfico pizza especificamente */
    .stPlotlyChart .legend text {
        fill: var(--text-primary) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* Corrigir labels do gráfico pizza */
    .stPlotlyChart .pie text {
        fill: var(--text-primary) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }
    
    /* Corrigir tabelas de dados */
    .stDataFrame, .stTable {
        background-color: var(--bg-card) !important;
    }
    
    .stDataFrame table, .stTable table {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stDataFrame th, .stDataFrame td {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }
    
    /* Corrigir métricas */
    .stMetric {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stMetric > div {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: var(--text-primary) !important;
    }
    
    /* ===== PRINT STYLES ===== */
    @media print {
        .stSidebar {
            display: none !important;
        }
        
        .main .block-container {
            max-width: none !important;
            padding: 0 !important;
        }
        
        .card {
            box-shadow: none !important;
            border: 1px solid #ccc !important;
        }
    }
    </style>
    <script>
    // Forçar tema escuro nos gráficos Plotly com cores do logo
    document.addEventListener('DOMContentLoaded', function() {
        // Aguardar carregamento dos gráficos
        setTimeout(function() {
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(plot) {
                if (plot && plot.layout) {
                    // Fundo escuro
                    plot.layout.paper_bgcolor = '#2d2d2d';
                    plot.layout.plot_bgcolor = '#2d2d2d';
                    plot.layout.font = { color: '#ffffff', size: 14 };
                    
                    // Corrigir eixos
                    if (plot.layout.xaxis) {
                        plot.layout.xaxis.color = '#ffffff';
                        plot.layout.xaxis.gridcolor = '#404040';
                        plot.layout.xaxis.tickfont = { color: '#ffffff', size: 12 };
                    }
                    if (plot.layout.yaxis) {
                        plot.layout.yaxis.color = '#ffffff';
                        plot.layout.yaxis.gridcolor = '#404040';
                        plot.layout.yaxis.tickfont = { color: '#ffffff', size: 12 };
                    }
                    
                    // Corrigir legenda - TORNAR VISÍVEL
                    if (plot.layout.legend) {
                        plot.layout.legend.bgcolor = '#2d2d2d';
                        plot.layout.legend.font = { color: '#ffffff', size: 14 };
                        plot.layout.legend.bordercolor = '#87CEEB';
                        plot.layout.legend.borderwidth = 2;
                    }
                    
                    // Corrigir títulos
                    if (plot.layout.title) {
                        plot.layout.title.font = { color: '#ffffff', size: 16 };
                    }
                    
                    // Para gráficos de pizza, corrigir labels
                    if (plot.data) {
                        plot.data.forEach(function(trace) {
                            if (trace.type === 'pie') {
                                trace.textfont = { color: '#ffffff', size: 12 };
                                trace.marker = trace.marker || {};
                                trace.marker.line = { color: '#87CEEB', width: 2 };
                            }
                        });
                    }
                    
                    if (typeof Plotly !== 'undefined') {
                        Plotly.redraw(plot);
                    }
                }
            });
        }, 1000);
        
        // Reaplicar após 3 segundos para garantir
        setTimeout(function() {
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(plot) {
                if (typeof Plotly !== 'undefined' && plot) {
                    Plotly.redraw(plot);
                }
            });
        }, 3000);
    });
    </script>
""", unsafe_allow_html=True)


# --- 2. CONFIGURAÇÃO DO BANCO DE DADOS E SENHA ---
# Carregar variáveis de ambiente do arquivo .env
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = None
ph = None
try:
    if DATABASE_URL:
        engine = sqlalchemy.create_engine(DATABASE_URL)
        ph = PasswordHasher()
    else:
        st.error("ERRO CRÍTICO: A variável de ambiente DATABASE_URL não foi encontrada.")
        st.stop()
except Exception as e:
    st.error(f"ERRO CRÍTICO na inicialização do sistema de autenticação: {e}")
    st.stop()


# --- 3. FUNÇÃO DE LOGIN ---

def verificar_usuario_existe(email):
    """Verifica se um usuário existe no banco de dados"""
    try:
        if not engine:
            raise Exception("Engine não configurado")
        
        with engine.connect() as conn:
            query = sqlalchemy.text("SELECT nome FROM usuarios WHERE email = :email")
            result = conn.execute(query, {"email": email}).first()
            return result is not None, result[0] if result else None
    except Exception as e:
        # Log do erro para debug (remover em produção se necessário)
        print(f"Erro em verificar_usuario_existe: {e}")
        return False, None

def check_login(email, password):
    user_data = None
    try:
        with engine.connect() as conn:
            query = sqlalchemy.text(
                "SELECT nome, senha_hash, ultima_carteira, ultimos_pesos, "
                "data_inicio_salva, data_fim_salva, status_assinatura "
                "FROM usuarios WHERE email = :email"
            )
            result = conn.execute(query, {"email": email}).first()
            if result:
                user_data = result
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        return False, "DB_ERROR", None, None, None, None  # Retorna 6 valores

    if user_data:
        (nome_usuario, senha_hash_salva, ultima_carteira, ultimos_pesos,
         data_inicio, data_fim, status_assinatura) = user_data

        try:
            ph.verify(senha_hash_salva, password)
            if status_assinatura == 'ativo':
                # Verificar se é senha padrão (primeiro acesso)
                if password == "123456":
                    # Primeiro acesso - forçar troca de senha
                    return True, nome_usuario, ultima_carteira, ultimos_pesos, data_inicio, data_fim, "FIRST_ACCESS"
                else:
                    # Login bem-sucedido normal
                    return True, nome_usuario, ultima_carteira, ultimos_pesos, data_inicio, data_fim
            else:
                # Senha correta, mas assinatura inativa
                return False, "INACTIVE_SUBSCRIPTION", None, None, None, None
        except VerifyMismatchError:
            # Senha incorreta
            pass
        except InvalidHashError:
            # Hash inválido - usuário precisa redefinir senha
            return False, "INVALID_HASH", None, None, None, None

    # Email não encontrado ou senha incorreta
    return False, "INVALID_CREDENTIALS", None, None, None, None


def update_password(email, new_password):
    """Atualiza a senha de um usuário"""
    try:
        with engine.connect() as conn:
            # Gerar novo hash da senha
            new_hash = ph.hash(new_password)
            
            # Atualizar no banco
            query = sqlalchemy.text("UPDATE usuarios SET senha_hash = :new_hash WHERE email = :email")
            result = conn.execute(query, {"new_hash": new_hash, "email": email})
            conn.commit()
            
            if result.rowcount > 0:
                return True, "Senha atualizada com sucesso"
            else:
                return False, "Usuário não encontrado"
    except Exception as e:
        return False, f"Erro ao atualizar senha: {e}"

def reset_password_to_default(email):
    """Reseta a senha de um usuário para a senha padrão 123456"""
    try:
        with engine.connect() as conn:
            # Gerar hash da senha padrão 123456
            default_password = "123456"
            new_hash = ph.hash(default_password)
            
            # Atualizar no banco
            query = sqlalchemy.text("UPDATE usuarios SET senha_hash = :new_hash WHERE email = :email")
            result = conn.execute(query, {"new_hash": new_hash, "email": email})
            conn.commit()
            
            if result.rowcount > 0:
                return True, "Senha resetada para padrão (123456) com sucesso!"
            else:
                return False, "Usuário não encontrado."
    except Exception as e:
        return False, f"Erro ao resetar senha: {str(e)}"


# --- 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if 'resultados_otimizacao' not in st.session_state:
    st.session_state.resultados_otimizacao = None
if 'ativos_otimizados' not in st.session_state:
    st.session_state.ativos_otimizados = []
if 'gerar_analise_ia' not in st.session_state:
    st.session_state.gerar_analise_ia = False
if 'force_password_change' not in st.session_state:
    st.session_state.force_password_change = False

# --- 5. VERIFICAR TOKEN DE ATIVAÇÃO ---
# Verificar se há token na URL (para ativação)
if 'token' in st.query_params and not st.session_state.get("authentication_status"):
    token = st.query_params['token']
    
    # Processar ativação da conta
    try:
        with engine.connect() as conn:
            # Verificar se o token é válido
            query_token = sqlalchemy.text("""
                SELECT email, nome, status_conta 
                FROM usuarios 
                WHERE token_ativacao = :token
            """)
            result = conn.execute(query_token, {"token": token}).first()
            
            if result:
                email, nome, status_conta = result
                
                if status_conta == 'pendente':
                    # Ativar a conta
                    query_ativar = sqlalchemy.text("""
                        UPDATE usuarios 
                        SET status_conta = 'ativo', 
                            token_ativacao = NULL,
                            data_ativacao = CURRENT_TIMESTAMP
                        WHERE token_ativacao = :token
                    """)
                    conn.execute(query_ativar, {"token": token})
                    conn.commit()
                    
                    # Gerar senha temporária
                    import secrets
                    senha_temporaria = secrets.token_urlsafe(8)
                    
                    # Atualizar senha temporária no banco
                    query_senha = sqlalchemy.text("""
                        UPDATE usuarios 
                        SET senha_hash = :senha_hash 
                        WHERE email = :email
                    """)
                    senha_hash_temp = ph.hash(senha_temporaria)
                    conn.execute(query_senha, {"senha_hash": senha_hash_temp, "email": email})
                    conn.commit()
                    
                    # Salvar credenciais na sessão
                    st.session_state["activation_credentials"] = {
                        "email": email,
                        "senha": senha_temporaria,
                        "nome": nome
                    }
                    
                    st.success(f"✅ Conta ativada com sucesso! Bem-vindo(a), {nome}!")
                    
                    # Mostrar informações de login
                    st.markdown("### 🔑 Suas Credenciais de Login:")
                    st.markdown(f"**Email:** `{email}`")
                    st.markdown(f"**Senha temporária:** `{senha_temporaria}`")
                    st.warning("⚠️ **IMPORTANTE:** Use esta senha temporária para fazer login. Você será obrigado a alterá-la na primeira vez.")
                    
                elif status_conta == 'ativo':
                    st.info("✅ Sua conta já está ativa! Você pode fazer login normalmente.")
                else:
                    st.error("❌ Status da conta inválido. Entre em contato conosco.")
            else:
                st.error("❌ Token inválido ou não encontrado.")
                
    except Exception as e:
        st.error(f"❌ Erro ao processar ativação: {e}")
        st.info("💡 Entre em contato conosco se o problema persistir.")

# --- 6. LÓGICA DA INTERFACE ---
if st.session_state.get("authentication_status"):
    # SE ESTIVER LOGADO, MOSTRA O DASHBOARD COMPLETO
    st.sidebar.image("prints/slogan_preto.png", width=150)
    st.sidebar.title(f'Bem-vindo(a), {st.session_state["name"]}!')
    
    # Verificar se é primeiro acesso e forçar troca de senha
    if st.session_state.get("force_password_change", False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style='
            background: #fff3cd;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 1rem 0;
        '>
            <h4 style='color: #856404; margin-top: 0;'>🔐 Primeiro Acesso</h4>
            <p style='color: #856404; margin-bottom: 0;'>
                Por segurança, você deve alterar sua senha padrão antes de continuar.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interface de troca de senha obrigatória
        st.sidebar.subheader("🔑 Alterar Senha (Obrigatório)")
        
        new_password = st.sidebar.text_input(
            "Nova Senha", 
            type="password",
            placeholder="Digite sua nova senha",
            key="new_password_first_access"
        )
        confirm_password = st.sidebar.text_input(
            "Confirmar Nova Senha", 
            type="password",
            placeholder="Confirme sua nova senha",
            key="confirm_password_first_access"
        )
        
        if st.sidebar.button("✅ Alterar Senha", use_container_width=True, type="primary"):
            if new_password and confirm_password:
                if new_password == confirm_password:
                    if len(new_password) >= 6:
                        success, message = update_password(st.session_state["email"], new_password)
                        if success:
                            st.sidebar.success("Senha alterada com sucesso!")
                            st.session_state["force_password_change"] = False
                            st.rerun()
                        else:
                            st.sidebar.error(f"Erro: {message}")
                    else:
                        st.sidebar.error("A senha deve ter pelo menos 6 caracteres.")
                else:
                    st.sidebar.error("As senhas não coincidem.")
            else:
                st.sidebar.error("Preencha todos os campos.")
        
        # Não mostrar o dashboard até trocar a senha
        st.stop()

    # LÓGICA DO LOGOUT E TROCA DE SENHA
    if 'confirming_logout' not in st.session_state:
        st.session_state.confirming_logout = False
    if 'show_change_password' not in st.session_state:
        st.session_state.show_change_password = False
    
    # Botões de ação do usuário - alinhados verticalmente
    st.markdown("""
    
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
    
    """, unsafe_allow_html=True)
    

    # --- INÍCIO DO CÓDIGO DO DASHBOARD ---

    plt.style.use('seaborn-v0_8-darkgrid')

    # DADOS INICIAIS E MAPEAMENTOS
    DATA_PATH = "dados"
    MAPA_GERAL_ATIVOS = {**MAPA_ATIVOS, **MAPA_FIIS}
    MAPA_BENCHMARK = {'IBOVESPA': 'IBOV_BVSP.csv', 'IFIX': 'IFIX.SA.csv', 'IDIV': 'IDIV.SA.csv', 'CDI': 'CDI.csv',
                      'IPCA': 'IPCA.csv'}
    PREGOES_NO_ANO = 252
    TAXA_LIVRE_DE_RISCO = 0.105

    try:
        todos_arquivos = os.listdir(DATA_PATH)
        disponiveis = [arquivo.replace('.csv', '') for arquivo in todos_arquivos if arquivo.endswith('.SA.csv')]
        disponiveis.sort()
        if not disponiveis:
            st.error(f"Nenhum arquivo de ativo (.SA.csv) encontrado na pasta '{DATA_PATH}'.")
            st.stop()
    except FileNotFoundError:
        st.error(f"Pasta de dados '{DATA_PATH}' não encontrada.")
        st.stop()


    st.sidebar.header('Definição da Carteira')

    # Lógica para carregar a carteira salva
    default_selection = []
    carteira_salva_str = st.session_state.get("ultima_carteira")
    if carteira_salva_str:
        default_selection = [ativo for ativo in carteira_salva_str.split(',') if ativo in disponiveis]

    # Se não houver carteira salva, usa o padrão antigo
    if not default_selection:
        default_selection = [ativo for ativo in ['PETR4.SA', 'WEGE3.SA', 'ITUB4.SA'] if ativo in disponiveis]

    st.sidebar.markdown("**Digite ou selecione os tickers dos ativos:**")
    ativos_selecionados = st.sidebar.multiselect( 
        label="Selecione os ativos",
        options=disponiveis, 
        default=default_selection,
        help="💡 **Dica:** Você pode digitar o nome do ticker para filtrar rapidamente (ex: 'PETR' para encontrar PETR4.SA)",
        placeholder="Digite para buscar ou clique para selecionar..."
    )

    # Lógica para SALVAR a carteira no banco de dados se houver mudança
    nova_carteira_str = ",".join(ativos_selecionados)
    if nova_carteira_str != carteira_salva_str:
        try:
            with engine.connect() as conn:
                query = sqlalchemy.text("UPDATE usuarios SET ultima_carteira = :carteira WHERE email = :email")
                # Assumindo que o email do usuário logado está em st.session_state
                # Precisamos adicioná-lo ao session_state no login!
                conn.execute(query, {"carteira": nova_carteira_str, "email": st.session_state.email})
                conn.commit()
                st.session_state["ultima_carteira"] = nova_carteira_str  # Atualiza o estado da sessão
        except Exception as e:
            st.sidebar.error(f"Erro ao salvar a carteira: {e}")

    #---- FIM DA DEFINIÇÃO DE CARTEIRA
    
    if len(ativos_selecionados) < 2:
        st.warning("⚠️ Selecione pelo menos 2 ativos para realizar a otimização.")
        st.stop()
    
    if len(ativos_selecionados) >= 2:
        # Bloco de código NOVO E CORRIGIDO

        # Bloco CORRIGIDO para leitura dos ativos
        try:
            lista_dfs = []
            for ativo in ativos_selecionados:
                caminho_arquivo = os.path.join(DATA_PATH, f"{ativo}.csv")
                # Adicionamos skiprows=[1] para pular a linha extra que causa erros
                df_ativo = pd.read_csv(caminho_arquivo, index_col='Date', parse_dates=True, skiprows=[1])
                df_ativo.rename(columns={'Close': ativo}, inplace=True)
                lista_dfs.append(df_ativo)

            df_portfolio_completo = pd.concat(lista_dfs, axis=1)
            df_portfolio_completo = df_portfolio_completo.apply(pd.to_numeric, errors='coerce')
            df_portfolio_completo.sort_index(inplace=True)
            df_portfolio_completo.dropna(inplace=True)

        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os arquivos de dados dos ativos: {e}")
            st.stop()

        st.sidebar.subheader('Opções de Otimização e Simulação')
        data_minima = df_portfolio_completo.index.min().date()
        data_maxima = df_portfolio_completo.index.max().date()

        # Usa a data salva, ou um padrão se não houver
        data_inicio_salva = st.session_state.get("data_inicio_salva")
        data_fim_salva = st.session_state.get("data_fim_salva")

        data_inicio = st.sidebar.date_input("Data de Início",
                                            value=data_inicio_salva or (data_maxima - timedelta(days=365)),
                                            min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
        data_fim = st.sidebar.date_input("Data de Fim",
                                         value=data_fim_salva or data_maxima,
                                         min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")

        if data_inicio > data_fim:
            st.sidebar.error("A data de início não pode ser posterior à data de fim.")
            st.stop()

        data_inicio = pd.to_datetime(data_inicio)  # ← NOVA LINHA
        data_fim = pd.to_datetime(data_fim)  # ← NOVA LINHA
        df_portfolio = df_portfolio_completo.loc[data_inicio:data_fim].copy()  # ← MODIFICADA com .copy()

        pesos = []
        st.sidebar.subheader('Pesos da Carteira Atual (%)')
        # Converte a string de pesos salvos em uma lista de números
        pesos_salvos_str = st.session_state.get("ultimos_pesos")
        pesos_salvos = []
        if pesos_salvos_str:
            try:
                pesos_salvos = [float(p) for p in pesos_salvos_str.split(',')]
            except:
                pesos_salvos = []  # Ignora se houver erro na conversão

        for i, ativo in enumerate(ativos_selecionados):
            # Usa o peso salvo se ele existir para este ativo, senão usa o padrão
            valor_padrao = pesos_salvos[i] if i < len(pesos_salvos) else round(100 / len(ativos_selecionados), 2)
            peso = st.sidebar.number_input(f'Peso para {ativo}', min_value=0.0, max_value=100.0,
                                           value=valor_padrao, step=1.0, key=f'peso_{i}')
            pesos.append(peso)

        # Adicione este bloco na barra lateral, após os inputs de peso
        if st.sidebar.button("Salvar Configuração da Carteira"):
            # Formata os pesos para salvar como texto
            pesos_para_salvar = ",".join([str(p) for p in pesos])

            try:
                with engine.connect() as conn:
                    query = sqlalchemy.text(
                        "UPDATE usuarios SET "
                        "ultima_carteira = :carteira, "
                        "ultimos_pesos = :pesos, "
                        "data_inicio_salva = :data_inicio, "
                        "data_fim_salva = :data_fim "
                        "WHERE email = :email"
                    )
                    conn.execute(query, {
                        "carteira": ",".join(ativos_selecionados),
                        "pesos": pesos_para_salvar,
                        "data_inicio": data_inicio,
                        "data_fim": data_fim,
                        "email": st.session_state.email
                    })
                    conn.commit()
                    st.sidebar.success("Configuração salva com sucesso!")
                    # Atualiza o estado da sessão com os novos valores
                    st.session_state["ultima_carteira"] = ",".join(ativos_selecionados)
                    st.session_state["ultimos_pesos"] = pesos_para_salvar
                    st.session_state["data_inicio_salva"] = data_inicio
                    st.session_state["data_fim_salva"] = data_fim
            except Exception as e:
                st.sidebar.error(f"Erro ao salvar: {e}")

        # Verificar se a soma dos pesos está dentro da tolerância aceitável
        soma_pesos = sum(pesos)
        if abs(soma_pesos - 100.0) > 0.5:  # Tolerância de 0.5% para arredondamentos
            st.error(f"⚠️ **Erro nos pesos da carteira!** A soma total dos pesos deve estar próxima de 100% (tolerância de 0.5%), mas está em {soma_pesos:.2f}%. Por favor, ajuste os pesos para que a soma esteja entre 99.5% e 100.5% antes de continuar.")
            st.stop()
        
        if soma_pesos <= 0:
            st.error("A soma dos pesos não pode ser zero.")
            st.stop()
            
        # Converter para proporção (0 a 1) para os cálculos
        pesos = np.array(pesos, dtype=float) / 100.0
        # st.write(df_portfolio[ativos_selecionados].dtypes) ## imprime o tipo de dados
        # st.write(pesos)
        df_portfolio['Carteira'] = (df_portfolio[ativos_selecionados] * pesos).sum(axis=1)

        # Data à esquerda com fonte menor
        st.markdown(
            f"<p style='text-align: left; font-size: 14px; color: #666; margin-bottom: 1rem;'>Análise da Carteira de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</p>",
            unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        # Bloco NOVO e CORRIGIDO (com lógica de busca inteligente)

        with col1:
            st.subheader('Composição da Carteira')
            visao_pizza = st.radio("Visualizar por:", ('Ativo', 'Setor'), horizontal=True, key='visao_pizza')

            if visao_pizza == 'Ativo':
                # Ordena ativos por peso (maior para menor)
                ativos_pesos_ordenados = sorted(zip(ativos_selecionados, pesos), key=lambda x: x[1], reverse=True)
                ativos_ordenados = [item[0] for item in ativos_pesos_ordenados]
                pesos_ordenados = [item[1] for item in ativos_pesos_ordenados]
                
                fig_pizza = go.Figure(data=[go.Pie(
                    labels=ativos_ordenados, 
                    values=pesos_ordenados, 
                    hole=.3, 
                    textinfo='label+percent',
                    textfont=dict(size=12, color='white'),
                    marker=dict(
                        colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                    ),
                    sort=False,
                    direction='clockwise'
                )])
                fig_pizza.update_layout(
                    title=dict(text="Composição por Ativo", font=dict(size=16, color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )
            else:  # Lógica para visão por Setor
                pesos_setor = {}
                for ativo, peso in zip(ativos_selecionados, pesos):

                    # --- LÓGICA DE BUSCA INTELIGENTE ---
                    # 1. Tenta encontrar uma correspondência exata primeiro (bom para FIIs e Units como 'BTLG11.SA')
                    info_ativo = MAPA_GERAL_ATIVOS.get(ativo)

                    # 2. Se não encontrar, tenta encontrar pelo radical (ex: 'PETR4.SA' -> 'PETR.SA')
                    if not info_ativo:
                        match = re.search(r'\d', ativo)  # Encontra o primeiro número no nome do ativo
                        if match:
                            indice_do_numero = match.start()
                            ticker_base = ativo[:indice_do_numero] + '.SA'  # Cria o radical, ex: 'PETR.SA'
                            info_ativo = MAPA_GERAL_ATIVOS.get(ticker_base,
                                                               {'setor': 'Outros'})  # Tenta a busca de novo
                        else:
                            info_ativo = {'setor': 'Outros'}  # Se não tiver número, classifica como Outros

                    setor = info_ativo.get('setor', 'Outros')  # Busca segura final
                    # --- FIM DA LÓGICA ---

                    if setor in pesos_setor:
                        pesos_setor[setor] += peso
                    else:
                        pesos_setor[setor] = peso

                # Ordena setores por peso (maior para menor)
                setores_pesos_ordenados = sorted(pesos_setor.items(), key=lambda x: x[1], reverse=True)
                setores_ordenados = [item[0] for item in setores_pesos_ordenados]
                pesos_setores_ordenados = [item[1] for item in setores_pesos_ordenados]

                fig_pizza = go.Figure(data=[go.Pie(
                    labels=setores_ordenados, 
                    values=pesos_setores_ordenados, 
                    hole=.3,
                    textinfo='label+percent',
                    textfont=dict(size=12, color='white'),
                    marker=dict(
                        colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                    ),
                    sort=False,
                    direction='clockwise'
                )])
                fig_pizza.update_layout(
                    title=dict(text="Composição por Setor", font=dict(size=16, color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )

            st.plotly_chart(fig_pizza, use_container_width=True)

        with col2:
            st.subheader('Carteira vs. Benchmark')
            benchmark_selecionado = st.selectbox("Selecione o Benchmark:", list(MAPA_BENCHMARK.keys()))
            caminho_bench = os.path.join(DATA_PATH, MAPA_BENCHMARK[benchmark_selecionado])
            try:
                # Linha CORRIGIDA do Benchmark (removido skiprows)
                df_bench = pd.read_csv(caminho_bench, index_col='Date', parse_dates=True)
                df_bench = df_bench.reindex(df_portfolio.index).ffill().dropna()

                # Garantir que os dados são numéricos
                df_bench['Close'] = pd.to_numeric(df_bench['Close'], errors='coerce')
                df_portfolio['Carteira'] = pd.to_numeric(df_portfolio['Carteira'], errors='coerce')
                
                retornos_diarios_comp = pd.DataFrame(
                    {'Carteira': df_portfolio['Carteira'], 'Benchmark': df_bench['Close']}).pct_change().dropna()

                if retornos_diarios_comp.empty or len(retornos_diarios_comp) < 2:
                    st.warning(
                        f"Dados insuficientes para o benchmark '{benchmark_selecionado}' no período para gerar o gráfico.")
                else:
                    df_acumulado = (1 + retornos_diarios_comp).cumprod() * 100
                    df_acumulado.iloc[0] = 100
                    fig_desempenho = go.Figure()
                    fig_desempenho.add_trace(
                        go.Scatter(x=df_acumulado.index, y=df_acumulado['Carteira'], mode='lines',
                                   name='Minha Carteira'))
                    fig_desempenho.add_trace(go.Scatter(x=df_acumulado.index, y=df_acumulado['Benchmark'], mode='lines',
                                                        name=benchmark_selecionado))
                    fig_desempenho.update_layout(title_text='Desempenho Comparativo (Base 100)', template='plotly_dark')
                    st.plotly_chart(fig_desempenho, use_container_width=True)
            except Exception as e:
                st.error(
                    f"Não foi possível carregar ou processar os dados do benchmark '{benchmark_selecionado}'. Verifique o arquivo .csv. Erro: {e}")

        st.markdown("---")

        ## ------------------------------------


        # --- Seção 2: Otimização, Guia e Projeções (Tudo em Um) ---
        
        # --- CONTROLES UNIFICADOS NA SIDEBAR ---
        num_carteiras_simuladas = st.sidebar.slider('Simulações de Markowitz', 1000, 10000, 5000, key='sim_markowitz')
        valor_investimento = st.sidebar.number_input("Valor do Investimento (R$)", min_value=1000.0, value=50000.0,
                                                     step=1000.0, key='val_investimento')
        anos_projecao = st.sidebar.slider("Anos de Projeção (Monte Carlo)", 1, 30, 10, key='anos_projecao')
        num_simulacoes_mc = st.sidebar.select_slider("Simulações de Monte Carlo", options=[100, 250, 500],
                                                     value=250, key='sim_mc')


        # Inicializa o estado da sessão para guardar todos os resultados
        if 'resultados_gerados' not in st.session_state:
            st.session_state.resultados_gerados = None

        # Funções de comparação de algoritmos
        def risk_parity_puro(matriz_covariancia):
            """
            Implementa Risk Parity puro (contribuição igual de risco)
            """
            n_ativos = len(matriz_covariancia)
            # Inicializar com pesos iguais
            pesos = np.ones(n_ativos) / n_ativos
            
            # Iterar até convergir para contribuições iguais de risco
            for _ in range(50):
                # Calcular contribuição de risco atual
                risco_portfolio = np.sqrt(np.dot(pesos.T, np.dot(matriz_covariancia, pesos)))
                contribuicao_risco = (pesos * np.dot(matriz_covariancia, pesos)) / risco_portfolio
                
                # Ajustar pesos para equalizar contribuições
                contribuicao_media = np.mean(contribuicao_risco)
                for i in range(n_ativos):
                    if contribuicao_risco[i] > contribuicao_media:
                        pesos[i] *= 0.95
                    else:
                        pesos[i] *= 1.05
                
                # Normalizar para soma = 1
                pesos = pesos / np.sum(pesos)
            
            return pesos
        
        def markowitz_hibrido_v2(pesos_markowitz, pesos_risk_parity, proporcao=0.5):
            """
            Versão 2: Mistura 50% Markowitz + 50% Risk Parity
            """
            pesos_hibridos = proporcao * pesos_markowitz + (1 - proporcao) * pesos_risk_parity
            return pesos_hibridos / np.sum(pesos_hibridos)  # Normalizar

        # Função Risk Parity Híbrido (definida fora do botão para melhor performance)
        def risk_parity_hibrido(pesos_markowitz, matriz_covariancia, threshold=None, max_iter=20):
            """
            Implementa Risk Parity Híbrido para balancear carteiras concentradas
            
            Args:
                pesos_markowitz: Pesos do Markowitz tradicional
                matriz_covariancia: Matriz de covariância dos ativos
                threshold: Limite máximo de contribuição de risco (calculado automaticamente se None)
                max_iter: Número máximo de iterações
            
            Returns:
                pesos_hibridos: Pesos balanceados com Risk Parity
            """
            # Calcular threshold dinâmico baseado no número de ativos
            if threshold is None:
                n_ativos = len(pesos_markowitz)
                if n_ativos == 2:
                    # Para 2 ativos: máximo 50% cada (risk parity ideal)
                    threshold = 0.5
                elif n_ativos == 3:
                    # Para 3 ativos: máximo 40% cada (mais restritivo)
                    threshold = 0.40
                elif n_ativos == 4:
                    # Para 4 ativos: máximo 35% cada
                    threshold = 0.35
                else:
                    # Para 5+ ativos: máximo 30% cada (mais conservador)
                    threshold = 0.30
            
            pesos = pesos_markowitz.copy()
            
            for iteracao in range(max_iter):
                # Calcular contribuição de risco de cada ativo
                risco_portfolio = np.sqrt(np.dot(pesos.T, np.dot(matriz_covariancia, pesos)))
                contribuicao_risco = (pesos * np.dot(matriz_covariancia, pesos)) / risco_portfolio
                
                # Verificar se há concentração excessiva
                max_contribuicao = np.max(contribuicao_risco)
                
                if max_contribuicao <= threshold:
                    break  # Carteira já está balanceada
                
                # Identificar ativo com maior contribuição
                ativo_problematico = np.argmax(contribuicao_risco)
                
                # Reduzir peso do ativo problemático mais agressivamente
                reducao = (contribuicao_risco[ativo_problematico] - threshold) * 0.9
                peso_original = pesos[ativo_problematico]
                pesos[ativo_problematico] = peso_original * (1 - reducao)
                
                # Redistribuir o peso reduzido igualmente entre outros ativos
                outros_ativos = [i for i in range(len(pesos)) if i != ativo_problematico]
                if outros_ativos:
                    peso_redistribuido = peso_original * reducao
                    incremento_por_ativo = peso_redistribuido / len(outros_ativos)
                    for i in outros_ativos:
                        pesos[i] += incremento_por_ativo
                
                # Normalizar para garantir que soma = 1
                pesos = pesos / np.sum(pesos)
                
                # Garantir que todos os pesos sejam positivos (mínimo 5%)
                pesos = np.maximum(pesos, 0.05)
                pesos = pesos / np.sum(pesos)
            
            return pesos

        if st.button('Clique aqui para Otimização e Projeções', type='primary', use_container_width=True):
            with st.spinner('Realizando todos os cálculos... Isso pode levar um momento.'):
                
                # 1. CÁLCULO DE MARKOWITZ + RISK PARITY HÍBRIDO
                retornos_diarios = df_portfolio[ativos_selecionados].pct_change().dropna()
                matriz_covariancia = retornos_diarios.cov() * PREGOES_NO_ANO

                resultados_retorno, resultados_risco, resultados_sharpe, matriz_pesos = [[] for _ in range(4)]
                for i in range(num_carteiras_simuladas):
                    pesos_sim = np.random.random(len(ativos_selecionados))
                    pesos_sim /= np.sum(pesos_sim)
                    matriz_pesos.append(pesos_sim)
                    retorno = np.sum(retornos_diarios.mean() * pesos_sim) * PREGOES_NO_ANO
                    risco = np.sqrt(np.dot(pesos_sim.T, np.dot(matriz_covariancia, pesos_sim)))
                    resultados_retorno.append(retorno)
                    resultados_risco.append(risco)
                    resultados_sharpe.append((retorno - TAXA_LIVRE_DE_RISCO) / risco)

                st.session_state.resultados_otimizacao = {
                    'risco': np.array(resultados_risco), 'retorno': np.array(resultados_retorno),
                    'sharpe': np.array(resultados_sharpe),
                    'pesos': matriz_pesos,
                    'retornos_individuais': retornos_diarios.mean() * PREGOES_NO_ANO,
                    'volatilidades_individuais': retornos_diarios.std() * np.sqrt(PREGOES_NO_ANO)
                }
                st.session_state.ativos_otimizados = ativos_selecionados.copy()


                res_markowitz = {
                    'risco': np.array(resultados_risco), 'retorno': np.array(resultados_retorno),
                    'sharpe': np.array(resultados_sharpe), 'pesos': matriz_pesos,
                    'retornos_individuais': retornos_diarios.mean() * PREGOES_NO_ANO,
                    'volatilidades_individuais': retornos_diarios.std() * np.sqrt(PREGOES_NO_ANO)
                }
                indice_max_sharpe = np.argmax(resultados_sharpe)
                pesos_markowitz_puro = matriz_pesos[indice_max_sharpe]
                
                # CALCULAR PESOS PARA OS DIFERENTES ALGORITMOS
                pesos_risk_parity_puro = risk_parity_puro(matriz_covariancia)
                
                # USAR HÍBRIDO V2 (50/50) COMO ALGORITMO PRINCIPAL
                pesos_otimos = markowitz_hibrido_v2(pesos_markowitz_puro, pesos_risk_parity_puro, 0.5)
                
                # Salvar comparações no session state (para referência futura)
                st.session_state.comparacao_algoritmos = {
                    "markowitz_puro": pesos_markowitz_puro,
                    "hibrido_atual": risk_parity_hibrido(pesos_markowitz_puro, matriz_covariancia),
                    "risk_parity_puro": pesos_risk_parity_puro,
                    "hibrido_v2": pesos_otimos,
                    "ativos": ativos_selecionados
                }
                
                # Recalcular métricas com pesos híbridos
                retorno_hibrido = np.sum(retornos_diarios.mean() * pesos_otimos) * PREGOES_NO_ANO
                risco_hibrido = np.sqrt(np.dot(pesos_otimos.T, np.dot(matriz_covariancia, pesos_otimos)))
                sharpe_hibrido = (retorno_hibrido - TAXA_LIVRE_DE_RISCO) / risco_hibrido
                
                # Salvar pesos híbridos na matriz de resultados
                matriz_pesos[indice_max_sharpe] = pesos_otimos
                resultados_retorno[indice_max_sharpe] = retorno_hibrido
                resultados_risco[indice_max_sharpe] = risco_hibrido
                resultados_sharpe[indice_max_sharpe] = sharpe_hibrido

                # 2. BUSCA DE PREÇOS E GUIA DE INVESTIMENTO (CÓDIGO MOVIDO)
                res = st.session_state.resultados_otimizacao
                indice_max_sharpe = res['sharpe'].argmax()
                pesos_otimos = res['pesos'][indice_max_sharpe]
                dados_recentes = yf.download(ativos_selecionados, period="5d", auto_adjust=False)['Close']
                ultimos_precos = dados_recentes.iloc[-1]
                df_guia = pd.DataFrame({'Ativo': ativos_selecionados, 'Peso (%)': [p * 100 for p in pesos_otimos]})

                df_guia['Valor a Investir (R$)'] = df_guia['Peso (%)'] / 100 * valor_investimento
                df_guia['Último Preço (R$)'] = df_guia['Ativo'].map(ultimos_precos)
                
                # Tratamento para evitar NaN e infinitos na conversão
                df_guia['Último Preço (R$)'] = df_guia['Último Preço (R$)'].fillna(0)
                df_guia['Último Preço (R$)'] = df_guia['Último Preço (R$)'].replace([np.inf, -np.inf], 0)
                
                quantidade_calc = df_guia['Valor a Investir (R$)'] / df_guia['Último Preço (R$)']
                quantidade_calc = quantidade_calc.replace([np.inf, -np.inf], 0)
                quantidade_calc = quantidade_calc.fillna(0)
                df_guia['Quantidade de Ações'] = quantidade_calc.astype(int)

                # 3. CÁLCULO DE MONTE CARLO
                retorno_anual_esperado = resultados_retorno[indice_max_sharpe]
                risco_anual_esperado = resultados_risco[indice_max_sharpe]
                retorno_diario_medio = retorno_anual_esperado / PREGOES_NO_ANO
                volatilidade_diaria = risco_anual_esperado / np.sqrt(PREGOES_NO_ANO)
                dias_projecao = anos_projecao * PREGOES_NO_ANO
                matriz_resultados = np.zeros((dias_projecao, num_simulacoes_mc))
                for i in range(num_simulacoes_mc):
                    retornos_aleatorios = np.random.normal(retorno_diario_medio, volatilidade_diaria, dias_projecao)
                    caminho_patrimonio = np.zeros(dias_projecao)
                    caminho_patrimonio[0] = valor_investimento * (1 + retornos_aleatorios[0])
                    for j in range(1, dias_projecao):
                        caminho_patrimonio[j] = caminho_patrimonio[j - 1] * (1 + retornos_aleatorios[j])
                    matriz_resultados[:, i] = caminho_patrimonio

                df_simulacao = pd.DataFrame(matriz_resultados)
                datas_projecao = pd.bdate_range(start=datetime.now().date(), periods=dias_projecao)
                df_simulacao.index = datas_projecao
                fig_mc = go.Figure()
                simulacoes_a_mostrar = min(num_simulacoes_mc, 500)
                for i in range(simulacoes_a_mostrar):
                    fig_mc.add_trace(go.Scatter(x=df_simulacao.index, y=df_simulacao.iloc[:, i], mode='lines',
                                                line=dict(width=1, color='lightblue'), showlegend=False,
                                                opacity=0.1))
                fig_mc.add_trace(
                    go.Scatter(x=df_simulacao.index, y=df_simulacao.quantile(0.05, axis=1), mode='lines',
                               line=dict(color='red', width=2), name='Pior Cenário (5%)'))
                fig_mc.add_trace(
                    go.Scatter(x=df_simulacao.index, y=df_simulacao.quantile(0.50, axis=1), mode='lines',
                               line=dict(color='orange', width=3), name='Cenário Mediano (50%)'))
                fig_mc.add_trace(
                    go.Scatter(x=df_simulacao.index, y=df_simulacao.quantile(0.95, axis=1), mode='lines',
                               line=dict(color='lightgreen', width=2), name='Melhor Cenário (95%)'))
                fig_mc.update_layout(title_text=f'Projeção de Patrimônio em {anos_projecao} Anos',
                                     xaxis_title='Data', yaxis_title='Patrimônio (R$)', template='plotly_dark',
                                     showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                patrimonio_final_mediano = df_simulacao.iloc[-1].median()
                patrimonio_final_pior_cenario = df_simulacao.iloc[-1].quantile(0.05)
                patrimonio_final_melhor_cenario = df_simulacao.iloc[-1].quantile(0.95)

                # 4. SALVAR TUDO EM UM ÚNICO LUGAR
                st.session_state.resultados_gerados = {
                    "markowitz": res,
                    "guia_investimento": df_guia,
                    "ativos_otimizados": ativos_selecionados.copy(),
                    "monte_carlo_fig": fig_mc,
                    "monte_carlo_text_data": {
                        'investimento': valor_investimento, 'simulacoes': num_simulacoes_mc, 'anos': anos_projecao,
                        'mediano': patrimonio_final_mediano, 'pior': patrimonio_final_pior_cenario,
                        'melhor': patrimonio_final_melhor_cenario
                    },
                    "parametros": {
                        'anos_projecao': anos_projecao,
                        'num_simulacoes_mc': num_simulacoes_mc,
                        'valor_investimento': valor_investimento
                    }
                }

        # --- DETECÇÃO DE MUDANÇAS NOS ATIVOS E PARÂMETROS ---
        # Verificar se os ativos ou parâmetros mudaram desde a última otimização
        if st.session_state.resultados_gerados:
            ativos_otimizados_anteriores = st.session_state.resultados_gerados.get("ativos_otimizados", [])
            parametros_anteriores = st.session_state.resultados_gerados.get("parametros", {})
            
            # Verificar mudanças nos ativos
            ativos_mudaram = set(ativos_selecionados) != set(ativos_otimizados_anteriores)
            
            # Verificar mudanças nos parâmetros de Monte Carlo
            parametros_mudaram = (
                parametros_anteriores.get('anos_projecao', 5) != anos_projecao or
                parametros_anteriores.get('num_simulacoes_mc', 250) != num_simulacoes_mc or
                parametros_anteriores.get('valor_investimento', 50000.0) != valor_investimento
            )
            
            if ativos_mudaram or parametros_mudaram:
                if ativos_mudaram:
                    st.warning("⚠️ **Atenção:** Você alterou a seleção de ativos. Os resultados anteriores não são mais válidos. Clique no botão 'Otimização e Projeções' para recalcular.")
                else:
                    st.warning("⚠️ **Atenção:** Você alterou os parâmetros de projeção (anos, simulações ou valor de investimento). Os resultados anteriores não são mais válidos. Clique no botão 'Otimização e Projeções' para recalcular.")
                st.session_state.resultados_gerados = None
                st.stop()

        # --- BLOCO DE EXIBIÇÃO (SÓ MOSTRA OS RESULTADOS) ---
        if st.session_state.resultados_gerados:
            resultados = st.session_state.resultados_gerados
            res = resultados["markowitz"]
            ativos_otimizados = resultados["ativos_otimizados"]
            indice_max_sharpe = res['sharpe'].argmax()
            pesos_otimos = res['pesos'][indice_max_sharpe]
            indice_min_risco = res['risco'].argmin()

            # --- COMPOSIÇÃO DA CARTEIRA ÓTIMA E MÉTRICAS ---
            col_pizza_otima, col_metricas = st.columns([1, 1])
            
            with col_pizza_otima:
                st.subheader('Composição da Carteira Ótima (Markowitz + Risk Parity)')
                # Criar DataFrame com os pesos ótimos
                df_pesos_otimos = pd.DataFrame(pesos_otimos, index=ativos_otimizados, columns=['Peso'])
                
                # --- ALTERAÇÃO AQUI: Criando as legendas personalizadas ---
                legendas_personalizadas = [f"{ativo} ({peso:.2%})" for ativo, peso in
                                           df_pesos_otimos['Peso'].items()]

                # Ordena a carteira ótima por peso (maior para menor)
                df_pesos_otimos_ordenado = df_pesos_otimos.sort_values('Peso', ascending=False)
                legendas_personalizadas_ordenadas = [f"{ativo} ({peso:.2%})" for ativo, peso in df_pesos_otimos_ordenado['Peso'].items()]

                fig_pie_otima = go.Figure(
                    data=[go.Pie(
                        labels=legendas_personalizadas_ordenadas,
                        values=df_pesos_otimos_ordenado['Peso'],
                        hole=.3,
                        textinfo='percent',
                        textfont=dict(size=12, color='white'),
                        marker=dict(
                            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                        ),
                        sort=False,
                        direction='clockwise'
                    )]
                )

                fig_pie_otima.update_layout(
                    #title=dict(text="Carteira Ótima", font=dict(size=16, color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1.3,
                        xanchor="left",
                        x=0.02
                    )
                )
                st.plotly_chart(fig_pie_otima, use_container_width=True)
            
            with col_metricas:
                st.subheader('Carteira Atual vs Carteira Otimizada')
                
                # Garantir que todos os arrays tenham o mesmo tamanho
                # Usar apenas os ativos que estão na carteira otimizada
                ativos_comparacao = ativos_otimizados
                pesos_atuais_comparacao = [pesos[i] if i < len(pesos) else 0 for i in range(len(ativos_comparacao))]
                pesos_otimos_comparacao = pesos_otimos
                
                # Criar gráfico de barras horizontais
                fig_comparacao = go.Figure()
                
                # Adicionar barras para carteira atual
                fig_comparacao.add_trace(go.Bar(
                    y=ativos_comparacao,
                    x=[p * 100 for p in pesos_atuais_comparacao],
                    name='Carteira Atual',
                    orientation='h',
                    marker_color='#FF6B6B',
                    text=[f"{p*100:.1f}%" for p in pesos_atuais_comparacao],
                    textposition='auto',
                    textfont=dict(size=14, color='white'),
                    texttemplate='%{text}'
                ))
                    
                # Adicionar barras para carteira otimizada
                fig_comparacao.add_trace(go.Bar(
                    y=ativos_comparacao,
                    x=[p * 100 for p in pesos_otimos_comparacao],
                    name='Carteira Otimizada',
                    orientation='h',
                    marker_color='#4ECDC4',
                    text=[f"{p*100:.1f}%" for p in pesos_otimos_comparacao],
                    textposition='auto',
                    textfont=dict(size=14, color='white'),
                    texttemplate='%{text}'
                ))
                
                fig_comparacao.update_layout(
                    title='Comparação de Pesos por Ativo',
                    xaxis_title='Porcentagem (%)',
                    yaxis_title='Ativos',
                    template='plotly_dark',
                    height=400,
                    barmode='group',
                    margin=dict(l=100, r=100, t=50, b=50)  # Aumenta margem direita para acomodar texto fora das barras
                )
                
                # Exibir apenas o gráfico (sem tabela)
                st.plotly_chart(fig_comparacao, use_container_width=True)
            
            st.markdown("---")

            # --- MÉTRICAS DOS ATIVOS ---
            st.subheader('Métricas dos Ativos')

            # Remover st.info de debug após a correção
            # st.info("🔍 **Debug ativo** - Investigando por que os dividendos estão zerados") 

            # Buscar dados de dividendos para calcular retorno total
            try:
                # Criar lista de tickers sem .SA para buscar dividendos
                tickers_yf_pure = [ativo.replace('.SA', '') for ativo in ativos_otimizados]
                
                # Listas para armazenar os resultados por ativo
                dividend_yield_anualizado = []
                retornos_preco_12m_list = [] # Renomeada para evitar conflito de nome no loop
                
                for i, ticker_pure in enumerate(tickers_yf_pure):
                    ticker_full = f"{ticker_pure}.SA"
                    
                    # Iniciar valores para o caso de erro ou dados insuficientes
                    retorno_preco_ativo = 0.0
                    yield_dividendo_ativo = 0.0

                    try:
                        # 1. Buscar histórico de preços do último ano (aproximadamente 252 pregões)
                        # Usar period="1y" para alinhar com o cálculo do retorno de preço
                        ticker_data = yf.Ticker(ticker_full)
                        hist = ticker_data.history(period="1y", interval="1d") # interval="1d" para garantir diário
                        
                        if hist.empty or len(hist) < 2:
                            # Dados insuficientes, adicionar 0 e pular para o próximo ativo
                            retornos_preco_12m_list.append(retorno_preco_ativo)
                            dividend_yield_anualizado.append(yield_dividendo_ativo)
                            continue # Pula para o próximo ativo no loop

                        # Data de referência: o último dia de pregão no histórico
                        data_fim_periodo = hist.index[-1]
                        data_inicio_periodo = hist.index[0] # Preço inicial para cálculo do yield

                        # Calcular retorno de preço dos últimos 12 meses
                        retorno_preco_ativo = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100 # Em percentual
                        
                        # 2. Calcular dividendos pagos no período de 12 meses (alinhado com o histórico)
                        dividendos_hist = ticker_data.dividends
                        
                        if not dividendos_hist.empty:
                            # Filtrar dividendos que caíram DENTRO do período de 12 meses de `hist`
                            # Margem de 7 dias antes para capturar o começo do ano fiscal ou último dividendo
                            data_limite_dividendos = data_fim_periodo - pd.DateOffset(months=12, days=-7) 
                            
                            # Se o histórico de dividendos é curto, ajusta a data limite para não perder nenhum
                            if not dividendos_hist.empty and dividendos_hist.index.min() > data_limite_dividendos:
                                data_limite_dividendos = dividendos_hist.index.min()

                            dividendos_no_periodo = dividendos_hist[
                                (dividendos_hist.index >= data_limite_dividendos) &
                                (dividendos_hist.index <= data_fim_periodo)
                            ]
                            
                            soma_dividendos_brutos = dividendos_no_periodo.sum()

                            # 3. Calcular yield de dividendos (dividendos / preço inicial do período)
                            # O preço inicial do período é mais consistente para o retorno total
                            preco_referencia_yield = hist['Close'].iloc[0] # Preço no início dos 12 meses

                            if preco_referencia_yield > 0:
                                yield_dividendo_ativo = (soma_dividendos_brutos / preco_referencia_yield) * 100
                            else:
                                yield_dividendo_ativo = 0.0
                            
                            # Limitar yield a um valor razoável (máximo 50% ao ano)
                            yield_dividendo_ativo = min(yield_dividendo_ativo, 50.0)
                            
                        # Adiciona os resultados (mesmo que sejam 0.0)
                        retornos_preco_12m_list.append(retorno_preco_ativo)
                        dividend_yield_anualizado.append(yield_dividendo_ativo)
                        
                    except Exception as e:
                        # Em caso de erro para um ativo específico, adicionar 0 e seguir
                        st.warning(f"⚠️ Erro ao buscar dados para {ticker_full}: {e}. Usando 0 para retornos/dividendos.")
                        retornos_preco_12m_list.append(0.0)
                        dividend_yield_anualizado.append(0.0)
                
                # Calcular retorno total de forma consistente (soma dos retornos de preço e dividendos do mesmo período)
                retorno_total_12m = np.array(retornos_preco_12m_list) + np.array(dividend_yield_anualizado)
                
                # Criar DataFrame com dados consistentes (todos dos últimos 12 meses)
                df_metricas = pd.DataFrame({
                    'Ativo': ativos_otimizados,
                    'Retorno Preço (a.a.)': retornos_preco_12m_list,
                    'Yield Dividendos (a.a.)': dividend_yield_anualizado,
                    'Retorno Total (a.a.)': retorno_total_12m,
                    'Volatilidade (a.a.)': np.array(res['volatilidades_individuais']) * 100 # Volatilidade já vem anualizada, converter para %
                })
                
                st.dataframe(df_metricas, column_config={
                    "Retorno Preço (a.a.)": st.column_config.ProgressColumn("Retorno Preço (a.a.)", format="%.1f%%", min_value=-50, max_value=100),
                    "Yield Dividendos (a.a.)": st.column_config.ProgressColumn("Yield Dividendos (a.a.)", format="%.1f%%", min_value=0, max_value=15),
                    "Retorno Total (a.a.)": st.column_config.ProgressColumn("Retorno Total (a.a.)", format="%.1f%%", min_value=-50, max_value=100),
                    "Volatilidade (a.a.)": st.column_config.ProgressColumn("Volatilidade (a.a.)", format="%.0f%%", min_value=0, max_value=100)
                }, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"Erro geral no cálculo de métricas: {e}")
                # Fallback: calcular retorno de preço dos últimos 12 meses mesmo sem dividendos
                retornos_preco_12m_fallback = []
                for ticker_pure in [ativo.replace('.SA', '') for ativo in ativos_otimizados]:
                    try:
                        hist = yf.Ticker(f"{ticker_pure}.SA").history(period="1y")
                        if len(hist) > 1:
                            retorno_preco = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1
                            retornos_preco_12m_fallback.append(retorno_preco * 100)
                        else:
                            retornos_preco_12m_fallback.append(0.0)
                    except:
                        retornos_preco_12m_fallback.append(0.0)
                
                df_metricas_fallback = pd.DataFrame({
                    'Ativo': ativos_otimizados,
                    'Retorno Preço (a.a.)': retornos_preco_12m_fallback,
                    'Volatilidade (a.a.)': np.array(res['volatilidades_individuais']) * 100 # Volatilidade também em %
                })
                st.dataframe(df_metricas_fallback, column_config={
                    "Retorno Preço (a.a.)": st.column_config.ProgressColumn("Retorno Preço (a.a.)", format="%.1f%%", min_value=-50, max_value=100),
                    "Volatilidade (a.a.)": st.column_config.ProgressColumn("Volatilidade (a.a.)", format="%.0f%%", min_value=0, max_value=100)
                }, use_container_width=True, hide_index=True)
                st.warning("⚠️ Não foi possível carregar dados completos para as métricas. Mostrando apenas retorno de preços dos últimos 12 meses e volatilidade.")

            # Legendas abaixo da tabela com linguagem mais acessível
            st.markdown("---") # Separador para o conteúdo abaixo
            
            # Explicação das métricas em expander
            with st.expander("💡 **Entenda as métricas da tabela**", expanded=False):
                st.markdown("""
                **Retorno Preço (a.a.):** É o quanto o preço do ativo subiu ou desceu nos últimos 12 meses, expresso em porcentagem anual. *Exemplo: 10% significa que o preço do ativo valorizou 10% em um ano.*
                
                **Yield Dividendos (a.a.):** É a porcentagem dos rendimentos que o ativo pagou em dividendos (ou proventos) nos últimos 12 meses, em relação ao seu preço inicial. É o quanto você recebeu de volta em dinheiro. *Exemplo: 5% significa que você recebeu 5% do valor inicial do ativo em dividendos.*
                
                **Retorno Total (a.a.):** É a soma de todo o ganho que o ativo gerou nos últimos 12 meses, considerando tanto a valorização do preço quanto os dividendos pagos. É o ganho completo do seu investimento. *Exemplo: Se o Retorno de Preço foi 7% e o Yield de Dividendos foi 3%, o Retorno Total é 10%.*
                
                **Volatilidade (a.a.):** Indica o 'balanço' ou a 'instabilidade' do preço do ativo ao longo do ano. Quanto maior a volatilidade, maior a variação (para cima ou para baixo) e, geralmente, maior o risco. *Exemplo: 20% de volatilidade significa que o preço pode oscilar bastante para cima ou para baixo em torno da média.*
                """)
            
            st.markdown("---") # Separador final

            # EXIBIÇÃO DE MONTE CARLO
            st.subheader("Projeção de Patrimônio Futuro (Monte Carlo)")
            
            col_graf_mc, col_metricas_mc = st.columns([2, 1])
            
            with col_graf_mc:
                st.plotly_chart(resultados["monte_carlo_fig"], use_container_width=True)
            
            with col_metricas_mc:
                res_mc_text = resultados["monte_carlo_text_data"]
                
                # 1. Pega os dados do dicionário e calcula as porcentagens de retorno
                investimento_inicial = res_mc_text['investimento']
                retorno_mediano_pct = (res_mc_text['mediano'] / investimento_inicial - 1) * 100
                retorno_otimista_pct = (res_mc_text['melhor'] / investimento_inicial - 1) * 100
                retorno_pessimista_pct = (res_mc_text['pior'] / investimento_inicial - 1) * 100

                # Calcula a data final da projeção
                data_final_projecao = datetime.now().date() + timedelta(days=res_mc_text['anos'] * 365)

                # 2. Exibe o resumo em 4 linhas com st.metric
                st.metric(
                    label=f"Cenário Atual ({datetime.now().strftime('%d %b %Y')})",
                    value=f"R$ {investimento_inicial:,.2f}",
                    delta="0.00%"
                )
                
                st.metric(
                    label=f"Esperado ({data_final_projecao.strftime('%d %b %Y')})",
                    value=f"R$ {res_mc_text['mediano']:,.2f}",
                    delta=f"{retorno_mediano_pct:.2f}%"
                )
                
                st.metric(
                    label=f"Otimista ({data_final_projecao.strftime('%d %b %Y')})",
                    value=f"R$ {res_mc_text['melhor']:,.2f}",
                    delta=f"{retorno_otimista_pct:.2f}%"
                )
                
                st.metric(
                    label=f"Pessimista ({data_final_projecao.strftime('%d %b %Y')})",
                    value=f"R$ {res_mc_text['pior']:,.2f}",
                    delta=f"{retorno_pessimista_pct:.2f}%"
                )
            
            # Explicação do Monte Carlo com botão de recolher/expandir
            with st.expander("Como Ler o Gráfico da Simulação?", expanded=False):
                st.markdown(f"""
                Nós criamos {res_mc_text['simulacoes']} simulações de como sua carteira de investimentos **(R$ {res_mc_text['investimento']:,.2f})** poderia se comportar nos próximos **{res_mc_text['anos']} anos**. Este gráfico resume tudo isso.

                **🎯 O Alvo Principal (Linha Laranja):**
                Esta linha no meio representa o **resultado central** de todas as simulações. É o valor mais provável que seu patrimônio pode atingir, chegando a cerca de **R$ {res_mc_text['mediano']:,.2f}**.

                **↔️ A Faixa de Resultados Realista:**
                Nossa análise mostra uma probabilidade de 90% de que o patrimônio final fique na seguinte faixa:
                
                • **Cenário Pessimista:** R$ {res_mc_text['pior']:,.2f}
                
                • **Cenário Otimista:** R$ {res_mc_text['melhor']:,.2f}

                **O que fazer com essa informação?**
                Use esta projeção para ter uma ideia se o plano de investimentos atual está alinhado com seus sonhos. A faixa de valores te dá uma visão realista do que esperar, ajudando a planejar o futuro com mais segurança e menos surpresas.

                **Obs.:** Lembrando que, caso deseje alterar, o valor inicial da carteira está na aba lateral!
                """)

            

            # EXIBIÇÃO DE MARKOWITZ
            st.subheader('Fronteira Eficiente Markowitz (Versão Híbrida de risco)')
            
            # Gráfico com altura reduzida
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.scatter(res['risco'], res['retorno'], c=res['sharpe'], cmap='viridis', marker='.', s=5,
                       alpha=0.4)

            cores_ativos = ['#FF4B4B', '#3E6D8E', '#6B4E9A']
            for i, ticker in enumerate(st.session_state.ativos_otimizados):
                ax.scatter(res['volatilidades_individuais'].iloc[i], res['retornos_individuais'].iloc[i], marker='D',
                           color=cores_ativos[i % len(cores_ativos)], s=150, label=ticker, zorder=5)

            ax.scatter(res['risco'][indice_min_risco], res['retorno'][indice_min_risco], marker='X',
                       color='red', s=200, label='Carteira Risco Mínimo', zorder=5)
            ax.scatter(res['risco'][indice_max_sharpe], res['retorno'][indice_max_sharpe], marker='*',
                       color='gold', s=300, label='Carteira Sharpe Máximo', zorder=5)

            ax.set_title('Otimização de Portfólio', fontsize=12)
            ax.set_xlabel('Risco (Volatilidade)', fontsize=10)
            ax.set_ylabel('Retorno Esperado', fontsize=10)
            ax.legend(loc='upper right', fontsize=8)
            st.pyplot(fig)
            
            # Texto recolhível abaixo do gráfico
            with st.expander("📖 **Clique para entender o Gráfico de Markowitz (Versão Híbrida de risco)**", expanded=False):
                st.markdown("**O que é?**")
                st.markdown("Uma teoria vencedora do Prêmio Nobel que provou matematicamente o velho ditado: 'não coloque todos os ovos na mesma cesta'. A ideia é que, ao combinar ativos diferentes, você pode reduzir o risco geral da sua carteira sem sacrificar muito do seu retorno.")
                
                st.markdown("**🔄 Versão Híbrida de risco:**")
                st.markdown("Nossa implementação combina o Markowitz tradicional com técnicas de Risk Parity, garantindo carteiras mais diversificadas e praticáveis, evitando concentração excessiva em poucos ativos.")
                
                st.markdown("**O que o gráfico significa?**")
                st.markdown("• **Eixo Vertical (Retorno):** Quanto mais alto, melhor.")
                st.markdown("• **Eixo Horizontal (Risco):** Quanto mais para a **esquerda**, melhor.")
                st.markdown("• **Nuvem de Pontos:** Cada ponto é uma carteira possível com uma combinação de pesos diferente. A cor indica a qualidade (relação risco/retorno), sendo amarelo a melhor.")
                st.markdown("• **Estrela Dourada (★):** A carteira 'ótima', com o melhor equilíbrio entre risco e retorno.")
                st.markdown("• **'X' Vermelho:** A carteira com o menor risco possível.")
                
                st.markdown("**Como usar?**")
                st.markdown("Compare a posição dos ativos individuais (losangos) com as estrelas. O gráfico te ajuda a visualizar o poder da diversificação: ao combinar os ativos, é possível criar carteiras (as estrelas) que são melhores do que qualquer um dos ativos sozinhos.")

            # EXIBIÇÃO DO GUIA DE INVESTIMENTO (OCUPANDO TODA A LARGURA)
            st.markdown("---")
            st.subheader("Guia de Investimento para a Carteira Ótima")
            
            # Dataframe ocupando toda a largura disponível
            st.dataframe(resultados["guia_investimento"],
                            column_config={
                                "Peso (%)": st.column_config.ProgressColumn("Peso (%)", format="%.1f%%", min_value=0,
                                                                            max_value=100),
                                "Valor a Investir (R$)": st.column_config.NumberColumn("Valor a Investir (R$)",
                                                                                    format="R$ %.2f"),
                                "Último Preço (R$)": st.column_config.NumberColumn("Último Preço (R$)",
                                                                                format="R$ %.2f"),
                                "Quantidade de Ações": st.column_config.NumberColumn("Qtde. Ações (aprox.)")
                            },
                            use_container_width=True,
                            hide_index=True,
                            #height=400
                            )

            if st.button("Limpar Análise"):
                st.session_state.resultados_gerados = None
                st.rerun()
                
            st.markdown("---")

            # Disclaimer para a Simulação de Monte Carlo
            st.warning("⚠️ **Disclaimer Importante sobre a Simulação:**")
            st.markdown("""
            As **simulações de Monte Carlo e Markowitz (Versão Híbrida de risco)**, são modelos matemáticos que utilizam dados históricos para projetar cenários futuros possíveis.
            """)
            st.markdown("""
            **Por favor, esteja ciente de que:**
            - **Não é uma garantia:** Os resultados apresentados são apenas projeções e **não constituem uma promessa ou garantia** de retornos futuros.
            - **Baseado em dados passados:** A simulação utiliza dados de desempenho passado, e o **desempenho passado não é um indicador confiável de resultados futuros.**
            - **Múltiplos cenários:** A simulação considera uma vasta gama de cenários possíveis, mas a **realidade pode divergir** significativamente das projeções.
            - **Propósito:** Esta ferramenta serve como um auxílio para **visualizar e entender a gama de possibilidades e riscos** associados ao investimento, ajudando na tomada de decisão informada.

            """)
            st.markdown("---")    
            
    else:
        st.warning('Por favor, selecione pelo menos um ativo para a análise.')

    # =============================================================================
    # --- BOTÕES DE LOGOUT E TROCAR SENHA (APENAS QUANDO LOGADO) ---
    # =============================================================================
    # Inicializar estados da sessão
    if 'confirming_logout' not in st.session_state:
        st.session_state.confirming_logout = False
    if 'show_change_password' not in st.session_state:
        st.session_state.show_change_password = False
    
    # --- BOTÕES NO FINAL DA SIDEBAR ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Configurações")
    
    # Botões um acima do outro para melhor alinhamento
    if st.sidebar.button("🚪 Logout", key="logout_logged_in", use_container_width=True):
        st.session_state.confirming_logout = True
        st.rerun()
    
    if st.sidebar.button("🔑 Trocar Senha", key="change_password_logged_in", use_container_width=True):
        st.session_state.show_change_password = True
        st.rerun()

    # Confirmação de logout
    if st.session_state.confirming_logout:
        st.sidebar.warning("Você tem certeza que deseja sair?")
        col1_logout, col2_logout = st.sidebar.columns(2)
        if col1_logout.button("Sim", use_container_width=True, type="primary", key="confirm_logout_yes"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if col2_logout.button("Não", use_container_width=True, key="confirm_logout_no"):
            st.session_state.confirming_logout = False
            st.rerun()

    # Interface de troca de senha
    if st.session_state.show_change_password:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔑 Trocar Senha")
        
        current_password = st.sidebar.text_input(
            "Senha Atual",
            type="password",
            placeholder="Digite sua senha atual",
            key="current_password"
        )
        new_password = st.sidebar.text_input(
            "Nova Senha",
            type="password",
            placeholder="Digite sua nova senha",
            key="new_password_change"
        )
        confirm_password = st.sidebar.text_input(
            "Confirmar Nova Senha",
            type="password",
            placeholder="Confirme sua nova senha",
            key="confirm_password_change"
        )
        
        col_change1, col_change2 = st.sidebar.columns(2)
        
        with col_change1:
            if st.sidebar.button("✅ Salvar", use_container_width=True, key="save_new_password"):
                if current_password and new_password and confirm_password:
                    # Verificar senha atual
                    login_result = check_login(st.session_state["email"], current_password)
                    is_logged_in = login_result[0] if login_result else False
                    if is_logged_in:
                        if new_password == confirm_password:
                            if len(new_password) >= 6:
                                success, message = update_password(st.session_state["email"], new_password)
                                if success:
                                    st.sidebar.success("Senha alterada com sucesso!")
                                    st.session_state.show_change_password = False
                                    st.rerun()
                                else:
                                    st.sidebar.error(f"Erro: {message}")
                            else:
                                st.sidebar.error("A senha deve ter pelo menos 6 caracteres.")
                        else:
                            st.sidebar.error("As senhas não coincidem.")
                    else:
                        st.sidebar.error("Senha atual incorreta.")
                else:
                    st.sidebar.error("Preencha todos os campos.")
        
        with col_change2:
            if st.sidebar.button("❌ Cancelar", use_container_width=True, key="cancel_password_change"):
                st.session_state.show_change_password = False
                st.rerun()

else:
    # Container responsivo para evitar overflow
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # LOGO CENTRALIZADO - APENAS IMAGEM
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    
    with col_logo2:
        try:
            # Tentar carregar o logo
            if os.path.exists("prints/slogan_preto.png"):
                st.image("prints/slogan_preto.png", width=800)
            else:
                st.error("Logo não encontrado: prints/slogan_preto.png")
        except Exception as e:
            st.error(f"Erro ao carregar logo: {e}")
    
    # Cards de Funcionalidades
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="background: var(--card-bg, #ffffff); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid var(--border-color, #e0e0e0); height: 250px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 3rem; margin-bottom: 20px;">⭐</div>
            <h3 style="color: #667eea; margin: 0 0 15px 0; font-size: 1.3rem;">Análise Markowitz</h3>
            <p style="color: #6c757d; font-size: 0.9rem; line-height: 1.4; margin: 0;">
                Otimização de carteiras com análise de risco e retorno, 
                encontrando a melhor combinação de ativos para seus objetivos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="background: var(--card-bg, #ffffff); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid var(--border-color, #e0e0e0); height: 250px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 3rem; margin-bottom: 20px;">📈</div>
            <h3 style="color: #667eea; margin: 0 0 15px 0; font-size: 1.3rem;">Simulação Monte Carlo</h3>
            <p style="color: #6c757d; font-size: 0.9rem; line-height: 1.4; margin: 0;">
                Projeções de cenários futuros com milhares de simulações, 
                ajudando você a tomar decisões mais informadas
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="background: var(--card-bg, #ffffff); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid var(--border-color, #e0e0e0); height: 250px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 3rem; margin-bottom: 20px;">⚡</div>
            <h3 style="color: #667eea; margin: 0 0 15px 0; font-size: 1.3rem;">Métricas em Tempo Real</h3>
            <p style="color: #6c757d; font-size: 0.9rem; line-height: 1.4; margin: 0;">
                Dados atualizados constantemente com análises de volatilidade, 
                Sharpe ratio e comparações com benchmarks
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Seção de Benefícios
    st.markdown("###  Por que escolher o Ponto Ótimo Invest?")
    
    col_ben1, col_ben2 = st.columns(2)
    
    with col_ben1:
        st.markdown("""
        **✅ Interface Intuitiva**  
        Design moderno e fácil de usar
        
        **✅ Análise Profissional**  
        Ferramentas de nível institucional
        
        **✅ Dados Confiáveis**  
        Fontes oficiais da B3 e CVM
        """)
    
    with col_ben2:
        st.markdown("""
        **✅ Otimização Avançada**  
        Algoritmos híbridos Markowitz + Risk Parity
        
        **✅ Projeções Realistas**  
        Simulações Monte Carlo precisas
        
        **✅ Suporte Especializado**  
        Atendimento personalizado
        """)
    
    # Call to Action com link para compra
    st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h2 style="color: #667eea; margin-bottom: 20px;">Ainda não tem acesso?</h2>
        <p style="color: #ccc; font-size: 1.1rem; margin-bottom: 30px;">
            Adquira agora e comece a otimizar seus investimentos
        </p>
        <a href="https://pontootimo.hotmart.host/carteira-ideal" target="_blank" style="
            background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 16px;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(255, 75, 75, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(255, 75, 75, 0.3)'">
            🛒 Comprar Agora
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Fechar container responsivo
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção de Login
    st.markdown("---")
    st.markdown("### 🔑 Já tem acesso? Faça login:")
    
    # Área principal - apenas espaçamento
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Sidebar com login melhorado
    st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: #ffffff; margin-bottom: 0;'>🔑 Login</h1>
        <p style='color: #cccccc; font-size: 14px; margin-top: 0.5rem;'>Acesse sua conta</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Preencher automaticamente se houver credenciais de ativação
    email_default = ""
    password_default = ""
    if "activation_credentials" in st.session_state:
        email_default = st.session_state["activation_credentials"]["email"]
        password_default = st.session_state["activation_credentials"]["senha"]
        # Limpar credenciais após usar
        del st.session_state["activation_credentials"]
    
    st.sidebar.markdown("**📧 Email:**")
    email = st.sidebar.text_input(
        "Email", 
        value=email_default,
        placeholder="seu@email.com",
        help="Digite o email cadastrado na Hotmart",
        label_visibility="collapsed"
    )
    st.sidebar.markdown("**🔒 Senha:**")
    password = st.sidebar.text_input(
        "Senha", 
        value=password_default,
        type="password",
        placeholder="Sua senha",
        help="Digite a senha da sua conta Hotmart",
        label_visibility="collapsed"
    )

    # Botão de login estilizado
    col_btn1, col_btn2, col_btn3 = st.sidebar.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 Entrar", type="primary", use_container_width=True):
            login_result = check_login(email, password)
            
            # Verificar se é primeiro acesso
            if len(login_result) == 7 and login_result[6] == "FIRST_ACCESS":
                is_logged_in, user_name, ultima_carteira, ultimos_pesos, data_inicio, data_fim, _ = login_result
                st.session_state["authentication_status"] = True
                st.session_state["name"] = user_name
                st.session_state["email"] = email
                st.session_state["ultima_carteira"] = ultima_carteira
                st.session_state["ultimos_pesos"] = ultimos_pesos
                st.session_state["data_inicio_salva"] = data_inicio
                st.session_state["data_fim_salva"] = data_fim
                st.session_state["force_password_change"] = True
                st.rerun()
            elif len(login_result) == 6:
                is_logged_in, user_name, ultima_carteira, ultimos_pesos, data_inicio, data_fim = login_result
                if is_logged_in:
                    st.session_state["authentication_status"] = True
                    st.session_state["name"] = user_name
                    st.session_state["email"] = email
                    st.session_state["ultima_carteira"] = ultima_carteira
                    st.session_state["ultimos_pesos"] = ultimos_pesos
                    st.session_state["data_inicio_salva"] = data_inicio
                    st.session_state["data_fim_salva"] = data_fim
                    st.rerun()
                else:
                    st.session_state["authentication_status"] = False
                    if user_name == "INACTIVE_SUBSCRIPTION":
                        st.sidebar.error("Sua assinatura não está ativa.")
                    elif user_name == "INVALID_HASH":
                        st.sidebar.error("⚠️ Sua senha precisa ser redefinida. Use o link abaixo.")
                        st.session_state["show_password_reset"] = True
                    else:
                        st.sidebar.error("Email ou senha incorreta.")

    # Botão "Esqueci minha senha"
    st.sidebar.markdown("---")
    
    # Botão de ajuda
    if st.sidebar.button("🔑 Esqueci minha senha", use_container_width=True):
        st.session_state["show_forgot_password"] = True
        st.rerun()
    
    # Informações de suporte
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;'>
        <h4 style='color: #333; margin-top: 0; margin-bottom: 10px;'>Precisa de ajuda?</h4>
        <p style='color: #667eea; font-weight: bold; margin: 5px 0 0 0; font-size: 12px;'>
            pontootimoinvest@gmail.com
        </p>
    </div>
    """, unsafe_allow_html=True)


    # Seção de "Esqueci minha senha"
    if st.session_state.get("show_forgot_password", False):
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔑 Esqueci minha senha")
        
        # Etapa 1: Verificação de email
        if not st.session_state.get("email_verificado"):
            email_verificacao = st.sidebar.text_input(
                "📧 Digite seu email para verificar",
                placeholder="seu@email.com",
                key="email_verificacao"
            )
            
            col_verify, col_close = st.sidebar.columns(2)
            
            with col_verify:
                if st.button("🔍 Verificar Email", use_container_width=True, key="verify_email_button"):
                    if email_verificacao:
                        try:
                            existe, nome = verificar_usuario_existe(email_verificacao)
                            if existe:
                                st.session_state["email_verificado"] = email_verificacao
                                st.session_state["nome_verificado"] = nome
                                st.sidebar.success(f"✅ Email encontrado!")
                                st.rerun()
                            else:
                                st.sidebar.error("❌ Email não encontrado. Verifique se digitou corretamente.")
                        except Exception as e:
                            st.sidebar.error(f"❌ Erro ao verificar email: {str(e)}")
                    else:
                        st.sidebar.error("❌ Por favor, digite um email válido.")
            
            with col_close:
                if st.button("❌ Fechar", use_container_width=True, key="close_forgot_password"):
                    st.session_state["show_forgot_password"] = False
                    st.session_state["email_verificado"] = None
                    st.session_state["nome_verificado"] = None
                    st.rerun()
        
        # Etapa 2: Verificação de nome completo
        elif not st.session_state.get("nome_confirmado"):
            st.sidebar.info("🔒 **Verificação de Segurança**")
            st.sidebar.markdown("Para sua segurança, confirme seu **nome completo** como cadastrado:")
            
            nome_digitado = st.sidebar.text_input(
                "👤 Nome completo",
                placeholder="Digite seu nome completo",
                key="nome_completo"
            )
            
            col_confirm, col_back = st.sidebar.columns(2)
            
            with col_confirm:
                if st.button("✅ Confirmar", use_container_width=True, key="confirm_name_button"):
                    if nome_digitado:
                        nome_cadastrado = st.session_state.get("nome_verificado", "")
                        # Comparação case-insensitive
                        if nome_digitado.lower().strip() == nome_cadastrado.lower().strip():
                            st.session_state["nome_confirmado"] = True
                            # Reset automático da senha
                            email_verificado = st.session_state.get("email_verificado")
                            success, message = reset_password_to_default(email_verificado)
                            if success:
                                st.session_state["senha_resetada"] = True
                                st.rerun()
                            else:
                                st.sidebar.error(f"❌ Erro ao resetar senha: {message}")
                        else:
                            st.sidebar.error("❌ Nome não confere com o cadastro.")
                    else:
                        st.sidebar.error("❌ Por favor, digite seu nome completo.")
            
            with col_back:
                if st.button("⬅️ Voltar", use_container_width=True, key="back_to_email_verification"):
                    st.session_state["email_verificado"] = None
                    st.session_state["nome_verificado"] = None
                    st.rerun()
        
        # Etapa 3: Confirmação de sucesso
        elif st.session_state.get("senha_resetada"):
            st.sidebar.markdown("""
            <div style='background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 15px;'>
                <h4 style='color: #155724; margin-top: 0;'>✅ Senha Resetada com Sucesso!</h4>
                <p style='color: #155724; margin-bottom: 0; font-size: 14px;'>
                    Sua senha foi resetada para a senha enviada no seu <strong>email de boas-vindas</strong>.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.sidebar.markdown("**Passos para fazer login:**")
            st.sidebar.markdown("1. Use o email verificado acima")
            st.sidebar.markdown("2. Use a senha do email de boas-vindas")
            st.sidebar.markdown("3. Após o login, você poderá alterar sua senha")
            
            if st.sidebar.button("✅ Entendi", use_container_width=True, key="understood_button"):
                # Limpar todos os estados
                st.session_state["show_forgot_password"] = False
                st.session_state["email_verificado"] = None
                st.session_state["nome_verificado"] = None
                st.session_state["nome_confirmado"] = None
                st.session_state["senha_resetada"] = None
                st.rerun()

    # Seção de redefinição de senha
    if st.session_state.get("show_password_reset", False):
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔑 Redefinir Senha")
        
        if email:  # Se o usuário já digitou o email
            st.sidebar.info(f"Redefinindo senha para: {email}")
            
            new_password = st.sidebar.text_input(
                "Nova Senha", 
                type="password",
                placeholder="Digite sua nova senha",
                key="new_password"
            )
            confirm_password = st.sidebar.text_input(
                "Confirmar Nova Senha", 
                type="password",
                placeholder="Confirme sua nova senha",
                key="confirm_password"
            )
            
            col_reset1, col_reset2 = st.sidebar.columns(2)
            
            with col_reset1:
                if st.button("✅ Salvar", use_container_width=True):
                    if new_password and confirm_password:
                        if new_password == confirm_password:
                            if len(new_password) >= 6:
                                success, message = update_password(email, new_password)
                                if success:
                                    st.sidebar.success("Senha redefinida com sucesso! Faça login novamente.")
                                    st.session_state["show_password_reset"] = False
                                    st.rerun()
                                else:
                                    st.sidebar.error(f"Erro: {message}")
                            else:
                                st.sidebar.error("A senha deve ter pelo menos 6 caracteres.")
                        else:
                            st.sidebar.error("As senhas não coincidem.")
                    else:
                        st.sidebar.error("Preencha todos os campos.")
            
            with col_reset2:
                if st.button("❌ Cancelar", use_container_width=True, key="cancel_password_reset"):
                    st.session_state["show_password_reset"] = False
                    st.rerun()
        else:
            st.sidebar.warning("Digite seu email primeiro para redefinir a senha.")
