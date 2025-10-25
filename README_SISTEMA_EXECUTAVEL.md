# 🚀 SISTEMA PONTO ÓTIMO INVEST - EXECUTÁVEL LOCAL

## 📋 **DESCRIÇÃO**

Este é um sistema completo e executável que contém toda a funcionalidade do Ponto Ótimo Invest em um único arquivo Python. Ideal para desenvolvimento, testes e backup enquanto resolvemos problemas de deploy.

## 🎯 **FUNCIONALIDADES**

- ✅ **Webhook Hotmart** - Recebe notificações de compra
- ✅ **Banco de dados SQLite** - Armazena usuários localmente
- ✅ **Email Gmail SMTP** - Envia emails de ativação
- ✅ **Ativação de conta** - Sistema completo de ativação
- ✅ **Troca de senha** - Obrigatória no primeiro login
- ✅ **Interface web** - Página de ativação HTML

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
```

### 3. **Executar o sistema:**
```bash
python3 sistema_completo_executavel.py
```

### 4. **Testar o sistema:**
```bash
python3 testar_sistema_executavel.py
```

## 🌐 **ENDPOINTS DISPONÍVEIS**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/` | Página inicial |
| POST | `/webhook` | Webhook Hotmart |
| POST | `/test-email` | Testar envio de email |
| GET | `/ativar/<token>` | Página de ativação |
| POST | `/api/ativar/<token>` | API de ativação |

## 📧 **TESTE DE EMAIL**

### **Via interface web:**
1. Acesse: http://localhost:5000
2. Clique em "Testar Email"

### **Via API:**
```bash
curl -X POST http://localhost:5000/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "seu@email.com", "nome": "Seu Nome"}'
```

## 🔄 **SIMULAÇÃO DE WEBHOOK**

### **Via API:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EV12345678",
    "event": "PURCHASE_APPROVED",
    "status": "approved",
    "product": {"id": 12345, "name": "Produto Teste"},
    "buyer": {"email": "cliente@email.com", "name": "Cliente Teste"},
    "purchase": {"price": 99.90, "currency": "BRL"}
  }'
```

## 💾 **BANCO DE DADOS**

O sistema usa SQLite local (`sistema_local.db`) com a seguinte estrutura:

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255),
    senha_hash VARCHAR(255),
    token_ativacao VARCHAR(255) UNIQUE,
    expiracao_token TIMESTAMP,
    status_conta VARCHAR(50) DEFAULT 'pendente',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 **CONFIGURAÇÕES**

### **Variáveis de ambiente:**
- `GMAIL_EMAIL` - Email do Gmail (padrão: pontootimoinvest@gmail.com)
- `GMAIL_APP_PASSWORD` - Senha de app do Gmail
- `APP_URL` - URL base (padrão: http://localhost:5000)

### **Porta:**
- **Padrão:** 5000
- **Alterar:** Modifique a linha `app.run(host='0.0.0.0', port=5000, debug=True)`

## 🧪 **TESTES**

### **Teste automático:**
```bash
python3 testar_sistema_executavel.py
```

### **Teste manual:**
1. **Health check:** http://localhost:5000/health
2. **Página inicial:** http://localhost:5000/
3. **Teste de email:** http://localhost:5000/test-email

## 📝 **LOGS**

O sistema gera logs detalhados no console:
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
- Delete `sistema_local.db` para recriar

## 🔄 **FLUXO COMPLETO**

1. **Webhook recebido** → Usuário criado no banco
2. **Email enviado** → Link de ativação
3. **Usuário clica** → Página de ativação
4. **Conta ativada** → Senha temporária gerada
5. **Login** → Troca de senha obrigatória

## 📁 **ARQUIVOS**

- `sistema_completo_executavel.py` - Sistema principal
- `testar_sistema_executavel.py` - Script de teste
- `README_SISTEMA_EXECUTAVEL.md` - Esta documentação
- `sistema_local.db` - Banco de dados (criado automaticamente)

## 🎉 **VANTAGENS**

- ✅ **Portável** - Funciona em qualquer máquina
- ✅ **Completo** - Todas as funcionalidades
- ✅ **Testável** - Fácil de testar localmente
- ✅ **Backup** - Sistema funcionando independente
- ✅ **Desenvolvimento** - Ideal para desenvolvimento

## 🚀 **PRÓXIMOS PASSOS**

1. **Teste o sistema** localmente
2. **Configure as variáveis** de ambiente
3. **Teste o fluxo completo** de ativação
4. **Use como backup** enquanto resolvemos o Railway
5. **Desenvolva novas funcionalidades** localmente

---

**💡 Dica:** Este sistema executável é perfeito para você trabalhar localmente enquanto resolvemos os problemas do Railway!
