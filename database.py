# arquivo: database.py

import sqlite3

def criar_tabelas():
    """Cria/Verifica todas as tabelas necessárias para o sistema."""
    conn = sqlite3.connect('meubanco.db')
    cursor = conn.cursor()

    # ... (tabelas clientes, estoque, venda_itens - sem alterações) ...
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        telefone TEXT,
        instagram TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        codigo TEXT PRIMARY KEY,
        descricao TEXT NOT NULL,
        valor_compra REAL NOT NULL,
        valor_venda REAL NOT NULL,
        quantidade INTEGER NOT NULL
    );
    """)
    # Tabela de Vendas - COM NOVA COLUNA 'status'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        metodo_pagamento TEXT NOT NULL,
        parcelas INTEGER,
        desconto REAL DEFAULT 0,
        valor_total REAL NOT NULL,
        status_pagamento TEXT DEFAULT 'N/A', -- Conciliado, Pendente
        status TEXT DEFAULT 'Ativa', -- NOVO CAMPO: 'Ativa' ou 'Estornada'
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venda_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER NOT NULL,
        produto_codigo TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_unitario REAL NOT NULL,
        FOREIGN KEY (venda_id) REFERENCES vendas (id),
        FOREIGN KEY (produto_codigo) REFERENCES estoque (codigo)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes_financeiras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL, 
        natureza TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        venda_id INTEGER,
        status TEXT DEFAULT 'Ativo',
        FOREIGN KEY (venda_id) REFERENCES vendas (id)
    );
    """)

    print("Tabelas verificadas/criadas com sucesso!")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_tabelas()