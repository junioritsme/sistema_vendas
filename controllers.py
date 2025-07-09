# arquivo: controllers.py

import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tkinter import filedialog
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import hashlib

# --- GERENCIAMENTO DA CONEXÃO E SENHA ---
_conn = None
SENHA_HASH = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918' 

def conectar():
    global _conn
    if _conn is None: _conn = sqlite3.connect('meubanco.db', check_same_thread=False)
    print("Banco de dados conectado.")

def desconectar():
    global _conn
    if _conn is not None: _conn.close(); _conn = None
    print("Banco de dados desconectado.")

def verificar_senha(s):
    sha = hashlib.sha256(); sha.update(s.encode('utf-8')); return sha.hexdigest() == SENHA_HASH

def format_currency(v):
    if v is None: v = 0.0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- FUNÇÕES DE CADASTRO E BUSCA ---
def adicionar_cliente(nome, telefone, instagram):
    cursor = _conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome, telefone, instagram) VALUES (?, ?, ?)", (nome, telefone, instagram))
        _conn.commit()
        return "Cliente adicionado com sucesso!"
    except sqlite3.IntegrityError:
        _conn.rollback(); return f"Erro: Cliente com o nome '{nome}' já existe."
def buscar_cliente(termo):
    cursor = _conn.cursor(); cursor.execute("SELECT id, nome FROM clientes WHERE nome LIKE ?", ('%' + termo + '%',)); return cursor.fetchall()
def listar_clientes():
    cursor = _conn.cursor(); cursor.execute("SELECT id, nome, telefone, instagram FROM clientes"); return cursor.fetchall()
def adicionar_produto(codigo, descricao, valor_compra, valor_venda, quantidade):
    cursor = _conn.cursor()
    try:
        cursor.execute("INSERT INTO estoque (codigo, descricao, valor_compra, valor_venda, quantidade) VALUES (?, ?, ?, ?, ?)",
                       (codigo, descricao, valor_compra, valor_venda, quantidade))
        _conn.commit()
        return "Produto adicionado com sucesso!"
    except sqlite3.IntegrityError:
        _conn.rollback(); return f"Erro: O código '{codigo}' já existe."
def buscar_produto(termo):
    cursor = _conn.cursor(); cursor.execute("SELECT codigo, descricao, valor_venda, quantidade FROM estoque WHERE (codigo LIKE ? OR descricao LIKE ?) AND quantidade > 0",
                   ('%' + termo + '%', '%' + termo + '%')); return cursor.fetchall()
def listar_produtos():
    cursor = _conn.cursor(); cursor.execute("SELECT codigo, descricao, valor_compra, valor_venda, quantidade FROM estoque"); return cursor.fetchall()
def verificar_estoque(codigo, qtd_desejada):
    cursor = _conn.cursor(); cursor.execute("SELECT quantidade FROM estoque WHERE codigo = ?", (codigo,)); resultado = cursor.fetchone()
    return resultado and resultado[0] >= qtd_desejada

# --- FUNÇÕES DE EDIÇÃO (ADMIN) ---
def atualizar_cliente(id_cliente, nome, telefone, instagram):
    cursor = _conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET nome = ?, telefone = ?, instagram = ? WHERE id = ?", (nome, telefone, instagram, id_cliente)); _conn.commit()
        return "Cliente atualizado com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao atualizar cliente: {e}"
def atualizar_produto(codigo_original, novo_codigo, descricao, val_compra, val_venda, qtd):
    cursor = _conn.cursor()
    try:
        cursor.execute("UPDATE estoque SET codigo = ?, descricao = ?, valor_compra = ?, valor_venda = ?, quantidade = ? WHERE codigo = ?",
                       (novo_codigo, descricao, val_compra, val_venda, qtd, codigo_original)); _conn.commit()
        return "Produto atualizado com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao atualizar produto: {e}"

# --- FUNÇÕES FINANCEIRAS (INCLUINDO AS QUE FALTAVAM) ---
def add_transacao_financeira(tipo, natureza, descricao, valor, status='Ativo'):
    cursor = _conn.cursor(); data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transacoes_financeiras (tipo, natureza, descricao, valor, data, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (tipo, natureza, descricao, valor, data, status)); _conn.commit(); return cursor.lastrowid
def get_transacoes(tipo):
    cursor = _conn.cursor(); cursor.execute("SELECT data, descricao, valor, natureza FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo' ORDER BY data DESC", (tipo,)); return cursor.fetchall()
