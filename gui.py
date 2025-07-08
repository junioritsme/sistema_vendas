# arquivo: gui.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
from tkcalendar import DateEntry
import controllers as ctl
import datetime
import webbrowser # Módulo para abrir links no navegador

# =================================================================================
# DEFINIÇÃO DE TODAS AS CLASSES COMPONENTES (ABAS E JANELAS)
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
        self.tree_carrinho.heading('codigo', text='Código')
        self.tree_carrinho.heading('descricao', text='Descrição')
        self.tree_carrinho.heading('qtd', text='Qtd')
        self.tree_carrinho.heading('valor_unit', text='Vlr. Unit.')
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
                                             values=['Dinheiro', 'PIX', 'Cartão de Débito', 'Cartão de Crédito'])
        self.metodo_pag_combo.grid(row=0, column=1, padx=5, pady=5)
        self.metodo_pag_combo.bind('<<ComboboxSelected>>', self.toggle_parcelas)
        self.label_parcelas = ttk.Label(frame_pagamento, text="Parcelas:")
        self.parcelas_var = tk.IntVar(value=1)
        self.parcelas_spinbox = ttk.Spinbox(frame_pagamento, from_=1, to=12, textvariable=self.parcelas_var, width=5)
        ttk.Label(frame_pagamento, text="Desconto (R$):").grid(row=1, column=0, padx=5, pady=5)
        self.desconto_var = tk.DoubleVar(value=0.0)
        desconto_entry = ttk.Entry(frame_pagamento, textvariable=self.desconto_var, width=10)
        desconto_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        desconto_entry.bind('<KeyRelease>', self.atualizar_tree_carrinho)
        self.label_valor_total = ttk.Label(frame_pagamento, text="Total: R$ 0,00", font=('Arial', 12, 'bold'))
        self.label_valor_total.grid(row=1, column=2, padx=20, pady=5)
        ttk.Button(frame_pagamento, text="FINALIZAR VENDA", command=self.finalizar_venda).grid(row=0, rowspan=2, column=3, padx=20, pady=5, ipady=10)
        self.atualizar_lista_clientes()
        self.atualizar_lista_produtos()
    def add_ao_carrinho(self):
        try:
            selecionado = self.lista_produtos.get(self.lista_produtos.curselection())
            codigo, _ = selecionado.split(' - ', 1)
            produto_info = next((p for p in ctl.buscar_produto(codigo) if p[0] == codigo), None)
            if not produto_info: messagebox.showerror("Erro", "Produto não encontrado."); return
            quantidade = self.qtd_produto_var.get()
            if quantidade > produto_info[3]: messagebox.showwarning("Estoque", f"Estoque insuficiente. Disponível: {produto_info[3]}"); return
            item_existente = next((item for item in self.carrinho if item['codigo'] == codigo), None)
            if item_existente:
                item_existente['quantidade'] += quantidade
            else:
                self.carrinho.append({'codigo': codigo, 'descricao': produto_info[1], 'quantidade': quantidade, 'valor_venda': produto_info[2]})
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
        except tk.TclError:
            desconto = 0.0
        total_final = total_bruto - desconto
        self.label_valor_total.config(text=f"Total: {ctl.format_currency(total_final)}")
    def finalizar_venda(self):
        if not self.cliente_selecionado: messagebox.showerror("Erro", "Nenhum cliente selecionado."); return
        if not self.carrinho: messagebox.showerror("Erro", "Carrinho está vazio."); return
        if not self.metodo_pag_var.get(): messagebox.showerror("Erro", "Selecione um método de pagamento."); return
        cliente_id = self.cliente_selecionado['id']
        metodo = self.metodo_pag_var.get()
        parcelas = self.parcelas_var.get() if metodo == 'Cartão de Crédito' else 1
        desconto = self.desconto_var.get()
        resultado = ctl.registrar_venda(cliente_id, metodo, parcelas, desconto, self.carrinho)
        messagebox.showinfo("Resultado", resultado)
        if "sucesso" in resultado:
            self.carrinho.clear()
            self.cliente_selecionado = None
            self.label_cliente_selecionado.config(text="Nenhum cliente selecionado.")
            self.desconto_var.set(0.0)
            self.atualizar_tree_carrinho()
            self.atualizar_lista_produtos()
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
    def toggle_parcelas(self, event=None):
        if self.metodo_pag_var.get() == 'Cartão de Crédito':
            self.label_parcelas.grid(row=0, column=4, padx=(10,0)); self.parcelas_spinbox.grid(row=0, column=5, padx=(0,10))
        else:
            self.label_parcelas.grid_remove(); self.parcelas_spinbox.grid_remove()

class ClientesTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_cadastro = ttk.LabelFrame(self, text="Novo Cliente")
        frame_cadastro.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.nome_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.nome_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_cadastro, text="Telefone:").grid(row=1, column=0, padx=5, pady=5)
        self.tel_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.tel_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(frame_cadastro, text="Instagram:").grid(row=2, column=0, padx=5, pady=5)
        self.insta_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.insta_var, width=40).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame_cadastro, text="Adicionar Cliente", command=self.add_cliente).grid(row=3, column=1, sticky='e', padx=5, pady=10)
        frame_lista = ttk.LabelFrame(self, text="Clientes Cadastrados")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('id', 'nome', 'telefone', 'instagram')
        self.tree_clientes = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        self.tree_clientes.heading('id', text='ID'); self.tree_clientes.heading('nome', text='Nome')
        self.tree_clientes.heading('telefone', text='Telefone'); self.tree_clientes.heading('instagram', text='Instagram')
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
        ttk.Label(frame_cadastro, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.codigo_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.codigo_var).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Descrição:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.desc_var = tk.StringVar()
        ttk.Entry(frame_cadastro, textvariable=self.desc_var, width=50).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Valor Compra:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.compra_var = tk.DoubleVar()
        ttk.Entry(frame_cadastro, textvariable=self.compra_var).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Valor Venda:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.venda_var = tk.DoubleVar()
        ttk.Entry(frame_cadastro, textvariable=self.venda_var).grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_cadastro, text="Quantidade:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.qtd_var = tk.IntVar()
        ttk.Entry(frame_cadastro, textvariable=self.qtd_var).grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(frame_cadastro, text="Adicionar Produto", command=self.add_produto).grid(row=5, column=1, sticky='e', padx=5, pady=10)
        frame_lista = ttk.LabelFrame(self, text="Estoque Atual")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('codigo', 'descricao', 'compra', 'venda', 'qtd')
        self.tree_estoque = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        self.tree_estoque.heading('codigo', text='Código'); self.tree_estoque.heading('descricao', text='Descrição')
        self.tree_estoque.heading('compra', text='Vlr. Compra'); self.tree_estoque.heading('venda', text='Vlr. Venda')
        self.tree_estoque.heading('qtd', text='Quantidade')
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

# Em gui.py, substitua apenas esta classe

class RelatorioVendasTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.dados_para_pdf = []
        self.resumo_para_pdf = ""
        frame_filtros = ttk.LabelFrame(self, text="Filtros")
        frame_filtros.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5, pady=5)
        self.data_inicio = DateEntry(frame_filtros, date_pattern='yyyy-mm-dd', width=12)
        self.data_inicio.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5, pady=5)
        self.data_fim = DateEntry(frame_filtros, date_pattern='yyyy-mm-dd', width=12)
        self.data_fim.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(frame_filtros, text="Pagamento:").grid(row=0, column=4, padx=5, pady=5)
        self.pag_var = tk.StringVar(value='Todos')
        ttk.Combobox(frame_filtros, textvariable=self.pag_var, values=['Todos', 'Dinheiro', 'PIX', 'Cartão de Débito', 'Cartão de Crédito']).grid(row=0, column=5)
        ttk.Button(frame_filtros, text="Gerar Relatório", command=self.gerar_relatorio).grid(row=0, column=6, padx=20, pady=5)
        ttk.Button(frame_filtros, text="Gerar PDF", command=self.gerar_pdf).grid(row=0, column=7, padx=5, pady=5)
        frame_resultados = ttk.LabelFrame(self, text="Resultados")
        frame_resultados.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('data', 'cliente', 'produto', 'qtd', 'venda', 'desconto', 'pagamento', 'parcelas', 'status')
        self.tree_relatorio = ttk.Treeview(frame_resultados, columns=colunas, show='headings')
        for col in colunas: self.tree_relatorio.heading(col, text=col.replace('_', ' ').title())
        self.tree_relatorio.column('status', width=80, anchor='center')
        self.tree_relatorio.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame_resultados, orient=tk.VERTICAL, command=self.tree_relatorio.yview)
        self.tree_relatorio.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.tree_relatorio.tag_configure('estornada', foreground='gray', font=('Arial', 9, 'overstrike'))
        self.label_resumo = ttk.Label(self, text="", font=('Arial', 11, 'bold'))
        self.label_resumo.pack(pady=10)

    def gerar_relatorio(self):
        for i in self.tree_relatorio.get_children(): self.tree_relatorio.delete(i)
        
        di = self.data_inicio.get_date().strftime('%Y-%m-%d')
        df = self.data_fim.get_date().strftime('%Y-%m-%d')
        relatorio = ctl.relatorio_vendas(di, df, self.pag_var.get())
        
        total_vendido, total_custo, total_desconto = 0, 0, 0
        self.dados_para_pdf.clear()

        vendas_agrupadas = {}
        # data, cliente, produto, qtd, vlr_compra, vlr_venda, desconto, pagamento, parcelas, status
        for row in relatorio:
            id_venda = (row[0], row[1], row[6], row[7], row[8], row[9]) # Chave de agrupamento
            if id_venda not in vendas_agrupadas:
                vendas_agrupadas[id_venda] = {'itens': [], 'desconto': row[6], 'pagamento': row[7], 'parcelas': row[8], 'status': row[9]}
            vendas_agrupadas[id_venda]['itens'].append({'produto': row[2], 'qtd': row[3], 'vlr_compra': row[4], 'vlr_venda': row[5]})

        for (data, cliente, desconto, pagamento, parcelas, status), venda_info in vendas_agrupadas.items():
            tag = ('estornada',) if status == 'Estornada' else ()
            
            valor_total_venda = sum(item['vlr_venda'] * item['qtd'] for item in venda_info['itens'])
            custo_total_venda = sum(item['vlr_compra'] * item['qtd'] for item in venda_info['itens'])
            
            if status == 'Ativa':
                total_vendido += valor_total_venda
                total_custo += custo_total_venda
                total_desconto += desconto

            for i, item in enumerate(venda_info['itens']):
                desconto_item = desconto if i == 0 else 0
                data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                values = (data_formatada, cliente, item['produto'], item['qtd'],
                          ctl.format_currency(item['vlr_venda'] * item['qtd']),
                          ctl.format_currency(desconto_item), pagamento, parcelas, status)
                self.tree_relatorio.insert('', tk.END, values=values, tags=tag)
            
            # --- ALTERAÇÃO AQUI: Passando os dados corretos para o PDF ---
            data_formatada_pdf = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            self.dados_para_pdf.append({
                "data": data_formatada_pdf, "cliente": cliente, 
                "produto": ', '.join([i['produto'] for i in venda_info['itens']]),
                "qtd": sum(i['qtd'] for i in venda_info['itens']),
                "venda_total": valor_total_venda - desconto,
                "pagamento": pagamento, "parcelas": parcelas, "status": status
            })

        lucro_bruto = (total_vendido - total_desconto) - total_custo
        self.resumo_para_pdf = f"Total Bruto Vendido (Ativas): {ctl.format_currency(total_vendido)}\nTotal Descontos (Ativas): {ctl.format_currency(total_desconto)}\n" \
                               f"Total Líquido Vendido (Ativas): {ctl.format_currency(total_vendido - total_desconto)}\n" \
                               f"Custo Total dos Produtos (Ativas): {ctl.format_currency(total_custo)}\nLucro Bruto (Ativas): {ctl.format_currency(lucro_bruto)}"
        self.label_resumo.config(text=self.resumo_para_pdf.replace('\n', '   |   '))

    def gerar_pdf(self):
        # --- ALTERAÇÃO AQUI: Removemos o aviso e chamamos a função ---
        if not self.dados_para_pdf:
            messagebox.showwarning("Atenção", "Gere um relatório primeiro antes de exportar para PDF.")
            return
        resultado = ctl.gerar_pdf_relatorio(self.dados_para_pdf, self.data_inicio.get_date().strftime('%d/%m/%Y'),
                                            self.data_fim.get_date().strftime('%d/%m/%Y'), self.resumo_para_pdf)
        messagebox.showinfo("PDF", resultado)

class CaixaFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_saldo = ttk.Frame(self)
        frame_saldo.pack(fill='x', padx=10, pady=5)
        self.label_saldo = ttk.Label(frame_saldo, text="Saldo do Caixa: R$ 0,00", font=('Arial', 14, 'bold'))
        self.label_saldo.pack()
        frame_saida = ttk.LabelFrame(self, text="Registrar Saída do Caixa")
        frame_saida.pack(fill='x', padx=10, pady=10)
        ttk.Label(frame_saida, text="Valor (R$):").grid(row=0, column=0)
        self.saida_valor_var = tk.DoubleVar()
        ttk.Entry(frame_saida, textvariable=self.saida_valor_var).grid(row=0, column=1)
        ttk.Label(frame_saida, text="Descrição:").grid(row=0, column=2)
        self.saida_desc_var = tk.StringVar()
        ttk.Entry(frame_saida, textvariable=self.saida_desc_var, width=40).grid(row=0, column=3)
        ttk.Button(frame_saida, text="Registrar Saída", command=self.registrar_saida).grid(row=0, column=4, padx=10)
        frame_lista = ttk.LabelFrame(self, text="Histórico do Caixa (Apenas Transações Ativas)")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('data', 'descricao', 'valor', 'natureza')
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.title())
        self.tree.pack(fill='both', expand=True)
        self.refresh()
    def registrar_saida(self):
        try:
            valor = self.saida_valor_var.get()
            desc = self.saida_desc_var.get()
            if valor > 0 and desc:
                ctl.add_transacao_financeira('Caixa', 'Saída', desc, valor)
                self.saida_valor_var.set(0.0)
                self.saida_desc_var.set('')
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
        saldo = ctl.get_saldo('Caixa')
        self.label_saldo.config(text=f"Saldo do Caixa: {ctl.format_currency(saldo)}")

class BancoFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_saldo = ttk.Frame(self)
        frame_saldo.pack(fill='x', padx=10, pady=5)
        self.label_saldo = ttk.Label(frame_saldo, text="Saldo do Banco: R$ 0,00", font=('Arial', 14, 'bold'))
        self.label_saldo.pack()
        frame_pendentes = ttk.LabelFrame(self, text="Vendas Pendentes de Conciliação")
        frame_pendentes.pack(fill='x', padx=10, pady=10)
        colunas_pend = ('id', 'data', 'cliente', 'valor', 'metodo')
        self.tree_pendentes = ttk.Treeview(frame_pendentes, columns=colunas_pend, show='headings', height=5)
        for col in colunas_pend: self.tree_pendentes.heading(col, text=col.title())
        self.tree_pendentes.pack(fill='x')
        ttk.Button(frame_pendentes, text="Conciliar Venda Selecionada", command=self.conciliar).pack(pady=5)
        frame_hist = ttk.LabelFrame(self, text="Histórico do Banco (Apenas Transações Ativas)")
        frame_hist.pack(fill='both', expand=True, padx=10, pady=10)
        colunas_hist = ('data', 'descricao', 'valor', 'natureza')
        self.tree_hist = ttk.Treeview(frame_hist, columns=colunas_hist, show='headings')
        for col in colunas_hist: self.tree_hist.heading(col, text=col.title())
        self.tree_hist.pack(fill='both', expand=True)
        self.refresh()
    def conciliar(self):
        try:
            selecionado = self.tree_pendentes.selection()[0]
            venda_id = self.tree_pendentes.item(selecionado, 'values')[0]
            valor_bruto_str = self.tree_pendentes.item(selecionado, 'values')[3]
            valor_liquido = simpledialog.askfloat("Conciliação", f"Venda #{venda_id} - Valor Bruto: {valor_bruto_str}\n\nDigite o valor líquido recebido:", parent=self)
            if valor_liquido is not None:
                resultado = ctl.conciliar_venda(venda_id, valor_liquido)
                messagebox.showinfo("Resultado", resultado)
                self.app.on_data_changed()
        except IndexError:
            messagebox.showwarning("Atenção", "Selecione uma venda pendente para conciliar.")
    def refresh(self):
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        for data, desc, valor, natureza in ctl.get_transacoes('Banco'):
            valor_fmt = ctl.format_currency(valor)
            if natureza != 'Entrada': valor_fmt = f"- {valor_fmt}"
            data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.tree_hist.insert('', 'end', values=(data_formatada, desc, valor_fmt, natureza))
        saldo_banco = ctl.get_saldo('Banco')
        self.label_saldo.config(text=f"Saldo do Banco: {ctl.format_currency(saldo_banco)}")
        for i in self.tree_pendentes.get_children(): self.tree_pendentes.delete(i)
        for id_v, data, cliente, valor, metodo in ctl.get_vendas_pendentes():
            data_formatada = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
            self.tree_pendentes.insert('', 'end', values=(id_v, data_formatada, cliente, ctl.format_currency(valor), metodo))

class FinanceiroTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.caixa_frame = CaixaFrame(notebook, self.app)
        self.banco_frame = BancoFrame(notebook, self.app)
        notebook.add(self.caixa_frame, text='Caixa')
        notebook.add(self.banco_frame, text='Banco')
    def refresh_data(self):
        self.caixa_frame.refresh()
        self.banco_frame.refresh()

class EditClientesFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        ttk.Button(self, text="Editar Cliente Selecionado", command=self.abrir_janela_edicao).pack(pady=10)
        colunas = ('id', 'nome', 'telefone', 'instagram')
        self.tree = ttk.Treeview(self, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.title())
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.atualizar_lista_clientes_admin()
    def atualizar_lista_clientes_admin(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for cliente in ctl.listar_clientes(): self.tree.insert('', tk.END, values=cliente)
    def abrir_janela_edicao(self):
        try:
            selecionado = self.tree.selection()[0]
            dados_cliente = self.tree.item(selecionado, 'values')
            senha = simpledialog.askstring("Senha", "Digite a senha de administrador:", show='*')
            if senha is None: return
            if not ctl.verificar_senha(senha):
                messagebox.showerror("Erro", "Senha incorreta!")
                return
            JanelaEdicaoCliente(self, self.app, dados_cliente)
        except IndexError:
            messagebox.showwarning("Atenção", "Selecione um cliente na lista para editar.")

class JanelaEdicaoCliente(tk.Toplevel):
    def __init__(self, parent, app_ref, dados):
        super().__init__(parent)
        self.app = app_ref
        self.id_cliente = dados[0]
        self.title(f"Editando Cliente ID: {self.id_cliente}")
        self.transient(parent)
        self.grab_set()
        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20)
        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5)
        self.nome_var = tk.StringVar(value=dados[1])
        ttk.Entry(frame, textvariable=self.nome_var, width=40).grid(row=0, column=1)
        ttk.Label(frame, text="Telefone:").grid(row=1, column=0, sticky='w', pady=5)
        self.tel_var = tk.StringVar(value=dados[2])
        ttk.Entry(frame, textvariable=self.tel_var, width=40).grid(row=1, column=1)
        ttk.Label(frame, text="Instagram:").grid(row=2, column=0, sticky='w', pady=5)
        self.insta_var = tk.StringVar(value=dados[3])
        ttk.Entry(frame, textvariable=self.insta_var, width=40).grid(row=2, column=1)
        ttk.Button(frame, text="Salvar Alterações", command=self.salvar).grid(row=3, columnspan=2, pady=20)
    def salvar(self):
        resultado = ctl.atualizar_cliente(self.id_cliente, self.nome_var.get(), self.tel_var.get(), self.insta_var.get())
        messagebox.showinfo("Resultado", resultado)
        if "sucesso" in resultado:
            self.app.on_data_changed()
            self.destroy()

class EditProdutosFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        ttk.Button(self, text="Editar Produto Selecionado", command=self.abrir_janela_edicao).pack(pady=10)
        colunas = ('codigo', 'descricao', 'compra', 'venda', 'qtd')
        self.tree = ttk.Treeview(self, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.title())
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.atualizar_lista_produtos_admin()
    def atualizar_lista_produtos_admin(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for prod in ctl.listar_produtos():
            values = (prod[0], prod[1], ctl.format_currency(prod[2]), ctl.format_currency(prod[3]), prod[4])
            self.tree.insert('', tk.END, values=values)
    def abrir_janela_edicao(self):
        try:
            selecionado = self.tree.selection()[0]
            codigo_selecionado = self.tree.item(selecionado, 'values')[0]
            dados_produto_brutos = next((p for p in ctl.listar_produtos() if p[0] == codigo_selecionado), None)
            if not dados_produto_brutos:
                messagebox.showerror("Erro", "Não foi possível encontrar os dados originais do produto.")
                return
            senha = simpledialog.askstring("Senha", "Digite a senha de administrador:", show='*')
            if senha is None: return
            if not ctl.verificar_senha(senha):
                messagebox.showerror("Erro", "Senha incorreta!")
                return
            JanelaEdicaoProduto(self, self.app, dados_produto_brutos)
        except IndexError:
            messagebox.showwarning("Atenção", "Selecione um produto na lista para editar.")

class JanelaEdicaoProduto(tk.Toplevel):
    def __init__(self, parent, app_ref, dados):
        super().__init__(parent)
        self.app = app_ref
        self.codigo_original = dados[0]
        self.title(f"Editando Produto: {self.codigo_original}")
        self.transient(parent)
        self.grab_set()
        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20)
        ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky='w', pady=5)
        self.codigo_var = tk.StringVar(value=dados[0])
        ttk.Entry(frame, textvariable=self.codigo_var).grid(row=0, column=1)
        ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky='w', pady=5)
        self.desc_var = tk.StringVar(value=dados[1])
        ttk.Entry(frame, textvariable=self.desc_var, width=40).grid(row=1, column=1)
        ttk.Label(frame, text="Valor Compra:").grid(row=2, column=0, sticky='w', pady=5)
        self.compra_var = tk.DoubleVar(value=dados[2])
        ttk.Entry(frame, textvariable=self.compra_var).grid(row=2, column=1)
        ttk.Label(frame, text="Valor Venda:").grid(row=3, column=0, sticky='w', pady=5)
        self.venda_var = tk.DoubleVar(value=dados[3])
        ttk.Entry(frame, textvariable=self.venda_var).grid(row=3, column=1)
        ttk.Label(frame, text="Quantidade:").grid(row=4, column=0, sticky='w', pady=5)
        self.qtd_var = tk.IntVar(value=dados[4])
        ttk.Entry(frame, textvariable=self.qtd_var).grid(row=4, column=1)
        ttk.Button(frame, text="Salvar Alterações", command=self.salvar).grid(row=5, columnspan=2, pady=20)
    def salvar(self):
        try:
            resultado = ctl.atualizar_produto(self.codigo_original, self.codigo_var.get(), self.desc_var.get(),
                                            self.compra_var.get(), self.venda_var.get(), self.qtd_var.get())
            messagebox.showinfo("Resultado", resultado)
            if "sucesso" in resultado:
                self.app.on_data_changed()
                self.destroy()
        except tk.TclError:
            messagebox.showerror("Erro", "Valores e quantidade devem ser numéricos.")

