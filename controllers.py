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

_conn = None

def conectar():
    global _conn
    if _conn is None: _conn = sqlite3.connect('meubanco.db', check_same_thread=False)
    print("Banco de dados conectado.")

def desconectar():
    global _conn
    if _conn is not None: _conn.close(); _conn = None
    print("Banco de dados desconectado.")

def format_currency(v):
    if v is None: v = 0.0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def verificar_login(username, password):
    cursor = _conn.cursor(); cursor.execute("SELECT id, password_hash FROM usuarios WHERE username = ?", (username,)); user_data = cursor.fetchone()
    if user_data:
        user_id, stored_hash = user_data; sha = hashlib.sha256(); sha.update(password.encode('utf-8'))
        if sha.hexdigest() == stored_hash: return user_id
    return None

def registrar_log(usuario_id, acao, detalhes=""):
    cursor = _conn.cursor(); timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (timestamp, usuario_id, acao, detalhes) VALUES (?, ?, ?, ?)",
                   (timestamp, usuario_id, acao, detalhes)); _conn.commit()

def criar_usuario(admin_user_id, username, password, nome_completo):
    cursor = _conn.cursor()
    try:
        sha = hashlib.sha256(); sha.update(password.encode('utf-8')); hash_senha = sha.hexdigest()
        cursor.execute("INSERT INTO usuarios (username, password_hash, nome_completo) VALUES (?, ?, ?)",
                       (username, hash_senha, nome_completo)); _conn.commit()
        registrar_log(admin_user_id, "CRIACAO_USUARIO", f"Usuário '{username}' criado.")
        return "Usuário criado com sucesso!"
    except sqlite3.IntegrityError: _conn.rollback(); return f"Erro: O nome de usuário '{username}' já existe."
    except Exception as e: _conn.rollback(); return f"Erro ao criar usuário: {e}"

def listar_usuarios():
    cursor = _conn.cursor(); cursor.execute("SELECT id, username, nome_completo FROM usuarios ORDER BY nome_completo"); return cursor.fetchall()

def deletar_usuario(admin_user_id, id_usuario_deletar):
    if id_usuario_deletar == 1: return "Erro: Não é permitido deletar o usuário administrador padrão."
    cursor = _conn.cursor()
    try:
        cursor.execute("SELECT username FROM usuarios WHERE id = ?", (id_usuario_deletar,)); username = cursor.fetchone()[0]
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario_deletar,)); _conn.commit()
        registrar_log(admin_user_id, "DELECAO_USUARIO", f"Usuário '{username}' (ID: {id_usuario_deletar}) deletado.")
        return "Usuário deletado com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao deletar usuário: {e}"

def verificar_estoque(codigo, qtd_desejada):
    cursor = _conn.cursor(); cursor.execute("SELECT quantidade FROM estoque WHERE codigo = ?", (codigo,)); r = cursor.fetchone()
    return r and r[0] >= qtd_desejada

def add_transacao_financeira(usuario_id, tipo, natureza, descricao, valor, status='Ativo'):
    cursor = _conn.cursor(); data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transacoes_financeiras (tipo, natureza, descricao, valor, data, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (tipo, natureza, descricao, valor, data, status))
    _conn.commit()
    if status == 'Ativo': registrar_log(usuario_id, "TRANSACAO_FINANCEIRA", f"{natureza} em {tipo}: {descricao} - Valor: {valor}")
    return cursor.lastrowid

def adicionar_cliente(usuario_id, nome, telefone, aniversario, endereco, instagram):
    cursor = _conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome, telefone, aniversario, endereco, instagram) VALUES (?, ?, ?, ?, ?)",
                       (nome, telefone, aniversario, endereco, instagram)); _conn.commit()
        registrar_log(usuario_id, "CADASTRO_CLIENTE", f"Cliente '{nome}' adicionado.")
        return "Cliente adicionado com sucesso!"
    except sqlite3.IntegrityError: _conn.rollback(); return f"Erro: Cliente com o nome '{nome}' já existe."

def atualizar_cliente(usuario_id, id_cliente, nome, telefone, aniversario, endereco, instagram):
    cursor = _conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET nome = ?, telefone = ?, aniversario = ?, endereco = ?, instagram = ? WHERE id = ?",
                       (nome, telefone, aniversario, endereco, instagram, id_cliente)); _conn.commit()
        registrar_log(usuario_id, "EDICAO_CLIENTE", f"Cliente ID #{id_cliente} ('{nome}') atualizado.")
        return "Cliente atualizado com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao atualizar cliente: {e}"

