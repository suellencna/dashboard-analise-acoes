# 🚂 Guia de Deploy na Railway

## Pré-requisitos

- Conta no GitHub com repositório `dashboard-analise-acoes`
- Banco de dados Neon PostgreSQL configurado
- Token HOTTOK da Hotmart

## Passo a Passo

### 1. Criar Conta na Railway

1. Acesse: https://railway.app
2. Clique em **"Login with GitHub"**
3. Autorize a Railway a acessar sua conta GitHub

### 2. Criar Novo Projeto

1. No dashboard, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório: `dashboard-analise-acoes`
4. A Railway vai detectar automaticamente que é um projeto Python

### 3. Configurar Variáveis de Ambiente

No painel do projeto, vá em **"Variables"** e adicione:

#### Obrigatórias:

```
DATABASE_URL=postgresql://seu_usuario:sua_senha@seu_host.neon.tech/seu_database
HOTMART_HOTTOK=seu_token_da_hotmart
```

#### Como obter os valores:

**DATABASE_URL:**
- Acesse o painel do Neon (https://console.neon.tech)
- Selecione seu projeto
- Copie a "Connection String"
- Cole no campo DATABASE_URL

**HOTMART_HOTTOK:**
- Acesse o painel da Hotmart
- Vá em Ferramentas → Webhooks
- Copie o token "Hot TOK"
- Cole no campo HOTMART_HOTTOK

### 4. Configurar Deploy

A Railway vai usar automaticamente:
- ✅ `Procfile` - para comando de start
- ✅ `requirements.txt` - para instalar dependências  
- ✅ `runtime.txt` - para versão do Python (3.11.10)
- ✅ `railway.json` - configurações adicionais

**Não precisa fazer nada manualmente!**

### 5. Aguardar Deploy

1. A Railway vai iniciar o build automaticamente
2. Acompanhe os logs na aba **"Deployments"**
3. Quando aparecer "Deployed", está pronto! ✅

### 6. Obter URL do Serviço

1. Vá na aba **"Settings"**
2. Em **"Networking"**, clique em **"Generate Domain"**
3. Copie a URL gerada (ex: `https://dashboard-analise-acoes-production.up.railway.app`)

### 7. Testar Endpoints

Abra o terminal e teste:

```bash
# Teste básico
curl https://sua-url.railway.app/

# Health check
curl https://sua-url.railway.app/health

# Deve retornar: {"status":"healthy","database":"neon_connected"}
```

### 8. Atualizar URL na Hotmart

1. Acesse o painel da Hotmart
2. Vá em **Ferramentas → Webhooks**
3. Atualize a URL para:
   ```
   https://sua-url.railway.app/webhook/hotmart
   ```
4. Salve as alterações

### 9. Fazer Teste de Webhook

Use este comando para simular uma compra:

```bash
curl -X POST https://sua-url.railway.app/webhook/hotmart \
  -H "Content-Type: application/json" \
  -H "X-Hotmart-Hottok: SEU_HOTTOK" \
  -d '{
    "event": "PURCHASE_APPROVED",
    "data": {
      "buyer": {
        "email": "teste@exemplo.com",
        "name": "Usuario Teste"
      }
    }
  }'
```

**Resposta esperada:**
```json
{
  "status": "processing",
  "message": "Purchase processing started"
}
```

### 10. Verificar Logs

1. No dashboard Railway, vá em **"Deployments"**
2. Clique no último deploy
3. Veja os logs em tempo real
4. Verifique se não há erros

## Monitoramento

### Métricas Disponíveis

A Railway mostra automaticamente:
- 📊 **CPU Usage** - uso de processador
- 💾 **Memory Usage** - uso de memória
- 🌐 **Network** - tráfego de rede
- ⏱️ **Response Time** - tempo de resposta

### Custos Estimados

Com o tráfego esperado:
- Webhook: **$3-5/mês**
- Você recebe **$5 de crédito/mês** no plano Hobby

**Dica:** Monitore o uso na aba "Usage" para evitar surpresas!

## Troubleshooting

### Deploy falhou?

1. Verifique os logs de build
2. Confirme que `requirements.txt` está completo
3. Verifique se as variáveis de ambiente estão corretas

### Webhook retorna erro 500?

1. Verifique os logs do serviço
2. Confirme que DATABASE_URL está correta
3. Teste a conexão com o banco Neon

### Erro 401 no webhook?

- Verifique se o HOTMART_HOTTOK está correto
- Confirme que o header `X-Hotmart-Hottok` está sendo enviado

## Suporte

- 📚 Documentação Railway: https://docs.railway.app
- 💬 Discord Railway: https://discord.gg/railway
- 🐛 Issues GitHub: Crie um issue no repositório

## Próximos Passos

Após 1 semana de uso:
- ✅ Verificar se não há mais erros 408
- ✅ Analisar custos reais
- ✅ Decidir se precisa adicionar Redis (Plano B)

---

**✨ Tudo pronto! Seu webhook está na Railway e funcionando perfeitamente!**

