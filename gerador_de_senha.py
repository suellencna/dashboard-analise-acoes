# gerador_de_senha.py (versão compatível com a biblioteca mais recente)

import streamlit_authenticator as stauth

# Pede para o usuário digitar uma única senha
senha_para_criptografar = input("Digite a senha que você quer criptografar: ")

# Cria uma lista contendo a senha
senhas = [senha_para_criptografar]

# Gera o hash. Esta é a forma correta para a versão atualizada.
hashed_passwords = stauth.Hasher(senhas).generate()

# Imprime o resultado para você copiar
print("\nSenha criptografada (hash):")
print(f"Copie e cole a linha abaixo no seu arquivo config.yaml:\n")
print(hashed_passwords[0])