def get_saldo(tipo):
    cursor = _conn.cursor(); cursor.execute("SELECT SUM(CASE WHEN natureza = 'Entrada' THEN valor ELSE -valor END) FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo'", (tipo,)); saldo = cursor.fetchone()[0]
    return saldo if saldo is not None else 0

# --- FUNÇÕES DE VENDA E CONTAS A RECEBER ---
def registrar_venda(cliente_id, metodo_pagamento, numero_parcelas, desconto, carrinho, data_primeira_parcela_str=None):
    cursor = _conn.cursor()
    try:
        for item in carrinho:
            if not verificar_estoque(item['codigo'], item['quantidade']): return f"Erro: Estoque insuficiente para {item['descricao']}."
        valor_bruto = sum(item['valor_venda'] * item['quantidade'] for item in carrinho); valor_final = valor_bruto - desconto
        data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO vendas (cliente_id, data, metodo_pagamento, numero_parcelas, desconto, valor_total, status) VALUES (?, ?, ?, ?, ?, ?, 'Ativa')",
                       (cliente_id, data_venda, metodo_pagamento, numero_parcelas, desconto, valor_final)); venda_id = cursor.lastrowid
        for item in carrinho:
            cursor.execute("INSERT INTO venda_itens (venda_id, produto_codigo, quantidade, valor_unitario) VALUES (?, ?, ?, ?)",
                           (venda_id, item['codigo'], item['quantidade'], item['valor_venda']))
            cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE codigo = ?", (item['quantidade'], item['codigo']))
        valor_parcela = round(valor_final / numero_parcelas, 2); diferenca = round(valor_final - (valor_parcela * numero_parcelas), 2)
        data_vencimento_base = datetime.strptime(data_primeira_parcela_str, '%Y-%m-%d') if data_primeira_parcela_str else datetime.now()
        for i in range(numero_parcelas):
            valor_da_parcela_atual = valor_parcela
            if i == 0: valor_da_parcela_atual += diferenca
            vencimento = (data_vencimento_base + relativedelta(months=i)).strftime('%Y-%m-%d') if metodo_pagamento == 'Crediário' else data_vencimento_base.strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO parcelas (venda_id, numero_parcela, valor_parcela, data_vencimento) VALUES (?, ?, ?, ?)",
                           (venda_id, i + 1, valor_da_parcela_atual, vencimento))
        _conn.commit(); return f"Venda #{venda_id} registrada com sucesso. {numero_parcelas} parcela(s) gerada(s)."
    except Exception as e: _conn.rollback(); return f"Ocorreu um erro ao registrar a venda: {e}"
def get_contas_a_receber(cliente_id=None, metodo_pagamento=None):
    cursor = _conn.cursor()
    query = """
        SELECT p.id, v.id, c.nome, p.numero_parcela, v.numero_parcelas, p.valor_parcela, p.data_vencimento, v.metodo_pagamento
        FROM parcelas p JOIN vendas v ON p.venda_id = v.id JOIN clientes c ON v.cliente_id = c.id
        WHERE p.status = 'Pendente' AND v.status = 'Ativa'
    """
    params = []
    if cliente_id: query += " AND c.id = ?"; params.append(cliente_id)
    if metodo_pagamento and metodo_pagamento != 'Todos': query += " AND v.metodo_pagamento = ?"; params.append(metodo_pagamento)
    query += " ORDER BY p.data_vencimento ASC"
    cursor.execute(query, params); return cursor.fetchall()
def liquidar_parcelas(lista_ids_parcelas, destino, valor_recebido):
    cursor = _conn.cursor()
    try:
        soma_valor_parcelas = 0
        for parcela_id in lista_ids_parcelas:
            cursor.execute("SELECT valor_parcela FROM parcelas WHERE id = ?", (parcela_id,)); soma_valor_parcelas += cursor.fetchone()[0]
        descricao = f"Liquidação de {len(lista_ids_parcelas)} parcela(s). IDs: {', '.join(map(str, lista_ids_parcelas))}"
        transacao_id = add_transacao_financeira(destino, 'Entrada', descricao, valor_recebido)
        taxa = soma_valor_parcelas - valor_recebido
        if taxa > 0: add_transacao_financeira(destino, 'Saída', f"Taxas ref. {descricao}", taxa)
        for parcela_id in lista_ids_parcelas: cursor.execute("UPDATE parcelas SET status = 'Liquidada', transacao_id = ? WHERE id = ?", (transacao_id, parcela_id,))
        _conn.commit(); return "Parcela(s) liquidada(s) com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao liquidar parcelas: {e}"