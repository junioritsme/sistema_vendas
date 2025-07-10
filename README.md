# Sistema de Gestão de Vendas em Python

![Demonstração do Sistema](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Demonstração do Sistema](https://img.shields.io/badge/License-MIT-green.svg)

## 📖 Descrição

Este é um sistema de Ponto de Venda (PDV) e gestão comercial completo, desenvolvido em **Python** com a interface gráfica **Tkinter** e banco de dados **SQLite**. Ele foi projetado para ser uma solução desktop simples, robusta e intuitiva para pequenos comércios e vendedores autônomos, centralizando as operações de venda, estoque, clientes e financeiro em um único lugar.

O sistema não requer conexão com a internet e armazena todos os dados localmente, garantindo agilidade e segurança para o usuário.

## ✨ Funcionalidades Principais

O sistema é organizado em abas, facilitando a navegação e o acesso às suas múltiplas funcionalidades:

### **Módulo de Vendas (PDV)**
* Busca dinâmica de clientes e produtos para agilizar o processo de venda.
* Carrinho de compras interativo.
* Suporte a múltiplos métodos de pagamento: Dinheiro, PIX, Cartão de Débito, Cartão de Crédito e Crediário.
* Geração automática de parcelas para vendas a prazo (Crediário e Cartão de Crédito).
* Aplicação de descontos sobre o valor total da venda.

### **Clientes e Estoque**
* **Gestão de Clientes:** Cadastro, edição e listagem completa de clientes.
* **Controle de Estoque:** Cadastro de produtos com código, descrição, valor de compra, valor de venda e quantidade. O estoque é atualizado automaticamente após cada venda ou estorno.

### **Financeiro e Contas a Receber**
* **Contas a Receber:** Painel para visualizar todas as parcelas pendentes, com filtros por cliente e método de pagamento. As parcelas vencidas são destacadas visualmente.
* **Liquidação de Parcelas:** Permite liquidar uma ou mais parcelas de uma vez, registrando a entrada no "Caixa" ou "Banco" e calculando taxas (caso o valor recebido seja menor que o esperado).
* **Extratos Financeiros:** Controle separado para as contas "Caixa" e "Banco", com extrato detalhado de todas as entradas e saídas e exibição do saldo atual.
* **Registro de Saídas:** Permite registrar despesas manuais para um controle financeiro preciso.

### **Relatórios Gerenciais**
* Gere relatórios detalhados para:
    * Lista completa de **Clientes**.
    * Posição do **Estoque**, com filtro para produtos com baixo estoque.
    * Histórico de **Vendas**, com filtros por período, cliente e status (Ativa/Estornada).
    * **Contas a Receber**, com filtros por cliente e status de vencimento.
    * **Extratos Financeiros** por conta e período.
* **Exportação para PDF:** Todos os relatórios podem ser exportados para um arquivo PDF com um único clique.

### **Painel de Administração**
* **Gestão de Usuários:** Crie e delete usuários para acesso ao sistema.
* **Estorno de Vendas:** Uma ferramenta segura (requer senha do administrador) para estornar uma venda completa. Esta ação reverte todas as operações: os produtos voltam para o estoque e os lançamentos financeiros associados são cancelados.
* **Logs de Ações:** O sistema registra as ações importantes (criação de usuários, vendas, estornos, etc.) para fins de auditoria.

------------------------------------------------------------------------------------------------------------------------------
## 🛠️ Como Instalar e Executar

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

### ✅ Pré-requisitos

- Python **3.8 ou superior**

### 1. Clone o Repositório

```bash
git clone https://github.com//junioritsme/sistema_vendas.git
cd /sistema_vendas
````

### 2. Instale as Dependências
Este projeto utiliza algumas bibliotecas externas. Instale todas de uma vez com o comando:

```bash
Copiar
Editar
pip install tkcalendar reportlab python-dateutil
```

### 3. Crie o Banco de Dados
Antes de iniciar o aplicativo, você precisa criar o arquivo de banco de dados e as tabelas. Para isso, execute o script database.py:

```bash
Copiar
Editar
python database.py
Este comando criará um arquivo meubanco.db no mesmo diretório. Ele também criará um usuário padrão para o primeiro acesso.
```

Usuário: admin

Senha: admin

### 4. Execute o Sistema
Com tudo configurado, inicie o sistema executando o arquivo app.py:

```bash
Copiar
Editar
python app.py
```

A janela de login aparecerá. Use as credenciais padrão para entrar e começar a usar!

📜 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
