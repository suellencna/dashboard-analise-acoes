# Instruções de Deploy - Dashboard Análise de Ações

## Problemas Corrigidos

### 1. Comando de Deploy Incorreto
**Problema:** O Render estava tentando executar `gunicorn webhook_server:app` mas o arquivo principal era `app.py` (Streamlit).

**Solução:** 
- Criado `Procfile` com comando correto: `gunicorn webhook_server:app --bind 0.0.0.0:$PORT`
- Criado `render.yaml` para configuração específica do Render
- O projeto agora tem dois componentes:
  - `app.py`: Dashboard Streamlit (para uso local)
  - `webhook_server.py`: API Flask para webhooks (para deploy no Render)

### 2. Erro 400 Bad Request no Webhook
**Problema:** O webhook estava recebendo requisições malformadas e não tratava adequadamente erros de parsing JSON.

**Solução:**
- Adicionada validação robusta de JSON com `request.is_json` e `request.get_json(silent=True)`
- Melhorado tratamento de erros com mensagens específicas
- Adicionado endpoint `/test` para debugging

### 3. Dependências Faltando
**Problema:** Algumas dependências não estavam no `requirements.txt`.

**Solução:**
- Atualizado `requirements.txt` com todas as dependências necessárias
- Especificada versão exata do Python no `runtime.txt`

## Arquivos de Configuração Criados

### Procfile
```
web: gunicorn webhook_server:app --bind 0.0.0.0:$PORT
```

### render.yaml
```yaml
services:
  - type: web
    name: analise-acoes-api-webhook
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn webhook_server:app --bind 0.0.0.0:$PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: HOTMART_HOTTOK
        sync: false
    healthCheckPath: /health
```

## Variáveis de Ambiente Necessárias

Configure no Render:
- `DATABASE_URL`: URL de conexão com o banco PostgreSQL
- `HOTMART_HOTTOK`: Token de autenticação do Hotmart

## Endpoints Disponíveis

- `GET /`: Status básico do servidor
- `GET /health`: Health check com status do banco
- `GET /test`: Endpoint de teste
- `POST /webhook/hotmart`: Webhook principal do Hotmart

## Testando o Deploy

### Localmente
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o webhook server
python webhook_server.py

# Em outro terminal, testar
python test_webhook.py
```

### No Render
1. Faça push das alterações para o repositório
2. O Render detectará automaticamente o `Procfile` ou `render.yaml`
3. Configure as variáveis de ambiente
4. Acesse a URL fornecida pelo Render

## Monitoramento

- Use o endpoint `/health` para verificar se o serviço está funcionando
- Use o endpoint `/test` para debugging
- Monitore os logs no Render para identificar problemas

## Próximos Passos

1. Faça o deploy das alterações
2. Teste o webhook com dados reais do Hotmart
3. Monitore os logs para garantir que não há mais erros 400
4. Configure alertas no Render para monitoramento contínuo

