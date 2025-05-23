from my_app.db import get_db
import time

'''Função somente para filtragem usando o parâmetro EMPRESA'''


def buscar_contratos( empresa, data, cursor):
    cursor.execute("""
        SELECT COUNT(*) AS total_contratos FROM contratos WHERE fornecedor = ? AND data_adicao = ?
""", (empresa, data))
    resultado = cursor.fetchone()
    print('Total de contratos: ', resultado[0])
    resultado = resultado[0]
    return resultado


def buscar_compras(empresa, data, cursor): 
    inicio = time.time()
    cursor.execute("""
        SELECT COUNT(*) AS total_compras FROM compras_diretas WHERE fornecedor_vencedor = ? AND data_adicao = ?
        UNION ALL
        SELECT COUNT(*) FROM outras_compras WHERE fornecedor_vencedor = ? AND data_adicao = ?
""", (empresa, data, empresa, data))
        
    resultado = cursor.fetchall()

    total_diretas = resultado[0]['total_compras']       
    total_outras = resultado[1]['total_compras']
    print('O total de compras diretas foi de: ', total_diretas)
    print('O total de outras compras foi de: ', total_outras)

    resultado_contratos = buscar_contratos(empresa, data, cursor)
    fim =  time.time()
    tempo = fim - inicio
    print(f'Tempo gasto na função BUSCAR_COMPRAS: {tempo:.6f} segundos')              
    return total_diretas, total_outras, resultado_contratos

def ultima_compra_direta(cursor, empresa, data):
    
    cursor.execute("SELECT data_aprovacao, id_processo FROM compras_diretas WHERE (data_adicao = ? AND fornecedor_vencedor = ?) ORDER BY data_aprovacao DESC LIMIT 1", (data, empresa))
    res = cursor.fetchone()
    data_ultima_compra_diretas, processo_diretas = res   
    fim = time.time()
    return data_ultima_compra_diretas, processo_diretas



def ultima_compra_outra(cursor, empresa, data):
    print('Iniciando a busca pela última compra usando empresa como parâmetro')
    cursor.execute("SELECT data_aprovacao, id_processo FROM outras_compras WHERE (data_adicao = ? AND fornecedor_vencedor = ?) ORDER BY data_aprovacao DESC LIMIT 1", (data, empresa))
    res = cursor.fetchone()
    data_ultima_compra_outras, processo_outras = res   
    return data_ultima_compra_outras, processo_outras
    

    '''Funções para filtragem através do parâmetro CNPJ'''

def buscar_contratos_cnpj(cursor, cnpj, data):
    cursor.execute("SELECT COUNT(*) AS total_contratos FROM contratos WHERE cpf_cnpj = ? AND data_adicao = ?" ,(cnpj, data))
    resultado = cursor.fetchone()
    resultado = resultado[0]
    print('O total de contratos foi de: ', resultado)
    
    return resultado

