# 🛒 SISTEMA DE VENDAS COM VALIDAÇÃO - PONTO ÓTIMO INVEST

## 📋 **DESCRIÇÃO**

Sistema completo de vendas com validação de compra ativa. Permite vender seu app com controle total de acesso baseado no status da compra.

## 🎯 **FUNCIONALIDADES**

- ✅ **Validação de compra ativa** - Só funciona se compra válida
- ✅ **Controle de expiração** - Para de funcionar se cancelar
- ✅ **Email de boas-vindas** - Link do app + token de acesso
- ✅ **Sistema de tokens** - Acesso único por cliente
- ✅ **Webhook Hotmart** - Processamento automático de compras
- ✅ **Banco de dados** - Controle completo de clientes

## 🚀 **COMO USAR**

### 1. **Instalar dependências:**
```bash
pip install flask argon2-cffi sqlite3
```

### 2. **Configurar variáveis de ambiente (opcional):**
```bash
export GMAIL_EMAIL="pontootimoinvest@gmail.com"
export GMAIL_APP_PASSWORD="sua_senha_app"
export APP_URL="http://localhost:5000"
export APP_DOWNLOAD_URL="https://seu-app.com/download"
```

### 3. **Executar o sistema:**
```bash
python3 sistema_vendas_executavel.py
```

### 4. **Testar o sistema:**
```bash
python3 testar_sistema_vendas.py
```

## 🌐 **ENDPOINTS DISPONÍVEIS**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/` | Página inicial |
| POST | `/webhook` | Webhook Hotmart (compras) |
| GET | `/validar?token=XXX` | Validar acesso do cliente |
| POST | `/test-email` | Testar email de boas-vindas |

## 🛒 **FLUXO DE VENDAS**

### **1. Cliente compra:**
- Webhook recebido da Hotmart
- Sistema valida dados da compra
- Cliente criado/atualizado no banco

### **2. Email de boas-vindas:**
- Link de download do app
- Token de acesso único
- Data de expiração
- Instruções de uso

### **3. Cliente acessa o app:**
- Sistema valida token de acesso
- Verifica status da compra
- Controla expiração automática

### **4. Controle de acesso:**
- ✅ **Compra ativa** → Acesso liberado
- ❌ **Compra cancelada** → Acesso negado
- ⏰ **Compra expirada** → Acesso negado

## 📧 **TESTE DE EMAIL**

### **Via interface web:**
1. Acesse: http://localhost:5000
2. Clique em "Testar Email"

### **Via API:**
```bash
curl -X POST http://localhost:5000/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "cliente@email.com", "nome": "Cliente Teste"}'
```

## 🔄 **SIMULAÇÃO DE COMPRA**

### **Compra aprovada:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EV12345678",
    "event": "PURCHASE_APPROVED",
    "status": "approved",
    "product": {"id": "PROD123", "name": "Ponto Ótimo Invest"},
    "buyer": {"email": "cliente@email.com", "name": "Cliente Teste"},
    "purchase": {"price": 99.90, "currency": "BRL"}
  }'
```

### **Compra cancelada:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EV12345679",
    "event": "PURCHASE_CANCELED",
    "status": "canceled",
    "product": {"id": "PROD123", "name": "Ponto Ótimo Invest"},
    "buyer": {"email": "cliente@email.com", "name": "Cliente Teste"},
    "purchase": {"price": 99.90, "currency": "BRL"}
  }'
```

## 🔐 **VALIDAÇÃO DE ACESSO**

### **Página de validação:**
- **URL:** http://localhost:5000/validar?token=SEU_TOKEN
- **Função:** Validar se cliente tem acesso ativo
- **Retorno:** Status da compra e dados do cliente

### **API de validação:**
```bash
curl "http://localhost:5000/api/validar-acesso?token=SEU_TOKEN"
```

## 💾 **BANCO DE DADOS**