def listar_clientes():
    cursor = _conn.cursor(); cursor.execute("SELECT * FROM clientes ORDER BY nome"); return cursor.fetchall()

def buscar_cliente_por_termo(termo=""):
    cursor = _conn.cursor(); cursor.execute("SELECT id, nome FROM clientes WHERE nome LIKE ? ORDER BY nome", ('%' + termo + '%',)); return cursor.fetchall()

def adicionar_produto(usuario_id, codigo, descricao, valor_compra, valor_venda, quantidade):
    cursor = _conn.cursor()
    try:
        cursor.execute("INSERT INTO estoque (codigo, descricao, valor_compra, valor_venda, quantidade) VALUES (?, ?, ?, ?, ?)",
                       (codigo, descricao, valor_compra, valor_venda, quantidade)); _conn.commit()
        registrar_log(usuario_id, "CADASTRO_PRODUTO", f"Produto '{codigo} - {descricao}' adicionado.")
        return "Produto adicionado com sucesso!"
    except sqlite3.IntegrityError: _conn.rollback(); return f"Erro: O código '{codigo}' já existe."

def atualizar_produto(usuario_id, codigo_original, novo_codigo, descricao, val_compra, val_venda, qtd):
    cursor = _conn.cursor()
    try:
        cursor.execute("UPDATE estoque SET codigo = ?, descricao = ?, valor_compra = ?, valor_venda = ?, quantidade = ? WHERE codigo = ?",
                       (novo_codigo, descricao, val_compra, val_venda, qtd, codigo_original)); _conn.commit()
        registrar_log(usuario_id, "EDICAO_PRODUTO", f"Produto '{novo_codigo}' (original: {codigo_original}) atualizado.")
        return "Produto atualizado com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao atualizar produto: {e}"

def buscar_produto(termo):
    cursor = _conn.cursor(); cursor.execute("SELECT codigo, descricao, valor_venda, quantidade FROM estoque WHERE (codigo LIKE ? OR descricao LIKE ?) AND quantidade > 0",
                   ('%' + termo + '%', '%' + termo + '%')); return cursor.fetchall()

def listar_produtos():
    cursor = _conn.cursor(); cursor.execute("SELECT codigo, descricao, valor_compra, valor_venda, quantidade FROM estoque ORDER BY descricao"); return cursor.fetchall()

def registrar_venda(usuario_id, cliente_id, metodo_pagamento, numero_parcelas, desconto, carrinho, data_primeira_parcela_str=None):
    cursor = _conn.cursor()
    try:
        for item in carrinho:
            if not verificar_estoque(item['codigo'], item['quantidade']): return f"Erro: Estoque insuficiente para {item['descricao']}."
        valor_bruto = sum(item['valor_venda'] * item['quantidade'] for item in carrinho); valor_final = valor_bruto - desconto
        data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO vendas (cliente_id, data, metodo_pagamento, numero_parcelas, desconto, valor_total, status, usuario_id) VALUES (?, ?, ?, ?, ?, ?, 'Ativa', ?)",
                       (cliente_id, data_venda, metodo_pagamento, numero_parcelas, desconto, valor_final, usuario_id)); venda_id = cursor.lastrowid
        for item in carrinho:
            cursor.execute("INSERT INTO venda_itens (venda_id, produto_codigo, quantidade, valor_unitario) VALUES (?, ?, ?, ?)",
                           (venda_id, item['codigo'], item['quantidade'], item['valor_venda']))
            cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE codigo = ?", (item['quantidade'], item['codigo']))
        valor_parcela = round(valor_final / numero_parcelas, 2); diferenca = round(valor_final - (valor_parcela * numero_parcelas), 2)
        data_vencimento_base = datetime.strptime(data_primeira_parcela_str, '%Y-%m-%d') if data_primeira_parcela_str else datetime.now()
        for i in range(numero_parcelas):
            valor_da_parcela_atual = valor_parcela + (diferenca if i == 0 else 0)
            vencimento = (data_vencimento_base + relativedelta(months=i)).strftime('%Y-%m-%d') if metodo_pagamento == 'Crediário' else data_vencimento_base.strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO parcelas (venda_id, numero_parcela, valor_parcela, data_vencimento) VALUES (?, ?, ?, ?)",
                           (venda_id, i + 1, valor_da_parcela_atual, vencimento))
        _conn.commit(); registrar_log(usuario_id, "REGISTRO_VENDA", f"Venda #{venda_id} para cliente ID {cliente_id}, Valor: {valor_final:.2f}")
        return f"Venda #{venda_id} registrada com sucesso. {numero_parcelas} parcela(s) gerada(s)."
    except Exception as e: _conn.rollback(); return f"Ocorreu um erro ao registrar a venda: {e}"

