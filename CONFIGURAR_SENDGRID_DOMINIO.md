# 🔧 Configurar SendGrid com Domínio pontootimo.com.br

**Tempo estimado:** 30-45 minutos  
**Método:** API (recomendado)

---

## ✅ Pré-requisitos

- [x] Domínio comprado: pontootimo.com.br ✅
- [ ] Conta SendGrid criada
- [ ] Acesso ao painel do Registro.br

---

## 📋 Passo a Passo

### PARTE 1: Criar Conta SendGrid (10 min)

#### 1. Criar Conta

1. **Acesse:** https://signup.sendgrid.com
2. **Preencha:**
   - Email: seu_email@gmail.com
   - Password: (crie uma senha forte)
   - Nome: Suellen
   - Empresa: Ponto Ótimo Invest
3. **Plano:** Free (100 emails/dia)
4. **Confirme seu email** (check inbox)

#### 2. Completar Perfil

SendGrid vai pedir:
- Tipo de negócio: Education/Technology
- Uso: Transactional emails
- Volume esperado: < 100/dia

**Responda honestamente!**

---

### PARTE 2: Autenticar Domínio (20 min)

#### 3. Iniciar Autenticação

**No painel SendGrid:**

1. Menu esquerdo → **Settings**
2. Clique em **Sender Authentication**
3. Clique no botão **"Authenticate Your Domain"**

#### 4. Configurar Domínio

**Tela 1 - DNS Host:**
- Pergunta: "Which DNS host do you use?"
- Resposta: **"Other Host (Not Listed)"**
- Next

**Tela 2 - Domínio:**
- Domain You Send From: **`pontootimo.com.br`**
- Would you also like to brand the links? **Yes** (recomendado)
- Next

**Tela 3 - Configurações Avançadas:**
- Use automated security: **Yes**
- Next

#### 5. Copiar Registros DNS

SendGrid vai mostrar **3 registros CNAME**:

```
Exemplo (seus valores serão diferentes):

┌─────────────────────────────────────────────────────────┐
│ CNAME Record 1                                          │
├─────────────────────────────────────────────────────────┤
│ Host: em1234                                            │
│ Value: u1234567.wl123.sendgrid.net                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ CNAME Record 2                                          │
├─────────────────────────────────────────────────────────┤
│ Host: s1._domainkey                                     │
│ Value: s1.domainkey.u1234567.wl123.sendgrid.net         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ CNAME Record 3                                          │
├─────────────────────────────────────────────────────────┤
│ Host: s2._domainkey                                     │
│ Value: s2.domainkey.u1234567.wl123.sendgrid.net         │
└─────────────────────────────────────────────────────────┘
```

**⚠️ COPIE TODOS OS 3 REGISTROS!** Vamos usar agora.

**NÃO FECHE ESTA PÁGINA** - deixe aberta para verificar depois.

---

### PARTE 3: Configurar DNS no Registro.br (15 min)

#### 6. Acessar Painel Registro.br

1. **Acesse:** https://registro.br
2. **Login** com sua conta
3. **Meus Domínios** → Clique em **pontootimo.com.br**

#### 7. Editar Zona DNS

1. Procure opção **"Editar Zona"** ou **"DNS"** ou **"Gerenciar DNS"**
2. Modo de edição: **"Modo Avançado"** ou **"Adicionar Registro"**

#### 8. Adicionar os 3 CNAMEs

**Para cada um dos 3 registros do SendGrid:**

**CNAME 1:**
```
Tipo: CNAME
Nome: em1234.pontootimo.com.br
Dados: u1234567.wl123.sendgrid.net
TTL: 3600 (ou padrão)
```

**CNAME 2:**
```
Tipo: CNAME
Nome: s1._domainkey.pontootimo.com.br
Dados: s1.domainkey.u1234567.wl123.sendgrid.net
TTL: 3600
```

**CNAME 3:**
```
Tipo: CNAME
Nome: s2._domainkey.pontootimo.com.br
Dados: s2.domainkey.u1234567.wl123.sendgrid.net
TTL: 3600
```

**⚠️ ATENÇÃO:**
- Substitua pelos valores EXATOS que o SendGrid te deu
- **Não** adicione `pontootimo.com.br` se o painel já adiciona automaticamente
- Alguns painéis querem só `em1234`, outros querem `em1234.pontootimo.com.br`

#### 9. Salvar Mudanças

- Clique em **"Salvar"** ou **"Aplicar Mudanças"**
- Confirme a operação

---

### PARTE 4: Verificar Autenticação (5-60 min)

#### 10. Aguardar Propagação DNS

**Tempo:** 15 min - 48 horas (geralmente < 1 hora)

#### 11. Verificar no SendGrid

**Volte para a página do SendGrid que você deixou aberta:**

1. Clique em **"Verify"** (botão na página dos CNAMEs)
2. SendGrid vai checar os registros DNS

**Resultados possíveis:**

✅ **Sucesso:** Todos os 3 checks verdes
- Você pode usar o domínio!

⏳ **Pendente:** "DNS records not found yet"
- Aguarde mais alguns minutos
- Clique em "Verify" novamente

❌ **Erro:** "Invalid CNAME"
- Verifique se copiou corretamente
- Verifique se adicionou no Registro.br correto

#### 12. Testar Enquanto Aguarda (Opcional)

**Usar Single Sender temporariamente:**

1. SendGrid → Sender Authentication → **Single Sender Verification**
2. Create New Sender:
   - From Name: Ponto Ótimo Invest
   - From Email: **seu_email@gmail.com**
   - Reply To: mesmo
3. Verificar email
4. **Pode usar TEMPORARIAMENTE** enquanto domínio não verifica

