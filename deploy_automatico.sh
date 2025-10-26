#!/bin/bash

# 🚀 SCRIPT DE DEPLOY AUTOMÁTICO
# ================================
# Este script automatiza o deploy do sistema completo

echo "🚀 INICIANDO DEPLOY AUTOMÁTICO DO SISTEMA"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se as dependências estão instaladas
print_status "Verificando dependências..."

if ! command -v git &> /dev/null; then
    print_error "Git não está instalado. Instale o Git primeiro."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_error "Python3 não está instalado. Instale o Python3 primeiro."
    exit 1
fi

print_success "Dependências verificadas"

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    print_warning "Arquivo .env não encontrado. Criando template..."
    cat > .env << EOF
# Configurações do Banco de Dados
DATABASE_URL=postgresql://usuario:senha@host:porta/database

# Configurações do Gmail
GMAIL_EMAIL=pontootimoinvest@gmail.com
GMAIL_APP_PASSWORD=sua_senha_de_app_do_gmail

# URLs dos Serviços
RENDER_APP_URL=https://ponto-otimo-invest.onrender.com
RAILWAY_APP_URL=https://seu-projeto.railway.app

# Configurações do MailerSend (opcional)
MAILERSEND_API_KEY=sua_api_key_do_mailersend
FROM_EMAIL=noreply@pontootimo.com.br
TEMPLATE_ATIVACAO_ID=351ndgwyenxlzqx8
TEMPLATE_BOAS_VINDAS_ID=
EOF
    print_warning "Arquivo .env criado. Configure as variáveis antes de continuar."
    print_warning "Pressione Enter quando terminar de configurar..."
    read
fi

# Instalar dependências Python
print_status "Instalando dependências Python..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    print_success "Dependências Python instaladas"
else
    print_error "Erro ao instalar dependências Python"
    exit 1
fi

# Verificar se o Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI não está instalado. Instalando..."
    npm install -g @railway/cli
    if [ $? -eq 0 ]; then
        print_success "Railway CLI instalado"
    else
        print_error "Erro ao instalar Railway CLI"
        exit 1
    fi
fi

# Fazer login no Railway
print_status "Fazendo login no Railway..."
railway login
if [ $? -eq 0 ]; then
    print_success "Login no Railway realizado"
else
    print_error "Erro no login do Railway"
    exit 1
fi

# Deploy no Railway
print_status "Fazendo deploy no Railway..."
railway up --service webhook
if [ $? -eq 0 ]; then
    print_success "Deploy no Railway realizado"
else
    print_error "Erro no deploy do Railway"
    exit 1
fi

# Configurar variáveis de ambiente no Railway
print_status "Configurando variáveis de ambiente no Railway..."
railway variables set DATABASE_URL="$DATABASE_URL"
railway variables set GMAIL_EMAIL="$GMAIL_EMAIL"
railway variables set GMAIL_APP_PASSWORD="$GMAIL_APP_PASSWORD"
railway variables set RENDER_APP_URL="$RENDER_APP_URL"
railway variables set RAILWAY_APP_URL="$(railway status --json | jq -r '.services[0].url')"

print_success "Variáveis de ambiente configuradas no Railway"

# Obter URL do Railway
RAILWAY_URL=$(railway status --json | jq -r '.services[0].url')
print_success "URL do Railway: $RAILWAY_URL"

# Atualizar .env com a URL real do Railway
sed -i.bak "s|RAILWAY_APP_URL=.*|RAILWAY_APP_URL=$RAILWAY_URL|" .env

# Testar o sistema
print_status "Testando o sistema..."
python3 testar_fluxo_completo.py

# Instruções finais
echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "==================="
echo ""
echo "📋 Próximos passos:"
echo "1. Configure o webhook na Hotmart:"
echo "   URL: $RAILWAY_URL/webhook/hotmart"
echo "   Eventos: PURCHASE_APPROVED"
echo ""
echo "2. Configure o sistema no Render:"
echo "   - Conecte seu repositório GitHub"
echo "   - Use as configurações do render.yaml"
echo "   - Configure as variáveis de ambiente"
echo ""
echo "3. Teste o fluxo completo:"
echo "   python3 testar_fluxo_completo.py"
echo ""
echo "📞 Suporte: pontootimoinvest@gmail.com"
echo ""
