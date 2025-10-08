# 📊 Coleta Automática de Dados - IFIX e IDIV

## ✅ O QUE MUDOU?

**ANTES:**
- ❌ Download manual do Investing.com
- ❌ Limpeza manual dos dados
- ❌ Processo demorado e sujeito a erros

**AGORA:**
- ✅ **Coleta 100% automática** usando Python
- ✅ **Dados de 10 anos** em segundos
- ✅ **Formato já padronizado** (Date, Close)
- ✅ **Sempre atualizado** com os últimos dados

---

## 🚀 COMO USAR

### 1️⃣ **Executar Manualmente**

```bash
cd /Users/suellenpinto/projetos/dashboard-analise-acoes
source venv/bin/activate
python coleta_ifix_idiv_automatica.py
```

**Resultado:**
- ✅ Arquivo `dados/IFIX.SA.csv` atualizado
- ✅ Arquivo `dados/IDIV.SA.csv` atualizado
- ✅ ~2480 registros cada (10 anos de dados)

---

### 2️⃣ **Automatizar (Recomendado)**

#### **No Mac/Linux (usando cron):**

Edite o crontab:
```bash
crontab -e
```

Adicione esta linha para rodar todo dia às 18h:
```bash
0 18 * * * cd /Users/suellenpinto/projetos/dashboard-analise-acoes && source venv/bin/activate && python coleta_ifix_idiv_automatica.py >> logs/coleta_ifix_idiv.log 2>&1
```

#### **No Windows (Agendador de Tarefas):**

1. Abra o "Agendador de Tarefas"
2. Criar Tarefa Básica
3. Ação: Iniciar um programa
4. Programa: `python`
5. Argumentos: `coleta_ifix_idiv_automatica.py`
6. Diretório: `/Users/suellenpinto/projetos/dashboard-analise-acoes`

---

## 📁 ARQUIVOS

### **Script Novo:**
- `coleta_ifix_idiv_automatica.py` - **Coleta automática** (USE ESTE!)

### **Scripts Antigos (podem ser deletados):**
- `limpeza_benchmarks.py` - ❌ Processo manual
- `downloads_brutos/` - ❌ Pasta com downloads manuais

---

## 🔧 CONFIGURAÇÃO

### **Alterar período de coleta:**

Edite o arquivo `coleta_ifix_idiv_automatica.py`:

```python
ANOS_HISTORICO = 10  # Mude para 5, 15, etc.
```

### **Adicionar novos índices:**

```python
INDICES_CONFIG = {
    'BM&FBOVESPA Real Estate IFIX': 'IFIX.SA.csv',
    'Bovespa Dividend': 'IDIV.SA.csv',
    'Ibovespa': 'IBOV.csv',  # Exemplo
}
```

---

## 🎯 BENEFÍCIOS

✅ **Economia de tempo:** De 10 minutos para 5 segundos  
✅ **Sempre atualizado:** Rode quando quiser  
✅ **Sem erros manuais:** Processo totalmente automatizado  
✅ **Histórico completo:** 10 anos de dados em um comando  
✅ **Gratuito:** Usa a biblioteca `investpy` (sem custos)

---

## ⚠️ IMPORTANTE

### **Biblioteca `investpy`:**
- ✅ Já está instalada no projeto
- ⚠️ Pode mostrar warning sobre `pkg_resources` (é seguro ignorar)
- ✅ Funciona perfeitamente para IFIX e IDIV

### **Nomes dos índices no investpy:**
- `BM&FBOVESPA Real Estate IFIX` → IFIX
- `Bovespa Dividend` → IDIV

---

## 🧹 LIMPEZA RECOMENDADA

Após verificar que tudo funciona, você pode deletar:

```bash
# Arquivos antigos do processo manual
rm -rf downloads_brutos/
rm limpeza_benchmarks.py
```

---

## 📝 EXEMPLO DE SAÍDA

```
======================================================================
📊 COLETA AUTOMÁTICA DE DADOS - IFIX E IDIV
======================================================================
Período: Últimos 10 anos
Destino: dados/

📅 Período de coleta: 11/10/2015 até 08/10/2025

🔄 Processando: BM&FBOVESPA Real Estate IFIX...
   ✅ IFIX.SA.csv
      📊 2481 registros salvos
      📅 De 13/10/2015 até 08/10/2025
      💰 Último fechamento: R$ 3575.58

🔄 Processando: Bovespa Dividend...
   ✅ IDIV.SA.csv
      📊 2482 registros salvos
      📅 De 13/10/2015 até 08/10/2025
      💰 Último fechamento: R$ 10295.51

======================================================================
🎉 COLETA FINALIZADA!
======================================================================
```

---

## 🆘 SUPORTE

Se encontrar algum problema:

1. Verifique se o `investpy` está instalado: `pip list | grep investpy`
2. Verifique sua conexão com a internet
3. Verifique se a pasta `dados/` existe

---

**Criado em:** Outubro 2025  
**Status:** ✅ Funcionando perfeitamente

