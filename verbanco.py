# arquivo: visualizar_tabela_sql_puro.py

import sqlite3

# --- ESCOLHA A TABELA QUE VOCÊ QUER VISUALIZAR ---
# Opções: 'clientes', 'estoque', 'vendas', 'venda_itens', 'transacoes_financeiras'
NOME_DA_TABELA = 'transacoes_financeiras'
# ----------------------------------------------------


print(f"\n--- Visualizando a tabela: '{NOME_DA_TABELA}' (com SQL puro) ---\n")

try:
    # Conecta ao banco de dados
    conn = sqlite3.connect('meubanco.db')
    cursor = conn.cursor()

    # Etapa 1: Executar a consulta e buscar os dados e cabeçalhos
    cursor.execute(f"SELECT * FROM {NOME_DA_TABELA}")
    
    # Pega os nomes das colunas a partir da descrição do cursor
    nomes_colunas = [description[0] for description in cursor.description]
    
    # Pega todas as linhas de dados
    linhas = cursor.fetchall()

    if not linhas:
        print("A tabela está vazia ou não existe.")
    else:
        # Etapa 2: Calcular a largura máxima de cada coluna para formatação
        # Começamos com a largura dos próprios cabeçalhos
        larguras_colunas = [len(str(nome)) for nome in nomes_colunas]
        
        # Agora, verificamos cada linha de dados para ver se algum valor é maior
        for linha in linhas:
            for i, valor in enumerate(linha):
                if len(str(valor)) > larguras_colunas[i]:
                    larguras_colunas[i] = len(str(valor))
        
        # Etapa 3: Imprimir a tabela formatada
        
        # Cria o formato da linha com base nas larguras calculadas
        # Ex: "| {:<10} | {:<25} |"
        formato_linha = " | ".join([f"{{:<{largura}}}" for largura in larguras_colunas])

        # Imprime o cabeçalho
        print(formato_linha.format(*nomes_colunas))
        
        # Imprime a linha separadora
        separador = "-+-".join(['-' * largura for largura in larguras_colunas])
        print(separador)

        # Imprime cada linha de dados
        for linha in linhas:
            print(formato_linha.format(*[str(v) for v in linha]))


except sqlite3.OperationalError as e:
    # Erro comum se a tabela não existir
    print(f"Ocorreu um erro de SQL: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()

print("\n--- Fim da visualização ---\n")