---

### PARTE 5: Criar API Key (5 min)

#### 13. Gerar API Key

**No SendGrid:**

1. Settings → **API Keys**
2. **Create API Key**
3. **Nome:** "Railway Webhook Ponto Otimo"
4. **Permissions:** 
   - Full Access (mais simples)
   - OU: Restricted Access → Mail Send (mais seguro)
5. **Create & View**

#### 14. COPIAR A CHAVE

```
SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ IMPORTANTE:**
- Aparece SÓ UMA VEZ!
- Copie e salve em local seguro
- Se perder, precisa criar nova

---

### PARTE 6: Configurar na Railway (5 min)

#### 15. Adicionar Variáveis

**Railway Dashboard:**

1. Seu projeto → **Variables**
2. **New Variable:**

```
Nome: SENDGRID_API_KEY
Valor: SG.xxxxxxxx... (cole a chave)
```

3. **New Variable:**

```
Nome: FROM_EMAIL
Valor: noreply@pontootimo.com.br
```

**OU se ainda não verificou domínio:**
```
Valor: seu_email@gmail.com (temporário)
```

4. **Salvar** (Railway fará redeploy)

---

### PARTE 7: Testar (10 min)

#### 16. Adicionar SendGrid ao requirements.txt

**No seu projeto local:**

```bash
cd /Users/suellenpinto/projetos/dashboard-analise-acoes
echo "sendgrid==6.11.0" >> requirements.txt
git add requirements.txt email_service.py
git commit -m "Adiciona integração SendGrid"
git push origin main
```

**Aguarde Railway fazer redeploy (2-3 min)**

#### 17. Testar Envio

**Opção A: Via código Python (local):**

```bash
export SENDGRID_API_KEY="SG.sua_chave_aqui"
export FROM_EMAIL="noreply@pontootimo.com.br"
python3 email_service.py
```

Digite seu email quando pedir e veja se recebe!

**Opção B: Via Railway (produção):**

Aguardar implementar webhook completo (próximo passo)

---

## ✅ Checklist de Verificação

### SendGrid:
- [ ] Conta criada
- [ ] Email confirmado
- [ ] Domínio adicionado
- [ ] 3 CNAMEs configurados no Registro.br
- [ ] Domínio verificado (checks verdes) ✅
- [ ] API Key criada
- [ ] API Key salva em local seguro

### Railway:
- [ ] SENDGRID_API_KEY adicionada
- [ ] FROM_EMAIL configurada
- [ ] APP_URL já existe (✅ já tem)

### Código:
- [ ] sendgrid==6.11.0 em requirements.txt
- [ ] email_service.py criado
- [ ] Push para GitHub
- [ ] Railway fez redeploy

### Teste:
- [ ] Email de teste enviado
- [ ] Email recebido na caixa de entrada
- [ ] Não caiu em spam

---

## 🐛 Troubleshooting

### Domínio não verifica (após 1h)

**Verificar:**

1. **DNS está correto?**
   - Teste: `dig em1234.pontootimo.com.br CNAME`
   - Deve retornar o valor do SendGrid

2. **Propagação completa?**
   - Use: https://dnschecker.org
   - Digite: `em1234.pontootimo.com.br`
   - Veja se propagou mundialmente

3. **Formato correto?**
   - Registro.br: alguns campos são só `em1234`, outros `em1234.pontootimo.com.br`
   - Teste ambos formatos

### Email cai em spam

**Soluções:**

1. **Domínio precisa estar verificado** (checks verdes)
2. **Aguardar 24-48h** após verificação (reputação do domínio)
3. **Pedir destinatário marcar como "Não é spam"**
4. **Adicionar SPF** (opcional):
   ```
   TXT: v=spf1 include:sendgrid.net ~all
   ```

### API Key não funciona

**Verificar:**

1. Copiou a chave completa? (começa com `SG.`)
2. Permissions estão corretas? (Full Access ou Mail Send)
3. Key não foi deletada/revogada?

---

## 💡 Dicas Importantes

### 1. Verificação Leva Tempo

- Mínimo: 15 minutos
- Normal: 1-2 horas
- Máximo: 48 horas

**Seja paciente!** DNS demora para propagar.

### 2. Use Single Sender Enquanto Aguarda

**Pode usar seu Gmail temporariamente:**
- FROM_EMAIL=seu_email@gmail.com
- Funciona imediatamente
- Troca depois quando domínio verificar

### 3. Monitore SendGrid

**Dashboard SendGrid → Activity:**
- Veja emails enviados
- Status de entrega
- Taxa de abertura (depois)

---

## 🎯 Próximos Passos (Após Configurar)

Quando SendGrid estiver funcionando:

1. ✅ Migrar banco (adicionar colunas)
2. ✅ Criar página de ativação
3. ✅ Modificar webhook
4. ✅ Testar fluxo completo

---

## 📞 Status Atual

```
✅ Domínio: pontootimo.com.br comprado
⏳ SendGrid: Aguardando você configurar
⏳ DNS: Aguardando adicionar CNAMEs
📧 Templates: Prontos (email_service.py)
```

---

## 🚀 Comece Agora!

**Siga este guia passo a passo:**

1. Criar conta SendGrid (10 min)
2. Autenticar domínio (get CNAMEs)
3. Configurar DNS no Registro.br (15 min)
4. Aguardar verificação (15 min - 2h)
5. Criar API Key
6. Testar email

**Enquanto você faz isso, eu crio a página de ativação!** 🎨

---

**Me avise quando:**
- ✅ SendGrid criado
- ✅ CNAMEs adicionados no Registro.br
- ✅ API Key obtida

**Aí continuamos com o resto!** 🚀

