# arquivo: app.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font, filedialog
from tkcalendar import DateEntry
import controllers as ctl
import datetime
import webbrowser

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Login - Sistema de Vendas"); self.geometry("300x180"); self.resizable(False, False)
        self.user_id = None; self.username = None; self.protocol("WM_DELETE_WINDOW", self.on_closing); self.eval('tk::PlaceWindow . center')
        frame = ttk.Frame(self, padding="10"); frame.pack(expand=True)
        ttk.Label(frame, text="Usuário:").pack(pady=(10,0)); self.user_var = tk.StringVar()
        user_entry = ttk.Entry(frame, textvariable=self.user_var, width=30); user_entry.pack(); user_entry.focus()
        ttk.Label(frame, text="Senha:").pack(pady=(10,0)); self.pass_var = tk.StringVar()
        pass_entry = ttk.Entry(frame, textvariable=self.pass_var, show="*", width=30); pass_entry.pack()
        pass_entry.bind("<Return>", self.attempt_login)
        ttk.Button(frame, text="Entrar", command=self.attempt_login).pack(pady=20)
    def attempt_login(self, event=None):
        user, pwd = self.user_var.get(), self.pass_var.get()
        if not user or not pwd: messagebox.showerror("Erro", "Usuário e senha são obrigatórios."); return
        user_id = ctl.verificar_login(user, pwd)
        if user_id: self.user_id = user_id; self.username = user; self.destroy()
        else: messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.")
    def on_closing(self): self.user_id = None; self.destroy()

class VendasTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref; self.carrinho = []; self.cliente_selecionado = None
        frame_cliente = ttk.LabelFrame(self, text="1. Selecionar Cliente"); frame_cliente.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_cliente, text="Buscar Cliente:").grid(row=0, column=0, padx=5, pady=5); self.cliente_busca_var = tk.StringVar()
        self.cliente_busca_entry = ttk.Entry(frame_cliente, textvariable=self.cliente_busca_var, width=40); self.cliente_busca_entry.grid(row=0, column=1, padx=5, pady=5)
        self.cliente_busca_entry.bind('<KeyRelease>', self.atualizar_lista_clientes)
        self.lista_clientes = tk.Listbox(frame_cliente, height=3); self.lista_clientes.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.lista_clientes.bind('<<ListboxSelect>>', self.selecionar_cliente)
        self.label_cliente_selecionado = ttk.Label(frame_cliente, text="Nenhum cliente selecionado.", font=('Arial', 10, 'bold')); self.label_cliente_selecionado.grid(row=2, column=0, columnspan=2, pady=5)
        frame_produto = ttk.LabelFrame(self, text="2. Adicionar Produtos"); frame_produto.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_produto, text="Buscar Produto:").grid(row=0, column=0, padx=5, pady=5); self.produto_busca_var = tk.StringVar()
        self.produto_busca_entry = ttk.Entry(frame_produto, textvariable=self.produto_busca_var, width=40); self.produto_busca_entry.grid(row=0, column=1, padx=5, pady=5)
        self.produto_busca_entry.bind('<KeyRelease>', self.atualizar_lista_produtos)
        self.lista_produtos = tk.Listbox(frame_produto, height=4); self.lista_produtos.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        ttk.Label(frame_produto, text="Qtd:").grid(row=1, column=2, padx=5, pady=5); self.qtd_produto_var = tk.IntVar(value=1)
        self.qtd_produto_entry = ttk.Spinbox(frame_produto, from_=1, to=999, textvariable=self.qtd_produto_var, width=5); self.qtd_produto_entry.grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(frame_produto, text="Adicionar ao Carrinho", command=self.add_ao_carrinho).grid(row=1, column=4, padx=10, pady=5)
        frame_carrinho = ttk.LabelFrame(self, text="Carrinho"); frame_carrinho.pack(fill='both', expand=True, padx=10, pady=5)
        colunas = ('codigo', 'descricao', 'qtd', 'valor_unit', 'valor_total'); self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=colunas, show='headings')
        for col in colunas: self.tree_carrinho.heading(col, text=col.title().replace("_", " "))
        self.tree_carrinho.pack(side=tk.LEFT, fill='both', expand=True); scrollbar = ttk.Scrollbar(frame_carrinho, orient=tk.VERTICAL, command=self.tree_carrinho.yview)
        self.tree_carrinho.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill='y')
        frame_pagamento = ttk.LabelFrame(self, text="3. Finalizar Venda"); frame_pagamento.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_pagamento, text="Método:").grid(row=0, column=0, padx=5, pady=5); self.metodo_pag_var = tk.StringVar()
        self.metodo_pag_combo = ttk.Combobox(frame_pagamento, textvariable=self.metodo_pag_var, values=['Dinheiro', 'PIX', 'Cartão de Débito', 'Cartão de Crédito', 'Crediário'])
        self.metodo_pag_combo.grid(row=0, column=1, padx=5, pady=5); self.metodo_pag_combo.bind('<<ComboboxSelected>>', self.toggle_opcoes_pagamento)
        self.label_parcelas = ttk.Label(frame_pagamento, text="Nº de Parcelas:"); self.parcelas_var = tk.IntVar(value=1)
        self.parcelas_spinbox = ttk.Spinbox(frame_pagamento, from_=1, to=36, textvariable=self.parcelas_var, width=5)
        self.label_vencimento = ttk.Label(frame_pagamento, text="Venc. 1ª Parcela:"); self.data_vencimento_entry = DateEntry(frame_pagamento, date_pattern='yyyy-mm-dd', width=12)
        ttk.Label(frame_pagamento, text="Desconto (R$):").grid(row=1, column=0, padx=5, pady=5); self.desconto_var = tk.DoubleVar(value=0.0)
        desconto_entry = ttk.Entry(frame_pagamento, textvariable=self.desconto_var, width=10); desconto_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        desconto_entry.bind('<KeyRelease>', self.atualizar_tree_carrinho)
        self.label_valor_total = ttk.Label(frame_pagamento, text="Total: R$ 0,00", font=('Arial', 12, 'bold')); self.label_valor_total.grid(row=1, column=2, padx=20, pady=5, columnspan=2)
        ttk.Button(frame_pagamento, text="REGISTRAR VENDA", command=self.finalizar_venda).grid(row=0, rowspan=2, column=4, padx=20, pady=5, ipady=10)
        self.atualizar_lista_clientes(); self.atualizar_lista_produtos()
    def toggle_opcoes_pagamento(self, event=None):
        metodo = self.metodo_pag_var.get()
        self.label_parcelas.grid_remove(); self.parcelas_spinbox.grid_remove(); self.label_vencimento.grid_remove(); self.data_vencimento_entry.grid_remove()
        if metodo in ['Cartão de Crédito', 'Crediário']:
            self.label_parcelas.grid(row=0, column=2, padx=(10,0)); self.parcelas_spinbox.grid(row=0, column=3, padx=(0,10))
            if metodo == 'Crediário': self.label_vencimento.grid(row=1, column=2, padx=(10,0)); self.data_vencimento_entry.grid(row=1, column=3, padx=(0,10))
    def add_ao_carrinho(self):
        try:
            selecionado = self.lista_produtos.get(self.lista_produtos.curselection())
            codigo, _ = selecionado.split(' - ', 1); produto_info = next((p for p in ctl.buscar_produto(codigo) if p[0] == codigo), None)
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
            valor_total_item = item['valor_venda'] * item['quantidade']; total_bruto += valor_total_item
            self.tree_carrinho.insert('', tk.END, values=(item['codigo'], item['descricao'], item['quantidade'], ctl.format_currency(item['valor_venda']), ctl.format_currency(valor_total_item)))
        try: desconto = self.desconto_var.get()
        except tk.TclError: desconto = 0.0
        self.label_valor_total.config(text=f"Total: {ctl.format_currency(total_bruto - desconto)}")
    def finalizar_venda(self):
        if not self.cliente_selecionado: messagebox.showerror("Erro", "Nenhum cliente selecionado."); return
        if not self.carrinho: messagebox.showerror("Erro", "Carrinho está vazio."); return
        metodo = self.metodo_pag_var.get()
        if not metodo: messagebox.showerror("Erro", "Selecione um método de pagamento."); return
        numero_parcelas = self.parcelas_var.get() if metodo in ['Cartão de Crédito', 'Crediário'] else 1
        data_venc_str = self.data_vencimento_entry.get_date().strftime('%Y-%m-%d') if metodo == 'Crediário' else None
        resultado = ctl.registrar_venda(self.app.usuario_id, self.cliente_selecionado['id'], metodo, numero_parcelas, self.desconto_var.get(), self.carrinho, data_venc_str)
        messagebox.showinfo("Resultado", resultado)
        if "sucesso" in resultado:
            self.carrinho.clear(); self.cliente_selecionado = None; self.label_cliente_selecionado.config(text="Nenhum cliente selecionado.")
            self.desconto_var.set(0.0); self.atualizar_tree_carrinho(); self.atualizar_lista_produtos(); self.app.on_data_changed()
    def atualizar_lista_clientes(self, event=None):
        self.lista_clientes.delete(0, tk.END)
        for id, nome in ctl.buscar_cliente_por_termo(self.cliente_busca_var.get()): self.lista_clientes.insert(tk.END, f"{id} - {nome}")
    def selecionar_cliente(self, event=None):
        try:
            id, nome = self.lista_clientes.get(self.lista_clientes.curselection()).split(' - ')
            self.cliente_selecionado = {'id': int(id), 'nome': nome}; self.label_cliente_selecionado.config(text=f"Cliente: {nome}")
        except: pass
    def atualizar_lista_produtos(self, event=None):
        self.lista_produtos.delete(0, tk.END)
        for cod, desc, _, qtd in ctl.buscar_produto(self.produto_busca_var.get()): self.lista_produtos.insert(tk.END, f"{cod} - {desc} (Estoque: {qtd})")

class ClientesTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref; self.id_cliente_editando = None
        frame_cadastro = ttk.LabelFrame(self, text="Adicionar / Editar Cliente"); frame_cadastro.pack(fill='x', padx=10, pady=10)
        self.labels_map = {"nome": "Nome:", "telefone": "Telefone:", "aniversario": "Aniversário (dd/mm/aaaa):", "endereco": "Endereço:", "instagram": "Instagram:"}
        self.vars = {"nome": tk.StringVar(), "telefone": tk.StringVar(), "aniversario": tk.StringVar(), "endereco": None, "instagram": tk.StringVar()}
        for i, (key, label_text) in enumerate(self.labels_map.items()):
            ttk.Label(frame_cadastro, text=label_text).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            if key == "endereco":
                self.vars["endereco"] = tk.Text(frame_cadastro, height=3, width=40); self.vars["endereco"].grid(row=i, column=1, sticky='w', padx=5, pady=2)
            elif key == "telefone":
                vcmd = (self.register(self.format_telefone), '%P'); self.tel_entry = ttk.Entry(frame_cadastro, textvariable=self.vars["telefone"], width=40, validate='key', validatecommand=vcmd); self.tel_entry.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            else:
                entry = ttk.Entry(frame_cadastro, textvariable=self.vars[key], width=40); entry.grid(row=i, column=1, sticky='w', padx=5, pady=2)
        self.btn_salvar = ttk.Button(frame_cadastro, text="Salvar Novo", command=self.salvar_cliente); self.btn_salvar.grid(row=len(self.labels_map), column=1, sticky='e', padx=5, pady=10)
        ttk.Button(frame_cadastro, text="Novo/Limpar", command=self.limpar_campos).grid(row=len(self.labels_map), column=0, sticky='w', padx=5, pady=10)
        frame_lista = ttk.LabelFrame(self, text="Clientes Cadastrados (Duplo-clique para editar)"); frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('id', 'nome', 'telefone', 'aniversario'); self.tree_clientes = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree_clientes.heading(col, text=col.title()); self.tree_clientes.column(col, width=150)
        self.tree_clientes.pack(side=tk.LEFT, fill='both', expand=True); self.tree_clientes.bind("<Double-1>", self.carregar_cliente_para_edicao)
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_clientes.yview); self.tree_clientes.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill='y')
        self.atualizar_lista()
    def format_telefone(self, value_after_change):
        digits = "".join(filter(str.isdigit, value_after_change)); l = len(digits)
        if l > 11: return False
        if l > 10: f = f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif l > 6: f = f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        elif l > 2: f = f"({digits[:2]}) {digits[2:]}"
        else: f = f"({digits[:]}"
        self.vars["telefone"].set(f); self.tel_entry.icursor(tk.END); return True
    def limpar_campos(self):
        self.id_cliente_editando = None; self.btn_salvar.config(text="Salvar Novo")
        for key, var in self.vars.items():
            if key == "endereco": var.delete("1.0", tk.END)
            else: var.set("")
    def carregar_cliente_para_edicao(self, event):
        if not self.tree_clientes.selection(): return
        item_id = self.tree_clientes.selection()[0]; dados = self.tree_clientes.item(item_id, 'values')
        cliente_completo = next((c for c in ctl.listar_clientes() if str(c[0]) == str(dados[0])), None)
        if not cliente_completo: return
        self.limpar_campos(); self.id_cliente_editando = cliente_completo[0]
        self.vars["nome"].set(cliente_completo[1]); self.vars["telefone"].set(cliente_completo[2] or "")
        self.vars["aniversario"].set(cliente_completo[3] or ""); self.vars["endereco"].insert("1.0", cliente_completo[4] or "")
        self.vars["instagram"].set(cliente_completo[5] or ""); self.btn_salvar.config(text="Salvar Alterações")
    def salvar_cliente(self):
        dados = {key: var.get("1.0", "end-1c").strip() if key == "endereco" else var.get() for key, var in self.vars.items()}
        if not dados["nome"]: messagebox.showerror("Erro", "O nome do cliente é obrigatório."); return
        if self.id_cliente_editando: resultado = ctl.atualizar_cliente(self.app.usuario_id, self.id_cliente_editando, **dados)
        else: resultado = ctl.adicionar_cliente(self.app.usuario_id, **dados)
        messagebox.showinfo("Resultado", resultado)
        if "sucesso" in resultado: self.limpar_campos(); self.app.on_data_changed()
    def atualizar_lista(self):
        for i in self.tree_clientes.get_children(): self.tree_clientes.delete(i)
        for cliente in ctl.listar_clientes(): self.tree_clientes.insert('', tk.END, values=(cliente[0], cliente[1], cliente[2], cliente[3]))

class EstoqueTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
        frame_cadastro = ttk.LabelFrame(self, text="Novo Produto"); frame_cadastro.pack(fill='x', padx=10, pady=10)
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
        frame_lista = ttk.LabelFrame(self, text="Estoque Atual"); frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('codigo', 'descricao', 'compra', 'venda', 'qtd'); self.tree_estoque = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree_estoque.heading(col, text=col.title().replace("_", " "))
        self.tree_estoque.pack(fill='both', expand=True)
        self.atualizar_lista()
    def add_produto(self):
        try:
            codigo, desc = self.codigo_var.get(), self.desc_var.get()
            if not codigo or not desc: messagebox.showerror("Erro", "Código e Descrição são obrigatórios."); return
            resultado = ctl.adicionar_produto(self.app.usuario_id, codigo, desc, self.compra_var.get(), self.venda_var.get(), self.qtd_var.get())
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
        super().__init__(parent); self.parent_frame = parent; self.app = app_ref; self.ids_parcelas = ids_parcelas
        self.title("Liquidar Parcelas"); self.transient(parent); self.grab_set()
        frame = ttk.Frame(self, padding="20"); frame.pack(expand=True, fill='both')
        ttk.Label(frame, text=f"Liquidando {len(ids_parcelas)} parcela(s).", font=('Arial', 10, 'bold')).pack(pady=5)
        ttk.Label(frame, text=f"Valor total esperado: {ctl.format_currency(valor_total_esperado)}").pack(pady=5)
        ttk.Label(frame, text="Destino do Pagamento:").pack(pady=(10,0)); self.destino_var = tk.StringVar(value="Banco")
        ttk.Combobox(frame, textvariable=self.destino_var, values=['Banco', 'Caixa']).pack()
        ttk.Label(frame, text="Valor Líquido Recebido:").pack(pady=(10,0)); self.valor_liq_var = tk.DoubleVar(value=valor_total_esperado)
        ttk.Entry(frame, textvariable=self.valor_liq_var).pack()
        ttk.Button(frame, text="Confirmar Liquidação", command=self.liquidar).pack(pady=20)
        self.eval('tk::PlaceWindow . center') # <-- LINHA A SER ADICIONADA
    def liquidar(self):
        destino = self.destino_var.get()
        try: valor_liq = self.valor_liq_var.get()
        except tk.TclError: messagebox.showerror("Erro", "O valor recebido deve ser um número.", parent=self); return
        if not destino: messagebox.showerror("Erro", "Selecione um destino (Banco ou Caixa).", parent=self); return
        if valor_liq <= 0: messagebox.showerror("Erro", "O valor recebido deve ser maior que zero.", parent=self); return
        resultado = ctl.liquidar_parcelas(self.app.usuario_id, self.ids_parcelas, destino, valor_liq)
        messagebox.showinfo("Resultado", resultado, parent=self.parent_frame)
        if "sucesso" in resultado: self.app.on_data_changed(); self.destroy()
        self.eval('tk::PlaceWindow . center') # <-- LINHA A SER ADICIONADA

class ContasAReceberTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
        frame_filtros = ttk.LabelFrame(self, text="Filtros"); frame_filtros.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_filtros, text="Cliente:").pack(side=tk.LEFT, padx=5); self.cliente_var = tk.StringVar()
        self.cliente_combo = ttk.Combobox(frame_filtros, textvariable=self.cliente_var, width=30); self.cliente_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_filtros, text="Método de Pag.:").pack(side=tk.LEFT, padx=5); self.pagamento_var = tk.StringVar(value="Todos")
        pag_combo = ttk.Combobox(frame_filtros, textvariable=self.pagamento_var, values=['Todos', 'Dinheiro', 'PIX', 'Cartão de Débito', 'Cartão de Crédito', 'Crediário']); pag_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_filtros, text="Buscar", command=self.buscar_parcelas).pack(side=tk.LEFT, padx=10)
        frame_parcelas = ttk.LabelFrame(self, text="Parcelas Pendentes"); frame_parcelas.pack(fill='both', expand=True, padx=10, pady=5)
        colunas = ('p_id', 'v_id', 'cliente', 'parcela', 'valor', 'vencimento', 'metodo'); self.tree = ttk.Treeview(frame_parcelas, columns=colunas, show='headings', selectmode='extended')
        for col in colunas: self.tree.heading(col, text=col.replace('_', ' ').title()); self.tree.column(col, width=120, anchor='center')
        self.tree.heading('cliente', anchor='w'); self.tree.column('cliente', anchor='w')
        self.tree.heading('valor', anchor='e'); self.tree.column('valor', anchor='e')
        self.tree.pack(side=tk.LEFT, fill='both', expand=True); scrollbar = ttk.Scrollbar(frame_parcelas, orient=tk.VERTICAL, command=self.tree.yview); self.tree.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree.tag_configure('vencida', background='#FFCCCB')
        frame_liq = ttk.LabelFrame(self, text="Ações"); frame_liq.pack(fill='x', padx=10, pady=5)
        ttk.Button(frame_liq, text="LIQUIDAR PARCELA(S) SELECIONADA(S)", command=self.abrir_janela_liquidacao).pack(pady=10)
        self.carregar_clientes(); self.buscar_parcelas()
    def carregar_clientes(self):
        clientes = ctl.listar_clientes(); self.clientes_map = {f"{c[1]} (ID: {c[0]})": c[0] for c in clientes}
        self.cliente_combo['values'] = ["Todos"] + list(self.clientes_map.keys()); self.cliente_combo.set("Todos")
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
        super().__init__(parent); self.app = app_ref
        notebook = ttk.Notebook(self); notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.caixa_frame = CaixaFrame(notebook, self.app); self.banco_frame = BancoFrame(notebook, self.app)
        notebook.add(self.caixa_frame, text='Extrato do Caixa'); notebook.add(self.banco_frame, text='Extrato do Banco')
    def refresh_data(self): self.caixa_frame.refresh(); self.banco_frame.refresh()

class CaixaFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
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
            if valor > 0 and desc: ctl.add_transacao_financeira(self.app.usuario_id, 'Caixa', 'Saída', desc, valor); self.saida_valor_var.set(0.0); self.saida_desc_var.set(''); self.app.on_data_changed()
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
        super().__init__(parent); self.app = app_ref
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
            if valor > 0 and desc: ctl.add_transacao_financeira(self.app.usuario_id, 'Banco', 'Saída', desc, valor); self.saida_valor_var.set(0.0); self.saida_desc_var.set(''); self.app.on_data_changed()
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

class BaseReportSubTab(ttk.Frame):
    def __init__(self, parent, app_ref, title):
        super().__init__(parent); self.app = app_ref; self.title = title
        self.headers = []; self.data_for_pdf = []
        self.filter_frame = ttk.LabelFrame(self, text="Filtros"); self.filter_frame.pack(fill='x', padx=10, pady=5)
        result_frame = ttk.Frame(self); result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(result_frame, show='headings');
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview); self.tree.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill='y')
        self.setup_filters()
    def setup_filters(self): raise NotImplementedError
    def buscar_dados(self): raise NotImplementedError
    def gerar_pdf(self):
        if not self.data_for_pdf: messagebox.showwarning("Atenção", "Gere um relatório primeiro."); return
        titulo = self.title; headers = self.headers; data = self.data_for_pdf
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"{titulo}.pdf")
        resultado = ctl.gerar_pdf_generico(filepath, titulo, headers, data)
        messagebox.showinfo("Gerar PDF", resultado)
    def popular_treeview(self, headers, data, format_map=None):
        self.headers = headers; self.data_for_pdf = [list(row) for row in data]
        if format_map is None: format_map = {}
        self.tree['columns'] = headers
        for i in self.tree.get_children(): self.tree.delete(i)
        for header in headers: self.tree.heading(header, text=header); self.tree.column(header, anchor='center', width=120)
        for i, row in enumerate(data):
            formatted_row = list(row)
            for col_index, format_func in format_map.items():
                if col_index < len(formatted_row):
                    self.data_for_pdf[i][col_index] = format_func(row[col_index])
                    formatted_row[col_index] = format_func(row[col_index])
            self.tree.insert('', 'end', values=formatted_row)

class RelatorioClientesSubTab(BaseReportSubTab):
    def setup_filters(self):
        ttk.Button(self.filter_frame, text="Gerar PDF", command=self.gerar_pdf).pack(side=tk.RIGHT, padx=5)
        self.buscar_dados()
    def buscar_dados(self):
        headers = ['ID', 'Nome', 'Telefone', 'Aniversário', 'Endereço', 'Instagram']
        data = ctl.listar_clientes(); self.popular_treeview(headers, data)

class RelatorioEstoqueSubTab(BaseReportSubTab):
    def setup_filters(self):
        self.baixo_estoque_var = tk.BooleanVar(); ttk.Checkbutton(self.filter_frame, text="Apenas baixo estoque (<=10)", variable=self.baixo_estoque_var, command=self.buscar_dados).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.filter_frame, text="Gerar PDF", command=self.gerar_pdf).pack(side=tk.RIGHT, padx=5)
        self.buscar_dados()
    def buscar_dados(self):
        headers = ['Código', 'Descrição', 'Qtd', 'Vlr. Compra', 'Vlr. Venda']
        data = ctl.relatorio_estoque_filtrado(baixo_estoque=self.baixo_estoque_var.get())
        self.popular_treeview(headers, data, format_map={3: ctl.format_currency, 4: ctl.format_currency})

# Em app.py, substitua esta classe:

