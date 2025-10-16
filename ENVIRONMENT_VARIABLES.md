# 🔐 Variáveis de Ambiente Necessárias

Este documento lista todas as variáveis de ambiente que precisam ser configuradas na Railway.

## Variáveis Obrigatórias

### DATABASE_URL
**Descrição:** URL de conexão com o banco de dados PostgreSQL (Neon)

**Formato:**
```
postgresql://usuario:senha@host.neon.tech/nome_database?sslmode=require
```

**Como obter:**
1. Acesse https://console.neon.tech
2. Selecione seu projeto
3. Vá em "Connection Details"
4. Copie a "Connection String" completa

**Exemplo:**
```
DATABASE_URL=postgresql://neondb_owner:AbCdEf123456@ep-exemplo-123.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

### HOTMART_HOTTOK
**Descrição:** Token de autenticação do webhook da Hotmart

**Como obter:**
1. Acesse o painel da Hotmart
2. Vá em Ferramentas → Webhooks
3. Encontre o campo "Hot TOK"
4. Copie o token

**Exemplo:**
```
HOTMART_HOTTOK=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

## Variáveis Opcionais

### PORT
**Descrição:** Porta onde o servidor Flask vai rodar

**Valor padrão:** 5000

**Nota:** A Railway injeta automaticamente esta variável. Você **não precisa** configurá-la manualmente.

```
PORT=5000
```

---

### SMTP_HOST (Opcional)
**Descrição:** Servidor SMTP para envio de emails

**Valor sugerido:** smtp.gmail.com

```
SMTP_HOST=smtp.gmail.com
```

---

### SMTP_PORT (Opcional)
**Descrição:** Porta do servidor SMTP

**Valor sugerido:** 587 (TLS)

```
SMTP_PORT=587
```

---

### SMTP_USER (Opcional)
**Descrição:** Email da conta SMTP

```
SMTP_USER=seu_email@gmail.com
```

---

### SMTP_PASS (Opcional)
**Descrição:** Senha de aplicativo do Gmail

**Como obter (Gmail):**
1. Acesse https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Vá em "Senhas de app"
4. Gere uma senha para "Mail"
5. Use essa senha (não sua senha normal do Gmail)

```
SMTP_PASS=abcd efgh ijkl mnop
```

---

## Configuração na Railway

Para adicionar essas variáveis na Railway:

1. Acesse o dashboard do seu projeto
2. Clique na aba **"Variables"**
3. Clique em **"New Variable"**
4. Adicione **uma por vez**:
   - Nome: `DATABASE_URL`
   - Valor: Cole a URL do Neon
5. Repita para `HOTMART_HOTTOK`

**⚠️ IMPORTANTE:**
- Nunca commite essas variáveis no código
- Nunca compartilhe esses valores
- Use valores diferentes para desenvolvimento e produção

---

## Validação

Para verificar se as variáveis estão corretas, teste os endpoints:

```bash
# 1. Health check (testa conexão com banco)
curl https://sua-url.railway.app/health

# Resposta esperada:
# {"status":"healthy","database":"neon_connected"}

# 2. Teste de webhook (testa HOTTOK)
curl -X POST https://sua-url.railway.app/webhook/hotmart \
  -H "Content-Type: application/json" \
  -H "X-Hotmart-Hottok: SEU_HOTTOK" \
  -d '{"event":"TEST","data":{"buyer":{"email":"teste@test.com"}}}'

# Resposta esperada:
# {"status":"processing","message":"Request received"}
```

---

## Troubleshooting

### Erro: "Database not available"
- ✅ Verifique se `DATABASE_URL` está configurada
- ✅ Confirme que a URL está completa (com usuário, senha, host, database)
- ✅ Teste a conexão diretamente no Neon

### Erro: "Unauthorized"
- ✅ Verifique se `HOTMART_HOTTOK` está correto
- ✅ Confirme que não há espaços extras no início/fim
- ✅ Copie novamente do painel da Hotmart

---

**✅ Checklist de Configuração:**
- [ ] DATABASE_URL configurada e testada
- [ ] HOTMART_HOTTOK configurada e testada
- [ ] Health check retorna "healthy"
- [ ] Webhook responde sem erro 401

