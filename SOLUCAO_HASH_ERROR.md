# Solução para o Erro InvalidHashError

## Problema Identificado

O erro `argon2.exceptions.InvalidHashError` ocorre quando há incompatibilidade entre o algoritmo de hash usado para armazenar a senha no banco de dados e o algoritmo usado para verificar a senha.

## Causa do Problema

1. **Mudança de algoritmo**: O sistema migrou de `bcrypt` (usado no `criar_usuario.py` antigo) para `argon2` (usado no `app.py`)
2. **Hashes incompatíveis**: Senhas criadas com bcrypt não podem ser verificadas com argon2
3. **Usuários antigos**: Usuários criados antes da migração têm hashes incompatíveis

## Soluções Implementadas

### 1. Script para Limpar Usuários Antigos
```bash
python limpar_usuarios.py
```
- Remove todos os usuários existentes do banco
- Permite recriar usuários com o algoritmo correto

### 2. Tratamento de Erro no Login
- Adicionado tratamento específico para `InvalidHashError`
- Quando detectado, o sistema oferece redefinição de senha
- Interface amigável para o usuário redefinir a senha

### 3. Funcionalidade de Troca de Senha
- **Na tela de login**: Para usuários com hash inválido
- **No dashboard**: Para usuários logados que querem trocar a senha
- Validação de senha atual antes de permitir mudança

### 4. Atualização do Sistema de Criação de Usuários
- `criar_usuario.py` agora usa argon2 em vez de bcrypt
- Consistência com o sistema principal

## Passos para Resolver

### Passo 1: Limpar Usuários Antigos
```bash
# Execute o script de limpeza
python limpar_usuarios.py
```

### Passo 2: Criar Novos Usuários
```bash
# Crie usuários com o algoritmo correto
python criar_usuario.py
```

### Passo 3: Testar o Sistema
```bash
# Teste o login e funcionalidades
python test_login.py
```

### Passo 4: Deploy das Correções
```bash
# Faça commit e push das alterações
git add .
git commit -m "Fix: Corrigir erro InvalidHashError e adicionar troca de senha"
git push
```

## Funcionalidades Adicionadas

### 1. Redefinição de Senha na Tela de Login
- Detecta automaticamente hash inválido
- Oferece interface para redefinir senha
- Validação de senha forte (mínimo 6 caracteres)

### 2. Troca de Senha no Dashboard
- Botão "Trocar Senha" na sidebar
- Verificação da senha atual
- Interface intuitiva com validações

### 3. Tratamento Robusto de Erros
- Diferentes tipos de erro são tratados adequadamente
- Mensagens claras para o usuário
- Logs detalhados para debugging

## Arquivos Modificados

- ✅ `app.py` - Tratamento de erro e interfaces de troca de senha
- ✅ `criar_usuario.py` - Migração para argon2
- ✅ `webhook_server.py` - Já estava usando argon2
- ✅ `limpar_usuarios.py` - Script para limpeza (NOVO)
- ✅ `test_login.py` - Script de teste (NOVO)

## Testando a Solução

### Teste Local
1. Execute `python limpar_usuarios.py`
2. Execute `python criar_usuario.py` para criar um usuário
3. Execute `python test_login.py` para testar
4. Execute `streamlit run app.py` e teste a interface

### Teste em Produção
1. Faça deploy das alterações
2. Acesse a aplicação
3. Tente fazer login com usuário existente
4. Se houver erro de hash, use a funcionalidade de redefinição

## Prevenção Futura

1. **Consistência**: Todos os scripts usam argon2
2. **Validação**: Testes automatizados para verificar hashes
3. **Documentação**: README atualizado com instruções
4. **Monitoramento**: Logs para detectar problemas similares

## Comandos Úteis

```bash
# Limpar usuários
python limpar_usuarios.py

# Criar usuário
python criar_usuario.py

# Testar login
python test_login.py

# Executar aplicação
streamlit run app.py

# Executar webhook
python webhook_server.py
```

## Suporte

Se ainda houver problemas:
1. Verifique os logs da aplicação
2. Execute o script de teste
3. Verifique se as variáveis de ambiente estão corretas
4. Confirme se o banco de dados está acessível
