# ✅ Checklist de Migração para Railway

Use este checklist para garantir que todos os passos foram executados corretamente.

---

## 📋 PRÉ-REQUISITOS

- [ ] Conta no GitHub com repositório `dashboard-analise-acoes`
- [ ] Banco de dados Neon PostgreSQL funcionando
- [ ] Acesso ao painel da Hotmart
- [ ] URL do DATABASE_URL (Neon)
- [ ] Token HOTMART_HOTTOK

---

## 🚀 PARTE 1: Preparação dos Arquivos (COMPLETO ✅)

- [x] Procfile atualizado (2 workers, 2 threads)
- [x] railway.json criado
- [x] RAILWAY_SETUP.md criado
- [x] ENVIRONMENT_VARIABLES.md criado
- [x] test_webhook_railway.py criado
- [x] Arquivos commitados no Git

---

## 🌐 PARTE 2: Configuração na Railway (VOCÊ FAZ AGORA)

### 2.1 Criar Conta
- [ ] Acessar https://railway.app
- [ ] Clicar em "Login with GitHub"
- [ ] Autorizar Railway a acessar GitHub
- [ ] Confirmar que está logado

### 2.2 Criar Projeto
- [ ] Clicar em "New Project"
- [ ] Selecionar "Deploy from GitHub repo"
- [ ] Escolher repositório: `dashboard-analise-acoes`
- [ ] Aguardar Railway detectar Python

### 2.3 Configurar Variáveis de Ambiente

**DATABASE_URL:**
- [ ] Ir em Variables → New Variable
- [ ] Nome: `DATABASE_URL`
- [ ] Valor: Cole a URL do Neon (começando com `postgresql://`)
- [ ] Clicar em "Add"

**HOTMART_HOTTOK:**
- [ ] Clicar em "New Variable" novamente
- [ ] Nome: `HOTMART_HOTTOK`
- [ ] Valor: Cole o token da Hotmart
- [ ] Clicar em "Add"

### 2.4 Verificar Build
- [ ] Ir na aba "Deployments"
- [ ] Verificar que build iniciou automaticamente
- [ ] Aguardar status "Deployed" (pode levar 2-3 minutos)
- [ ] Verificar que não há erros nos logs

### 2.5 Gerar Domínio
- [ ] Ir em Settings → Networking
- [ ] Clicar em "Generate Domain"
- [ ] Copiar a URL gerada (ex: `https://dashboard-analise-acoes-production.up.railway.app`)
- [ ] Salvar essa URL para os testes

---

## 🧪 PARTE 3: Testes (VOCÊ FAZ AGORA)

### 3.1 Teste Manual Básico

Abra o navegador e acesse:
- [ ] `https://sua-url.railway.app/` (deve mostrar mensagem)
- [ ] `https://sua-url.railway.app/health` (deve mostrar JSON com status:healthy)

### 3.2 Teste com Script Python

No terminal, execute:
```bash
cd /Users/suellenpinto/projetos/dashboard-analise-acoes
python3 test_webhook_railway.py
```

Quando solicitado:
- [ ] Cole a URL da Railway
- [ ] Cole o HOTMART_HOTTOK
- [ ] Verificar que todos os testes passaram ✅

### 3.3 Teste de Latência

```bash
time curl https://sua-url.railway.app/health
```

- [ ] Tempo < 2 segundos? ✅ Excelente!
- [ ] Tempo 2-5 segundos? ⚠️ Aceitável
- [ ] Tempo > 5 segundos? ❌ Investigar

---

## 🔄 PARTE 4: Atualização da Hotmart (VOCÊ FAZ AGORA)

### 4.1 Backup da Configuração Atual
- [ ] Anotar URL atual do webhook no Render
- [ ] Tirar screenshot das configurações

### 4.2 Atualizar URL
- [ ] Acessar painel Hotmart
- [ ] Ir em Ferramentas → Webhooks
- [ ] Atualizar URL para: `https://sua-url.railway.app/webhook/hotmart`
- [ ] Salvar alterações
- [ ] Verificar que salvou corretamente

---

## ✅ PARTE 5: Validação em Produção (VOCÊ FAZ AGORA)

### 5.1 Teste de Compra (Simulado)

Use o script para simular:
```bash
curl -X POST https://sua-url.railway.app/webhook/hotmart \
  -H "Content-Type: application/json" \
  -H "X-Hotmart-Hottok: SEU_HOTTOK" \
  -d '{
    "event": "PURCHASE_APPROVED",
    "data": {
      "buyer": {
        "email": "teste_validacao@exemplo.com",
        "name": "Teste Validacao"
      }
    }
  }'
```

