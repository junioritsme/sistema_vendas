# arquivo: app.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
from tkcalendar import DateEntry
import controllers as ctl
import datetime
import webbrowser

# =================================================================================
# DEFINIÇÃO DE TODAS AS CLASSES COMPONENTES (ABAS, JANELAS, ETC.)
# =================================================================================

class VendasTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        self.carrinho = []
        self.cliente_selecionado = None
        frame_cliente = ttk.LabelFrame(self, text="1. Selecionar Cliente")
        frame_cliente.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_cliente, text="Buscar Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.cliente_busca_var = tk.StringVar()
        self.cliente_busca_entry = ttk.Entry(frame_cliente, textvariable=self.cliente_busca_var, width=40)
        self.cliente_busca_entry.grid(row=0, column=1, padx=5, pady=5)
        self.cliente_busca_entry.bind('<KeyRelease>', self.atualizar_lista_clientes)
        self.lista_clientes = tk.Listbox(frame_cliente, height=3)
        self.lista_clientes.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.lista_clientes.bind('<<ListboxSelect>>', self.selecionar_cliente)
        self.label_cliente_selecionado = ttk.Label(frame_cliente, text="Nenhum cliente selecionado.", font=('Arial', 10, 'bold'))
        self.label_cliente_selecionado.grid(row=2, column=0, columnspan=2, pady=5)
        frame_produto = ttk.LabelFrame(self, text="2. Adicionar Produtos")
        frame_produto.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_produto, text="Buscar Produto:").grid(row=0, column=0, padx=5, pady=5)
        self.produto_busca_var = tk.StringVar()
        self.produto_busca_entry = ttk.Entry(frame_produto, textvariable=self.produto_busca_var, width=40)
        self.produto_busca_entry.grid(row=0, column=1, padx=5, pady=5)
        self.produto_busca_entry.bind('<KeyRelease>', self.atualizar_lista_produtos)
        self.lista_produtos = tk.Listbox(frame_produto, height=4)
        self.lista_produtos.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        ttk.Label(frame_produto, text="Qtd:").grid(row=1, column=2, padx=5, pady=5)
        self.qtd_produto_var = tk.IntVar(value=1)
        self.qtd_produto_entry = ttk.Spinbox(frame_produto, from_=1, to=999, textvariable=self.qtd_produto_var, width=5)
        self.qtd_produto_entry.grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(frame_produto, text="Adicionar ao Carrinho", command=self.add_ao_carrinho).grid(row=1, column=4, padx=10, pady=5)
        frame_carrinho = ttk.LabelFrame(self, text="Carrinho")
        frame_carrinho.pack(fill='both', expand=True, padx=10, pady=5)
        colunas = ('codigo', 'descricao', 'qtd', 'valor_unit', 'valor_total')
        self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=colunas, show='headings')
        self.tree_carrinho.heading('codigo', text='Código'); self.tree_carrinho.heading('descricao', text='Descrição')
        self.tree_carrinho.heading('qtd', text='Qtd'); self.tree_carrinho.heading('valor_unit', text='Vlr. Unit.')
        self.tree_carrinho.heading('valor_total', text='Vlr. Total')
        self.tree_carrinho.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame_carrinho, orient=tk.VERTICAL, command=self.tree_carrinho.yview)
        self.tree_carrinho.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        frame_pagamento = ttk.LabelFrame(self, text="3. Finalizar Venda")
        frame_pagamento.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_pagamento, text="Método:").grid(row=0, column=0, padx=5, pady=5)
        self.metodo_pag_var = tk.StringVar()
        self.metodo_pag_combo = ttk.Combobox(frame_pagamento, textvariable=self.metodo_pag_var,
                                             values=['Dinheiro', 'PIX', 'Cartão de Débito', 'Cartão de Crédito', 'Crediário'])
        self.metodo_pag_combo.grid(row=0, column=1, padx=5, pady=5)
        self.metodo_pag_combo.bind('<<ComboboxSelected>>', self.toggle_opcoes_pagamento)
        self.label_parcelas = ttk.Label(frame_pagamento, text="Nº de Parcelas:")
        self.parcelas_var = tk.IntVar(value=1)
        self.parcelas_spinbox = ttk.Spinbox(frame_pagamento, from_=1, to=36, textvariable=self.parcelas_var, width=5)
        self.label_vencimento = ttk.Label(frame_pagamento, text="Venc. 1ª Parcela:")
        self.data_vencimento_entry = DateEntry(frame_pagamento, date_pattern='yyyy-mm-dd', width=12)
        ttk.Label(frame_pagamento, text="Desconto (R$):").grid(row=1, column=0, padx=5, pady=5)
        self.desconto_var = tk.DoubleVar(value=0.0)
        desconto_entry = ttk.Entry(frame_pagamento, textvariable=self.desconto_var, width=10)
        desconto_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        desconto_entry.bind('<KeyRelease>', self.atualizar_tree_carrinho)
        self.label_valor_total = ttk.Label(frame_pagamento, text="Total: R$ 0,00", font=('Arial', 12, 'bold'))
        self.label_valor_total.grid(row=1, column=2, padx=20, pady=5, columnspan=2)
        ttk.Button(frame_pagamento, text="REGISTRAR VENDA", command=self.finalizar_venda).grid(row=0, rowspan=2, column=4, padx=20, pady=5, ipady=10)
        self.atualizar_lista_clientes()
        self.atualizar_lista_produtos()
    def toggle_opcoes_pagamento(self, event=None):
        metodo = self.metodo_pag_var.get()
        self.label_parcelas.grid_remove(); self.parcelas_spinbox.grid_remove()
        self.label_vencimento.grid_remove(); self.data_vencimento_entry.grid_remove()
        if metodo in ['Cartão de Crédito', 'Crediário']:
            self.label_parcelas.grid(row=0, column=2, padx=(10,0)); self.parcelas_spinbox.grid(row=0, column=3, padx=(0,10))
            if metodo == 'Crediário':
                self.label_vencimento.grid(row=1, column=2, padx=(10,0)); self.data_vencimento_entry.grid(row=1, column=3, padx=(0,10))
    def add_ao_carrinho(self):
        try:
            selecionado = self.lista_produtos.get(self.lista_produtos.curselection())
            codigo, _ = selecionado.split(' - ', 1)
            produto_info = next((p for p in ctl.buscar_produto(codigo) if p[0] == codigo), None)
            if not produto_info: messagebox.showerror("Erro", "Produto não encontrado."); return
            quantidade = self.qtd_produto_var.get()
            if quantidade > produto_info[3]: messagebox.showwarning("Estoque", f"Estoque insuficiente. Disponível: {produto_info[3]}"); return
            item_existente = next((item for item in self.carrinho if item['codigo'] == codigo), None)
            if item_existente: item_existente['quantidade'] += quantidade
            else: self.carrinho.append({'codigo': codigo, 'descricao': produto_info[1], 'quantidade': quantidade, 'valor_venda': produto_info[2]})
            self.atualizar_tree_carrinho()
        except Exception: messagebox.showerror("Erro", "Selecione um produto da lista.")
    def atualizar_tree_carrinho(self, event=None):
        for i in self.tree_carrinho.get_children(): self.tree_carrinho.delete(i)
        total_bruto = 0
        for item in self.carrinho:
            valor_total_item = item['valor_venda'] * item['quantidade']
            total_bruto += valor_total_item
            self.tree_carrinho.insert('', tk.END, values=(item['codigo'], item['descricao'], item['quantidade'], ctl.format_currency(item['valor_venda']), ctl.format_currency(valor_total_item)))
        try:
            desconto = self.desconto_var.get()
        except tk.TclError: desconto = 0.0
        total_final = total_bruto - desconto
        self.label_valor_total.config(text=f"Total: {ctl.format_currency(total_final)}")
    def finalizar_venda(self):
        if not self.cliente_selecionado: messagebox.showerror("Erro", "Nenhum cliente selecionado."); return
        if not self.carrinho: messagebox.showerror("Erro", "Carrinho está vazio."); return
        metodo = self.metodo_pag_var.get()
        if not metodo: messagebox.showerror("Erro", "Selecione um método de pagamento."); return
        numero_parcelas = self.parcelas_var.get() if metodo in ['Cartão de Crédito', 'Crediário'] else 1
        data_venc_str = self.data_vencimento_entry.get_date().strftime('%Y-%m-%d') if metodo == 'Crediário' else None
        resultado = ctl.registrar_venda(self.cliente_selecionado['id'], metodo, numero_parcelas, self.desconto_var.get(), self.carrinho, data_venc_str)
        messagebox.showinfo("Resultado", resultado)
        if "sucesso" in resultado:
            self.carrinho.clear(); self.cliente_selecionado = None
            self.label_cliente_selecionado.config(text="Nenhum cliente selecionado.")
            self.desconto_var.set(0.0); self.atualizar_tree_carrinho(); self.atualizar_lista_produtos()
            self.app.on_data_changed()
    def atualizar_lista_clientes(self, event=None):
        self.lista_clientes.delete(0, tk.END)
        for id, nome in ctl.buscar_cliente(self.cliente_busca_var.get()): self.lista_clientes.insert(tk.END, f"{id} - {nome}")
    def selecionar_cliente(self, event=None):
        try:
            id, nome = self.lista_clientes.get(self.lista_clientes.curselection()).split(' - ')
            self.cliente_selecionado = {'id': int(id), 'nome': nome}
            self.label_cliente_selecionado.config(text=f"Cliente: {nome}")
        except: pass
    def atualizar_lista_produtos(self, event=None):
        self.lista_produtos.delete(0, tk.END)
        for cod, desc, _, qtd in ctl.buscar_produto(self.produto_busca_var.get()): self.lista_produtos.insert(tk.END, f"{cod} - {desc} (Estoque: {qtd})")

class ClientesTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_cadastro = ttk.LabelFrame(self, text="Novo Cliente")
        frame_cadastro.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5); self.nome_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.nome_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_cadastro, text="Telefone:").grid(row=1, column=0, padx=5, pady=5); self.tel_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.tel_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(frame_cadastro, text="Instagram:").grid(row=2, column=0, padx=5, pady=5); self.insta_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.insta_var, width=40).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame_cadastro, text="Adicionar Cliente", command=self.add_cliente).grid(row=3, column=1, sticky='e', padx=5, pady=10)
        frame_lista = ttk.LabelFrame(self, text="Clientes Cadastrados")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('id', 'nome', 'telefone', 'instagram')
        self.tree_clientes = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree_clientes.heading(col, text=col.title())
        self.tree_clientes.pack(fill='both', expand=True)
        self.atualizar_lista()
    def add_cliente(self):
        nome = self.nome_var.get()
        if not nome: messagebox.showerror("Erro", "O nome do cliente é obrigatório."); return
        resultado = ctl.adicionar_cliente(nome, self.tel_var.get(), self.insta_var.get())
        messagebox.showinfo("Cadastro", resultado)
        if "sucesso" in resultado:
            self.nome_var.set(''); self.tel_var.set(''); self.insta_var.set('')
            self.app.on_data_changed()
    def atualizar_lista(self):
        for i in self.tree_clientes.get_children(): self.tree_clientes.delete(i)
        for cliente in ctl.listar_clientes(): self.tree_clientes.insert('', tk.END, values=cliente)

class EstoqueTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_cadastro = ttk.LabelFrame(self, text="Novo Produto")
        frame_cadastro.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_cadastro, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky='w'); self.codigo_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.codigo_var).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Descrição:").grid(row=1, column=0, padx=5, pady=5, sticky='w'); self.desc_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.desc_var, width=50).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Valor Compra:").grid(row=2, column=0, padx=5, pady=5, sticky='w'); self.compra_var = tk.DoubleVar()
        ttk.Entry(frame_cadastro, textvariable=self.compra_var).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Valor Venda:").grid(row=3, column=0, padx=5, pady=5, sticky='w'); self.venda_var = tk.DoubleVar()
        ttk.Entry(frame_cadastro, textvariable=self.venda_var).grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Quantidade:").grid(row=4, column=0, padx=5, pady=5, sticky='w'); self.qtd_var = tk.IntVar()
        ttk.Entry(frame_cadastro, textvariable=self.qtd_var).grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(frame_cadastro, text="Adicionar Produto", command=self.add_produto).grid(row=5, column=1, sticky='e', padx=5, pady=10)
        frame_lista = ttk.LabelFrame(self, text="Estoque Atual")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('codigo', 'descricao', 'compra', 'venda', 'qtd')
        self.tree_estoque = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree_estoque.heading(col, text=col.title())
        self.tree_estoque.pack(fill='both', expand=True)
        self.atualizar_lista()
    def add_produto(self):
        try:
            codigo, desc = self.codigo_var.get(), self.desc_var.get()
            if not codigo or not desc: messagebox.showerror("Erro", "Código e Descrição são obrigatórios."); return
            resultado = ctl.adicionar_produto(codigo, desc, self.compra_var.get(), self.venda_var.get(), self.qtd_var.get())
            messagebox.showinfo("Cadastro", resultado)
            if "sucesso" in resultado:
                self.codigo_var.set(''); self.desc_var.set(''); self.compra_var.set(0.0); self.venda_var.set(0.0); self.qtd_var.set(0)
                self.app.on_data_changed()
        except tk.TclError: messagebox.showerror("Erro", "Valores e quantidade devem ser numéricos.")
    def atualizar_lista(self):
        for i in self.tree_estoque.get_children(): self.tree_estoque.delete(i)
        for prod in ctl.listar_produtos():
            values = (prod[0], prod[1], ctl.format_currency(prod[2]), ctl.format_currency(prod[3]), prod[4])
            self.tree_estoque.insert('', tk.END, values=values)