def liquidar_parcelas(usuario_id, lista_ids_parcelas, destino, valor_recebido):
    cursor = _conn.cursor()
    try:
        soma_valor_parcelas = 0
        for parcela_id in lista_ids_parcelas:
            cursor.execute("SELECT valor_parcela FROM parcelas WHERE id = ?", (parcela_id,)); soma_valor_parcelas += cursor.fetchone()[0]
        descricao = f"Liquidação de {len(lista_ids_parcelas)} parcela(s). IDs: {', '.join(map(str, lista_ids_parcelas))}"
        transacao_id = add_transacao_financeira(usuario_id, destino, 'Entrada', descricao, valor_recebido)
        taxa = soma_valor_parcelas - valor_recebido
        if taxa > 0: add_transacao_financeira(usuario_id, destino, 'Saída', f"Taxas ref. {descricao}", taxa)
        for parcela_id in lista_ids_parcelas: cursor.execute("UPDATE parcelas SET status = 'Liquidada', transacao_id = ? WHERE id = ?", (transacao_id, parcela_id,))
        _conn.commit(); registrar_log(usuario_id, "LIQUIDACAO_PARCELA", f"IDs: {lista_ids_parcelas}. Valor: {valor_recebido} para {destino}")
        return "Parcela(s) liquidada(s) com sucesso!"
    except Exception as e: _conn.rollback(); return f"Erro ao liquidar parcelas: {e}"

# Em controllers.py, substitua esta função:

def estornar_venda_completa(usuario_id, venda_id):
    """
    Orquestra o estorno completo de uma venda:
    1. Reverte TODAS as transações financeiras associadas.
    2. Devolve os itens ao estoque.
    3. Marca a venda e suas parcelas como 'Estornada'.
    """
    cursor = _conn.cursor()
    try:
        # Etapa 1: Reverter o financeiro (LÓGICA CORRIGIDA E MAIS ROBUSTA)
        # Pega os IDs dos grupos de liquidação das parcelas pagas desta venda
        cursor.execute("SELECT transacao_id FROM parcelas WHERE venda_id = ? AND status = 'Liquidada'", (venda_id,))
        grupos_a_estornar = {row[0] for row in cursor.fetchall() if row[0] is not None}

        for grupo_id in grupos_a_estornar:
            # Encontra todas as transações (entrada e taxas) daquele grupo
            cursor.execute("SELECT id, tipo, natureza, descricao, valor FROM transacoes_financeiras WHERE grupo_liquidacao = ? AND status = 'Ativo'", (grupo_id,))
            transacoes_do_grupo = cursor.fetchall()

            for id_trans, tipo, natureza, desc, valor in transacoes_do_grupo:
                # Cria a transação de estorno (oposta)
                add_transacao_financeira(usuario_id, tipo, 'Saída' if natureza == 'Entrada' else 'Entrada', f"Estorno: {desc}", valor, status='Estornado')
                # Marca a transação original como estornada
                cursor.execute("UPDATE transacoes_financeiras SET status = 'Estornado' WHERE id = ?", (id_trans,))

        # Etapa 2: Estornar a venda e suas parcelas
        cursor.execute("UPDATE vendas SET status = 'Estornada' WHERE id = ?", (venda_id,))
        cursor.execute("UPDATE parcelas SET status = 'Estornada' WHERE venda_id = ?", (venda_id,))
        
        # Etapa 3: Devolver itens ao estoque
        cursor.execute("SELECT produto_codigo, quantidade FROM venda_itens WHERE venda_id = ?", (venda_id,))
        for produto_codigo, quantidade in cursor.fetchall():
            cursor.execute("UPDATE estoque SET quantidade = quantidade + ? WHERE codigo = ?", (quantidade, produto_codigo))
        
        _conn.commit()
        registrar_log(usuario_id, "ESTORNO_VENDA", f"Venda #{venda_id} estornada.")
        return f"Venda #{venda_id} estornada com sucesso! O estoque foi atualizado e o financeiro revertido."
    except Exception as e: _conn.rollback(); return f"Erro ao estornar venda: {e}"

def get_transacoes(tipo):
    cursor = _conn.cursor(); cursor.execute("SELECT data, descricao, valor, natureza FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo' ORDER BY data DESC", (tipo,)); return cursor.fetchall()
