# arquivo: controllers.py

import sqlite3
from datetime import datetime
from tkinter import filedialog
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import hashlib

# --- GERENCIAMENTO DA CONEXÃO E SENHA ---
_conn = None
SENHA_HASH = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9' # Hash para "admin123"

def conectar():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect('meubanco.db')
    print("Banco de dados conectado.")

def desconectar():
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
        print("Banco de dados desconectado.")

def verificar_senha(senha_digitada):
    sha256 = hashlib.sha256()
    sha256.update(senha_digitada.encode('utf-8'))
    hash_digitado = sha256.hexdigest()
    return hash_digitado == SENHA_HASH

def format_currency(value):
    if value is None: value = 0.0
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- LÓGICA DE ESTORNO ATUALIZADA ---

def estornar_venda_completa(venda_id):
    """
    Orquestra o estorno completo de uma venda:
    1. Reverte as transações financeiras.
    2. Devolve os itens ao estoque.
    3. Marca a venda como 'Estornada'.
    """
    cursor = _conn.cursor()
    try:
        # Etapa 1: Reverter o financeiro
        cursor.execute("SELECT id FROM transacoes_financeiras WHERE venda_id = ? AND status = 'Ativo'", (venda_id,))
        transacoes_financeiras = cursor.fetchall()
        for trans_id_tuple in transacoes_financeiras:
            trans_id = trans_id_tuple[0]
            cursor.execute("SELECT tipo, natureza, descricao, valor, venda_id FROM transacoes_financeiras WHERE id = ?", (trans_id,))
            tipo, natureza, descricao, valor, v_id = cursor.fetchone()
            
            nova_natureza = 'Saída' if natureza == 'Entrada' else 'Entrada'
            nova_descricao = f"Estorno (Venda #{venda_id}): {descricao}"
            add_transacao_financeira(tipo, nova_natureza, nova_descricao, valor, v_id, status='Estornado')

            cursor.execute("UPDATE transacoes_financeiras SET status = 'Estornado' WHERE id = ?", (trans_id,))

        # Etapa 2: Devolver itens ao estoque
        cursor.execute("SELECT produto_codigo, quantidade FROM venda_itens WHERE venda_id = ?", (venda_id,))
        itens_vendidos = cursor.fetchall()
        for produto_codigo, quantidade in itens_vendidos:
            cursor.execute("UPDATE estoque SET quantidade = quantidade + ? WHERE codigo = ?", (quantidade, produto_codigo))

        # Etapa 3: Marcar a venda e seu pagamento como estornados
        cursor.execute("UPDATE vendas SET status = 'Estornada', status_pagamento = 'Estornado' WHERE id = ?", (venda_id,))
        
        _conn.commit()
        return f"Venda #{venda_id} estornada com sucesso! O estoque foi atualizado e as finanças revertidas."
    except Exception as e:
        _conn.rollback()
        return f"Erro ao estornar venda: {e}"

# --- FUNÇÕES DE BUSCA ATUALIZADAS ---

def relatorio_vendas(data_inicio, data_fim, tipo_pagamento):
    """Busca vendas para o relatório, incluindo o novo status da venda."""
    cursor = _conn.cursor()
    query = """
    SELECT v.data, c.nome, e.descricao, vi.quantidade, e.valor_compra, vi.valor_unitario, 
           v.desconto, v.metodo_pagamento, v.parcelas, v.status
    FROM vendas v
    JOIN clientes c ON v.cliente_id = c.id
    JOIN venda_itens vi ON v.id = vi.venda_id
    JOIN estoque e ON vi.produto_codigo = e.codigo
    WHERE DATE(v.data) BETWEEN ? AND ?
    """
    params = [data_inicio, data_fim]
    if tipo_pagamento != 'Todos':
        query += " AND v.metodo_pagamento = ?"
        params.append(tipo_pagamento)
    query += " ORDER BY v.data DESC;"
    cursor.execute(query, params)
    return cursor.fetchall()

def get_vendas_ativas():
    """Pega apenas as vendas ativas para a tela de estorno."""
    cursor = _conn.cursor()
    cursor.execute("""
        SELECT v.id, v.data, c.nome, v.valor_total
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        WHERE v.status = 'Ativa'
        ORDER BY v.id DESC
    """)
    return cursor.fetchall()