- [ ] Retornou status 200? ✅
- [ ] Tempo de resposta < 5s? ✅
- [ ] Verificar logs na Railway (deve mostrar processamento)

### 5.2 Verificar Banco de Dados

Conectar ao Neon e verificar:
- [ ] Usuário `teste_validacao@exemplo.com` foi criado?
- [ ] Status da assinatura está "ativo"?
- [ ] Senha foi gerada (hash presente)?

### 5.3 Teste Real (IMPORTANTE!)

**Fazer uma venda teste na Hotmart:**
- [ ] Fazer compra teste (ou simular no painel Hotmart)
- [ ] Verificar logs na Railway (webhook recebido?)
- [ ] Verificar que usuário foi criado no banco
- [ ] Verificar que NÃO houve erro 408
- [ ] Tempo de resposta foi aceitável?

---

## 📊 PARTE 6: Monitoramento (PRIMEIRAS 24-48 HORAS)

### 6.1 Monitorar Métricas
- [ ] Acessar dashboard Railway → Metrics
- [ ] Verificar CPU usage (deve ser baixo, < 20%)
- [ ] Verificar Memory usage (deve ser < 200MB)
- [ ] Verificar Response time (deve ser < 2s)

### 6.2 Verificar Logs
- [ ] Ir em Deployments → View Logs
- [ ] Verificar se não há erros
- [ ] Confirmar que webhooks estão sendo recebidos
- [ ] Verificar que conexões com banco estão OK

### 6.3 Verificar Custos
- [ ] Ir em Usage → Current Usage
- [ ] Verificar consumo atual (deve estar dentro dos $5 de crédito)
- [ ] Anotar uso diário para estimar custo mensal

---

## 🎉 PARTE 7: Finalização

### 7.1 Desativar Render (DEPOIS DE CONFIRMAR QUE RAILWAY ESTÁ OK)
- [ ] Aguardar 48 horas de Railway funcionando sem problemas
- [ ] Acessar painel do Render
- [ ] Pausar ou deletar o serviço antigo
- [ ] Liberar recursos

### 7.2 Documentação
- [ ] Atualizar README.md com nova URL
- [ ] Documentar credenciais da Railway (em local seguro)
- [ ] Salvar URL do projeto Railway

### 7.3 Comunicação
- [ ] Avisar time/clientes sobre mudança (se aplicável)
- [ ] Monitorar reclamações de acesso nos primeiros dias

---

## 🚨 PLANO DE ROLLBACK (Se algo der errado)

### Se Railway não funcionar:

1. **IMEDIATO:**
   - [ ] Voltar URL na Hotmart para Render
   - [ ] Verificar que Render ainda está funcionando
   - [ ] Comunicar problema

2. **INVESTIGAÇÃO:**
   - [ ] Verificar logs na Railway
   - [ ] Confirmar variáveis de ambiente
   - [ ] Testar endpoints manualmente
   - [ ] Verificar conexão com banco Neon

3. **CORREÇÃO:**
   - [ ] Corrigir problema identificado
   - [ ] Fazer novo deploy na Railway
   - [ ] Testar novamente
   - [ ] Se OK, atualizar Hotmart novamente

---

## 📈 CRITÉRIOS DE SUCESSO

A migração será considerada bem-sucedida quando:

- ✅ Zero erros 408 da Hotmart
- ✅ Tempo de resposta consistente < 5 segundos
- ✅ Clientes recebem acesso em até 1 minuto após compra
- ✅ Custo mensal < $10
- ✅ Sem reclamações de clientes sobre acesso
- ✅ 100% de uptime nos primeiros 7 dias

---

## 📞 SUPORTE

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**Problemas Técnicos:**
- Verificar logs na Railway
- Consultar RAILWAY_SETUP.md
- Consultar ENVIRONMENT_VARIABLES.md

---

## ✨ PRÓXIMOS PASSOS (Após 1 semana)

- [ ] Avaliar se ainda há timeouts (considerar Redis se sim)
- [ ] Analisar custos reais vs estimados
- [ ] Avaliar performance geral
- [ ] Decidir se continua na Railway ou ajusta plano

---

**Data de início da migração:** _______________  
**Data de conclusão:** _______________  
**Responsável:** _______________

---

**🎯 Status Geral:**
- [ ] 🔴 Não iniciado
- [ ] 🟡 Em andamento
- [ ] 🟢 Concluído com sucesso
- [ ] 🔵 Rollback realizado

