# 🚀 DEPLOY COMPLETO - SISTEMA HOTMART → RAILWAY → NEON → GMAIL → RENDER

## 📋 Visão Geral do Sistema

Este sistema implementa um fluxo completo de integração:

1. **Cliente compra na Hotmart** → Hotmart envia webhook
2. **Railway recebe webhook** → Processa compra e cadastra usuário
3. **NEON armazena dados** → Banco de dados PostgreSQL
4. **Gmail envia email** → Credenciais de acesso para o cliente
5. **Cliente acessa RENDER** → Sistema principal de análise

## 🛠️ Arquivos Principais

- `webhook_hotmart_unificado.py` - Webhook principal para Railway
- `app.py` - Sistema principal para Render
- `railway.json` - Configuração do Railway
- `render.yaml` - Configuração do Render
- `testar_fluxo_completo.py` - Script de teste

## 🔧 Configuração do Railway

### 1. Deploy no Railway

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Fazer login
railway login

# 3. Inicializar projeto
railway init

# 4. Deploy
railway up
```

### 2. Variáveis de Ambiente no Railway

Configure as seguintes variáveis no painel do Railway:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/database
GMAIL_EMAIL=pontootimoinvest@gmail.com
GMAIL_APP_PASSWORD=sua_senha_de_app_do_gmail
RENDER_APP_URL=https://ponto-otimo-invest.onrender.com
RAILWAY_APP_URL=https://seu-projeto.railway.app
```

### 3. Configurar Webhook na Hotmart

1. Acesse o painel da Hotmart
2. Vá em "Webhooks"
3. Adicione nova URL: `https://seu-projeto.railway.app/webhook/hotmart`
4. Selecione eventos: "PURCHASE_APPROVED"
5. Salve a configuração

## 🌐 Configuração do Render

### 1. Deploy no Render

1. Acesse [render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Selecione o repositório do projeto
4. Configure como "Web Service"
5. Use as configurações do `render.yaml`

### 2. Variáveis de Ambiente no Render

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/database
GMAIL_EMAIL=pontootimoinvest@gmail.com
GMAIL_APP_PASSWORD=sua_senha_de_app_do_gmail
RENDER_APP_URL=https://ponto-otimo-invest.onrender.com
RAILWAY_APP_URL=https://seu-projeto.railway.app
```

## 🗄️ Configuração do Banco NEON

### 1. Criar Banco no NEON

1. Acesse [neon.tech](https://neon.tech)
2. Crie um novo projeto
3. Copie a string de conexão
4. Configure como `DATABASE_URL` nos serviços

### 2. Estrutura da Tabela

O sistema criará automaticamente a tabela `usuarios`:

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    status_conta VARCHAR(50) DEFAULT 'pendente',
    token_ativacao VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ativacao TIMESTAMP,
    hotmart_transaction_id VARCHAR(255),
    status_assinatura VARCHAR(50) DEFAULT 'ativo'
);
```

## 📧 Configuração do Gmail

### 1. Configurar Senha de App

1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em "Segurança" → "Verificação em duas etapas"
3. Ative a verificação em duas etapas
4. Vá em "Senhas de app"
5. Gere uma senha para "Mail"
6. Use esta senha como `GMAIL_APP_PASSWORD`

### 2. Configurar Email

- **Email:** `pontootimoinvest@gmail.com`
- **Senha de App:** (gerada no passo anterior)

## 🧪 Testando o Sistema

### 1. Teste Automático

```bash
python testar_fluxo_completo.py
```

### 2. Teste Manual

1. **Health Check:**
   ```bash
   curl https://seu-projeto.railway.app/health
   ```

2. **Teste de Email:**
   ```bash
   curl -X POST https://seu-projeto.railway.app/test-email \
        -H "Content-Type: application/json" \
        -d '{"email":"seu@email.com","nome":"Seu Nome"}'
   ```

3. **Teste de Webhook:**
   ```bash
   curl -X POST https://seu-projeto.railway.app/webhook/hotmart \
        -H "Content-Type: application/json" \
        -d '{
          "buyer": {"email":"teste@exemplo.com","name":"Cliente Teste"},
          "transaction": {"id":"TEST123"},
          "status": "approved"
        }'
   ```

## 🔄 Fluxo Completo

### 1. Cliente Compra na Hotmart
- Cliente faz compra do produto
- Hotmart processa pagamento
- Status: "approved"

### 2. Hotmart Envia Webhook
- POST para `https://seu-projeto.railway.app/webhook/hotmart`
- Dados: email, nome, transaction_id, status

### 3. Railway Processa Webhook
- Recebe dados da Hotmart
- Cadastra usuário no NEON
- Gera token de ativação
- Envia email via Gmail
- Responde "200 OK" para Hotmart

### 4. Cliente Recebe Email
- Email com link de ativação
- Credenciais temporárias
- Instruções de acesso

### 5. Cliente Ativa Conta
- Clica no link do email
- Acessa `https://seu-projeto.railway.app/ativar/token`
- Conta é ativada no banco
- Senha temporária é definida

### 6. Cliente Acessa Sistema
- Vai para `https://ponto-otimo-invest.onrender.com`
- Faz login com email e senha temporária
- É obrigado a trocar a senha
- Acessa o sistema completo

## 🚨 Troubleshooting

### Problemas Comuns

1. **Webhook não recebe dados:**
   - Verifique se a URL está correta na Hotmart
   - Teste o health check
   - Verifique os logs do Railway

2. **Email não é enviado:**
   - Verifique `GMAIL_APP_PASSWORD`
   - Confirme se a verificação em duas etapas está ativa
   - Teste o endpoint `/test-email`

3. **Banco de dados não conecta:**
   - Verifique `DATABASE_URL`
   - Confirme se o banco NEON está ativo
   - Teste a conexão

4. **Sistema RENDER não carrega:**
   - Verifique se o deploy foi bem-sucedido
   - Confirme as variáveis de ambiente
   - Verifique os logs do Render

### Logs e Monitoramento

- **Railway:** Painel → Logs
- **Render:** Dashboard → Logs
- **NEON:** Console → Queries

## 📞 Suporte

Para problemas ou dúvidas:
- **Email:** pontootimoinvest@gmail.com
- **Sistema:** Use o botão "Esqueci minha senha" no login

## ✅ Checklist de Deploy

- [ ] Railway configurado e funcionando
- [ ] Render configurado e funcionando
- [ ] NEON configurado e funcionando
- [ ] Gmail configurado e funcionando
- [ ] Webhook configurado na Hotmart
- [ ] Testes passando
- [ ] Fluxo completo testado

## 🎯 Próximos Passos

1. **Monitoramento:** Configure alertas para falhas
2. **Backup:** Configure backup automático do banco
3. **Escalabilidade:** Monitore performance e recursos
4. **Segurança:** Implemente rate limiting e validações
5. **Analytics:** Adicione métricas de uso

---

**Sistema desenvolvido para Ponto Ótimo Investimentos**  
*Integração completa Hotmart → Railway → NEON → Gmail → Render*
