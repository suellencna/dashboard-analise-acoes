# 🔧 Configurar MailerSend com pontootimo.com.br

**Tempo estimado:** 30-40 minutos  
**Plano:** Free (12.000 emails/mês) 🎉

---

## ✅ Por Que MailerSend É Melhor

| Característica | SendGrid Free | MailerSend Free |
|----------------|---------------|-----------------|
| Emails/mês | 3.000 | **12.000** 🏆 |
| Interface | Antiga | **Moderna** ✨ |
| Analytics | Bom | **Excelente** 📊 |
| Templates | Sim | **Sim + Editor** 🎨 |

**Você fez a escolha certa!** ✅

---

## 📋 Passo a Passo

### PARTE 1: Conta MailerSend (5 min)

#### 1. Acessar/Login

- **URL:** https://app.mailersend.com
- Se já fez login: ✅ Perfeito!
- Se não: Sign up com Google/Email

#### 2. Plano Free

- Confirme que está no **Free tier**
- 12.000 emails/mês
- Sem cartão de crédito necessário

---

### PARTE 2: Adicionar Domínio (15 min)

#### 3. Adicionar Domínio

**No painel MailerSend:**

1. Menu lateral → **Domains**
2. Clique em **"Add Domain"**
3. Digite: `pontootimo.com.br`
4. Clique em **"Add domain"**

#### 4. Copiar Registros DNS

MailerSend vai mostrar registros DNS para adicionar:

**Registro 1 - SPF (TXT):**
```
Type: TXT
Host: @ (ou pontootimo.com.br)
Value: v=spf1 include:spf.mailersend.net ~all
```

**Registro 2 - DKIM (CNAME):**
```
Type: CNAME
Host: ms1._domainkey
Value: ms1._domainkey.mailersend.net
```

**Registro 3 - DKIM (CNAME):**
```
Type: CNAME  
Host: ms2._domainkey
Value: ms2._domainkey.mailersend.net
```

**Registro 4 - Tracking (CNAME) - Opcional:**
```
Type: CNAME
Host: track
Value: track.mailersend.net
```

**⚠️ COPIE ESSES VALORES EXATOS!**

**Dica:** MailerSend mostra os valores exatos para você copiar/colar.

---

### PARTE 3: Configurar DNS no Registro.br (15 min)

#### 5. Acessar Painel Registro.br

1. **URL:** https://registro.br
2. **Login** com seu CPF/CNPJ
3. **Meus Domínios** → `pontootimo.com.br`
4. **Editar Zona DNS** ou **DNS**

#### 6. Adicionar Registros

**TXT (SPF):**
```
Tipo: TXT
Nome: @ (ou deixe vazio se auto-completa)
Dados: v=spf1 include:spf.mailersend.net ~all
TTL: 3600
```

**CNAME 1 (DKIM):**
```
Tipo: CNAME
Nome: ms1._domainkey
Dados: ms1._domainkey.mailersend.net
TTL: 3600
```

**CNAME 2 (DKIM):**
```
Tipo: CNAME
Nome: ms2._domainkey
Dados: ms2._domainkey.mailersend.net
TTL: 3600
```

**CNAME 3 (Tracking - Opcional):**
```
Tipo: CNAME
Nome: track
Dados: track.mailersend.net
TTL: 3600
```

**Salvar todas as mudanças!**

---

### PARTE 4: Verificar Domínio (5-60 min)

#### 7. Aguardar Propagação

**Tempo:** 5 minutos - 2 horas (geralmente 15-30 min)

**Enquanto aguarda:**
- Pode tomar café ☕
- Pode configurar outras coisas
- DNS está propagando...

#### 8. Verificar no MailerSend

**Volte ao painel MailerSend:**

1. Domains → `pontootimo.com.br`
2. Clique em **"Verify DNS records"**

**Status possível:**

✅ **Verificado:** Todos checks verdes
- SPF: ✅
- DKIM: ✅  
- Tracking: ✅ (opcional)

⏳ **Pendente:** "DNS records not found"
- Aguarde mais 10-15 minutos
- Clique em "Verify" novamente

❌ **Erro:** "Invalid record"
- Verifique se copiou corretamente
- Confira formato no Registro.br

---

