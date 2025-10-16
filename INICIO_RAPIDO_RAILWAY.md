# 🚀 Início Rápido - Deploy na Railway

**Tempo estimado: 30 minutos**

## 📝 Antes de Começar

Você vai precisar de:

1. ✅ Conta no GitHub (já tem)
2. ✅ URL do banco Neon (`DATABASE_URL`)
3. ✅ Token da Hotmart (`HOTMART_HOTTOK`)

## 🎯 Passo a Passo (Versão Curta)

### 1️⃣ Criar Conta Railway (5 min)

```
1. Abra: https://railway.app
2. Clique em "Login with GitHub"
3. Autorize a Railway
4. Você está logado! ✅
```

### 2️⃣ Criar Projeto (2 min)

```
1. Clique em "New Project"
2. Escolha "Deploy from GitHub repo"
3. Selecione: dashboard-analise-acoes
4. Aguarde detectar Python
```

### 3️⃣ Configurar Variáveis (3 min)

```
1. Clique em "Variables"
2. Adicione:
   - DATABASE_URL = sua_url_do_neon
   - HOTMART_HOTTOK = seu_token_hotmart
3. Salve
```

### 4️⃣ Aguardar Deploy (5 min)

```
1. Railway inicia build automático
2. Vá em "Deployments" para ver progresso
3. Aguarde status "Deployed" ✅
```

### 5️⃣ Obter URL (1 min)

```
1. Vá em Settings → Networking
2. Clique "Generate Domain"
3. Copie a URL (salve em algum lugar!)
```

### 6️⃣ Testar (5 min)

**No navegador:**
```
https://sua-url.railway.app/health
```

Deve mostrar:
```json
{"status":"healthy","database":"neon_connected"}
```

**No terminal:**
```bash
python3 test_webhook_railway.py
```

### 7️⃣ Atualizar Hotmart (3 min)

```
1. Painel Hotmart → Webhooks
2. Atualize URL para:
   https://sua-url.railway.app/webhook/hotmart
3. Salve
```

### 8️⃣ Teste Final (5 min)

Faça uma venda teste na Hotmart e verifique:
- ✅ Webhook recebido (veja logs Railway)
- ✅ Usuário criado no banco
- ✅ SEM erro 408!

## ✅ Pronto!

Se tudo funcionou:
- ✨ Seu webhook está na Railway
- ⚡ Resposta rápida (< 5s)
- 💰 Custo baixo (~$3-5/mês)
- 🎉 Zero erros 408

## 🆘 Problemas?

**Build falhou?**
→ Veja logs em Deployments

**Health check retorna erro?**
→ Verifique DATABASE_URL nas Variables

**Erro 401 no webhook?**
→ Verifique HOTMART_HOTTOK

**Precisa de mais ajuda?**
→ Consulte `RAILWAY_SETUP.md` (guia completo)

---

## 📚 Documentação Completa

- **Guia Detalhado:** `RAILWAY_SETUP.md`
- **Checklist:** `MIGRACAO_RAILWAY_CHECKLIST.md`
- **Variáveis:** `ENVIRONMENT_VARIABLES.md`
- **Comparação:** `RENDER_VS_RAILWAY.md`

---

**⏰ Próximos passos (após deploy):**
1. Monitorar por 24-48h
2. Verificar custos
3. Desativar Render (se tudo OK)

**Boa sorte! 🚀**

