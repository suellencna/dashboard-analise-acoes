# 🔧 MIGRAÇÃO DO BANCO - PASSO A PASSO

## 📋 **SIGA ESTES PASSOS:**

### **1️⃣ Acessar o Neon Dashboard**

1. Abra no navegador: https://console.neon.tech
2. Faça login com sua conta
3. Você verá seu projeto `dashboard-analise-acoes`

---

### **2️⃣ Abrir o SQL Editor**

1. Clique no projeto `dashboard-analise-acoes`
2. No menu lateral esquerdo, procure por **"SQL Editor"**
3. Clique em **"SQL Editor"**
4. Uma tela de editor SQL vai abrir

---

### **3️⃣ Copiar o SQL Abaixo**

**COPIE TODO O CÓDIGO ABAIXO (Ctrl+C / Cmd+C):**

```sql
-- Migração: Adicionar campos para sistema de ativação de conta
-- Data: 2025-10-18

-- 1. Adicionar coluna status_conta
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS status_conta VARCHAR(20) DEFAULT 'pendente';

-- 2. Adicionar coluna token_ativacao
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS token_ativacao VARCHAR(100) UNIQUE;

-- 3. Adicionar coluna data_expiracao_token
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS data_expiracao_token TIMESTAMP;

-- 4. Adicionar coluna data_aceite_termos
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS data_aceite_termos TIMESTAMP;

-- 5. Adicionar coluna data_ativacao
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS data_ativacao TIMESTAMP;

-- 6. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_token_ativacao ON usuarios(token_ativacao);
CREATE INDEX IF NOT EXISTS idx_status_conta ON usuarios(status_conta);
CREATE INDEX IF NOT EXISTS idx_data_expiracao ON usuarios(data_expiracao_token);

-- 7. Atualizar usuários existentes
UPDATE usuarios 
SET status_conta = 'ativo' 
WHERE senha_hash IS NOT NULL 
AND (status_conta IS NULL OR status_conta = 'pendente');

-- 8. Comentários nas colunas
COMMENT ON COLUMN usuarios.status_conta IS 'Status da conta: pendente, ativo, suspenso, cancelado';
COMMENT ON COLUMN usuarios.token_ativacao IS 'Token único para ativação de conta via email';
COMMENT ON COLUMN usuarios.data_expiracao_token IS 'Data de expiração do token (48 horas após criação)';
COMMENT ON COLUMN usuarios.data_aceite_termos IS 'Data e hora que o usuário aceitou os termos de uso';
COMMENT ON COLUMN usuarios.data_ativacao IS 'Data e hora que a conta foi ativada';
```

---

### **4️⃣ Colar no SQL Editor**

1. Cole (Ctrl+V / Cmd+V) no editor SQL do Neon
2. Certifique-se de que TODO o código foi colado

---

### **5️⃣ Executar o SQL**

1. Clique no botão **"Run"** ou **"Execute"** (geralmente um botão verde)
2. Aguarde alguns segundos
3. Você verá mensagens de sucesso

**Mensagens esperadas:**
```
✅ ALTER TABLE
✅ CREATE INDEX
✅ UPDATE 1 (ou o número de usuários que você tem)
✅ COMMENT
```

---

### **6️⃣ Verificar se Funcionou**

Ainda no SQL Editor, execute esta query para verificar:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'usuarios'
ORDER BY ordinal_position;
```

**Você deve ver estas novas colunas:**
- ✅ `status_conta`
- ✅ `token_ativacao`
- ✅ `data_expiracao_token`
- ✅ `data_aceite_termos`
- ✅ `data_ativacao`

---

## ✅ **PRONTO! MIGRAÇÃO CONCLUÍDA!**

Quando terminar, me avise e vamos testar o sistema completo!

---

## ❓ **Problemas?**

### **Erro: "column already exists"**
✅ **Normal!** Pode executar de novo sem problemas.

### **Erro: "table usuarios does not exist"**
❌ Problema: tabela não existe. Verifique se está no banco correto.

### **Erro: "permission denied"**
❌ Problema: usuário sem permissão. Verifique se está logado corretamente.

---

## 📞 **ME AVISE:**

Quando executar, me diga:
1. ✅ "Migração executada com sucesso!" ou
2. ❌ "Erro: [mensagem do erro]"