# ... (O restante das funções permanece o mesmo da resposta anterior) ...
# (Copie o restante do seu controllers.py aqui para garantir que nada se perca)
def registrar_venda(cliente_id, metodo_pagamento, parcelas, desconto, carrinho):
    for item in carrinho:
        if not verificar_estoque(item['codigo'], item['quantidade']):
            return f"Erro: Estoque insuficiente para o produto {item['descricao']}."
    cursor = _conn.cursor()
    valor_bruto = sum(item['valor_venda'] * item['quantidade'] for item in carrinho)
    valor_total_final = valor_bruto - desconto
    status_pagamento = 'Conciliado' if metodo_pagamento == 'Dinheiro' else 'Pendente'
    try:
        data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO vendas (cliente_id, data, metodo_pagamento, parcelas, desconto, valor_total, status_pagamento, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Ativa')
            """,(cliente_id, data_venda, metodo_pagamento, parcelas, desconto, valor_total_final, status_pagamento))
        venda_id = cursor.lastrowid
        for item in carrinho:
            cursor.execute("INSERT INTO venda_itens (venda_id, produto_codigo, quantidade, valor_unitario) VALUES (?, ?, ?, ?)",
                           (venda_id, item['codigo'], item['quantidade'], item['valor_venda']))
            cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE codigo = ?",
                           (item['quantidade'], item['codigo']))
        if metodo_pagamento == 'Dinheiro':
            add_transacao_financeira('Caixa', 'Entrada', f'Venda #{venda_id}', valor_total_final, venda_id)
        _conn.commit()
        return f"Venda #{venda_id} registrada com sucesso!"
    except Exception as e:
        _conn.rollback()
        return f"Ocorreu um erro ao registrar a venda: {e}"

def gerar_pdf_relatorio(dados_relatorio, data_inicio, data_fim, resumo):
    filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not filepath: return "Geração de PDF cancelada."
    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Relatório de Vendas - Período: {data_inicio} a {data_fim}", styles['Title']))
    elements.append(Spacer(1, 12))
    table_data = [['Data', 'Cliente', 'Produto', 'Qtd', 'Custo Total', 'Venda Total', 'Pagamento', 'Parc.', 'Status']]
    for row in dados_relatorio:
        formatted_row = list(row)
        formatted_row[0] = row[0] 
        formatted_row[4] = format_currency(row[4])
        formatted_row[5] = format_currency(row[5])
        table_data.append(formatted_row)
    style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12), ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                        ('GRID', (0,0), (-1,-1), 1, colors.black)])
    t = Table(table_data)
    t.setStyle(style)
    elements.append(t)
    elements.append(Spacer(1, 24))
    for linha_resumo in resumo.split('\n'):
        elements.append(Paragraph(linha_resumo, styles['h3']))
    doc.build(elements)
    return f"PDF salvo com sucesso em: {filepath}"

def add_transacao_financeira(tipo, natureza, descricao, valor, venda_id=None, status='Ativo'):
    cursor = _conn.cursor()
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO transacoes_financeiras (tipo, natureza, descricao, valor, data, venda_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (tipo, natureza, descricao, valor, data, venda_id, status))
    _conn.commit()

def get_transacoes(tipo):
    cursor = _conn.cursor()
    cursor.execute("SELECT data, descricao, valor, natureza FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo' ORDER BY data DESC", (tipo,))
    return cursor.fetchall()

def get_todas_as_transacoes():
    cursor = _conn.cursor()
    cursor.execute("SELECT id, data, tipo, descricao, valor, natureza, status, venda_id FROM transacoes_financeiras ORDER BY data DESC")
    return cursor.fetchall()

def get_saldo(tipo):
    cursor = _conn.cursor()
    cursor.execute("SELECT SUM(CASE WHEN natureza = 'Entrada' THEN valor ELSE -valor END) FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo'", (tipo,))
    saldo = cursor.fetchone()[0]
    return saldo if saldo is not None else 0

def get_vendas_pendentes():
    cursor = _conn.cursor()
    query = """
        SELECT v.id, v.data, c.nome, v.valor_total, v.metodo_pagamento 
        FROM vendas v JOIN clientes c ON v.cliente_id = c.id
        WHERE v.status_pagamento = 'Pendente' AND v.status = 'Ativa'
        ORDER BY v.data DESC
    """
    cursor.execute(query)
    return cursor.fetchall()

def conciliar_venda(venda_id, valor_liquido):
    cursor = _conn.cursor()
    try:
        cursor.execute("SELECT valor_total FROM vendas WHERE id = ?", (venda_id,))
        valor_bruto = cursor.fetchone()[0]
        cursor.execute("UPDATE vendas SET status_pagamento = 'Conciliado' WHERE id = ?", (venda_id,))
        add_transacao_financeira('Banco', 'Entrada', f'Recebimento Venda #{venda_id}', valor_bruto, venda_id)
        taxa = valor_bruto - valor_liquido
        if taxa > 0:
            add_transacao_financeira('Banco', 'Saída', f'Taxas Venda #{venda_id}', taxa, venda_id)
        _conn.commit()
        return "Venda conciliada com sucesso!"
    except Exception as e:
        _conn.rollback()
        return f"Erro ao conciliar: {e}"

def estornar_transacao_financeira(id_transacao):
    return "Ação obsoleta. Use 'Estornar Venda' na aba de Administração."

def adicionar_cliente(nome, telefone, instagram):
    cursor = _conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome, telefone, instagram) VALUES (?, ?, ?)", (nome, telefone, instagram))
        _conn.commit()
        return "Cliente adicionado com sucesso!"
    except sqlite3.IntegrityError:
        _conn.rollback()
        return f"Erro: Cliente com o nome '{nome}' já existe."

def buscar_cliente(termo):
    cursor = _conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes WHERE nome LIKE ?", ('%' + termo + '%',))
    return cursor.fetchall()

def listar_clientes():
    cursor = _conn.cursor()
    cursor.execute("SELECT id, nome, telefone, instagram FROM clientes")
    return cursor.fetchall()

def adicionar_produto(codigo, descricao, valor_compra, valor_venda, quantidade):
    cursor = _conn.cursor()
    try:
        cursor.execute("INSERT INTO estoque (codigo, descricao, valor_compra, valor_venda, quantidade) VALUES (?, ?, ?, ?, ?)",
                       (codigo, descricao, valor_compra, valor_venda, quantidade))
        _conn.commit()
        return "Produto adicionado com sucesso!"
    except sqlite3.IntegrityError:
        _conn.rollback()
        return f"Erro: O código '{codigo}' já existe."

def buscar_produto(termo):
    cursor = _conn.cursor()
    cursor.execute("SELECT codigo, descricao, valor_venda, quantidade FROM estoque WHERE (codigo LIKE ? OR descricao LIKE ?) AND quantidade > 0",
                   ('%' + termo + '%', '%' + termo + '%'))
    return cursor.fetchall()

def listar_produtos():
    cursor = _conn.cursor()
    cursor.execute("SELECT codigo, descricao, valor_compra, valor_venda, quantidade FROM estoque")
    return cursor.fetchall()

def verificar_estoque(codigo, qtd_desejada):
    cursor = _conn.cursor()
    cursor.execute("SELECT quantidade FROM estoque WHERE codigo = ?", (codigo,))
    resultado = cursor.fetchone()
    return resultado and resultado[0] >= qtd_desejada

def atualizar_cliente(id_cliente, nome, telefone, instagram):
    cursor = _conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET nome = ?, telefone = ?, instagram = ? WHERE id = ?",
                       (nome, telefone, instagram, id_cliente))
        _conn.commit()
        return "Cliente atualizado com sucesso!"
    except Exception as e:
        _conn.rollback()
        return f"Erro ao atualizar cliente: {e}"

def atualizar_produto(codigo_original, novo_codigo, descricao, val_compra, val_venda, qtd):
    cursor = _conn.cursor()
    try:
        cursor.execute("""
            UPDATE estoque 
            SET codigo = ?, descricao = ?, valor_compra = ?, valor_venda = ?, quantidade = ?
            WHERE codigo = ?
        """, (novo_codigo, descricao, val_compra, val_venda, qtd, codigo_original))
        _conn.commit()
        return "Produto atualizado com sucesso!"
    except Exception as e:
        _conn.rollback()
        return f"Erro ao atualizar produto: {e}"