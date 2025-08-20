# database_setup.py
import sqlite3

conn = sqlite3.connect('users.db') # Isso cria o arquivo do banco de dados
cursor = conn.cursor()

# Cria a tabela de usuários se ela não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()

print("Banco de dados e tabela 'users' criados com sucesso.")