# arquivo: gerar_senha.py

import hashlib

# --- DIGITE A SENHA QUE VOCÊ DESEJA USAR AQUI ---
minha_senha_secreta = "admin123" 
# ----------------------------------------------------

# O código abaixo irá gerar o hash seguro da sua senha
sha256 = hashlib.sha256()
sha256.update(minha_senha_secreta.encode('utf-8'))
hash_da_senha = sha256.hexdigest()

print("--- SENHA GERADA COM SUCESSO ---")
print("Copie a linha abaixo e cole no arquivo 'controllers.py' onde for indicado.")
print("\n")
print(f"SENHA_HASH = '{hash_da_senha}'")