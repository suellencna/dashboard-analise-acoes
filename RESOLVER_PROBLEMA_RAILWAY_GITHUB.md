# 🔧 Resolver "No repositories found" na Railway

## Problema
Ao tentar criar deploy na Railway, aparece: **"No repositories found - try a different search"**

## Causa
Railway não tem permissão para acessar seus repositórios no GitHub.

---

## ✅ Solução Passo a Passo

### Método 1: Autorizar Railway no GitHub (RECOMENDADO)

#### Passo 1: Acessar Configurações do GitHub
1. Abra: https://github.com/settings/installations
2. Você verá uma lista de "Installed GitHub Apps"

#### Passo 2: Encontrar Railway
3. Procure por "Railway" na lista
4. Clique em "Configure" ao lado de Railway

#### Passo 3: Autorizar Repositório
5. Role até "Repository access"
6. Você verá duas opções:
   - **All repositories** (todos os repos)
   - **Only select repositories** (apenas alguns)

**Escolha uma das opções:**

**Opção A: Autorizar todos os repositórios**
- Selecione "All repositories"
- Clique em "Save"

**Opção B: Autorizar apenas dashboard-analise-acoes (RECOMENDADO)**
- Selecione "Only select repositories"
- Clique no dropdown "Select repositories"
- Encontre e selecione: `dashboard-analise-acoes`
- Clique em "Save"

#### Passo 4: Voltar para Railway
7. Volte para https://railway.app
8. Tente criar o projeto novamente:
   - New Project → Deploy from GitHub repo
9. Agora o repositório deve aparecer! ✅

---

### Método 2: Reinstalar Railway no GitHub

Se o Método 1 não funcionar, tente reinstalar:

#### Passo 1: Remover Railway
1. Acesse: https://github.com/settings/installations
2. Encontre "Railway"
3. Clique em "Configure"
4. Role até o final da página
5. Clique em "Uninstall" (botão vermelho)
6. Confirme a remoção

#### Passo 2: Reconectar na Railway
1. Volte para https://railway.app
2. Vá em Account Settings (canto superior direito)
3. Clique em "Connected Accounts"
4. Procure GitHub e clique em "Disconnect" (se estiver conectado)
5. Clique em "Connect" novamente
6. Autorize Railway a acessar GitHub

#### Passo 3: Autorizar Repositórios
1. Durante a autorização, escolha:
   - **All repositories** OU
   - **Only select repositories** → Selecione `dashboard-analise-acoes`
2. Clique em "Install & Authorize"

#### Passo 4: Criar Projeto
1. New Project → Deploy from GitHub repo
2. O repositório deve aparecer agora! ✅

---

### Método 3: Deploy Via CLI (Alternativa)

Se os métodos acima não funcionarem, use a CLI da Railway:

#### Passo 1: Instalar Railway CLI

**macOS (Homebrew):**
```bash
brew install railway
```

**Ou via npm:**
```bash
npm install -g @railway/cli
```

#### Passo 2: Fazer Login
```bash
railway login
```

Isso abrirá o navegador para você autorizar.

#### Passo 3: Fazer Deploy
```bash
cd /Users/suellenpinto/projetos/dashboard-analise-acoes
railway init
railway up
```

#### Passo 4: Adicionar Variáveis
```bash
railway variables set DATABASE_URL="sua_url_aqui"
railway variables set HOTMART_HOTTOK="seu_token_aqui"
```

---

## 🔍 Verificação

Depois de seguir um dos métodos acima, verifique:

### No GitHub
1. Acesse: https://github.com/settings/installations
2. Clique em "Configure" ao lado de Railway
3. Verifique que `dashboard-analise-acoes` está na lista

### Na Railway
1. New Project → Deploy from GitHub repo
2. Você deve ver `dashboard-analise-acoes` na lista
3. Clique nele para criar o projeto

---

## ❓ Troubleshooting

### Ainda não aparece o repositório?

**Verifique se o repositório é privado:**
- Repositórios privados precisam de permissão explícita
- Certifique-se de que selecionou o repo nas configurações

**Verifique se o repo está em uma organização:**
- Se o repo está em uma organização GitHub, você precisa:
  1. Acessar: https://github.com/organizations/NOME_ORG/settings/installations
  2. Configurar Railway lá também

**Limpe o cache do navegador:**
- Às vezes o navegador cacheia a lista vazia
- Tente em uma aba anônima/privada

**Aguarde alguns minutos:**
- Após autorizar, pode levar 1-2 minutos para sincronizar

---

## 🎯 Após Resolver

Quando o repositório aparecer:

1. ✅ Selecione `dashboard-analise-acoes`
2. ✅ Railway vai detectar Python automaticamente
3. ✅ Configure as variáveis (DATABASE_URL, HOTMART_HOTTOK)
4. ✅ Deploy automático vai começar
5. ✅ Continue seguindo o `INICIO_RAPIDO_RAILWAY.md`

---

## 📸 Capturas de Tela de Referência

### Como deve ficar no GitHub Settings:
```
GitHub Settings → Installations → Railway → Configure

Repository access:
⚪ All repositories
🔘 Only select repositories
   ✅ dashboard-analise-acoes

[Save button]
```

### Como deve ficar na Railway:
```
New Project → Deploy from GitHub repo

Search repositories: [dashboard-analise-acoes]

Results:
  📦 suellencna/dashboard-analise-acoes
     [Deploy button]
```

---

## 💡 Dica Pro

Para evitar problemas futuros:
- Use "Only select repositories" (mais seguro)
- Autorize apenas os repos que você vai fazer deploy
- Revise permissões periodicamente

---

## 🆘 Se Nada Funcionar

1. **Verifique status do Railway:**
   - https://status.railway.app
   - Pode estar em manutenção

2. **Tente outro navegador:**
   - Chrome, Firefox, Safari, Edge
   - Às vezes é problema de cookies/cache

3. **Entre em contato com suporte Railway:**
   - Discord: https://discord.gg/railway
   - Email: team@railway.app
   - Eles respondem rápido (geralmente < 1 hora)

4. **Use a CLI (Método 3 acima):**
   - Mais confiável que a interface web
   - Funciona sempre

---

**✅ A maioria dos casos se resolve com o Método 1!**

Siga o Método 1 primeiro, depois tente Método 2 se necessário.