### PARTE 5: Criar API Token (5 min)

#### 9. Gerar Token

**No MailerSend:**

1. Menu → **API Tokens**
2. **"Generate new token"**
3. **Nome:** "Railway Webhook Ponto Otimo"
4. **Scopes/Permissions:**
   - Full access (mais simples)
   - OU: Email send (mais seguro)
5. **Clique em "Create"**

#### 10. COPIAR TOKEN

```
mlsn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ IMPORTANTE:**
- Começa com `mlsn_`
- Aparece SÓ UMA VEZ!
- Salve em local seguro
- Se perder, crie novo

---

### PARTE 6: Configurar na Railway (5 min)

#### 11. Adicionar Variáveis

**Railway Dashboard:**

1. Seu projeto → **Variables**
2. **New Variable:**

```
Nome: MAILERSEND_API_KEY
Valor: mlsn_xxxxxxxxx... (cole o token)
```

3. **New Variable:**

```
Nome: FROM_EMAIL
Valor: noreply@pontootimo.com.br
```

4. **Confirme que já existe:**
```
APP_URL=https://web-production-e66d.up.railway.app
```

5. **Salvar** (Railway fará redeploy automático)

---

### PARTE 7: Testar (10 min)

#### 12. Aguardar Redeploy

**Railway:**
- Aguarde redeploy terminar (2-3 min)
- Verifique logs (sem erros)

#### 13. Testar Localmente (Opcional)

**No seu terminal:**

```bash
cd /Users/suellenpinto/projetos/dashboard-analise-acoes

# Configurar variáveis localmente
export MAILERSEND_API_KEY="mlsn_sua_chave_aqui"
export FROM_EMAIL="noreply@pontootimo.com.br"

