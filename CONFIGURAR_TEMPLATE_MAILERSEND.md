# 📧 CONFIGURAR TEMPLATE NO MAILERSEND

## 🎯 **OBJETIVO:**
Melhorar a entregabilidade dos emails usando o domínio `pontootimo.com.br` com template profissional.

---

## 📋 **PASSO A PASSO:**

### **1️⃣ Acessar MailerSend Dashboard**
1. Vá para: https://app.mailersend.com/
2. Faça login com sua conta
3. Vá em **"Templates"** no menu lateral

### **2️⃣ Criar Novo Template**
1. Clique em **"Create Template"**
2. Escolha **"Blank Template"**
3. Nome: `"Ativação de Conta - Ponto Ótimo Invest"`

### **3️⃣ Configurar Template**

#### **A. Conteúdo HTML:**
Copie o conteúdo do arquivo `template_email_simples.html` e cole no editor HTML do MailerSend.

#### **B. Variáveis do Template:**
Configure estas variáveis no MailerSend:
- `{{nome}}` → Nome do usuário
- `{{link_ativacao}}` → Link de ativação

#### **C. Assunto do Email:**
```
Ative sua conta - Ponto Ótimo Invest
```

#### **D. Remetente:**
- **Nome:** Ponto Ótimo Invest
- **Email:** noreply@pontootimo.com.br

### **4️⃣ Configurar Domínio (Se necessário)**
1. Vá em **"Domains"** no menu
2. Verifique se `pontootimo.com.br` está:
   - ✅ Verificado
   - ✅ SPF configurado
   - ✅ DKIM configurado
   - ✅ DMARC configurado

### **5️⃣ Testar Template**
1. Use a função **"Send Test"** do MailerSend
2. Envie para seus próprios emails
3. Verifique se chega na caixa de entrada

---

## 🔧 **MELHORAR ENTREGABILIDADE:**

### **A. Warming Up do Domínio (2-3 semanas)**
1. **Semana 1:** 10-20 emails/dia
2. **Semana 2:** 30-50 emails/dia  
3. **Semana 3:** 50-100 emails/dia
4. **Semana 4+:** Volume normal

### **B. Boas Práticas:**
- ✅ **Evitar palavras "spam"** no assunto/conteúdo
- ✅ **Conteúdo educacional** (não comercial)
- ✅ **Design limpo** e profissional
- ✅ **Links válidos** e funcionais
- ✅ **Unsubscribe** (opcional, mas recomendado)

### **C. Monitoramento:**
- 📊 **Taxa de abertura:** >20% é bom
- 📊 **Taxa de clique:** >5% é bom
- 📊 **Taxa de bounce:** <5% é bom
- 📊 **Taxa de spam:** <1% é bom

---

## 📝 **TEMPLATE OTIMIZADO PARA ENTREGABILIDADE:**

### **Assunto Sugerido:**
```
🔐 Ative sua conta - Ponto Ótimo Invest
```

### **Conteúdo Otimizado:**
- ✅ **Título claro** e não comercial
- ✅ **Conteúdo educacional** (ferramentas de análise)
- ✅ **Call-to-action** simples
- ✅ **Disclaimer CVM** (conformidade)
- ✅ **Design responsivo**

### **Evitar:**
- ❌ Palavras: "oferta", "promoção", "desconto", "grátis"
- ❌ Muitas imagens
- ❌ Links suspeitos
- ❌ Conteúdo muito comercial

---

## 🚀 **IMPLEMENTAÇÃO NO CÓDIGO:**

### **Atualizar `email_service.py`:**
```python
def enviar_email_ativacao(email, nome, token):
    # Usar template do MailerSend
    template_id = "seu_template_id_aqui"  # ID do template criado
    
    mailer = emails.NewEmail(MAILERSEND_API_KEY)
    
    # Usar template em vez de HTML customizado
    mailer.set_template_id(template_id)
    
    # Variáveis do template
    mailer.set_template_variables({
        "nome": nome,
        "link_ativacao": f"{APP_URL}/ativar/{token}"
    })
```

---

## 📊 **MÉTRICAS DE SUCESSO:**

### **Meta de Entregabilidade:**
- **Gmail:** 95%+ (já funciona)
- **Yahoo:** 70%+ (melhorar com warming up)
- **Hotmail/Outlook:** 60%+ (melhorar com warming up)
- **Outros:** 80%+

### **Timeline:**
- **Semana 1:** Implementar template
- **Semana 2-4:** Warming up gradual
- **Semana 4+:** Entregabilidade otimizada

---

## 🔍 **MONITORAMENTO:**

### **Ferramentas:**
1. **MailerSend Analytics** - Taxa de entrega
2. **Google Postmaster** - Reputação do domínio
3. **Microsoft SNDS** - Reputação no Outlook

### **Indicadores:**
- 📈 **Aumento gradual** da taxa de entrega
- 📈 **Redução** de emails em spam
- 📈 **Melhoria** da reputação do domínio

---

## ✅ **CHECKLIST DE IMPLEMENTAÇÃO:**

- [ ] Template criado no MailerSend
- [ ] Variáveis configuradas
- [ ] Domínio verificado
- [ ] DNS configurado (SPF, DKIM, DMARC)
- [ ] Teste enviado com sucesso
- [ ] Código atualizado para usar template
- [ ] Plano de warming up definido
- [ ] Monitoramento configurado

---

**🎯 Com essa estratégia, você deve conseguir 80%+ de entregabilidade em 3-4 semanas!**