def buscar_compras_cnpj(cursor, cnpj, data):
    cursor.execute("""
            SELECT COUNT(*) AS total_compras FROM compras_diretas WHERE cpf_cnpj = ? AND data_adicao = ?
            UNION ALL
            SELECT COUNT(*)  FROM outras_compras WHERE cpf_cnpj = ? AND data_adicao = ?                                                         
    """, (cnpj, data, cnpj, data)) 
    resultado = cursor.fetchall()
    total_diretas = resultado[0]['total_compras']
    total_outras = resultado[1]['total_compras']
    print('O total de compras diretas foi de: ', total_diretas)
    print('O total de outras compras foi de: ', total_outras)
    print('Fazendo a busca de contratos agora..')
    resultado_contratos = buscar_contratos_cnpj(cursor, cnpj, data)
    print('contratos passou')
    total_contratos = resultado_contratos
    print('O total de contratos foi de: ', total_contratos)

    print('Iniciando a busca pela última compra')
    ultima_compra = 'Nenhuma compra feita'
    if total_diretas == 0 and total_outras == 0:
        ultima_compra = 'Nenhuma compra'
    elif total_diretas == 0 and total_outras != 0:
        print('AQUI')
        ultima_compra_outra = ultima_compra_outra_cnpj(cursor, cnpj, data)
        data_outra, processo_outra = ultima_compra_outra
        ultima_compra = f'A última compra foi em: {data_outra} com o processo: {processo_outra}'
    elif total_diretas != 0  and total_outras == 0:
        print('aq')
        ultima_compra_direta = ultima_compra_direta_cnpj(cursor, cnpj, data)
        data_direta, processo_direta = ultima_compra_direta
        ultima_compra = f'A última compra foi em: {data_direta} com o processo: {processo_direta}'        
    else:
        print('oii')
        ultima_compra_direta = ultima_compra_direta_cnpj(cursor, cnpj, data)
        ultima_compra_outra = ultima_compra_outra_cnpj(cursor, cnpj, data)

        data_direta, processo_direta = ultima_compra_direta
        data_outra, processo_outra = ultima_compra_outra

        resultado = comparar_data(data_direta, data_outra)
        if resultado == data_direta:
            ultima_compra = f'A última compra foi em: {data_direta} com o processo: {processo_direta}'
        else:
            ultima_compra = f'A última compra foi em: {data_outra} com o processo: {processo_outra}'
    return total_diretas, total_outras, total_contratos, ultima_compra    

def ultima_compra_direta_cnpj(cursor, cnpj, data):
    inicio = time.time()
    cursor.execute("SELECT data_aprovacao, id_processo FROM compras_diretas WHERE (data_adicao = ? AND cpf_cnpj = ?) ORDER BY data_aprovacao DESC LIMIT 1", (data, cnpj))
    res = cursor.fetchone()
    data_ultima_compra_diretas, processo_diretas = res 
    fim =  time.time()
    tempo_total = fim - inicio
    print(f'Total de tempo gasto: {tempo_total:.6f}')
    return data_ultima_compra_diretas, processo_diretas 

def ultima_compra_outra_cnpj(cursor, cnpj, data):
    cursor.execute("SELECT data_aprovacao, id_processo FROM outras_compras WHERE (data_adicao = ? AND cpf_cnpj = ?) ORDER BY data_aprovacao DESC LIMIT 1", (data, cnpj))
    res = cursor.fetchone()
    data_ultima_compra_outras, processo_outras = res
    return data_ultima_compra_outras, processo_outras


'''Função para comparar DATA'''

def comparar_data(data1, data2):
    if data1 > data2:
        data_antiga = data1
    else:
        data_antiga = data2
    return data_antiga






# FUNÇÃO PARA ACOMPANHAMENTO_SIGA

from my_app.funcao_tabela_filtro_dados import dataframe_contratos, dataframe_fornecedores

def consulta_contratos_exclusao(conn, data2, data1):
    resultado = conn.execute("""
        SELECT id_processo FROM contratos WHERE data_adicao_db = ?
        EXCEPT
        SELECT id_processo FROM contratos WHERE data_adicao_db = ?
""", (data2, data1)).fetchall()
    data_excluido = 0
    total_excluido = 0
    if resultado:
        data_excluido = resultado
        total_excluido = len(data_excluido)


    return resultado, total_excluido


def consulta_fornecedores_exclusao(conn, data2, data1):
    resultado = conn.execute("""
        SELECT cpf_cnpj FROM fornecedores WHERE data_adicao_db = ?
        EXCEPT
        SELECT cpf_cnpj FROM fornecedores WHERE data_adicao_db = ?
""", (data2, data1)).fetchall()
    data_excluido = 0
    total_excluido = 0
    if resultado:
        data_excluido = resultado
        total_excluido = len(data_excluido)
    
    return total_excluido, data_excluido

