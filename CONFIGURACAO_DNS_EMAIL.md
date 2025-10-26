# 🔧 CONFIGURAÇÃO DNS PARA EMAILS - PONTO ÓTIMO INVEST

## 📋 REGISTROS DNS NECESSÁRIOS

### 1. SPF Record (Sender Policy Framework)
**Tipo:** TXT
**Nome:** @ (ou domínio raiz)
**Valor:** `v=spf1 include:_spf.google.com ~all`
**TTL:** 3600

### 2. DKIM (DomainKeys Identified Mail)
**Tipo:** TXT
**Nome:** google._domainkey
**Valor:** (obter no Google Admin Console)
**TTL:** 3600

### 3. DMARC (Domain-based Message Authentication)
**Tipo:** TXT
**Nome:** _dmarc
**Valor:** `v=DMARC1; p=quarantine; rua=mailto:dmarc@pontootimoinvest.com`
**TTL:** 3600

## 🎯 COMO CONFIGURAR NO GOOGLE

### Passo 1: Ativar DKIM no Gmail
1. Acesse: https://admin.google.com
2. Apps → G Suite → Gmail
3. Autenticação
4. Selecione seu domínio
5. Gere o registro DKIM
6. Copie o valor gerado

### Passo 2: Adicionar no DNS
- Nome: `google._domainkey`
- Tipo: TXT
- Valor: (copiado do Google)

## 🔍 VERIFICAÇÃO

### Testar Configuração:
1. https://mxtoolbox.com/spf.aspx
2. https://mxtoolbox.com/dkim.aspx
3. https://mxtoolbox.com/dmarc.aspx

### Testar Email:
1. https://www.mail-tester.com
2. Envie um email de teste
3. Verifique a pontuação (deve ser 8+)

## ⚠️ IMPORTANTE

- **Propagação DNS:** 24-48 horas
- **Teste após 24h** para confirmar funcionamento
- **Mantenha backups** dos registros originais

## 🆘 PROBLEMAS COMUNS

### SPF não funciona:
- Verifique se não há múltiplos registros SPF
- Use apenas um registro SPF por domínio

### DKIM falha:
- Confirme que o nome está correto: `google._domainkey`
- Verifique se o valor está completo

### DMARC rejeita emails:
- Mude de `p=reject` para `p=quarantine`
- Monitore relatórios em `rua=mailto:`
