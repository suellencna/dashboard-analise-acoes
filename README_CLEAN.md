# 🎯 Ponto Ótimo Invest - Sistema Completo

## 📋 Visão Geral

Sistema completo de análise de investimentos com:
- **Dashboard Streamlit** - Interface de análise
- **Sistema de Vendas** - Webhook Hotmart + validação
- **Controle de Acesso** - Por token de compra
- **Email Automático** - Boas-vindas profissionais

## 🚀 Deploy no Render

### **Configuração Automática:**
1. Conectar repositório GitHub
2. Render detecta `render.yaml` automaticamente
3. Cria 2 serviços:
   - **Dashboard:** `ponto-otimo-invest.onrender.com`
   - **Webhook:** `ponto-otimo-webhook.onrender.com`

### **Configuração Manual:**
1. **GMAIL_APP_PASSWORD:** Senha de app do Gmail
2. **APP_URL:** URL do dashboard principal
3. **APP_DOWNLOAD_URL:** Link para download do app

## 💰 Custos Render

- **Starter Plan:** $7/mês por serviço
- **Total:** $14/mês (2 serviços)
- **Recomendado:** Standard Plan ($25/mês) para produção

## 🔧 Arquivos Principais

- `app_clean.py` - Dashboard Streamlit
- `webhook_clean.py` - Sistema de vendas Flask
- `requirements_clean.txt` - Dependências
- `render.yaml` - Configuração Render

## 📱 Fluxo de Vendas

1. **Cliente compra** → Hotmart envia webhook
2. **Sistema valida** → Cria/atualiza cliente
3. **Email enviado** → Link + token de acesso
4. **Cliente acessa** → Validação automática
5. **Controle ativo** → Expiração automática

## 🎯 Funcionalidades

### **Dashboard:**
- Análise de ações em tempo real
- Análise de FIIs
- Composição de carteira
- Métricas de performance
- Interface responsiva

### **Sistema de Vendas:**
- Webhook Hotmart integrado
- Validação de compras
- Email de boas-vindas
- Controle de acesso por token
- Gestão de expiração

## 🔐 Segurança

- Autenticação por token
- Validação de compras
- Controle de expiração
- Banco de dados seguro
- Email criptografado

## 📞 Suporte

- **Email:** pontootimoinvest@gmail.com
- **Sistema:** Totalmente automatizado
- **Deploy:** Render (confiável e estável)