class RelatorioVendasSubTab(BaseReportSubTab):
    def setup_filters(self):
        ttk.Label(self.filter_frame, text="De:").pack(side=tk.LEFT, padx=5); self.dt_inicio = DateEntry(self.filter_frame, width=12, date_pattern='yyyy-mm-dd'); self.dt_inicio.pack(side=tk.LEFT)
        ttk.Label(self.filter_frame, text="Até:").pack(side=tk.LEFT, padx=5); self.dt_fim = DateEntry(self.filter_frame, width=12, date_pattern='yyyy-mm-dd'); self.dt_fim.pack(side=tk.LEFT)
        
        # Filtro por cliente
        ttk.Label(self.filter_frame, text="Cliente:").pack(side=tk.LEFT, padx=5); self.cliente_var = tk.StringVar(value="Todos")
        self.cliente_combo = ttk.Combobox(self.filter_frame, textvariable=self.cliente_var, width=25, state="readonly"); self.cliente_combo.pack(side=tk.LEFT, padx=5)

        # NOVO FILTRO DE STATUS
        ttk.Label(self.filter_frame, text="Status:").pack(side=tk.LEFT, padx=5); self.status_var = tk.StringVar(value="Todas")
        ttk.Combobox(self.filter_frame, textvariable=self.status_var, values=['Todas', 'Ativa', 'Estornada'], width=10, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Button(self.filter_frame, text="Buscar", command=self.buscar_dados).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.filter_frame, text="Gerar PDF", command=self.gerar_pdf).pack(side=tk.RIGHT, padx=5)
        
        self.carregar_clientes(); self.buscar_dados()

    def carregar_clientes(self):
        clientes = ctl.listar_clientes(); self.clientes_map = {f"{c[1]} (ID: {c[0]})": c[0] for c in clientes}
        self.cliente_combo['values'] = ["Todos"] + list(self.clientes_map.keys())
        
    def buscar_dados(self):
        headers = ['ID Venda', 'Data', 'Cliente', 'Pagamento', 'Nº Parc.', 'Valor Total', 'Status']
        cliente_id = self.clientes_map.get(self.cliente_var.get()) if self.cliente_var.get() != "Todos" else None
        status_filtro = self.status_var.get() # Pega o valor do novo filtro
        
        # A função de busca no controller já retorna o status, aqui só filtramos o resultado
        todas_as_vendas = ctl.relatorio_vendas_filtrado(self.dt_inicio.get_date(), self.dt_fim.get_date(), cliente_id)
        
        if status_filtro == 'Todas':
            data = todas_as_vendas
        else:
            data = [venda for venda in todas_as_vendas if venda[6] == status_filtro] # venda[6] é a coluna de status

        self.tree.tag_configure('estornada', foreground='gray', font=('Arial', 9, 'overstrike'))
        format_map = {5: ctl.format_currency}
        
        # Lógica de popular a Treeview
        self.headers = headers
        self.data_for_pdf = [list(row) for row in data]
        self.tree['columns'] = headers
        for i in self.tree.get_children(): self.tree.delete(i)
        for header in headers: self.tree.heading(header, text=header); self.tree.column(header, anchor='center', width=120)
        
        for i, row in enumerate(data):
            formatted_row = list(row)
            tag = ('estornada',) if row[6] == 'Estornada' else ()
            for col_index, format_func in format_map.items():
                if col_index < len(formatted_row):
                    self.data_for_pdf[i][col_index] = format_func(row[col_index])
                    formatted_row[col_index] = format_func(row[col_index])
            self.tree.insert('', 'end', values=formatted_row, tags=tag)

class RelatorioContasAReceberSubTab(BaseReportSubTab):
    def setup_filters(self):
        ttk.Label(self.filter_frame, text="Cliente:").pack(side=tk.LEFT, padx=5); self.cliente_var = tk.StringVar(value="Todos")
        self.cliente_combo = ttk.Combobox(self.filter_frame, textvariable=self.cliente_var, width=25); self.cliente_combo.pack(side=tk.LEFT, padx=5)
        self.vencidas_var = tk.BooleanVar(); ttk.Checkbutton(self.filter_frame, text="Apenas vencidas", variable=self.vencidas_var, command=self.buscar_dados).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.filter_frame, text="Gerar PDF", command=self.gerar_pdf).pack(side=tk.RIGHT, padx=5)
        self.carregar_clientes(); self.buscar_dados()
    def carregar_clientes(self):
        clientes = ctl.listar_clientes(); self.clientes_map = {f"{c[1]} (ID: {c[0]})": c[0] for c in clientes}
        self.cliente_combo['values'] = ["Todos"] + list(self.clientes_map.keys())
    def buscar_dados(self):
        headers = ['Cliente', 'ID Venda', 'Nº Parcela', 'Total Parc.', 'Vencimento', 'Valor Parcela']
        cliente_id = self.clientes_map.get(self.cliente_var.get()) if self.cliente_var.get() != "Todos" else None
        data = ctl.relatorio_contas_a_receber(cliente_id, self.vencidas_var.get())
        self.popular_treeview(headers, data, format_map={5: ctl.format_currency})

class RelatorioExtratosSubTab(BaseReportSubTab):
    def setup_filters(self):
        ttk.Label(self.filter_frame, text="De:").pack(side=tk.LEFT, padx=5); self.dt_inicio = DateEntry(self.filter_frame, width=12, date_pattern='yyyy-mm-dd'); self.dt_inicio.pack(side=tk.LEFT)
        ttk.Label(self.filter_frame, text="Até:").pack(side=tk.LEFT, padx=5); self.dt_fim = DateEntry(self.filter_frame, width=12, date_pattern='yyyy-mm-dd'); self.dt_fim.pack(side=tk.LEFT)
        ttk.Label(self.filter_frame, text="Conta:").pack(side=tk.LEFT, padx=5); self.conta_var = tk.StringVar(value="Banco")
        ttk.Combobox(self.filter_frame, textvariable=self.conta_var, values=['Banco', 'Caixa']).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.filter_frame, text="Buscar", command=self.buscar_dados).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.filter_frame, text="Gerar PDF", command=self.gerar_pdf).pack(side=tk.RIGHT, padx=5)
        self.buscar_dados()
    def buscar_dados(self):
        headers = ['Data', 'Descrição', 'Natureza', 'Valor']
        data = ctl.relatorio_extratos(self.conta_var.get(), self.dt_inicio.get_date(), self.dt_fim.get_date())
        self.popular_treeview(headers, data, format_map={3: ctl.format_currency})

class RelatoriosTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
        notebook = ttk.Notebook(self); notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.rel_clientes = RelatorioClientesSubTab(notebook, app_ref, "Lista de Clientes")
        self.rel_estoque = RelatorioEstoqueSubTab(notebook, app_ref, "Relatório de Estoque")
        self.rel_vendas = RelatorioVendasSubTab(notebook, app_ref, "Relatório de Vendas")
        self.rel_contas_receber = RelatorioContasAReceberSubTab(notebook, app_ref, "Relatório de Contas a Receber")
        self.rel_extratos = RelatorioExtratosSubTab(notebook, app_ref, "Extratos Financeiros")
        notebook.add(self.rel_clientes, text='Clientes'); notebook.add(self.rel_estoque, text='Estoque')
        notebook.add(self.rel_vendas, text='Vendas'); notebook.add(self.rel_contas_receber, text='Contas a Receber')
        notebook.add(self.rel_extratos, text='Extratos Financeiros')
    def refresh_reports(self):
        self.rel_clientes.buscar_dados(); self.rel_estoque.buscar_dados(); self.rel_vendas.buscar_dados()
        self.rel_contas_receber.buscar_dados(); self.rel_extratos.buscar_dados()

class GerenciarUsuariosFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
        frame_cadastro = ttk.LabelFrame(self, text="Adicionar Novo Usuário"); frame_cadastro.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_cadastro, text="Nome de Usuário:").grid(row=0, column=0, sticky='w', padx=5, pady=2); self.user_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.user_var, width=40).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_cadastro, text="Nome Completo:").grid(row=1, column=0, sticky='w', padx=5, pady=2); self.nome_completo_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.nome_completo_var, width=40).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(frame_cadastro, text="Senha:").grid(row=2, column=0, sticky='w', padx=5, pady=2); self.pass_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.pass_var, show="*", width=40).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(frame_cadastro, text="Confirmar Senha:").grid(row=3, column=0, sticky='w', padx=5, pady=2); self.confirm_pass_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.confirm_pass_var, show="*", width=40).grid(row=3, column=1, padx=5, pady=2)
        ttk.Button(frame_cadastro, text="Salvar Novo Usuário", command=self.salvar_usuario).grid(row=4, column=1, sticky='e', padx=5, pady=10)
        frame_lista = ttk.LabelFrame(self, text="Usuários do Sistema"); frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        ttk.Button(frame_lista, text="Deletar Selecionado", command=self.deletar_usuario_selecionado).pack(pady=5, anchor='ne')
        colunas = ('id', 'username', 'nome_completo'); self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.replace('_', ' ').title())
        self.tree.pack(fill='both', expand=True)
        self.atualizar_lista_usuarios()
    def salvar_usuario(self):
        user, nome, pwd, confirm_pwd = self.user_var.get(), self.nome_completo_var.get(), self.pass_var.get(), self.confirm_pass_var.get()
        if not all([user, nome, pwd]): messagebox.showerror("Erro", "Todos os campos são obrigatórios."); return
        if pwd != confirm_pwd: messagebox.showerror("Erro", "As senhas não coincidem."); return
        resultado = ctl.criar_usuario(self.app.usuario_id, user, pwd, nome)
        messagebox.showinfo("Resultado", resultado)
        if "sucesso" in resultado: self.user_var.set(''); self.nome_completo_var.set(''); self.pass_var.set(''); self.confirm_pass_var.set(''); self.atualizar_lista_usuarios()
    def deletar_usuario_selecionado(self):
        try:
            selecionado = self.tree.selection()[0]
            id_usuario, username = self.tree.item(selecionado, 'values')[0], self.tree.item(selecionado, 'values')[1]
            if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o usuário '{username}'?\nEsta ação não pode ser desfeita."):
                resultado = ctl.deletar_usuario(self.app.usuario_id, int(id_usuario))
                messagebox.showinfo("Resultado", resultado); self.atualizar_lista_usuarios()
        except IndexError: messagebox.showwarning("Atenção", "Selecione um usuário na lista para deletar.")
    def atualizar_lista_usuarios(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for usuario in ctl.listar_usuarios(): self.tree.insert('', 'end', values=usuario)

class EstornarVendaFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
        frame_botoes = ttk.Frame(self); frame_botoes.pack(pady=10)
        ttk.Button(frame_botoes, text="Estornar Venda Selecionada", command=self.estornar_venda).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar Lista", command=self.atualizar_lista_vendas).pack(side=tk.LEFT, padx=5)
        frame_lista = ttk.LabelFrame(self, text="Selecione uma Venda Ativa para Estornar"); frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('id', 'data', 'cliente', 'valor'); self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.title())
        self.tree.pack(fill='both', expand=True, side=tk.LEFT); scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill='y')
        self.atualizar_lista_vendas()
    def atualizar_lista_vendas(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for venda in ctl.get_vendas_ativas():
            id_v, data, cliente, valor = venda; data_fmt = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.tree.insert('', 'end', values=(id_v, data_fmt, cliente, ctl.format_currency(valor)))
    def estornar_venda(self):
        try:
            selecionado = self.tree.selection()[0]; venda_id = self.tree.item(selecionado, 'values')[0]
            senha = simpledialog.askstring("Senha", "Ação irreversível.\nDigite sua senha de login para confirmar:", show='*', parent=self)
            if senha is None: return
            user_id = ctl.verificar_login(self.app.username, senha)
            if not user_id: messagebox.showerror("Erro", "Senha incorreta!"); return
            if messagebox.askyesno("Confirmar Estorno", f"Tem certeza que deseja estornar a Venda #{venda_id}?\n\n- O estoque será devolvido.\n- A venda será marcada como 'Estornada'.\n- Lançamentos financeiros serão revertidos."):
                resultado = ctl.estornar_venda_completa(self.app.usuario_id, venda_id)
                messagebox.showinfo("Resultado", resultado);
                if "sucesso" in resultado: self.app.on_data_changed()
        except IndexError: messagebox.showwarning("Atenção", "Selecione uma venda na lista para estornar.")

class AdminTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent); self.app = app_ref
        notebook = ttk.Notebook(self); notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.gerenciar_usuarios_frame = GerenciarUsuariosFrame(notebook, self.app)
        self.estornar_venda_frame = EstornarVendaFrame(notebook, self.app)
        notebook.add(self.gerenciar_usuarios_frame, text='Gerenciar Usuários')
        notebook.add(self.estornar_venda_frame, text='Estornar Venda')
    def refresh_admin_views(self):
        self.gerenciar_usuarios_frame.atualizar_lista_usuarios()
        self.estornar_venda_frame.atualizar_lista_vendas()

class SobreTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        container = ttk.Frame(self); container.pack(expand=True)
        info_frame = ttk.LabelFrame(container, text="Sobre o Sistema"); info_frame.pack(padx=20, pady=20)
        nome_autor = "Antonio Junior"; email = "alvs.junior@gmail.com"; linkedin_url = "https://www.linkedin.com/euantoniojr"
        ttk.Label(info_frame, text="Este sistema foi desenvolvido por:", font=('Arial', 11)).pack(pady=(10, 2))
        ttk.Label(info_frame, text=nome_autor, font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        ttk.Label(info_frame, text=f"Email: {email}").pack(pady=5, anchor='w')
        link_font = font.Font(family='Arial', size=10, underline=True); link_label = ttk.Label(info_frame, text="LinkedIn", foreground="blue", cursor="hand2", font=link_font)
        link_label.pack(pady=10, anchor='w'); link_label.bind("<Button-1>", lambda e: self.open_link(linkedin_url))
    def open_link(self, url): webbrowser.open_new(url)

# =================================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# =================================================================================
class App(tk.Tk):
    def __init__(self, login_info):
        super().__init__(); self.usuario_id, self.username = login_info['id'], login_info['user']
        self.title(f"Sistema de Vendas - Usuário: {self.username}"); self.geometry("1280x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        notebook = ttk.Notebook(self); notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.vendas_frame = VendasTab(notebook, self)
        self.contas_receber_frame = ContasAReceberTab(notebook, self)
        self.financeiro_frame = FinanceiroTab(notebook, self)
        self.clientes_frame = ClientesTab(notebook, self)
        self.estoque_frame = EstoqueTab(notebook, self)
        self.relatorios_frame = RelatoriosTab(notebook, self)
        self.admin_frame = AdminTab(notebook, self)
        self.sobre_frame = SobreTab(notebook)
        notebook.add(self.vendas_frame, text='Vendas'); notebook.add(self.contas_receber_frame, text='Contas a Receber')
        notebook.add(self.financeiro_frame, text='Financeiro (Extratos)'); notebook.add(self.clientes_frame, text='Clientes')
        notebook.add(self.estoque_frame, text='Estoque'); notebook.add(self.relatorios_frame, text='Relatórios')
        notebook.add(self.admin_frame, text='Administração'); notebook.add(self.sobre_frame, text='Sobre')
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Você tem certeza que quer sair?"): ctl.desconectar(); self.destroy()
    def on_data_changed(self):
        self.estoque_frame.atualizar_lista(); self.contas_receber_frame.carregar_clientes()
        self.contas_receber_frame.buscar_parcelas(); self.clientes_frame.atualizar_lista()
        self.vendas_frame.atualizar_lista_clientes(); self.financeiro_frame.refresh_data()
        self.admin_frame.refresh_admin_views()
        self.relatorios_frame.refresh_reports()

# =================================================================================
# LÓGICA DE INICIALIZAÇÃO PRINCIPAL
# =================================================================================
if __name__ == "__main__":
    ctl.conectar()
    login = LoginWindow(); login.mainloop()
    if login.user_id:
        login_info = {'id': login.user_id, 'user': login.user_var.get()}
        app = App(login_info=login_info); app.mainloop()
    elif 'ctl' in locals() and ctl._conn is not None:
        ctl.desconectar(); print("Login cancelado. Encerrando o programa.")