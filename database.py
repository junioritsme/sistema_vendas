# arquivo: database.py

import sqlite3

def criar_tabelas():
    """Cria/Verifica todas as tabelas necessárias para o sistema."""
    conn = sqlite3.connect('meubanco.db')
    cursor = conn.cursor()

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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        metodo_pagamento TEXT NOT NULL,
        numero_parcelas INTEGER,
        desconto REAL DEFAULT 0,
        valor_total REAL NOT NULL,
        status TEXT DEFAULT 'Ativa', -- 'Ativa' ou 'Estornada'
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
    CREATE TABLE IF NOT EXISTS parcelas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER NOT NULL,
        numero_parcela INTEGER NOT NULL,
        valor_parcela REAL NOT NULL,
        data_vencimento TEXT NOT NULL,
        status TEXT DEFAULT 'Pendente', -- 'Pendente', 'Liquidada', 'Estornada'
        transacao_id INTEGER,
        FOREIGN KEY (venda_id) REFERENCES vendas (id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes_financeiras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL, -- 'Caixa' ou 'Banco'
        natureza TEXT NOT NULL, -- 'Entrada' ou 'Saída'
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        status TEXT DEFAULT 'Ativo' -- 'Ativo' ou 'Estornado'
    );
    """)
    print("Tabelas verificadas/criadas com sucesso!")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_tabelas()