# arquivo: database.py
import sqlite3
import hashlib

def criar_tabelas():
    conn = sqlite3.connect('meubanco.db')
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, telefone TEXT, aniversario TEXT, endereco TEXT, instagram TEXT);")
    cursor.execute("CREATE TABLE IF NOT EXISTS estoque (codigo TEXT PRIMARY KEY, descricao TEXT NOT NULL, valor_compra REAL NOT NULL, valor_venda REAL NOT NULL, quantidade INTEGER NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, nome_completo TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, data TEXT NOT NULL, metodo_pagamento TEXT NOT NULL, numero_parcelas INTEGER, desconto REAL DEFAULT 0, valor_total REAL NOT NULL, status TEXT DEFAULT 'Ativa', usuario_id INTEGER, FOREIGN KEY (cliente_id) REFERENCES clientes (id), FOREIGN KEY (usuario_id) REFERENCES usuarios (id));")
    cursor.execute("CREATE TABLE IF NOT EXISTS venda_itens (id INTEGER PRIMARY KEY AUTOINCREMENT, venda_id INTEGER NOT NULL, produto_codigo TEXT NOT NULL, quantidade INTEGER NOT NULL, valor_unitario REAL NOT NULL, FOREIGN KEY (venda_id) REFERENCES vendas (id), FOREIGN KEY (produto_codigo) REFERENCES estoque (codigo));")
    cursor.execute("CREATE TABLE IF NOT EXISTS parcelas (id INTEGER PRIMARY KEY AUTOINCREMENT, venda_id INTEGER NOT NULL, numero_parcela INTEGER NOT NULL, valor_parcela REAL NOT NULL, data_vencimento TEXT NOT NULL, status TEXT DEFAULT 'Pendente', transacao_id INTEGER, FOREIGN KEY (venda_id) REFERENCES vendas (id));")
    cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, usuario_id INTEGER NOT NULL, acao TEXT NOT NULL, detalhes TEXT, FOREIGN KEY (usuario_id) REFERENCES usuarios (id));")
    
    # Tabela de Transações Financeiras - COM NOVO CAMPO 'grupo_liquidacao'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes_financeiras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        natureza TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        status TEXT DEFAULT 'Ativo',
        grupo_liquidacao INTEGER 
    );
    """)

    print("Tabelas verificadas/criadas com sucesso!")
    
    cursor.execute("SELECT COUNT(id) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        print("Criando usuário padrão 'admin' com senha 'admin'...")
        senha_padrao = 'admin'
        sha = hashlib.sha256(); sha.update(senha_padrao.encode('utf-8'))
        hash_senha = sha.hexdigest()
        cursor.execute("INSERT INTO usuarios (username, password_hash, nome_completo) VALUES (?, ?, ?)",
                       ('admin', hash_senha, 'Administrador do Sistema'))
        print("Usuário padrão criado.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_tabelas()