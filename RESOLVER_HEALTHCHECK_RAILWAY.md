# 🔧 Resolver Falha de Healthcheck na Railway

## ❌ Problema
```
Attempt #8 failed with service unavailable
1/1 replicas never became healthy!
Healthcheck failed!
```

## 🔍 Causas Mais Comuns

### 1. Variáveis de Ambiente Não Configuradas ⚠️ **MAIS PROVÁVEL**

O webhook precisa de:
- `DATABASE_URL` (obrigatória)
- `HOTMART_HOTTOK` (obrigatória)

Se essas variáveis não estão configuradas, o serviço não inicia corretamente.

### 2. Banco Neon Inacessível

Se a URL do banco estiver incorreta ou o banco estiver pausado.

### 3. Porta Incorreta

O Railway injeta a variável `$PORT`, mas pode haver problema.

---

## ✅ SOLUÇÃO PASSO A PASSO

### Etapa 1: Verificar Variáveis de Ambiente

**No dashboard da Railway:**

1. Clique no seu serviço
2. Vá na aba **"Variables"**
3. Verifique se existem:
   - `DATABASE_URL`
   - `HOTMART_HOTTOK`

**Se NÃO existirem, adicione agora:**

#### Como Obter DATABASE_URL:
```
1. Acesse: https://console.neon.tech
2. Entre no seu projeto
3. Copie a "Connection String"
4. Deve ser algo como:
   postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

#### Como Obter HOTMART_HOTTOK:
```
1. Acesse: https://app.hotmart.com
2. Ferramentas → Webhooks
3. Copie o token "Hot TOK"
```

**Adicione na Railway:**
```
Variables → New Variable
- Name: DATABASE_URL
- Value: [cole aqui]

Variables → New Variable  
- Name: HOTMART_HOTTOK
- Value: [cole aqui]
```

**Depois de adicionar as variáveis, a Railway faz redeploy automático!**

---

### Etapa 2: Verificar Logs de Deploy

**Enquanto o redeploy acontece:**

1. Vá em **"Deployments"**
2. Clique no deploy atual
3. Procure por erros como:
   - `DATABASE_URL não encontrada`
   - `Erro de conexão`
   - `ModuleNotFoundError`

---

### Etapa 3: Testar Manualmente o Healthcheck

Depois que o deploy terminar, teste a URL:

```bash
# Substitua pela sua URL da Railway
curl https://sua-url.railway.app/health
```

**Resultado esperado:**
```json
{"status":"healthy","database":"neon_connected"}
```

**Se retornar erro:**
- Verifique as variáveis novamente
- Veja os logs de runtime (próxima etapa)

---

### Etapa 4: Ver Logs de Runtime (se ainda falhar)

**No dashboard Railway:**

1. Vá em **"Deployments"** → **"View Logs"**
2. Procure por:
   - Mensagens de erro do Flask/Gunicorn
   - Erros de conexão com banco
   - Exceções Python

**Erros comuns e soluções:**

```
❌ "Engine de banco não disponível"
→ DATABASE_URL não está configurada ou está errada

❌ "could not connect to server"
→ URL do Neon está incorreta ou banco está pausado

❌ "Name or service not known"
→ Host do banco está errado

❌ "password authentication failed"
→ Senha na DATABASE_URL está incorreta
```

---

### Etapa 5: Configurar Health Check Timeout (se necessário)

Se o serviço demora para iniciar:

**No dashboard Railway:**

1. Settings → Health Check
2. Aumente o timeout:
   - **Timeout:** 120 segundos (padrão é 100)
   - **Path:** `/health` (manter)

3. Salve e aguarde redeploy

---

## 🐛 Troubleshooting Avançado

### Problema: Variáveis estão corretas mas ainda falha

**Teste a conexão com o banco manualmente:**

1. No terminal, execute:
```bash
psql "sua_database_url_aqui"
```

2. Se conectar, o problema não é o banco
3. Se não conectar, revise a URL do Neon

---

### Problema: Logs mostram erro no código

**Se houver erro Python nos logs:**

1. Anote o erro completo
2. Verifique se não falta alguma dependência em `requirements.txt`
3. Verifique se o arquivo `webhook_hotmart_optimized.py` está OK

---

### Problema: Gunicorn não inicia

**Verifique o Procfile:**

Deve ser exatamente:
```
web: gunicorn webhook_hotmart_optimized:app --bind 0.0.0.0:$PORT --timeout 15 --workers 2 --threads 2
```

Se estiver diferente, corrija e faça novo deploy.

---

## 📋 Checklist de Verificação

Antes de pedir ajuda, confirme:

- [ ] `DATABASE_URL` está configurada nas Variables
- [ ] `HOTMART_HOTTOK` está configurada nas Variables
- [ ] DATABASE_URL está correta (copiei do Neon)
- [ ] Aguardei o redeploy após adicionar variáveis
- [ ] Testei a URL `/health` manualmente
- [ ] Verifiquei os logs de deploy e runtime
- [ ] Banco Neon está ativo (não pausado)

---

## 🎯 Solução Mais Provável (90% dos casos)

**O problema geralmente é:**

1. **Variáveis não configuradas** → Adicione DATABASE_URL e HOTMART_HOTTOK
2. **DATABASE_URL errada** → Copie novamente do Neon
3. **Banco Neon pausado** → Acesse Neon e ative o projeto

---

## 🚀 Próximos Passos Após Resolver

Quando o healthcheck passar:

1. ✅ Teste o webhook com `test_webhook_railway.py`
2. ✅ Atualize a URL na Hotmart
3. ✅ Faça uma venda teste
4. ✅ Monitore por 24h

---

## 💡 Dicas Importantes

1. **Railway faz redeploy automático** quando você adiciona/modifica variáveis
2. **Aguarde 2-3 minutos** após adicionar variáveis
3. **Logs de deploy** mostram o build, **logs de runtime** mostram a execução
4. **O healthcheck tenta por 100 segundos** antes de falhar
5. **Se DATABASE_URL estiver errada**, o serviço nunca vai iniciar

---

## 📞 Se Nada Funcionar

Entre no Discord da Railway e poste:

```
Build passou mas healthcheck falha
Serviço: Python/Flask  
Erro: service unavailable no /health
Variáveis configuradas: DATABASE_URL, HOTMART_HOTTOK
Logs: [cole os últimos logs aqui]
```

Discord Railway: https://discord.gg/railway

---

**✅ Na maioria dos casos, adicionar as variáveis resolve!**

Adicione DATABASE_URL e HOTMART_HOTTOK agora e aguarde o redeploy.