class EstornarVendaFrame(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=10)
        ttk.Button(frame_botoes, text="Estornar Venda Selecionada", command=self.estornar_venda).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar Lista", command=self.atualizar_lista_vendas).pack(side=tk.LEFT, padx=5)
        frame_lista = ttk.LabelFrame(self, text="Selecione uma Venda Ativa para Estornar")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        colunas = ('id', 'data', 'cliente', 'valor')
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        for col in colunas: self.tree.heading(col, text=col.title())
        self.tree.pack(fill='both', expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.atualizar_lista_vendas()
    def atualizar_lista_vendas(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for venda in ctl.get_vendas_ativas():
            id_v, data, cliente, valor = venda
            data_fmt = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.tree.insert('', 'end', values=(id_v, data_fmt, cliente, ctl.format_currency(valor)))
    def estornar_venda(self):
        try:
            selecionado = self.tree.selection()[0]
            venda_id = self.tree.item(selecionado, 'values')[0]
            senha = simpledialog.askstring("Senha", "Digite a senha de administrador:", show='*')
            if senha is None: return
            if not ctl.verificar_senha(senha):
                messagebox.showerror("Erro", "Senha incorreta!")
                return
            if not messagebox.askyesno("Confirmar Estorno", f"Tem certeza que deseja estornar a Venda #{venda_id}?\n\n- O financeiro será revertido.\n- Os produtos voltarão para o estoque.\n\nEsta ação é irreversível."):
                return
            resultado = ctl.estornar_venda_completa(venda_id)
            messagebox.showinfo("Resultado", resultado)
            if "sucesso" in resultado:
                self.app.on_data_changed()
        except IndexError:
            messagebox.showwarning("Atenção", "Selecione uma venda na lista para estornar.")

class AdminTab(ttk.Frame):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill='both')
        self.edit_clientes_frame = EditClientesFrame(notebook, self.app)
        self.edit_produtos_frame = EditProdutosFrame(notebook, self.app)
        self.estornar_venda_frame = EstornarVendaFrame(notebook, self.app)
        notebook.add(self.edit_clientes_frame, text='Editar Clientes')
        notebook.add(self.edit_produtos_frame, text='Editar Produtos')
        notebook.add(self.estornar_venda_frame, text='Estornar Venda')
    def refresh_admin_views(self):
        self.edit_clientes_frame.atualizar_lista_clientes_admin()
        self.edit_produtos_frame.atualizar_lista_produtos_admin()
        self.estornar_venda_frame.atualizar_lista_vendas()

class SobreTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        container = ttk.Frame(self)
        container.pack(expand=True)

        info_frame = ttk.LabelFrame(container, text="Sobre o Sistema")
        info_frame.pack(padx=20, pady=20)

        # Edite seus dados aqui
        nome_autor = "Antonio Junior"
        email = "alvs.junior@gmail.com"
        telefone = "(XX) 9XXXX-XXXX"
        linkedin_url = "https://www.linkedin.com/in/euantoniojr/"
        github = 'https://github.com/junioritsme/sistema_vendas'

        ttk.Label(info_frame, text="Este sistema foi desenvolvido por:", font=('Arial', 11)).pack(pady=(10, 2))
        ttk.Label(info_frame, text=nome_autor, font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Email: {email}").pack(pady=5, anchor='w')
        ttk.Label(info_frame, text=f"Telefone: {telefone}").pack(pady=5, anchor='w')

        # Criando o link clicável
        link_font = font.Font(family='Arial', size=10, underline=True)
        link_label = ttk.Label(info_frame, text="LinkedIn", foreground="blue", cursor="hand2", font=link_font)
        link_label.pack(pady=10, anchor='w')
        link_label.bind("<Button-1>", lambda e: self.open_link(linkedin_url))

        link_font = font.Font(family='Arial', size=10, underline=True)
        link_label = ttk.Label(info_frame, text="GitHub", foreground="blue", cursor="hand2", font=link_font)
        link_label.pack(pady=10, anchor='w')
        link_label.bind("<Button-1>", lambda e: self.open_link(github))

    def open_link(self, url):
        webbrowser.open_new(url)

# =================================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
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

        # Instanciando todas as abas
        self.vendas_frame = VendasTab(notebook, self)
        self.clientes_frame = ClientesTab(notebook, self)
        self.estoque_frame = EstoqueTab(notebook, self)
        self.relatorio_frame = RelatorioVendasTab(notebook)
        self.financeiro_frame = FinanceiroTab(notebook, self)
        self.admin_frame = AdminTab(notebook, self)
        self.sobre_frame = SobreTab(notebook) # Nova aba

        # Adicionando as abas ao notebook
        notebook.add(self.vendas_frame, text='Vendas')
        notebook.add(self.clientes_frame, text='Clientes')
        notebook.add(self.estoque_frame, text='Estoque')
        notebook.add(self.relatorio_frame, text='Relatório de Vendas')
        notebook.add(self.financeiro_frame, text='Financeiro')
        notebook.add(self.admin_frame, text='Administração')
        notebook.add(self.sobre_frame, text='Sobre') # Nova aba

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Você tem certeza que quer sair?"):
            ctl.desconectar()
            self.destroy()

    def on_data_changed(self):
        self.estoque_frame.atualizar_lista()
        self.financeiro_frame.refresh_data()
        self.clientes_frame.atualizar_lista()
        self.vendas_frame.atualizar_lista_clientes()
        self.vendas_frame.atualizar_lista_produtos()
        self.admin_frame.refresh_admin_views()
        self.relatorio_frame.gerar_relatorio()


if __name__ == "__main__":
    app = App()
    app.mainloop()