class JanelaLiquidacao(tk.Toplevel):
    def __init__(self, parent, app_ref, ids_parcelas, valor_total_esperado):
        super().__init__(parent)
        self.parent_frame = parent
        self.app = app_ref
        self.ids_parcelas = ids_parcelas
        self.title("Liquidar Parcelas"); self.transient(parent); self.grab_set()
        frame = ttk.Frame(self, padding="20"); frame.pack(expand=True, fill='both')
        ttk.Label(frame, text=f"Liquidando {len(ids_parcelas)} parcela(s).", font=('Arial', 10, 'bold')).pack(pady=5)
        ttk.Label(frame, text=f"Valor total esperado: {ctl.format_currency(valor_total_esperado)}").pack(pady=5)
        ttk.Label(frame, text="Destino do Pagamento:").pack(pady=(10,0)); self.destino_var = tk.StringVar(value="Banco")
        ttk.Combobox(frame, textvariable=self.destino_var, values=['Banco', 'Caixa']).pack()
        ttk.Label(frame, text="Valor Líquido Recebido:").pack(pady=(10,0)); self.valor_liq_var = tk.DoubleVar(value=valor_total_esperado)
        ttk.Entry(frame, textvariable=self.valor_liq_var).pack()
        ttk.Button(frame, text="Confirmar Liquidação", command=self.liquidar).pack(pady=20)
    def liquidar(self):
        destino = self.destino_var.get()
        try: valor_liq = self.valor_liq_var.get()
        except tk.TclError: messagebox.showerror("Erro", "O valor recebido deve ser um número.", parent=self); return
        if not destino: messagebox.showerror("Erro", "Selecione um destino (Banco ou Caixa).", parent=self); return
        if valor_liq <= 0: messagebox.showerror("Erro", "O valor recebido deve ser maior que zero.", parent=self); return
        resultado = ctl.liquidar_parcelas(self.ids_parcelas, destino, valor_liq)
        messagebox.showinfo("Resultado", resultado, parent=self.parent_frame)
        if "sucesso" in resultado:
            self.app.on_data_changed(); self.destroy()

class ContasAReceberTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_filtros = ttk.LabelFrame(self, text="Filtros")
        frame_filtros.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_filtros, text="Cliente:").pack(side=tk.LEFT, padx=5); self.cliente_var = tk.StringVar()
        self.cliente_combo = ttk.Combobox(frame_filtros, textvariable=self.cliente_var, width=30)
        self.cliente_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_filtros, text="Método de Pag.:").pack(side=tk.LEFT, padx=5); self.pagamento_var = tk.StringVar(value="Todos")
        pag_combo = ttk.Combobox(frame_filtros, textvariable=self.pagamento_var, values=['Todos', 'Dinheiro', 'PIX', 'Cartão de Débito', 'Cartão de Crédito', 'Crediário'])
        pag_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_filtros, text="Buscar", command=self.buscar_parcelas).pack(side=tk.LEFT, padx=10)
        frame_parcelas = ttk.LabelFrame(self, text="Parcelas Pendentes")
        frame_parcelas.pack(fill='both', expand=True, padx=10, pady=5)
        colunas = ('p_id', 'v_id', 'cliente', 'parcela', 'valor', 'vencimento', 'metodo')
        self.tree = ttk.Treeview(frame_parcelas, columns=colunas, show='headings', selectmode='extended')
        self.tree.heading('p_id', text='ID Parc.'); self.tree.column('p_id', width=60)
        self.tree.heading('v_id', text='ID Venda'); self.tree.column('v_id', width=60)
        self.tree.heading('cliente', text='Cliente'); self.tree.heading('parcela', text='Parcela'); self.tree.column('parcela', width=80, anchor='center')
        self.tree.heading('valor', text='Valor'); self.tree.column('valor', width=100, anchor='e')
        self.tree.heading('vencimento', text='Vencimento'); self.tree.column('vencimento', width=100, anchor='center')
        self.tree.heading('metodo', text='Método Pag.')
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame_parcelas, orient=tk.VERTICAL, command=self.tree.yview); self.tree.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree.tag_configure('vencida', background='#FFCCCB')
        frame_liq = ttk.LabelFrame(self, text="Ações"); frame_liq.pack(fill='x', padx=10, pady=5)
        ttk.Button(frame_liq, text="LIQUIDAR PARCELA(S) SELECIONADA(S)", command=self.abrir_janela_liquidacao).pack(pady=10)
        self.carregar_clientes(); self.buscar_parcelas()
    def carregar_clientes(self):
        clientes = ctl.listar_clientes()
        self.clientes_map = {f"{c[1]} (ID: {c[0]})": c[0] for c in clientes}
        self.cliente_combo['values'] = ["Todos"] + list(self.clientes_map.keys())
        self.cliente_combo.set("Todos")
    def buscar_parcelas(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        cliente_selecionado_str = self.cliente_var.get()
        cliente_id = self.clientes_map.get(cliente_selecionado_str) if cliente_selecionado_str != "Todos" else None
        metodo = self.pagamento_var.get()
        parcelas = ctl.get_contas_a_receber(cliente_id, metodo)
        for p in parcelas:
            parcela_str = f"{p[3]}/{p[4]}"; venc_dt = datetime.datetime.strptime(p[6], '%Y-%m-%d').date(); hoje = datetime.date.today()
            tag = ('vencida',) if venc_dt < hoje else ()
            self.tree.insert('', 'end', values=(p[0], p[1], p[2], parcela_str, ctl.format_currency(p[5]), p[6], p[7]), tags=tag)
    def abrir_janela_liquidacao(self):
        selecionados = self.tree.selection()
        if not selecionados: messagebox.showwarning("Atenção", "Selecione ao menos uma parcela para liquidar."); return
        ids_parcelas = [self.tree.item(item, 'values')[0] for item in selecionados]
        valor_total = sum(float(self.tree.item(item, 'values')[4].replace('R$ ', '').replace('.', '').replace(',', '.')) for item in selecionados)
        JanelaLiquidacao(self, self.app, ids_parcelas, valor_total)

class FinanceiroTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.caixa_frame = CaixaFrame(notebook, self.app)
        self.banco_frame = BancoFrame(notebook, self.app)
        notebook.add(self.caixa_frame, text='Extrato do Caixa')
        notebook.add(self.banco_frame, text='Extrato do Banco')
    def refresh_data(self):
        self.caixa_frame.refresh()
        self.banco_frame.refresh()

class CaixaFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_saldo = ttk.Frame(self); frame_saldo.pack(fill='x', padx=10, pady=5)
        self.label_saldo = ttk.Label(frame_saldo, text="Saldo do Caixa: R$ 0,00", font=('Arial', 14, 'bold')); self.label_saldo.pack()
        frame_saida = ttk.LabelFrame(self, text="Registrar Saída Manual do Caixa"); frame_saida.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_saida, text="Valor (R$):").grid(row=0, column=0); self.saida_valor_var = tk.DoubleVar()
        ttk.Entry(frame_saida, textvariable=self.saida_valor_var).grid(row=0, column=1)
        ttk.Label(frame_saida, text="Descrição:").grid(row=0, column=2); self.saida_desc_var = tk.StringVar()
        ttk.Entry(frame_saida, textvariable=self.saida_desc_var, width=40).grid(row=0, column=3)
        ttk.Button(frame_saida, text="Registrar Saída", command=self.registrar_saida).grid(row=0, column=4, padx=10)
        frame_lista = ttk.LabelFrame(self, text="Histórico de Transações Ativas"); frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('data', 'descricao', 'valor', 'natureza'); self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.title())
        self.tree.pack(fill='both', expand=True)
        self.refresh()
    def registrar_saida(self):
        try:
            valor = self.saida_valor_var.get(); desc = self.saida_desc_var.get()
            if valor > 0 and desc:
                ctl.add_transacao_financeira('Caixa', 'Saída', desc, valor); self.saida_valor_var.set(0.0); self.saida_desc_var.set('')
                self.app.on_data_changed()
            else: messagebox.showerror("Erro", "Valor e descrição são obrigatórios.")
        except tk.TclError: messagebox.showerror("Erro", "O valor da saída deve ser numérico.")
    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for data, desc, valor, natureza in ctl.get_transacoes('Caixa'):
            valor_fmt = ctl.format_currency(valor)
            if natureza == 'Saída': valor_fmt = f"- {valor_fmt}"
            data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.tree.insert('', 'end', values=(data_formatada, desc, valor_fmt, natureza))
        saldo = ctl.get_saldo('Caixa'); self.label_saldo.config(text=f"Saldo do Caixa: {ctl.format_currency(saldo)}")

class BancoFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_saldo = ttk.Frame(self); frame_saldo.pack(fill='x', padx=10, pady=5)
        self.label_saldo = ttk.Label(frame_saldo, text="Saldo do Banco: R$ 0,00", font=('Arial', 14, 'bold')); self.label_saldo.pack()
        frame_saida = ttk.LabelFrame(self, text="Registrar Saída Manual do Banco"); frame_saida.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_saida, text="Valor (R$):").grid(row=0, column=0); self.saida_valor_var = tk.DoubleVar()
        ttk.Entry(frame_saida, textvariable=self.saida_valor_var).grid(row=0, column=1)
        ttk.Label(frame_saida, text="Descrição:").grid(row=0, column=2); self.saida_desc_var = tk.StringVar()
        ttk.Entry(frame_saida, textvariable=self.saida_desc_var, width=40).grid(row=0, column=3)
        ttk.Button(frame_saida, text="Registrar Saída", command=self.registrar_saida).grid(row=0, column=4, padx=10)
        frame_hist = ttk.LabelFrame(self, text="Histórico de Transações Ativas"); frame_hist.pack(fill='both', expand=True, padx=10, pady=10)
        colunas_hist = ('data', 'descricao', 'valor', 'natureza'); self.tree_hist = ttk.Treeview(frame_hist, columns=colunas_hist, show='headings')
        for col in colunas_hist: self.tree_hist.heading(col, text=col.title())
        self.tree_hist.pack(fill='both', expand=True)
        self.refresh()
    def registrar_saida(self):
        try:
            valor = self.saida_valor_var.get(); desc = self.saida_desc_var.get()
            if valor > 0 and desc:
                ctl.add_transacao_financeira('Banco', 'Saída', desc, valor); self.saida_valor_var.set(0.0); self.saida_desc_var.set('')
                self.app.on_data_changed()
            else: messagebox.showerror("Erro", "Valor e descrição são obrigatórios.")
        except tk.TclError: messagebox.showerror("Erro", "O valor da saída deve ser numérico.")
    def refresh(self):
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        for data, desc, valor, natureza in ctl.get_transacoes('Banco'):
            valor_fmt = ctl.format_currency(valor)
            if natureza != 'Entrada': valor_fmt = f"- {valor_fmt}"
            data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.tree_hist.insert('', 'end', values=(data_formatada, desc, valor_fmt, natureza))
        saldo_banco = ctl.get_saldo('Banco'); self.label_saldo.config(text=f"Saldo do Banco: {ctl.format_currency(saldo_banco)}")

# =================================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO (DEFINIDA POR ÚLTIMO)
# =================================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Vendas e Financeiro")
        self.geometry("1280x800")
        
        ctl.conectar()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill='both')

        self.vendas_frame = VendasTab(notebook, self)
        self.contas_receber_frame = ContasAReceberTab(notebook, self)
        self.financeiro_frame = FinanceiroTab(notebook, self)
        self.clientes_frame = ClientesTab(notebook, self)
        self.estoque_frame = EstoqueTab(notebook, self)

        notebook.add(self.vendas_frame, text='Vendas')
        notebook.add(self.contas_receber_frame, text='Contas a Receber')
        notebook.add(self.financeiro_frame, text='Financeiro (Extratos)')
        notebook.add(self.estoque_frame, text='Estoque')
        notebook.add(self.clientes_frame, text='Clientes')
        
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Você tem certeza que quer sair?"):
            ctl.desconectar()
            self.destroy()

    def on_data_changed(self):
        """Atualiza todas as abas que exibem dados que podem ter sido alterados."""
        self.estoque_frame.atualizar_lista()
        self.contas_receber_frame.buscar_parcelas()
        self.clientes_frame.atualizar_lista()
        self.vendas_frame.atualizar_lista_clientes()
        self.financeiro_frame.refresh_data()


if __name__ == "__main__":
    app = App()
    app.mainloop()