def get_saldo(tipo):
    cursor = _conn.cursor(); cursor.execute("SELECT SUM(CASE WHEN natureza = 'Entrada' THEN valor ELSE -valor END) FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo'", (tipo,)); saldo = cursor.fetchone()[0]
    return saldo if saldo is not None else 0
def get_contas_a_receber(cliente_id=None, metodo_pagamento=None):
    cursor = _conn.cursor()
    query = "SELECT p.id, v.id, c.nome, p.numero_parcela, v.numero_parcelas, p.valor_parcela, p.data_vencimento, v.metodo_pagamento FROM parcelas p JOIN vendas v ON p.venda_id = v.id JOIN clientes c ON v.cliente_id = c.id WHERE p.status = 'Pendente' AND v.status = 'Ativa'"
    params = []
    if cliente_id: query += " AND c.id = ?"; params.append(cliente_id)
    if metodo_pagamento and metodo_pagamento != 'Todos': query += " AND v.metodo_pagamento = ?"; params.append(metodo_pagamento)
    query += " ORDER BY p.data_vencimento ASC"; cursor.execute(query, params); return cursor.fetchall()
def get_vendas_ativas():
    cursor = _conn.cursor(); cursor.execute("SELECT v.id, v.data, c.nome, v.valor_total FROM vendas v JOIN clientes c ON v.cliente_id = c.id WHERE v.status = 'Ativa' ORDER BY v.id DESC"); return cursor.fetchall()
    
def relatorio_clientes_filtrado(termo=""):
    cursor = _conn.cursor(); cursor.execute("SELECT id, nome, telefone, aniversario, endereco, instagram FROM clientes WHERE nome LIKE ? ORDER BY nome", ('%' + termo + '%',)); return cursor.fetchall()
def relatorio_estoque_filtrado(termo="", baixo_estoque=False, limite=10):
    query = "SELECT codigo, descricao, quantidade, valor_compra, valor_venda FROM estoque WHERE (descricao LIKE ? OR codigo LIKE ?)"
    params = ['%' + termo + '%', '%' + termo + '%']
    if baixo_estoque: query += " AND quantidade <= ?"; params.append(limite)
    query += " ORDER BY quantidade ASC"; cursor = _conn.cursor(); cursor.execute(query, params); return cursor.fetchall()
def relatorio_vendas_filtrado(dt_inicio, dt_fim, cliente_id=None):
    query = "SELECT v.id, v.data, c.nome, v.metodo_pagamento, v.numero_parcelas, v.valor_total, v.status FROM vendas v JOIN clientes c ON v.cliente_id = c.id WHERE DATE(v.data) BETWEEN ? AND ?"
    params = [dt_inicio, dt_fim]
    if cliente_id: query += " AND v.cliente_id = ?"; params.append(cliente_id)
    query += " ORDER BY v.data DESC"; cursor = _conn.cursor(); cursor.execute(query, params); return cursor.fetchall()
def relatorio_contas_a_receber(cliente_id=None, vencidas=False):
    query = "SELECT c.nome, v.id, p.numero_parcela, v.numero_parcelas, p.data_vencimento, p.valor_parcela FROM parcelas p JOIN vendas v ON p.venda_id = v.id JOIN clientes c ON v.cliente_id = c.id WHERE p.status = 'Pendente' AND v.status = 'Ativa'"
    params = []
    if cliente_id: query += " AND c.id = ?"; params.append(cliente_id)
    if vencidas: query += " AND DATE(p.data_vencimento) < DATE('now')";
    query += " ORDER BY p.data_vencimento ASC"; cursor = _conn.cursor(); cursor.execute(query, params); return cursor.fetchall()
def relatorio_extratos(tipo, dt_inicio, dt_fim):
    query = "SELECT data, descricao, natureza, valor FROM transacoes_financeiras WHERE tipo = ? AND status = 'Ativo' AND DATE(data) BETWEEN ? AND ?"
    params = [tipo, dt_inicio, dt_fim]; cursor = _conn.cursor(); cursor.execute(query, params); return cursor.fetchall()
def gerar_pdf_generico(filepath, titulo, headers, data):
    if not filepath: return "Geração de PDF cancelada."
    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
    elements = [Paragraph(titulo, getSampleStyleSheet()['Title']), Spacer(1, 24)]
    table_data = [headers] + data
    t = Table(table_data, repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    t.setStyle(style); elements.append(t); doc.build(elements)
    return f"PDF salvo com sucesso em: {filepath}"