### **Estrutura da tabela `clientes`:**
```sql
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255),
    status_compra VARCHAR(50) DEFAULT 'pendente',
    data_compra TIMESTAMP,
    data_expiracao TIMESTAMP,
    produto_id VARCHAR(100),
    valor_pago DECIMAL(10,2),
    token_acesso VARCHAR(255) UNIQUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP,
    acessos_totais INTEGER DEFAULT 0
);
```

### **Status de compra:**
- `pendente` - Aguardando confirmação
- `ativo` - Compra confirmada, acesso liberado
- `cancelado` - Compra cancelada, acesso negado
- `expirado` - Compra expirada, acesso negado

## 🔧 **CONFIGURAÇÕES**

### **Variáveis de ambiente:**
- `GMAIL_EMAIL` - Email do Gmail (padrão: pontootimoinvest@gmail.com)
- `GMAIL_APP_PASSWORD` - Senha de app do Gmail
- `APP_URL` - URL base (padrão: http://localhost:5000)
- `APP_DOWNLOAD_URL` - Link de download do seu app

### **Porta:**
- **Padrão:** 5000
- **Alterar:** Modifique a linha `app.run(host='0.0.0.0', port=5000, debug=True)`

## 🧪 **TESTES**

### **Teste automático:**
```bash
python3 testar_sistema_vendas.py
```

### **Teste manual:**
1. **Health check:** http://localhost:5000/health
2. **Página inicial:** http://localhost:5000/
3. **Teste de email:** http://localhost:5000/test-email
4. **Validação:** http://localhost:5000/validar?token=teste

## 📝 **LOGS**

O sistema gera logs detalhados:
- ✅ **INFO** - Operações normais
- ⚠️ **WARNING** - Avisos
- ❌ **ERROR** - Erros

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Erro de conexão:**
- Verifique se a porta 5000 está livre
- Execute: `lsof -i :5000`

### **Erro de email:**
- Verifique as variáveis de ambiente
- Confirme a senha de app do Gmail

### **Erro de banco:**
- Verifique permissões de escrita
- Delete `sistema_vendas.db` para recriar

## 🎯 **CASOS DE USO**

### **1. Venda de app:**
- Cliente compra → Recebe email com link
- Acessa app → Sistema valida compra
- Usa app → Controle de acesso ativo

### **2. Cancelamento:**
- Cliente cancela → Webhook recebido
- Sistema atualiza status → Acesso negado
- Cliente tenta acessar → Validação falha

### **3. Renovação:**
- Cliente compra novamente → Status atualizado
- Acesso liberado → Novo período de validade
- Controle automático → Sem intervenção manual

## 🔄 **INTEGRAÇÃO COM HOTMART**

### **Webhook configurado:**
- **URL:** https://seu-dominio.com/webhook
- **Eventos:** PURCHASE_APPROVED, PURCHASE_CANCELED
- **Processamento:** Automático em background

### **Dados processados:**
- Email do cliente
- Nome do cliente
- ID do produto
- Status da compra
- Valor pago

## 📁 **ARQUIVOS**

- `sistema_vendas_executavel.py` - Sistema principal
- `testar_sistema_vendas.py` - Script de teste
- `README_SISTEMA_VENDAS.md` - Esta documentação
- `sistema_vendas.db` - Banco de dados (criado automaticamente)

## 🎉 **VANTAGENS**

- ✅ **Controle total** - Acesso baseado em compra
- ✅ **Automático** - Processamento sem intervenção
- ✅ **Seguro** - Tokens únicos por cliente
- ✅ **Escalável** - Suporta milhares de clientes
- ✅ **Flexível** - Fácil de customizar

## 🚀 **PRÓXIMOS PASSOS**

1. **Teste o sistema** localmente
2. **Configure as variáveis** de ambiente
3. **Teste o fluxo completo** de vendas
4. **Integre com Hotmart** (webhook)
5. **Deploy em produção** (Railway/Render)

---

**💡 Dica:** Este sistema permite vender seu app com controle total de acesso baseado no status da compra!
