import sqlite3

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Criar a tabela users se não existir
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
''')

# Salvar (commit) as alterações e fechar a conexão
conn.commit()
conn.close()
