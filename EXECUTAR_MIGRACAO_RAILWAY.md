# 🔧 Como Executar a Migração no Railway

Este documento explica como executar a migração do banco de dados para adicionar os campos necessários ao sistema de ativação.

## 📋 **Opção 1: Executar via Railway CLI (Recomendado)**

### **Passo 1: Instalar Railway CLI**

```bash
npm install -g @railway/cli
```

### **Passo 2: Fazer Login**

```bash
railway login
```

### **Passo 3: Linkar o Projeto**

```bash
railway link
```

Selecione o projeto `dashboard-analise-acoes`

### **Passo 4: Executar Migração**

```bash
railway run python migrate_database.py
```

---

## 📋 **Opção 2: Executar via SQL Direto no Neon**

### **Passo 1: Acessar Neon Dashboard**

1. Acesse: https://console.neon.tech
2. Login com sua conta
3. Selecione o projeto `dashboard-analise-acoes`
4. Clique em "SQL Editor"

### **Passo 2: Executar SQL**

Copie e cole o conteúdo do arquivo `migrations/add_activation_fields.sql` no SQL Editor e execute.

---

## 📋 **Opção 3: Executar Localmente (Requer DATABASE_URL)**

### **Passo 1: Obter DATABASE_URL**

No Railway:
1. Acesse o projeto
2. Vá em "Variables"
3. Copie o valor de `DATABASE_URL`

### **Passo 2: Executar**

```bash
export DATABASE_URL="sua_database_url_aqui"
python migrate_database.py
```

---

## ✅ **Verificar se a Migração Funcionou**

Após executar a migração, verifique se as colunas foram adicionadas:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'usuarios'
ORDER BY ordinal_position;
```

### **Colunas Esperadas:**

- ✅ `status_conta` (VARCHAR)
- ✅ `token_ativacao` (VARCHAR)
- ✅ `data_expiracao_token` (TIMESTAMP)
- ✅ `data_aceite_termos` (TIMESTAMP)
- ✅ `data_ativacao` (TIMESTAMP)

---

## 🚀 **Após a Migração**

1. ✅ Migração executada
2. ✅ Código já está no Railway (último push)
3. ✅ Variáveis de ambiente configuradas
4. ✅ Sistema pronto para testar!

### **Testar o Sistema:**

1. Faça uma compra de teste no Hotmart
2. Verifique se o email de ativação chega
3. Clique no link de ativação
4. Crie sua senha
5. Verifique se a conta foi ativada

---

## 📧 **Email de Teste Manual**

Para testar o email de ativação sem fazer uma compra:

```bash
curl -X GET "https://web-production-e66d.up.railway.app/test-email?email=seu-email@exemplo.com"
```

---

## ❓ **Problemas Comuns**

### **Erro: "column already exists"**

✅ **Normal!** A migração usa `IF NOT EXISTS`, então é seguro executar várias vezes.

### **Erro: "password authentication failed"**

❌ DATABASE_URL incorreta. Verifique no Railway.

### **Erro: "connection timeout"**

❌ Firewall bloqueando. Use a Opção 1 (Railway CLI) ou Opção 2 (SQL direto no Neon).

---

## 📞 **Próximos Passos**

Após a migração:
1. ✅ Testar fluxo completo de ativação
2. ✅ Ajustar templates de email (se necessário)
3. ✅ Criar página de "Termos de Uso"
4. ✅ Testar integração com Hotmart

---

**🎯 Sistema de Ativação Completo!**

