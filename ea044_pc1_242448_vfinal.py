import streamlit as st
import pandas as pd
import numpy as np
import copy

# Algoritmo Simplex
def simplex(tab):
    not_finished = True # indica final do algoritmo
    var = len(tab.columns)-1 # número de variáveis (básicas + não básicas)
    sa = len(tab.index)-1 # número de restrições
    n = 0 # número de iterações
    tab_np = tab.to_numpy().astype(float) # converte dados para numpy array
        
    # testando se coeficientes b_ij são não-negativos e aplicando correção, caso necessário
    for i in range(len(tab_np)):
        if tab_np[i][var]<0:
            tab_np[i] = tab_np[i]*-1 # multiplica linha i por -1 caso bij seja negativo
    
    dfs = [tab] # dataframes das iterações
    results = [dfs] # resultados do algoritmo (indíce 0: dataframes das iterações, 1: tipo de solução)    
    
    #-------- início do algoritmo ----------------------
    while not_finished:
        if (tab_np[0] < 0).sum() != 0: # confere se há valores negativos na primeira linha do tableau
            n += 1 # próxima iteração
    
            # passo 4 - analisar próxima variável a entrar na base
            new = np.argmin(tab_np[0]) # variável a entrar na base
            aux = tab_np[1:,var]/tab_np[1:,new] # valores RHS divididos por coeficiente da nova variável básica
    
            if (aux < 0).sum() == sa: # testando se problema é ilimitado: todos coeficientes negativos na nova variável básica
                results.append('problema ilimitado')
                return results

            else:
                # passo 5 - analisando qual variável sairá da base
                out_base = np.where(aux > 0, aux, np.inf).argmin() + (var-sa) # índice da variável básica a sair (índice em relação às colunas)               
                out_base_var = list(tab.index[out_base - (var-sa) + 1])
                out_base_var.pop(0)
                out_base_index = int(''.join(out_base_var))
                base[np.where(base==out_base_index)] = new+1 # atualiza base com nova variável básica
                tab_new = copy.deepcopy(tab_np)

                # passo 6 - operações para adequar nova variável básica na matriz identidade
                tab_new[out_base - (var-sa) + 1] =tab_new[out_base - (var-sa) + 1]/tab_new[out_base - (var-sa) + 1][new]     
                
                for i in range(len(tab_new)):
                    if i == out_base - (var-sa) + 1:
                        continue
                    else:
                        tab_new[i] = tab_new[i] - (tab_new[out_base - (var-sa) + 1])*tab_new[i][new]
    
                # atualizando DataFrame
                tab = tab.rename(index={'x{}'.format(out_base_index): 'x{}'.format(new+1)})
                tab.iloc[:,:] = tab_new
                dfs.append(tab)
                
                # atualizando tabelas
                tab_np = copy.deepcopy(tab_new)
    
        elif (tab_np[0,:var] == 0).sum()>sa: # testa quantidade de zeros nos coeficientes das variáveis (solução múltipla)
            results.append('solução ótima múltipla') # se uma variável não básica tiver coeficiente nulo, vão haver, pelo menos 'var - 1' coeficientes nulos
            return results
        else: 
            results.append('solução ótima única')
            return results

# --------------------- Estruturação do app -----------------------------------------------
st.title('[EA044] Projeto Computacional 01')
st.markdown(
'''
### _Implementação do Algoritmo Simplex_

Aluno: Nathan Shen Baldon (RA: 242448)

---
''')

st.markdown('#### Preencha o tableau inicial:')
var = st.number_input('Número de variáveis (básicas + não-básicas):', value=0, min_value=0)
sa = st.number_input('Número de restrições:', value=0, min_value=0)

# definindo colunas do dataframe inicial
colunas = np.append(['v'], np.array(['x{}'.format(i+1) for i in range(var)]))
colunas  = np.append(colunas, ['rhs'])

# definindo índices do dataframe inicial
index = np.append(['1'], np.array(['x{}'.format(i+1+var-sa) for i in range(sa)]))

# definindo dados zerados do dataframe inicial
data = np.zeros((sa+1,var+2))

# criando o dataframe inicial
tab0 = pd.DataFrame(data=data, index=None, columns=colunas)
tab0['v'] = index
tab0.set_index('v', inplace=True)
tab_aux = st.data_editor(tab0)
manual = st.button('Implementar manualmente')
if manual:
    tab = tab_aux
    st.markdown('### Tableau Inicial:')
    st.dataframe(tab) # apresenta tableau inicial
    results = simplex(tab)
    
    # ---------- escrevendo solução ótima ---------------------
    tab_final = results[0][-1] # tabela da última iteração
    
    # seleciona variáveis básicas a partir da tabela
    base = list(tab_final.index) 
    base.pop(0)
    base_values = list(tab_final['rhs'])
    base_values.pop(0)
    
    # seleciona variáveis não-básicas a partir da tabela
    not_base = list(tab_final.columns)
    not_base.remove('rhs')
    for variable in base:
        not_base.remove(variable)
    not_base_values = [0]*len(not_base) # variáveis não-básicas são nulas
    
    # monta lista com todas as variáveis e lista com todos os valores das variáveis
    for variable in not_base:
        base.append(variable)
    for value in not_base_values: 
        base_values.append(value)
        
    # ordena ambas as listas com base no índice das variáveis (de x1 até xn)
    zipped_sol = zip(base, base_values)
    sorted_sol = sorted(zipped_sol)
    tuples = zip(*sorted_sol)
    variables, values = [ list(tuple) for tuple in  tuples] # listas das variávies e respectivos valores 
    solution = pd.DataFrame(data=values,index=variables, columns=['value'])
    
    '---' 
    
    tab3, tab4 = st.tabs(['Solução', 'Iterações'])

    with tab3:
        st.markdown('#### Solução do Problema')
        st.markdown('##### _({})_'.format(results[1]))
        
        st.write('- número iterações: {}'.format(len(results[0])-1))
        if results[1]!='problema ilimitado':
            st.write('- solução ótima: v = {}'.format(results[0][-1].iloc[0,-1]*int(tab_final.index[0])))
            st.dataframe(solution)
                
                
    with tab4: 
        for i in range(len(results[0])):
            st.write('Iteração {}'.format(i))
            st.dataframe(results[0][i])   