# Rodar teste
python3 email_service.py
```

Digite seu email e veja se recebe!

#### 14. Verificar Email Recebido

**Check inbox:**
- Email deve chegar em < 1 minuto
- Assunto: "🧪 Teste - MailerSend Configurado!"
- Se recebeu: ✅ Tudo OK!

---

## ✅ Checklist de Verificação

### MailerSend:
- [ ] Conta criada em app.mailersend.com
- [ ] Email confirmado
- [ ] Domínio pontootimo.com.br adicionado
- [ ] Registros DNS copiados
- [ ] Domínio verificado (checks verdes) ✅
- [ ] API Token criada
- [ ] Token salvo em local seguro

### Registro.br:
- [ ] Login feito
- [ ] Zona DNS acessada
- [ ] 1 TXT (SPF) adicionado
- [ ] 3 CNAMEs (DKIM + Track) adicionados
- [ ] Mudanças salvas

### Railway:
- [ ] MAILERSEND_API_KEY configurada
- [ ] FROM_EMAIL configurada
- [ ] Redeploy bem-sucedido
- [ ] Sem erros nos logs

### Teste:
- [ ] Email de teste enviado
- [ ] Email recebido (inbox)
- [ ] Não caiu em spam
- [ ] Template está bonito

---

## 🐛 Troubleshooting

### Domínio não verifica

**Problema:** "DNS records not found" após 1h

**Soluções:**

1. **Verificar DNS:**
```bash
dig pontootimo.com.br TXT
dig ms1._domainkey.pontootimo.com.br CNAME
```

2. **Testar propagação:**
- Use: https://dnschecker.org
- Digite: `ms1._domainkey.pontootimo.com.br`
- Veja se propagou em vários servidores

3. **Formato no Registro.br:**
- Alguns painéis querem: `ms1._domainkey`
- Outros querem: `ms1._domainkey.pontootimo.com.br`
- Teste os dois formatos

### Email não chega

**Causas:**

1. **Domínio não verificado ainda**
   - Aguarde verificação completa

2. **FROM_EMAIL incorreto**
   - Deve ser: `noreply@pontootimo.com.br`
   - NÃO pode ser: `noreply@gmail.com`

3. **API Token inválido**
   - Gere novo token
   - Configure novamente na Railway

### Email cai em spam

**Normal no início!**

**Soluções:**

1. Aguarde 24-48h (reputação do domínio)
2. Peça destinatários marcarem como "Não é spam"
3. Configure DMARC (avançado, pode fazer depois)

---

## 💡 Vantagens do MailerSend

### 1. Dashboard Excelente

**MailerSend mostra:**
- 📊 Emails enviados (tempo real)
- 📈 Taxa de entrega
- 👁️ Taxa de abertura
- 🖱️ Cliques em links
- ❌ Bounces e spam reports

### 2. Templates Visuais

**Pode criar templates no editor visual:**
- Arrastar e soltar blocos
- Preview em tempo real
- Salvar templates
- Reutilizar facilmente

### 3. Logs Detalhados

**Vê cada email:**
- Status: Delivered, Opened, Clicked
- Timestamp exato
- IP do destinatário
- Device usado

### 4. Webhooks (Avançado)

**MailerSend pode avisar seu sistema:**
- Quando email foi entregue
- Quando foi aberto
- Quando link foi clicado

**Útil para:** rastrear se cliente abriu email de ativação!

---

## 📊 Limites do Free Tier

### O Que Você Tem:

- ✅ 12.000 emails/mês
- ✅ ~400 emails/dia
- ✅ Analytics completo
- ✅ Templates ilimitados
- ✅ API completa
- ✅ Webhooks
- ✅ Suporte por email

### Quando Precisar Upgrade:

**Se passar de 12.000/mês:**
- Starter: $25/mês (50k emails)
- Ainda muito barato!

**Por enquanto:** 12.000 é MUITO para você! ✅

---

## 🎯 Próximos Passos (Após Configurar)

Quando MailerSend estiver OK:

1. ✅ Testar envio
2. ✅ Modificar webhook para usar
3. ✅ Criar página de ativação
4. ✅ Testar fluxo completo

---

## 📞 Status Atual

```
✅ Domínio: pontootimo.com.br comprado
✅ Código: Adaptado para MailerSend
✅ Templates: Prontos (email_service.py)
✅ requirements.txt: mailersend adicionado
⏳ MailerSend: Aguardando você configurar
⏳ DNS: Aguardando adicionar registros
```

---

## 🚀 Comece Agora!

### Sequência:

**1. Login MailerSend** (já fez? ✅)

**2. Domains → Add Domain** (5 min)
- pontootimo.com.br
- Copiar DNS records

**3. Registro.br → DNS** (15 min)
- Adicionar 1 TXT + 3 CNAMEs
- Salvar

**4. MailerSend → Verify** (aguardar 15-60 min)
- Clicar em "Verify DNS records"
- Aguardar checks verdes

**5. API Tokens → Create** (5 min)
- Nome: Railway
- Copiar token

**6. Railway → Variables** (5 min)
- MAILERSEND_API_KEY
- FROM_EMAIL

**7. Testar!** (5 min)
- `python3 email_service.py`

---

## ✨ Vantagens Extras do MailerSend

### 1. Email Templates (Visual Editor)

**Pode criar templates visuais:**
- Sem código HTML
- Arrastar blocos
- Preview imediato
- Salvar e reutilizar

**Útil para:** criar variações de emails facilmente!

### 2. Suppressions (Lista de Bloqueio)

**MailerSend gerencia automaticamente:**
- Emails que deram bounce
- Spam complaints
- Unsubscribes

**Você não precisa se preocupar!**

### 3. Scheduled Sending

**Pode agendar emails:**
- Enviar em horário específico
- Melhor taxa de abertura
- Útil para campanhas

---

## 🎯 O Que Fazer AGORA

**Passo 1:** Já está logada no MailerSend ✅

**Passo 2:** Seguir este guia:
1. Domains → Add Domain
2. Copiar DNS records
3. Adicionar no Registro.br
4. Aguardar verificação
5. Criar API Token
6. Configurar Railway

**Passo 3:** Me avisar quando tiver API Token!

---

**📁 Código pronto:** `email_service.py` (adaptado para MailerSend)  
**📋 Checklist:** Acima  
**⏰ Tempo:** ~45 minutos

**Bora configurar! 🚀**

---

## 📞 Me Avise Quando:

- ✅ Domínio adicionado no MailerSend
- ✅ DNS records copiados
- ✅ Registros adicionados no Registro.br
- ✅ API Token obtido
- ❓ Qualquer dúvida ou problema

**Enquanto você configura, vou criar a página de ativação HTML! 🎨**