def consulta_contratos(conn, data2, data1):
    ids_adicionados = dataframe_contratos(conn, data1, data2)
    data_adicionado = 0 
    total_adicionado = 0
    print(data_adicionado)
    if ids_adicionados:
        data_adicionado = ids_adicionados
        print(data_adicionado)
        total_adicionado = len(data_adicionado)
    resultado_exclusao = consulta_contratos_exclusao(conn, data2, data1)
    data_excluido = resultado_exclusao[0]
    total_excluido = resultado_exclusao[1]



    return total_adicionado, data_adicionado, total_excluido, data_excluido


def consulta_fornecedores(conn, data2, data1):
    resultado = dataframe_fornecedores(conn, data1, data2)
    data_adicionado = 0
    total_adicionado = 0
    if resultado:
        data_adicionado = resultado
        total_adicionado = len(resultado)
    
    resultado_exclusao = consulta_fornecedores_exclusao(conn, data2, data1)

    data_excluido = resultado_exclusao[0]
    total_excluido = resultado_exclusao[1]

    return total_adicionado, data_adicionado, total_excluido, data_excluido



#FUNCAO PARA COMPRAS


def consulta_compras_diretas_exclusao(conn, data2, data1):
    resultado = conn.execute("""
        SELECT id_processo FROM compras_diretas WHERE data_adicao_db = ?
        EXCEPT
        SELECT id_processo FROM compras_diretas WHERE data_adicao_db = ?
""", (data1, data2)).fetchall()
    data_excluido = 0
    total_excluido = 0
    if resultado is not None:
        data_excluido = resultado
        total_excluido = len(data_excluido)
    

    return data_excluido, total_excluido


def consulta_outras_compras_exclusao(conn, data2, data1):
    resultado = conn.execute(""" 
        SELECT cpf_cnpj FROM outras_compras WHERE data_adicao_db = ?
        EXCEPT
        SELECT cpf_cnpj FROM outras_compras WHERE data_adicao_db = ?
""", (data1, data2)).fetchall()
    data_excluido = 0
    total_excluido = 0
    if resultado is not None:
        data_excluido = resultado
        total_excluido = len(data_excluido)
    

    return data_excluido, total_excluido

def consulta_compras_diretas(conn, data2, data1):
    resultado = conn.execute("""
        SELECT id_processo FROM compras_diretas WHERE data_adicao_db = ?
        EXCEPT
        SELECT id_processo FROM compras_diretas WHERE data_adicao_db = ?
""", (data2, data1)).fetchall()
    data_adicionado = 0
    total_adicionado = 0
    if resultado is not None:
        data_adicionado = resultado
        total_adicionado = len(data_adicionado)
    resultado_exclusao = consulta_compras_diretas_exclusao(conn, data2, data1)

    data_excluido = resultado_exclusao[0]
    total_excluido = resultado_exclusao[1]

    return data_adicionado, total_adicionado, data_excluido, total_excluido


def consulta_outras_compras(conn, data2, data1):
    resultado = conn.execute(""" 
        SELECT cpf_cnpj FROM outras_compras WHERE data_adicao_db = ?
        EXCEPT
        SELECT cpf_cnpj FROM outras_compras WHERE data_adicao_db = ?
""", (data2, data1)).fetchall()
    if resultado is not None:
        data_adicionado = resultado
        total_adicionado = len(data_adicionado)
    resultado_exclusao = consulta_outras_compras_exclusao(conn, data2, data1)

    data_excluido = resultado_exclusao[0]
    total_excluido = resultado_exclusao[1]

    return data_adicionado, total_adicionado, data_excluido, total_excluido


def criar_dataframe(conn, ids, base):
    query = f"""
    SELECT n.*, r.*
    FROM ids
    NATURAL JOIN {base} r ON (n.id_processo = r.id_processo)
"""
    

#FUNÇÃO PARA EXCEL DO ACOMPANHAMENTO SIGA


