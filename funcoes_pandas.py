# -*- coding: utf-8 -*-

import math
import numpy
import sys
import io
from pympler import asizeof
import requests
import ast
import operator
import copy
import builtins

def create_df (data, index=None, dtype=None):
    """
    Função recebe um dicionário data e um vetor index e retorna a matriz df
    contendo seus dados e os vetores ind e col, contendo o nome de suas linhas e
    colunas, respectivamente.
    """

    #chaves do dicionario = colunas de df

    # econtrando o número de linhas
    num_linhas = len(next(iter(data.values())))

    df = []

    # criando df
    for i in range(num_linhas):
        linha = []

        for chave in data:
            if dtype == None:
                linha.append(data[chave][i])

            elif dtype == int:
                linha.append(int(data[chave][i]))
            elif dtype == float:
                linha.append(float(data[chave][i]))
            elif dtype == str:
                linha.append(str(data[chave][i]))
            elif dtype == bool:
                linha.append(bool(data[chave][i]))

        df.append(linha)

    # criando ind e col

    col = []
    ind = [0]*num_linhas

    # para o vetor de colunas, adicionamos as chaves do dicionario data
    for columns in data:
        col.append(columns)

    # já para o vetor de linhas, verificamos se ele é igual a None
    if index == None:
        # se for, o valor padrão dos rótulos das linhas devem ser inteiros de 0 até numero de linhas - 1
        for i in range(num_linhas):
            ind[i] = i
    else:
        for i in range(num_linhas):
            ind[i] = index[i]

    return df, ind, col

def shape(df):
    """
    Recebe uma matriz df e retorna uma tupla contendo suas dimensões no formato (numero_linhas, numero_colunas)
    """
    linhas =len(df)
    if linhas != 0:
        colunas =len(df[0])
    else:
        colunas = 0
    return (linhas,colunas)

def reshape(df, shape_df, order='C', copy=True):
  """
  Recebe um matriz df e a redimensiona de acordo com a dimensão e ordem passadas via parâmetro.
  O parâmetro order define o ordem na qual a matriz será reorganizada, podendo receber os seguintes
  valores:
    C: estilo C, reorganiza os dados linha por linha (itera o segundo índice primeiro);
    F: estilo Fortran, reorganiza os dados coluna por coluna (itera o primeiro índice primeiro);
  Se copy=True, retorna uma cópia de df redimensionada. Se não, altera a dimensão da matriz original.
  """
  shape_ant = shape(df)

  ind_linha = 0
  ind_coluna = 0

  # caso copy = True, faremos as alterações na matriz novo_df

  if copy == True:
    novo_df = []

    # caso a ordem seja C, os valores de df serão redimensionados por linha
    if order == 'C':
      for i in range(shape_df[0]):
        linha = []

        for j in range(shape_df[1]):
          if ind_coluna == shape_ant[1]:
            ind_linha +=1
            ind_coluna = 0

          linha.append(df[ind_linha][ind_coluna])

          ind_coluna += 1
        novo_df.append(linha)

    # caso a ordem seja F, os valores de df serão redimensionados por coluna

    if order == 'F':

      # Pra facilitar, vamos criar as linhas e colunas de novo_df e só depois inserir todos os valores coluna por coluna
      for i in range(shape_df[0]):
        linha = [None]*shape_df[1]

        novo_df.append(linha)

      for j in range(shape_df[1]):
        for i in range(shape_df[0]):
          if ind_coluna == shape_ant[1]:
            ind_linha +=1
            ind_coluna = 0

          novo_df[i][j] = df[ind_linha][ind_coluna]

          ind_coluna += 1

    return novo_df

  # caso copy = False, faremos as alterações diretamente em df

  else:
      copia = df.copy()

      # caso a ordem seja C, os valores de df serão redimensionados por linha

      # caso a quantidade de linhas anterior seja menor que a nova, criamos novas linhas para na matriz df
      if(shape_ant[0] < shape_df[0]):
        for i in range(shape_ant[0], shape_df[0]):
          df.append([None])

      if order == 'C':
        for i in range(shape_df[0]):
          linha = []

          for j in range(shape_df[1]):
            if ind_coluna == shape_ant[1]:
              ind_linha +=1
              ind_coluna = 0

            linha.append(copia[ind_linha][ind_coluna])

            ind_coluna += 1
          df[i] = linha

      # caso a ordem seja F, os valores de df serão redimensionados por coluna

      if order == 'F':
        for i in range(shape_df[0]):
          linha = [None]*shape_df[1]

          df[i] = linha

        for j in range(shape_df[1]):
          for i in range(shape_df[0]):
            if ind_coluna == shape_ant[1]:
              ind_linha +=1
              ind_coluna = 0

            df[i][j] = copia[ind_linha][ind_coluna]

            ind_coluna += 1

      # Depois de modificar as linhas necessessarias
      if shape_df[0] < shape_ant[0]:
        for i in range(shape_df[0], shape_ant[0]):
          df.remove(df[shape_df[0]])

def loc(df, index, columns, *, loc_ind=None, loc_col=None):
    """
    Recebe uma matriz df, seus vetores associados index e columns, que contém os rótulos de linha e coluna respectivamente,
    e os rótulos de linha (loc_ind) e de coluna (loc_col) os quais queremos acessar em df. Os parâmetros loc_ind e loc_col podem
    ser apenas um rótulo ou uma lista de rótulos. O valor de retorno será uma matriz contendo somente os elementos que estão
    em loc_ind e/ou loc_col em df, juntamente com seus vetores associados de linhas e colunas.
    """
    dimensao = shape(df)

    # criando uma nova matriz para inserir os elementos que estão em loc_ind e/ou loc_col em df
    new_df = []

    new_index = []
    new_col = []

    # transformando os parametros loc_ind e loc_col em listas caso não sejam
    if loc_ind == None:
        new_index = index.copy()
    elif type(loc_ind) != list:
        new_index.append(loc_ind)
    else:
        new_index = loc_ind.copy()


    if loc_col == None:
        new_col = columns.copy()
    elif type(loc_col) != list:
        new_col.append(loc_col)
    else:
        new_col = loc_col.copy()

    # iterando o df original para identificar os elementos serão inseridos em new_df
    for i in range(dimensao[0]):
        linha = []
        
        # como o usuário pode inserir somente uma lista/elemento de linhas ou colunas, ou ambos,
        # usaremos variáveis auxiliares para facilitar a separação dos elementos requeridos
        aux_l = False
        aux_c = False

        if new_index[0] != None:
            for k in range(len(new_index)):
                if index[i] == new_index[k]:
                    aux_l = True
        else:
            aux_l = True

        for j in range(dimensao[1]):
            aux_c = False

            if new_col[0] != None and aux_l == True:
                for k in range(len(new_col)):
                    if columns[j] == new_col[k]:
                        aux_c = True
            else:
                aux_c = True

            if aux_c == True and aux_l == True:
                linha.append(df[i][j])
            
        if linha != []:
            new_df.append(linha)
        

    return new_df,new_index,new_col

def iloc(df, index, columns, *, iloc_ind=None, iloc_col=None):
    """
    Recebe uma matriz df, seus vetores associados index e columns, que contém os rótulos de linha e coluna respectivamente,
    e os índices de linha (loc_ind) e de coluna (loc_col) os quais queremos acessar em df. Os parâmetros loc_ind e loc_col podem
    ser apenas um índice ou uma lista de índices. O valor de retorno será uma matriz contendo somente os elementos que estão
    em loc_ind e/ou loc_col em df, juntamente com seus vetores associados de linhas e colunas.
    """

    dimensao = shape(df)

    new_df = []

    new_index = []
    new_col = []

    int_index = []
    int_col = []

    if type(iloc_ind) != list:
        int_index.append(iloc_ind)
    else:
        int_index = iloc_ind.copy()


    if type(iloc_col) != list:
        int_col.append(iloc_col)
    else:
        int_col = iloc_col.copy()

    for i in range(dimensao[0]):
        linha = []

        aux_l = False
        aux_c = False

        if int_index[0] != None:
            for k in range(len(int_index)):
                if i == int_index[k]:
                    aux_l = True
        else:
            aux_l = True

        for j in range(dimensao[1]):
            aux_c = False

            if int_col[0] != None and aux_l == True:
                for k in range(len(int_col)):
                    if j == int_col[k]:
                        aux_c = True
            else:
                aux_c = True

            if aux_c == True and aux_l == True:
                linha.append(df[i][j])

                if (index[i] in new_index) == False:
                    new_index.append(index[i])

                if (columns[j] in new_col) == False:
                    new_col.append(columns[j])

        if linha != []:
            new_df.append(linha)

    return new_df,new_index,new_col

def insert (df, columns, loc, col, value, allowduplicates=False):
  """
  Insere uma nova coluna na matriz df e no vetor de colunas columns, de acordo com sua localização
  (parâmetro loc), nome da nova coluna (parâmetro col) e valor (parâmetro value).
  allowduplicates define se é possível criar colunas com nomes duplicados. Se for igual
  a False, não será permitido a criação de colunas com nomes duplicados.
  """

  l,c = shape(df)

  #verificando se o nome da nova coluna é repetido (caso allowduplicates seja False)

  if allowduplicates == False:
    for i in range(c):
      if col == columns[i]:
        print("Coluna com nome duplicado!")
        return

  #inserindo a coluna na lista de colunas 'columns'
  aux1 = col

  if loc < c:
    for i in range(loc, c):
      aux2 = columns[i]
      columns[i] = aux1
      aux1 = aux2

  columns.append(aux1)

  #inserindo nova coluna na matriz 'df'

  if type(value) == list: #se value for uma lista
    for i in range(l):
      aux1 = value[i]

      if loc < c:
        for j in range(loc,c):
          aux2 = df[i][j]
          df[i][j] = aux1
          aux1 = aux2

      df[i].append(aux1)

  else: # se value é um valor escalar
    for i in range(l):
      aux1 = value

      if loc < c:
        for j in range(loc,c):
          aux2 = df[i][j]
          df[i][j] = aux1
          aux1 = aux2

      df[i].append(aux1)

def rename (axis=1, mapper=None, *, index=None, columns=None, inplace=False):
    """
    Renomeia os rótulos de linha e coluna, representados pelos vetores index e columns.
    Além das listas de rótulos, também recebe um dicionário ou função mapper que será
    aplicado ao vetor para renomear seus valores, um inteiro axis que define qual eixo será
    alterado pelo parâmetro mapper e inplace, que define se a alteração será feita diretamente
    no vetor correspondente ou não.
    """

    if inplace == True:
        if axis == 0:
            num_linhas = len(index)

            if callable(mapper):
                for i in range(num_linhas):
                    index[i] = mapper(index[i])

            else:
                for i in range(num_linhas):
                    if index[i] in mapper:
                        index[i] = mapper[index[i]]

        elif axis == 1:
            num_col = len(columns)

            if callable(mapper):
                for i in range(num_col):
                    columns[i] = mapper(columns[i])

            else:
                for i in range(num_col):
                    if columns[i] in mapper:
                        columns[i] = mapper[columns[i]]

    else:
        if axis == 0:
            num_linhas = len(index)

            new_ind = []

            if callable(mapper):
                for i in range(num_linhas):
                    new_ind.append(mapper(index[i]))

            else:
                for i in range(num_linhas):
                    if index[i] in mapper:
                        new_ind.append(mapper[index[i]])
                    else:
                        new_ind.append(index[i])

            return new_ind

        elif axis == 1:
            num_col = len(columns)

            new_col = []

            if callable(mapper):
                for i in range(num_col):
                    new_col.append(mapper(columns[i]))

            else:
                for i in range(num_col):
                    if columns[i] in mapper:
                        new_col.append(mapper[columns[i]])
                    else:
                        new_col.append(mapper(columns[i]))

def null_check(valor):
    """
    Recebe valor e retorna True se valor for nulo e False caso contrário.
    """

    if valor == None or (type(valor) != str and numpy.isnan(valor)):
        return True
    else:
        return False

def notnull(df):
    """
    Recebe uma matriz df e retorna uma matriz contendo valores bool,
    do mesmo tamanho do original, de forma que os valores não nulos
    sejam mapeados como True e os nulos como False.
    """

    dimensao = shape(df)
    new_df = []

    for i in range(dimensao[0]):
        linha = []

        for j in range(dimensao[1]):
            if null_check(df[i][j]):
                linha.append(False)
            else:
                linha.append(True)

        new_df.append(linha)

    return new_df

def isnull(df):
    """
    Recebe uma matriz df e retorna uma matriz contendo valores bool,
    do mesmo tamanho do original, de forma que os valores nulos
    sejam mapeados como True e os não nulos como False.
    """

    dimensao = shape(df)
    new_df = []

    for i in range(dimensao[0]):
        linha = []

        for j in range(dimensao[1]):
            if null_check(df[i][j]):
                linha.append(True)
            else:
                linha.append(False)

        new_df.append(linha)

    return new_df

def max_col(df):
    """
    Recebe uma matriz df e retorna um vetor lista_max com n valores,
    onde o i-esimo elemento de lista_max corresponde a maior valor da
    i-esima coluna de df
    """

    lista_max = []

    dimensao = shape(df)

    for j in range(dimensao[1]):
        maior = df[0][j]
        for i in range(dimensao[0]):
            if df[i][j] > maior:
                maior = df[i][j]
        lista_max.append(maior)

    return lista_max

def min_col(df):
    """
    Recebe uma matriz df e retorna um vetor lista_min com n valores,
    onde o i-esimo elemento de lista_min corresponde a menor valor da
    i-esima coluna de df
    """

    lista_min = []

    dimensao = shape(df)

    for j in range(dimensao[1]):
        menor = df[0][j]
        for i in range(dimensao[0]):
            if df[i][j] < menor:
                menor = df[i][j]
        lista_min.append(menor)

    return lista_min

def minMaxScaler(df, feature_range=(0,1), *,copy=True, clip=False):
    """
    Recebe uma matriz df e normaliza seus valores com a técnica min-max,
    de forma que todos os seus elementos serão normalizados para o intervalo dado pela tupla feature_range
    (que possui valor padrão de 0 e 1). A matriz df normalizada será o valor de retorno da função caso
    copy = True, caso contrário a função não terá valor de retorno e as mudanças serão feitas diretamente em df.
    Caso clip=True, todos os valores resultantes da normalização que não estiverem no intervalo de feature_range serão
    forçados a estarem no intervalo.
    """

    dimensao = shape(df)

    lista_max = max_col(df)
    lista_min = min_col(df)

    if copy == True:
        new_df = []

        for i in range(dimensao[0]):
            linha = []

            for j in range(dimensao[1]):
                std = (df[i][j]-lista_min[j])/(lista_max[j]-lista_min[j])

                x = std * (feature_range[1] - feature_range[0]) + feature_range[0]

                if clip == True:
                    if x < feature_range[0]:
                        x = feature_range[0]
                    elif x > feature_range[1]:
                        x = feature_range[1]
                linha.append(x)
            new_df.append(linha)

        return new_df

    else:
        for i in range(dimensao[0]):
            for j in range(dimensao[1]):
                std = (df[i][j]-lista_min[j])/(lista_max[j]-lista_min[j])
                x = std * (feature_range[1] - feature_range[0]) + feature_range[0]

                if clip == True:
                    if x < feature_range[0]:
                        x = feature_range[0]
                    elif x > feature_range[1]:
                        x = feature_range[1]

                df[i][j] = x

def mean_col(df):
    """
    Recebe uma matriz df e retorna um vetor lista_media com n valores,
    onde o i-esimo elemento de lista_media corresponde a media da i-esima
    coluna de df
    """

    lista_media = []

    dimensao = shape(df)

    for j in range(dimensao[1]):
        cont = 0

        for i in range(dimensao[0]):
            cont+= df[i][j]

        lista_media.append(cont/dimensao[0])

    return lista_media

def std_col (df):
    """
    Recebe uma matriz df e retorna um vetor lista_dp com n valores, onde o
    i-esimo elemento de lista_dp corresponde ao desvio padrão da i-esima
    coluna de df
    """

    lista_dv = []

    medias = mean_col(df)

    dimensao = shape(df)

    for j in range(dimensao[1]):
        somatoria = 0

        for i in range(dimensao[0]):
            somatoria += (df[i][j]-medias[j])**2

        lista_dv.append(math.sqrt(somatoria/dimensao[0]))

    return lista_dv

def standardScaler(df, *, copy=True,with_mean=True, with_std=True):
    """
    Recebe uma matriz df e padroniza os dados de acordo com os parâmetros with_mean
    e with_std, podendo retornar uma matriz com os dados padronizados caso copy = True,
    caso contrário não possui valor de retorno, fazendo as modificações nos elementos da matriz original.
    Por padrão, obedece a formula z = (x - media_coluna) / desvio_padrao_coluna,
    onde z é o valor padronizado e x o valor orginal na matriz
    """

    dimensao = shape(df)

    lista_media = mean_col(df)
    lista_dv = std_col(df)

    if copy == True:
        novo_df = []

        for i in range(dimensao[0]):
            linha = []

            for j in range(dimensao[1]):
                divisor = 1
                dividendo = df[i][j]

                # se with_mean for verdadeiro, centraliza os valores (isto é, transforma a média em 0) fazendo com que o valor a ser dividido na formula seja o valor do elemento original, subtraindo o valor da média
                if with_mean == True:
                    dividendo -= lista_media[j]

                # se with_std for verdadeiro, transforma o desvio padrao de cada coluna em 1, fazendo com que o valor divisor da formula seja o desvio padrão original da coluna
                if with_std == True:
                    divisor = lista_dv[j]

                linha.append(dividendo/divisor)

            novo_df.append(linha)

        return novo_df

    else:
        for i in range(dimensao[0]):
            for j in range(dimensao[1]):
                divisor = 1
                dividendo = df[i][j]

                if with_mean == True:
                    dividendo -= lista_media[j]

                if with_std == True:
                    divisor = lista_dv[j]

                df[i][j] = dividendo/divisor

def dtype (e):
    """
    Recebe um elemento e retorna uma string contendo seu tipo.
    """

    if type(e) == int:
        return "int"
    elif type(e) == float:
        return "float"
    elif type(e) == str:
        return "str"
    elif type(e) == bool:
        return "bool"
    elif type(e) == complex:
        return "complex"

def find_column(df, col, v):
    """
    Recebe uma matriz e verifica se o valor já está presente na coluna
    recebida por parâmetro.
    """

    if dtype(v) != 'str' and math.isnan(v):
        for i in range(len(df)):
            if math.isnan(float(df[i][col])):
                return True
    else:
        for i in range(len(df)):
            if df[i][col] == v:
                return True
    return False

def count_value_series (series, v):
    """
    Recebe um vetor e retorna a quantidade de vezes que o valor recebido por parâmetro
    aparece no vetor.
    """

    cont = 0

    if dtype(v) != 'str' and math.isnan(v):
        for i in range(len(series)):
            if math.isnan(series[i]):
                cont+=1
    else:
        for i in range(len(series)):
            if series[i] == v:
                cont+=1

    return cont

def key_series(m):
    """
    Função auxiliar para ordenação em series_value_counts.
    """
    return m[1]

def min_value(v):
    """
    Recebe um vetor v e retorna o menor valor desse vetor.
    """

    menor = v[0]

    for i in range(len(v)):
        if v[i] < menor:
            menor = v[i]

    return menor

def max_value(v):
    """
    Recebe um vetor v e retorna o maior valor desse vetor.
    """

    maior = v[0]

    for i in range(len(v)):
        if v[i] > maior:
            maior = v[i]

    return maior

def series_value_counts (v, normalize=False, sort=True,ascending=False, bins=None,dropna=True):
    """
    Recebe um vetor v e retorna uma matriz contendo a quantidade de
    vezes que cada valor de v apareceu no vetor
    Quando bins for diferente de None, bins será a quantidade de
    intevalos os quais os dados serão agrupados para a contagem, de
    forma que o intervalo seja semi aberto a direita (não incluir o valor
    do limite inferior, porém inclui o valor do limite superior)
    """

    freq_total = len(v) # número total de elementos no vetor

    valor_qtd = [] # matriz a qual conterá os elementos e suas respectivas contagens

    if bins == None:
        for i in range(freq_total):
            linha = []

            # verifica se o elemento i de v já está presente ou não na matriz
            # valor_qtd, de modo que só irá acrescentar o referido elemento e
            # a quantidade de vezes que ele aparece em v se ele ainda não estiver
            # em valor_qtd
            if find_column(valor_qtd, 0, v[i]) == False:

                # se dropna for verdadeiro e v[i] igual a nan, então sua contagem não será incluida
                if dropna == True and math.isnan(v[i]):
                    continue

                # caso contrário, usamos o vetor auxiliar linha para inserir o elemento e sua respectiva contagem

                linha.append(v[i])

                # se normalize é igual a false, então a frequência absoluta simples do elemento será inseida no vetor
                if normalize == False:
                    linha.append(count_value_series(v, v[i]))

                # caso contrário, a frequência relativa (freq. absoluta/freq. total) será inserida no vetor
                else:
                    linha.append(count_value_series(v, v[i])/freq_total)

                # depois, inserimos o vetor auxiliar como uma nova linha de valor_qtd
                valor_qtd.append(linha)

    else:
        maior_v = max_value(v)
        menor_v = min_value(v)

        amplitude = (maior_v-menor_v)/bins

        inferior = menor_v-0.005
        superior = menor_v + amplitude

        for i in range(bins):
            linha = []
            cont = 0

            linha.append("("+str(inferior)+", "+str(superior)+"]")

            for j in range(len(v)):
                if v[j] > inferior and v[j] <= superior:
                    cont+=1

            linha.append(cont)
            valor_qtd.append(linha)

            inferior = superior
            superior += amplitude

    # depois, ordenar a matriz valor_qtd de acordo com o valor de ascending e sort
    if sort == True and ascending == False:
        valor_qtd.sort(reverse=True,key=key_series)
    elif sort == True and ascending == True:
        valor_qtd.sort(key=key_series)

    return valor_qtd

def find_value (series, e):
    """
    Recebe vetor series e um elemento e que pode ou não estar em vetor.
    Retorna True se e estiver em vetor e False caso contrário.
    """
    for i in range(len(series)):
        if series[i] == e:
            return True

    return False

def count_row (df, index, col, subset):
    """
    Conta quantas vezes uma linha de df aparece na matriz.
    """

    cont = 0
    aux = True

    for i in range(shape(df)[0]):
        aux = True

        for j in range(shape(df)[1]):
            if aux == True:
              if find_value(subset, col[j]):
                  if dtype(index[j]) != 'str' and math.isnan(index[j]):
                      if math.isnan(df[i][j]):
                          aux = True
                      else:
                          aux = False

                  else:
                      if df[i][j] == index[j]:
                          aux = True
                      else:
                          aux = False
                          break

        if aux == True:
            cont+=1

    return cont

def key_df(m):
    return m[len(m)-1]

def df_value_counts(df, col, subset=None, normalize=False, sort=True, ascending=False, dropna=True):
    """
    Função recebe uma matriz df e retorna uma matriz contendo a contagem de cada
    linha distinta presente em df, de acordo com os elementos que estão presentes
    em todas as colunas caso subset=None. Caso subset receba uma lista de rótulos
    das colunas, somente essas colunas serão levadas em consideração na contagem.
    Caso normalize==True, a matriz retornada conterá as contagens divididas pelo número
    de linhas. Caso sort=True, as contagens serão ordenadas de acordo com o valor de ascending.
    Se dropna=True, as linhas contendo valores nan serão desconsideradas.
    """

    num_linhas, num_col = shape(df)

    linhas_qtd = []

    aux = []

    if subset == None:
        subset = col.copy()

    for i in range(num_linhas):
        linha = []

        for j in range(num_col):
            # verificando se o elemento a ser inserido no vetor é nan e se dropna é verdadeiro
            if dropna == True and math.isnan(df[i][j]) and find_value(subset, col[j]):
                linha = [] # se for, deixar a linha vazia
                break

            if find_value(subset, col[j]):
                linha.append(df[i][j])

        # verifica se a linha i de v já está presente ou não na matriz e se está vazia
        if (linha in aux) == False and linha != []:

            aux.append(linha.copy())

            if normalize == False:
                linha.append(count_row(df,df[i], col, subset))

            else:
                linha.append(count_row(df,df[i], col, subset)/num_linhas)

            linhas_qtd.append(linha)

    if sort == True and ascending == False:
        linhas_qtd.sort(reverse=True,key=key_df)
    elif sort == True and ascending == True:
        linhas_qtd.sort(key=key_df)

    return linhas_qtd

def count_not_null_column(df, col):
    """
    Recebe uma matriz df e retorna a quantidade de valores não nulos da coluna de índice col.
    """

    numlin, numcol = shape(df)
    cont = 0

    for j in range(numlin):
        if df[j][col] != None:
            cont = cont + 1

    return cont

def types_df (df):
    """
    Recebe uma matriz df e retorna um vetor contendo todos os tipos dos valores
    presentes em df.
    """

    numlin, numcol = shape(df)

    tipos = []

    for i in range(numcol):
        linha = []

        tipo = dtype(df[0][i])

        if  find_column(tipos, 0, tipo) == False:
            linha.append(tipo)
            cont = 0

            for j in range(numcol):
                if dtype(df[0][j]) == tipo:
                    cont+=1
            linha.append(cont)

            tipos.append(linha)

    return tipos

def info(df, col, index, verbose=None, buf=None,  memory_usage=None, show_counts=None):
    """
    Recebe uma matriz df e seus vetores auxiliares contendo os rótulos das linhas
    e colunas col e index, respectivamente, e imprime informações sobre df, de acordo com os
    valores recebidos via parâmetro: verbose define se todas as informações serão
    impressas, buf define onde será impressa a saída, memory_usage define se será
    impresso o uso de memória de df e show_counts define se as contagens não nulas deverão ser
    impressas ou não.
    """

    numlin, numcol = shape(df)

    if buf == None or buf == sys.stdout:

        if df == []:
            print("RangeIndex:", numlin, "entries")
            print("Empty DataFrame")

        else:
            print("RangeIndex:", numlin, "entries,", index[0],"to", index[numlin-1])

            if (verbose == None or verbose == True):
                print("Data columns (total",numcol,"columns):")

                if show_counts == None or show_counts == True:

                    print('{0:^3} {1:10} {2:14} {3:10}'.format('#','Column','Non-Null Count','Dtype'))

                    print('{0:^3} {1:10} {2:14} {3:10}'.format('---','------','--------------','-----'))

                for i in range(numcol):
                    print('{0:^3} {1:<10} {2:<14} {3:<10}'.format(i,col[i],str(count_not_null_column(df,i))+' non-null',dtype(df[0][i])))

            else:
                print("Columns:", numcol, "entries,", col[0], "to", col[numcol-1])

            print("dtypes: ", end="")

            tipos = types_df(df)
            numtipos = len(tipos)

            for i in range(numtipos-1):
                print(tipos[i][0],"(",tipos[i][1],"), ",sep="",end="")
            print(tipos[numtipos-1][0],"(",tipos[numtipos-1][1],")",sep="")

            if memory_usage == True or memory_usage == None:
                print("memory usage: ",(sys.getsizeof(df)+sys.getsizeof(index)+sys.getsizeof(col)),"+ bytes",sep="")
            elif memory_usage == 'deep':
                print("memory usage: ",(asizeof.asizeof(df)+asizeof.asizeof(index)+asizeof.asizeof(col)),"+ bytes",sep="")

    elif isinstance(buf,io.IOBase) and buf.writable:

        if df == []:
            buf.write("RangeIndex:"+ str(numlin)+ "entries\n")
            buf.write("Empty DataFrame")

        else:
            buf.write("RangeIndex:"+ str(numlin)+ " entries "+ str(index[0])+" to "+ str(index[numlin-1])+"\n")

            if (verbose == None or verbose == True):
                buf.write("Data columns (total "+str(numcol)+" columns):"+"\n")

                if show_counts == None or show_counts == True:

                    buf.write('{0:^3} {1:10} {2:14} {3:10}'.format('#','Column','Non-Null Count','Dtype')+"\n")

                    buf.write('{0:^3} {1:10} {2:14} {3:10}'.format('---','------','--------------','-----')+"\n")

                for i in range(numcol):
                    buf.write('{0:^3} {1:<10} {2:<14} {3:<10}'.format(i,col[i],str(count_not_null_column(df,i))+' non-null',dtype(df[0][i]))+"\n")

            else:
                buf.write("Columns:", numcol, "entries,", col[0], "to", col[numcol-1]+"\n")

            buf.write("dtypes: ")

            tipos = types_df(df)
            numtipos = len(tipos)

            for i in range(numtipos-1):
                buf.write(str(tipos[i][0])+"("+str(tipos[i][1])+") + ")
            buf.write(str(tipos[numtipos-1][0])+"("+str(tipos[numtipos-1][1])+")"+"\n")

            if memory_usage == True or memory_usage == None:
                buf.write("memory usage: "+str((sys.getsizeof(df)+sys.getsizeof(index)+sys.getsizeof(col)))+"+ bytes"+"\n")
            elif memory_usage == 'deep':
                buf.write("memory usage: "+str(asizeof.asizeof(df)+asizeof.asizeof(index)+asizeof.asizeof(col))+"+ bytes"+"\n")
                
def count_not_null_column(df, col):
    """
    Recebe uma matriz df e retorna a quantidade de valores não nulos da coluna de índice col
    """
    numlin, numcol = shape(df)
    cont = 0.0

    for j in range(numlin):
        if df[j][col] != None:
            cont = cont + 1

    return cont

def max_value_col (df, col):
    """
    Recebe uma matriz df e retorna o maior elemento da coluna de índice col
    """
    dimensao = shape(df)

    maior = df[0][col]
    for i in range(dimensao[0]):
        if df[i][col] > maior:
            maior = df[i][col]

    return maior

def min_value_col (df, col):
    """
    Recebe uma matriz df e retorna o menor elemento da coluna de índice col
    """
    dimensao = shape(df)

    menor = df[0][col]
    for i in range(dimensao[0]):
        if null_check(df[i][col]) == True:
            menor = df[i][col]
            break
        
        if df[i][col] < menor:
            menor = df[i][col]

    return menor

def std_ind_col(df, col):
    """
    Recebe uma matriz df e retorna o desvio padrão da coluna de índice col
    """
    dimensao = shape(df)

    somatoria = 0

    for i in range(dimensao[0]):
        somatoria += (df[i][col]-mean_column(df,col))**2

    return math.sqrt(somatoria/(dimensao[0]-1))

def mean_column(df, col):
    """
    Recebe uma matriz df e retorna a média dos valores da coluna de índice col
    """
    numlin, numcol = shape(df)

    contador = 0

    for j in range(numlin):
        contador += df[j][col]

    return contador/numlin

def transform_col_series(df,col):
    """
    Recebe uma matriz df e um índice col e retorna um vetor contendo os elementos
    da coluna col de df
    """
    vetor = []
    numlinhas, numcol = shape(df)

    for i in range(numlinhas):
        vetor.append(df[i][col])

    return vetor

def get_percentile(df,col, p):
    """
    Recebe uma matriz df, um índice col e um percentil p e retorna o valor do
    referido percentil na coluna col de df.
    """
    numlinhas, numcol = shape(df)
    pos = p * (numlinhas-1)

    v = transform_col_series(df,col)

    v.sort()

    if(type(pos) == int):
        return v[pos]
    else:
        posinf = math.floor(pos)

        possup = math.ceil(pos)
        return v[posinf] + (pos - posinf) * (v[possup] - v[posinf])

def count_value_in_col(df,col,e):
    """
    Recebe uma matriz df, um índice col e um elemento e, retorna a quantidade de
    vezes que e aparece na coluna col em df.
    """
    numlin, numcol = shape(df)
    cont = 0

    for i in range(numlin):
        if df[i][col] == e:
            cont+= 1
    return cont

def most_common_column_value(df,col):
    """
    Recebe uma matriz df e retorna o valor mais comum da coluna de índice col.
    """
    freq = 0
    top = df[0][col]
    aux = 0

    numlin, numcol = shape(df)

    for i in range(numlin):
       aux = count_value_in_col(df,col,df[i][col])

       if aux > freq:
           freq = aux
           top = df[i][col]

    return top, freq

def count_unique_values(df, col):
    """
    Recebe uma matriz df e retorna a quantidade de valores únicos na coluna de índe col.
    """
    elementos_col = transform_col_series(df, col)

    valores_unicos = set(elementos_col)

    return len(valores_unicos)

def has_numeric_values(df):
    """
    Recebe uma matriz df e verifica se esta possui valores númericos.
    """
    numlin, numcol = shape(df)

    for i in range(numcol):
        if type(df[0][i]) == int or type(df[0][i]) == float:
            return True

    return False

def has_not_numeric_values(df):
    """
    Recebe uma matriz df e verifica se esta possui valores não numéricos.
    """
    numlin, numcol = shape(df)

    for i in range(numcol):
        if type(df[0][i]) != int and type(df[0][i]) != float:
            return True

    return False

def describe(df, col, percentiles=None, include=None, exclude=None):
    """
    Recebe uma matriz df e calcula os seguintes valores para suas colunas númericas:
    contagem de valores não nulos, média, desvio padrão, valor mínimo, valor máximo e os percentis.
    Para colunas não-numéricas, que no contexto da função chamamos de objetos, verifica as
    seguintes características: contagem de valores não nulos, contagem de valores únicos, valor que mais
    aparece na coluna e frequência do valor que mais aparece na coluna.
    """

    number = False
    obj = False
    ind = 0

    if(include == "all"):
        temnum = has_numeric_values(df)
        temobj = has_not_numeric_values(df)

        if temnum == True:
            number = True
        if temobj == True:
            obj = True
            ind = 3

    elif include != None:
        if "number" in include:
            number = True
        if "object" in include:
            obj = True
    else:
        number = True

    if exclude != None:
        if "number" in exclude:
            number = False
        if "object" in exclude:
            obj = False

    saida = []
    saida.append([" "])
    saida.append(["count"])

    if obj == True:
        saida.append(["unique"])
        saida.append(["top"])
        saida.append(["freq"])
    if number == True:
        saida.append(["mean"])
        saida.append(["std"])
        saida.append(["min"])
        if percentiles != None:
            percentiles.append(0.5)
            percentiles.sort()
            for i in range(len(percentiles)):
                saida.append([(str(int(percentiles[i]*100))+"%")])
        else:
            percentiles = []
            percentiles.append(0.25)
            percentiles.append(0.5)
            percentiles.append(0.75)
            saida.append(["25%"])
            saida.append(["50%"])
            saida.append(["75%"])
        saida.append(["max"])

    numlinhas, numcol = shape(df)

    for j in range(numcol):
        tipo = type(df[0][j])
        eh_num = True

        if (tipo != float and tipo != int):
            eh_num = False

        if (eh_num == True and number == True) or (eh_num == False and obj == True):
            saida[0].append(col[j])
            saida[1].append(count_not_null_column(df,j))

            if obj == True:
                if eh_num == False:
                    saida[2].append(count_unique_values(df,j))
                    t, f = most_common_column_value(df,j)
                    saida[3].append(t)
                    saida[4].append(f)
                else:
                    saida[2].append("NaN")
                    saida[3].append("NaN")
                    saida[4].append("NaN")
            if number == True:
                if eh_num == True:
                    saida[2+ind].append(mean_column(df,j))
                    saida[3+ind].append(std_ind_col(df,j))
                    saida[4+ind].append(min_value_col(df,j))
                    for i in range(len(percentiles)):
                        saida[5+i+ind].append(get_percentile(df,j,percentiles[i]))
                    saida[5+len(percentiles)+ind].append(max_value_col(df,j))
                else:
                    saida[2+ind].append("NaN")
                    saida[3+ind].append("NaN")
                    saida[4+ind].append("NaN")
                    for i in range(len(percentiles)):
                        saida[5+i+ind].append("NaN")
                    saida[5+len(percentiles)+ind].append("NaN")

    numlinhas_saida, numcol_saida = shape(saida)

    for i in range(numlinhas_saida):
        print('{0:<6}'.format(saida[i][0]), end=" ")
        for j in range(1, numcol_saida-1):
            if type(saida[i][j]) == float:
                print('{0:>10.4f}'.format(saida[i][j]), end=" ")
            else:
                print('{0:>10}'.format(saida[i][j]), end=" ")
        print('{0:>10}'.format(saida[i][j+1]))

    return saida

def quick_sort_col(a, by, index, ascending, ini=0, fim=None):
    """
    Algoritmo quick sort recursivo que ordena as linhas de a por coluna.
    """
    fim = fim if fim is not None else len(a)
    if ini < fim:
        pp = partition_col(a, ini, fim, by, index, ascending)
        quick_sort_col(a, by, index, ascending, ini, pp)
        quick_sort_col(a, by, index, ascending, pp + 1, fim)
    return a

def partition_col(a, ini, fim, by, index, ascending):
    """
    Realiza a etapa de partição do algoritmo quick sort por coluna, ordenando os valores das linhas de a.
    """
    pivo = a[fim - 1][by]

    for i in range(ini, fim):
        if ascending == True:
            if a[i][by] <= pivo:
                a[i], a[ini] = a[ini], a[i]
                index[i], index[ini] = index[ini], index[i]
                ini += 1

        else:
            if a[i][by] >= pivo:
                a[i], a[ini] = a[ini], a[i]
                index[i], index[ini] = index[ini], index[i]
                ini += 1

    return ini - 1

def quick_sort_index(a, by, columns, ascending, ini=0, fim=None):
    """
    Algoritmo quick sort recursivo que ordena as colunas de a por linha.
    """
    fim = fim if fim is not None else len(a[0])
    if ini < fim:
        pp = partition_index(a, ini, fim, by, columns, ascending)
        quick_sort_index(a, by, columns, ascending, ini, pp)
        quick_sort_index(a, by, columns, ascending, pp + 1, fim)
    return a

def partition_index(a, ini, fim, by, columns, ascending):
    """
    Realiza a etapa de partição do algoritmo quick sort por linha, ordenando os valores das colunas de a.
    """
    pivo = a[by][fim - 1]

    numlin, numcol = shape(a)

    for i in range(ini, fim):

        if ascending == True:
            if a[by][i] <= pivo:
                for y in range(numlin):
                    a[y][i], a[y][ini] = a[y][ini], a[y][i]
                columns[i], columns[ini] = columns[ini], columns[i]
                ini += 1

        else:
            if a[by][i] >= pivo:
                for y in range(numlin):
                    a[y][i], a[y][ini] = a[y][ini], a[y][i]
                print(columns)
                columns[i], columns[ini] = columns[ini], columns[i]
                ini += 1

    return ini - 1

def find_index(rotulos, nome):
    """
    Procura o valor do índice de um rótulo (parâmetro nome) em uma lista de
    rótulos (parâmetro rotulos).
    """
    tamanho = len(rotulos)
    for i in range(tamanho):
        if rotulos[i] == nome:
            return i

def organize_nan(df, index, columns, by, axis, position):
    """
    Organiza os valores nulos/nan do df na frente de todos os outros valores
    (caso position='first') ou atrás de todos os valores (caso position='last').
    """
    copy_df = []
    copy_ind = []
    copy_col = []

    numlin, numcol = shape(df)

    ini = 0
    fim = 0

    if axis == 0:
        fim = numlin
        cont = 0
        if position == 'last':
            for i in range(numlin):
                if null_check(df[i][by]) == False:
                    copy_df.append(df[i])
                    copy_ind.append(index[i])
                    cont+=1

            for i in range(numlin):
                if null_check(df[i][by]):
                    copy_df.append(df[i])
                    copy_ind.append(index[i])

            fim = cont
        else:

            for i in range(numlin):
                if null_check(df[i][by]):
                    cont+=1
                    copy_df.append(df[i])
                    copy_ind.append(index[i])

            for i in range(numlin):
                if null_check(df[i][by]) == False:
                    copy_df.append(df[i])
                    copy_ind.append(index[i])
            ini = cont
        return copy_df, copy_ind, ini, fim

    else:
        fim = numcol
        for i in range(numlin):
            copy_df.append([])

        if position == 'last':
            cont = 0
            for i in range(numcol):
                if null_check(df[by][i]) == False:
                    cont+=1
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            for i in range(numcol):
                if null_check(df[by][i]):
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            fim = cont

        else:
            cont = 0
            for i in range(numcol):
                if null_check(df[by][i]):
                    cont+=1
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            for i in range(numcol):
                if null_check(df[by][i]) == False:
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            ini = cont

        return copy_df, copy_col, ini, fim

def sort_values(df, by, index, columns, *, axis=0, ascending=True, inplace=False, na_position='last', ignore_index=False):
    """
    Ordena as linhas/colunas de um DataFrame de acordo com os valores de uma determinada linha/coluna.
    Seu valor de retorno se inplace=False será um DataFrame com os mesmos dados do
    original, porém ordenado, a depender dos valores enviados por parâmetro. Caso contrário,
    a função não retorna nada e a ordenação será realizada no df original.
    """

    numlin, numcol = shape(df)

    copy_index = []
    copy_columns = []
    copy_df = []

    if inplace == True:
        if axis == 0:
            pos_by = find_index(columns, by)
            copy_df, copy_index, ini, fim = organize_nan(df,index, columns, pos_by,axis,na_position)

            df.clear()
            index.clear()

            df.extend(copy_df)
            index.extend(copy_index)

            df = quick_sort_col(copy_df, by, index, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numlin):
                    index[i] = i
        else:
            pos_by = find_index(index, by)
            copy_df, copy_columns, ini, fim = organize_nan(df,index, columns, pos_by,axis,na_position)

            df.clear()
            columns.clear()

            df.extend(copy_df)
            columns.extend(copy_columns)

            df = quick_sort_index(copy_df, pos_by, columns, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numcol):
                    columns[i] = i

    else:
        if axis == 0:
            pos_by = find_index(columns, by)

            copy_df, copy_index, ini, fim = organize_nan(df,index, columns, pos_by,axis,na_position)

            copy_df = quick_sort_col(copy_df, pos_by, copy_index, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numlin):
                    copy_index[i] = i

            copy_columns.extend(columns)
        else:
            pos_by = find_index(index, by)
            copy_df, copy_columns, ini, fim = organize_nan(df,index, columns, pos_by,axis,na_position)

            copy_df = quick_sort_index(copy_df, pos_by, copy_columns, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numcol):
                    copy_columns[i] = i

            copy_index.extend(index)

        return copy_df, copy_index, copy_columns
    
def min_index_in_col(df, col):
    """
    Encontra o índice da linha do menor valor presente na matriz df e coluna col.
    """
    cont = 0
    menor = None
    pos_menor = 0
    dimensao = shape(df)

    while(cont < dimensao[0]):
        if null_check(df[cont][col]) == False:
            menor = df[cont][col]
            break
        cont+=1

    pos_menor = cont

    if menor != None:
        for i in range(dimensao[0]):
            if null_check(df[i][col]) == False and df[i][col] < menor:
                menor = df[i][col]
                pos_menor = i

    return pos_menor

def verify_null_col (df,col):
    """
    Recebe uma matriz df e um índice de coluna col e retorna o índice
    da linha que possuir valor nulo na referida coluna. Caso não houver, retorna -1.
    """
    dimensao = shape(df)

    for i in range(dimensao[0]):
        if null_check(df[i][col]) == True:
            return i
    return -1

def verify_null_index (df,ind):
    """
    Recebe uma matriz df e um índice de linha e retorna o índice
    da coluna que possuir valor nulo na referida linha. Caso não houver, retorna -1.
    """
    dimensao = shape(df)

    for i in range(dimensao[1]):
        if null_check(df[ind][i]) == True:
            return i
    return -1

def min_col_in_ind(df, ind):
    """
    Encontra o índice da coluna do menor valor presente na matriz df e linha ind.
    """
    cont = 0
    menor = None
    pos_menor = 0
    dimensao = shape(df)

    while(cont < dimensao[1]):
        if null_check(df[ind][cont]) == False:
            menor = df[ind][cont]
            break
        cont+=1

    pos_menor = cont

    if menor != None:

        for i in range(dimensao[1]):
            if null_check(df[ind][i]) == False and df[ind][i] < menor:
                menor = df[ind][i]
                pos_menor = i

    return pos_menor

def idxmin(df, index, columns, axis=0,skipna=True):
    """
    Recebe uma matriz df e retorna uma matriz contendo o rótulo da linha/coluna
    do menor valor de todas as colunas/linhas. Caso axis = True, encontra e adiciona a matriz de retorno
    o rótulo das linhas que possuem o menor valor de cada coluna. Caso contrário, encontra e adiciona a matriz de retorno
    o rótulo das colunas que possuem o menor valor em cada linha.
    Caso skipna=True, considera os valores nulos como menor valor, se houver.
    """
    new_df = []

    numlin, numcol = shape(df)

    if axis == 0 or axis == 'index':
        for i in range(numcol):
            linha = []
            linha.append(columns[i])

            if skipna == True:
                aux = verify_null_col(df,i)
                if aux != -1:
                    linha.append(index[aux])
                else:
                    linha.append(index[min_index_in_col(df,i)])
            else:
                linha.append(index[min_index_in_col(df,i)])
            new_df.append(linha)

    else:
        for i in range(numlin):
            linha = []
            linha.append(index[i])

            if skipna == True:
                aux = verify_null_index(df,i)
                if aux != -1:
                    linha.append(columns[aux])
                else:
                    linha.append(columns[min_col_in_ind(df,i)])
            else:
                linha.append(columns[min_col_in_ind(df,i)])
            new_df.append(linha)

    return new_df

def max_ind_in_col(df, col):
    """
    Encontra o índice da linha do maior valor presente na matriz df e coluna col.
    """
    cont = 0
    maior = None
    pos_maior = 0
    dimensao = shape(df)

    while(cont < dimensao[0]):
        if null_check(df[cont][col]) == False:
            maior = df[cont][col]
            break
        cont+=1

    pos_maior = cont

    if maior != None:
        for i in range(dimensao[0]):
            if null_check(df[i][col]) == False and df[i][col] > maior:
                maior = df[i][col]
                pos_maior = i

    return pos_maior

def max_col_in_ind(df, ind):
    """
    Encontra o índice da coluna do maior valor presente na matriz df e linha ind.
    """
    cont = 0
    maior = None
    pos_maior = 0
    dimensao = shape(df)

    while(cont < dimensao[1]):
        if null_check(df[ind][cont]) == False:
            maior = df[ind][cont]
            break
        cont+=1

    pos_maior = cont

    if maior != None:

        for i in range(dimensao[1]):
            if null_check(df[ind][i]) == False and df[ind][i] > maior:
                maior = df[ind][i]
                pos_maior = i

    return pos_maior

def idxmax(df, index, columns, axis=0):
    """
    Recebe uma matriz df e retorna uma matriz contendo o rótulo da linha/coluna
    do maior valor de todas as colunas/linhas. Caso axis = True, encontra e adiciona a matriz de retorno
    o rótulo das linhas que possuem o maior valor de cada coluna. Caso contrário, encontra e adiciona a matriz de retorno
    o rótulo das colunas que possuem o maior valor em cada linha.
    """
    new_df = []

    numlin, numcol = shape(df)

    if axis == 0 or axis == 'index':
        for i in range(numcol):
            linha = []
            linha.append(columns[i])
            linha.append(index[max_ind_in_col(df,i)])
            new_df.append(linha)

    else:
        for i in range(numlin):
            linha = []
            linha.append(index[i])
            linha.append(columns[max_col_in_ind(df,i)])
            new_df.append(linha)

    return new_df

# FUNÇÕES AUXILIARES

def verify_condition(v, na_rep, float_format, string_csv):

    """
    Função que verifica os argumentos de determinados parâmetros da função to_csv
    Seus parâmetros são:
     - v: Valor de uma célula do DataFrame
     - na_rep: Valor que será preenchido por padrão em caso de apresentar valores indeterminados/indefinidos
     - float_format: Define como será o formato dos valores float (ex:'.2f%')
     - string_csv: String que está armazenando o DataFrame
    Retorna: Uma string
    """

    if v == None or v == 'nan':
        string_csv += str(na_rep)

    elif float_format != None and isinstance(v, float):
        if isinstance(float_format, str):
            txt = '{:' + str(float_format) + '}'
            string_csv += txt.format(float(v))

        elif callable(float_format):
            string_csv += str(float_format(v))

    else:
        string_csv += str(v)

    return string_csv

def verify_columns(labels, columns):

    """
    Função que retorna os indexes numéricos das colunas
    Seus parâmetros são:
     - labels: Rótulos das colunas do DataFrame
     - columns: Colunas desejadas
    Retorna: Uma lista ou None (em caso de erro)
    """

    len_c = len(columns)

    list_aux = [None]*len_c
    aux = 0

    for i in range(len_c):
        for j in range(len(labels)):
            if str(columns[i]) == str(labels[j]):
                list_aux[aux] = j
                aux += 1

        if aux != i+1:
            return "Erro: A coluna " + str(columns[i]) + " não é válida" # Pensar em uma mensagem de erro melhor

    if aux == len_c:
        return list_aux

def verify_correspondence(left_row, col_l, right_row, col_r, cols, cols_aux, suffixes):

    """
    Função que verifica se há correspondência de valores nos DataFrames em colunas específicas
    Seus parâmetros são:
     - left_row: Recebe uma linha do primeiro DataFrame
     - col_l: Lista com os rótulos das colunas do primeiro DataFrame
     - right_row: Recebe uma linha do segundo DataFrame
     - col_r: Lista com os rótulos das colunas do segundo DataFrame
     - cols: Colunas que serã utilizadas como parâmetro para a verificação
     - cols_aux: Auxiliar de cols para quando seja especificado left_on e right_on, no qual este representa right_on
    Retorna: True caso houver correspondência em TODAS as colunas, se não, False
    """

    count = 0

    if cols_aux == None:
        cols_aux = cols

    # For externo que percorre as colunas (cols)
    # Um único for serve para as duas listas, cols e cols_aux, visto que o valor de cols[0] tem que corresponder a cols_aux[0] e assim sucessivamente
    for i in range(len(cols)):

        if cols[i] in col_l and cols_aux[i] in col_r:
            if left_row[col_l.index(cols[i])] == right_row[col_r.index(cols_aux[i])]:
                count += 1
        elif str(cols[i])+str(suffixes[0]) in col_l and str(cols_aux[i])+str(suffixes[1]) in col_r:
            if left_row[col_l.index(str(cols[i])+str(suffixes[0]))] == right_row[col_r.index(str(cols_aux[i])+str(suffixes[1]))]:
                count += 1

    if count == len(cols): # Verifica se o contador é igual a quantidade de elementos passados em cols, em que se for, significa que houve
                          # correspondência de valores em todas as colunas
        return True
    else:
        return False

def verify_row(l1, l2, col_result, cols, s):

    """
    Função que verifica qual linha é maior a partir das chaves de junção
    Seus parâmetros são:
     - l1: Uma linha (vetor)
     - l2: Outra linha (vetor) que será comparado com l1
     - col_result: Lista com os rótulos das colunas de l1 e l2
     - cols: Colunas de junção
    Retorna: True se uma chave for maior que a chave correspondente da outra linha e
             False se a chave não for maior ou se todas as chaves forem iguais
    """

    for i in range(len(cols)):

        if cols[i] in col_result:
            c = col_result.index(cols[i])

            if l1[c] > l2[c]:
                return True
            elif l1[c] < l2[c]:
                return False
        elif str(cols[i])+str(s) in col_result:
            c = col_result.index(str(cols[i])+str(s))

            if l1[c] > l2[c]:
                return True
            elif l1[c] < l2[c]:
                return False

    return False

def filter_df(df, col, ind, mask):

    """
    Função que recebe um máscara (lista com valores do tipo bool), que indica qual linha será filtrada
    do DataFrame
    Seus parâmetros são:
     - df: Matriz com os dados (DataFrame) que serão filtrados
     - col: Lista com os rótulos das colunas do DataFrame
     - ind: Lista com os indexes das linhas do DataFrame
     - mask: Lista com valores do tipo bool, no qual cada elemento representa uma respectiva linha do
       DataFrame, indicando qual linha será mantida (True) e qual será "removida" (False)
    Retorna: Um DataFrame (df, col, ind) com as linhas filtradas
    """

    df_result = []
    col_result = col.copy()
    ind_result = []

    for i in range(len(mask)):

        if mask[i]:
            df_result.append(df[i])
            ind_result.append(ind[i])

    return df_result, col_result, ind_result

def verify_tolerance(i, labels, tolerance):

    """
    Função que verifica se um determinado index está dentro da tolerância especificada
    Seus parâmetros são:
     - i: Index que será verificado
     - labels: Lista com os indexes antigos que servirá como critério
     - tolerancia: A tolerância permitida para relacionar o index i com um index de labels
    Retorna: A posição do index de labels se satisfazer o critério de tolerância ou -1, para caso não haja
    correspondência
    """

    aux = None

    for j in range(len(labels)):

        if abs(labels[j] - i) <= tolerance:

            if aux == None or abs(labels[j]-i) < aux:
                aux = labels[j]

    if aux != None:
        return labels.index(aux)
    else:
        return -1

def fill_method(df, list_indexes, axis, method, limit):

    """
    Função que recebe um DataFrame com brechas (NaN) e as preenche de acordo com as especificações de método,
    limite, eixo e as linhas/colunas que deverão ser completadas
    Seus parâmetros são:
     - df: DataFrame no qual será realizado a operação de preenchimento
     - list_indexes: Lista com os indexes das linhas/colunas que serão preenchidas
     - axis: Eixo que será realizado a operação
     - method: Método de preenchimento
     - limit: Limite para quantas brechas um valor poderá preencher
    Retorna: Nada
    """

    nan = (float("nan"), "NaN", "nan", None)

    if limit != None:
        limit -= 1

    if method == 'pad' or method == 'ffill':

        if axis == 0:
            for j in range(len(df[0])):
                obs = None
                count = 0

                for i in range(len(df)):
                    if (df[i][j] in nan or (isinstance(df[i][j], float) and numpy.isnan(df[i][j]))) and i in list_indexes and obs != None:
                        if limit == None or (limit != None and count < limit):
                            df[i][j] = obs
                            count += 1
                    elif not df[i][j] in nan and not (isinstance(df[i][j], float) and numpy.isnan(df[i][j])):
                        obs = df[i][j]
                        count = 0

        elif axis == 1: # A ser testado
            for i in range(len(df)):
                obs = None
                count = 0

                for j in range(len(df[i])):
                    if (df[i][j] in nan or (isinstance(df[i][j], float) and numpy.isnan(df[i][j]))) and j in list_indexes and obs != None:
                        if limit == None or (limit != None and count < limit):
                            df[i][j] = obs
                            count += 1
                    elif not df[i][j] in nan and not (isinstance(df[i][j], float) and numpy.isnan(df[i][j])):
                        obs = df[i][j]
                        count = 0

    elif method == 'backfill' or method == 'bfill':
        if axis == 0:
            for j in range(len(df[0])):
                obs = None
                count = 0

                for i in range(len(df)-1, -1, -1):
                    if (df[i][j] in nan or (isinstance(df[i][j], float) and numpy.isnan(df[i][j]))) and i in list_indexes and obs != None:
                        if limit == None or (limit != None and count < limit):
                            df[i][j] = obs
                            count += 1
                    elif not df[i][j] in nan and not (isinstance(df[i][j], float) and numpy.isnan(df[i][j])):
                        obs = df[i][j]
                        count = 0

        elif axis == 1:
            for i in range(len(df)):
                obs = None
                count = 0

                for j in range(len(df[i])-1, -1, -1):
                    if (df[i][j] in nan or (isinstance(df[i][j], float) and numpy.isnan(df[i][j]))) and j in list_indexes and obs != None:
                        if limit == None or (limit != None and count < limit):
                            df[i][j] = obs
                            count += 1
                    elif not df[i][j] in nan and not (isinstance(df[i][j], float) and numpy.isnan(df[i][j])):
                        obs = df[i][j]
                        count = 0

    elif method == 'nearest':
        if axis == 0:
            for j in range(len(df[0])):
                dict_limit = {}

                for i in range(len(df)):
                    k = 1
                    aux = True
                    obs = None

                    while k < len(df) and aux:
                        if i+k < len(df) and not df[i+k][j] in nan and not (isinstance(df[i+k][j], float) and numpy.isnan(df[i+k][j])):
                            obs = df[i+k][j]
                        elif i-k >= 0 and not df[i-k][j] in nan and not (isinstance(df[i-k][j], float) and numpy.isnan(df[i-k][j])):
                            obs = df[i-k][j]

                        if obs != None and not obs in dict_limit.keys():
                            dict_limit.update({obs:0})

                        if (df[i][j] in nan or (isinstance(df[i][j], float) and numpy.isnan(df[i][j]))) and i in list_indexes and obs != None:
                            if limit == None or (limit != None and dict_limit.get(obs) < limit):
                                df[i][j] = obs
                                dict_limit[obs] += 1
                                aux = False
                            else:
                                aux = False
                        k += 1
        elif axis == 1:
            for i in range(len(df)):
                dict_limit = {}

                for j in range(len(df[i])):
                    k = 1
                    aux = True
                    obs = None

                    while k < len(df[i]) and aux:
                        if j+k < len(df[i]) and not df[i][j+k] in nan and not (isinstance(df[i][j+k], float) and numpy.isnan(df[i][j+k])):
                            obs = df[i][j+k]
                        elif j-k >= 0 and not df[i][j-k] in nan and not (isinstance(df[i][j-k], float) and numpy.isnan(df[i][j-k])):
                            obs = df[i][j-k]

                        if obs != None and not obs in dict_limit.keys():
                            dict_limit.update({obs:0})

                        if (df[i][j] in nan or (isinstance(df[i][j], float) and numpy.isnan(df[i][j]))) and j in list_indexes and obs != None:
                            if limit == None or (limit != None and dict_limit.get(obs) < limit):
                                df[i][j] = obs
                                dict_limit[obs] += 1
                                aux = False
                            else:
                                aux = False
                        k += 1

def verify_function(name):

    """
    Função que verifica se existe uma função nativa do python a partir de um nome específico.
    Seus parâmetros são:
     - name: String com o nome que será verificado
    Retorna: True (1) para caso exista e False (0) para caso não exista.
    """

    return hasattr(builtins, name) and callable(getattr(builtins, name))

def apply_function(elements, func=None, *args, **kwargs):

    """
    Função que aplica uma determinada função sobre uma lista.
    Seus parâmetros são:
     - elements: Lista sobre qual será aplicada a função
     - func: Função a ser aplicada
     - *args: Argumentos posicionais adicionais para a aplicação da função
     - **kwargs: Argumentos nomeados adicionais para a aplicação da função
    Retorna: Um único valor com o resultado da aplicação da função sobre a lista
    """

    if callable(func): # Verifica se a função é chamável
        return func(elements, *args, **kwargs)

    elif isinstance(func, str): # Verifica se é o nome da função (String)
        if verify_function(func): # Verifica se ela existe na integração do Python
            return getattr(builtins, func)(elements, *args, **kwargs)

        elif globals().get(func) and callable(globals().get(func)): # Verifica se a função existe no escopo global e se é chamável
            return globals()[func](elements, *args, **kwargs)

def mean(x): # Função auxiliar para testagem
    return sum(x) / len(x)

def largest_group(l1, l2, col_result, by, as_index):

  """
  Função que verifica qual é o maior grupo dado duas linhas e as colunas de comparação.
  Seus parâmetros são:
   - l1: Uma linha (vetor)
   - l2: Outra linha (vetor) que será comparado com l1
   - col_result: Lista com os rótulos das colunas de l1 e l2
   - by: Define a(s) coluna(s) de parâmetro para agrupamento
   - as_index: Indica se as chaves de agrupamento serão utilizados como index no DataFrame resultante ou não
  Retorna: True se a linha l1 for maior que a linha l2 e False caso contrário.
  """

  if as_index == True:
        if isinstance(by, list):
            for i in range(len(by)):
                if str(l1[i]) > str(l2[i]):
                    return True
                else:
                    return False
        else:
            if str(l1) > str(l2):
                return True
            else:
                return False
  else:
      if isinstance(by, list):
          for i in range(len(by)):

              if by[i] in col_result:
                  aux_ind = col_result.index(by[i])

                  if str(l1[aux_ind]) > str(l2[aux_ind]):
                      return True
                  else:
                      return False
      else:
          if by in col_result:
              aux_ind = col_result.index(by)

              if str(l1[aux_ind]) > str(l2[aux_ind]):
                  return True
              else:
                  return False

def nan_list(elements):

    """
    Função que verifica se algum valor de uma lista é NaN (Not a Number)
    Seus parâmetros são:
    - elements: Lista a ser verificada
    Retorna: True para caso haja algum valor em elements que seja NaN
    """

    nan = ("nan", "NaN", float('nan'), numpy.nan)
    
    if iter(elements):
        for i in range(len(elements)):
            if elements[i] in nan:
                return True
      
    return False

def check_type(obj):

    """
    Função que recebe um "objeto" (matriz ou vetor) para verificar se é DataFrame ou Series.
    Retorna 1 (True) para DataFrame e 0 (False) para Series.
    """

    if len(obj) == 3:
        return 1
    elif len(obj) == 2:
        return 0

def inner_join(objs, axis=0):

    """
    Função que recebe uma lista de objetos (com vetores e matrizes que representam DataFrames e Series, respectivamente) e verifica, de acordo com a definição
    do parâmetro join='inner', quais serão as colunas/linhas concatenadas.
    Seus parâmetros são:
     - objs: Lista de "objetos" a ser verificado (DataFrames ou Series)
     - axis: Eixo de verificação
    Retorna uma lista com as colunas/linhas que serão concatenadas.
    """

    list_elements = []
    dict_elements = {} # Utilizado para relacionar as colunas/linhas com os DataFrames/Series pertencentes (contabilizado ao final)
    seq = 0 # Sequência do index para objetos do tipo Series

    for i in range(len(objs)):
        obj = objs[i] # Facilitar a manipulação

        if axis == 0 or axis == 'index': # Verificar o nome da coluna em caso de axis=0

            if check_type(obj): # DataFrame
                for j in range(len(obj[1])): # Acessando as colunas do DataFrame (matriz, colunas, indexes)
                    if obj[1][j] not in dict_elements.keys(): # Verifica se a coluna está presente no dicionário como uma chave
                        dict_elements.update({obj[1][j]:[]}) # Se não estiver, adiciona a coluna como uma chave vinculada a um vetor vazio
                        dict_elements.get(obj[1][j]).append(i) # Adiciona o index do objeto ao vetor associado

                    else: # Se a coluna já estiver como chave no dicionário
                        dict_elements.get(obj[1][j]).append(i) # Adiciona o index do objeto ao vetor associado

            else: # Series
                if seq not in dict_elements.keys(): # Verifica se o index sequencial utilizado para Series está presente no dicionário como uma chave
                    dict_elements.update({seq:[]}) # Se não estiver, adiciona o index sequencial como uma chave vinculada a um vetor vazio
                    dict_elements.get(seq).append(i) # Adiciona o index do objeto ao vetor associado
                else:
                    dict_elements.get(seq).append(i) # Adiciona o index do objeto ao vetor associado

                seq += 1 # Incrementa a sequência das Series

        elif axis == 1 or axis == 'columns': # Verificar o nome da linha em caso de axis=1

            if check_type(obj): # DataFrame
                for j in range(len(obj[2])): # Acessando as linhas do DataFrame
                    if obj[2][j] not in dict_elements.keys(): # Verifica se a linha está presente no dicionário como uma chave
                        dict_elements.update({obj[2][j]:[]}) # Se não estiver, adiciona a linha como uma chave vinculada a um vetor vazio
                        dict_elements.get(obj[2][j]).append(i) # Adiciona o index do objeto ao vetor associado

                    else: # Se a linha já estiver como chave no dicionário
                        dict_elements.get(obj[2][j]).append(i) # Adiciona o index do objeto ao vetor associado

            else: # Series
                for j in range(len(obj[1])): # Acessa os indexes da Series
                    if obj[1][j] not in dict_elements.keys(): # Verifica se a linha está presente no dicionário como uma chave
                        dict_elements.update({obj[1][j]:[]}) # Se não estiver, adiciona a linha como uma chave vinculada a um vetor vazio
                        dict_elements.get(obj[1][j]).append(i) # Adiciona o index do objeto ao vetor associado

                    else:
                        dict_elements.get(obj[1][j]).append(i) # Adiciona o index do objeto ao vetor associado

                seq += 1 # Incrementa a sequência das Series

    dictionary = dict_elements.items()
    dictionary = list(dictionary) # Tranforma o objeto do tipo 'dict_items' (resultante da chamada da função items do dicionário)

    for i in range(len(dictionary)):
        if len(dictionary[i][1]) == len(objs): # Compara a quantidade de valores presente no vetor associado a chave com a quantidade de objetos
            list_elements.append(dictionary[i][0]) # Adiciona as colunas/linhas que tiverem a quantidade de objetos que as possuam correspondente a quantidade de objetos

    return list_elements

# FUNÇÕES

def drop(df, col, ind, labels=None, axis=0, index=None, columns=None, inplace=False, errors='raise'):

    """
    Função que remove linhas ou colunas de um DataFrame
    Seus parâmetros são:
     - df: DataFrame no qual será realizada a operção de remoção
     - col: Rótulos das colunas do DataFrame
     - ind: Indexes das linhas do DataFrame
     - labels: Colunas ou linhas que serão removidas
     - axis: Eixo da operção de remoção, em que:
        - 0: Opera em linhas (index)
        - 1: Opera em colunas (columns)
     - index: Parâmetro alternativo para especificação do eixo, equivalente a labels, axis=0
     - columns: Parâmetro alternativo para especificação do eixo, equivalente a labels, axis=1
     - inplace: Define se a remoção será realizada diretamente no DataFrame informado ou se será
       realizado em uma cópia do DataFrame, em que:
        - False: Cria uma cópia e opera a remoção nela
        - True: Opera a remoção diretamente no DataFrame
     - errors: Determina se os erros serão informados (com a interrupção da operação) ou ignorados, em que:
        - 'raise': Informa os erros e interrompe a operação
        - 'ignore': Ignora os erros e continua a operação com as linhas/colunas válidas
    """

    if labels != None and (index != None or columns != None):
        return "Erro: Não é possível especificar ambos os parâmetros 'labels' e 'index/columns'"

    ind_len = len(ind)
    rem = 1 # Variável utilizada para saber se será removida linha e coluna

    if inplace == False:

        # Copia linha por linha
        new_df = [None]*ind_len
        for i in range(ind_len):
            new_df[i] = df[i].copy()

        new_col = col.copy()
        new_ind = ind.copy()
    else:
        new_df = df
        new_col = col
        new_ind = ind

    if index != None:
        labels = index
        axis = 0

    elif columns != None:
        labels = columns
        axis = 1

    if index != None and columns != None:
        rem = 2

    for r in range(rem):
        if labels != None and isinstance(labels, list):
            count = 0

            if axis == 0: # Remoção em linha
                for aux in range(len(labels)):
                    for i in range(ind_len):
                        if i < len(new_ind) and new_ind[i] == labels[aux]:
                            new_df.pop(i)
                            new_ind.pop(i)
                            count += 1

                    # Verifica se alguma linha não foi encontrada no DataFrame
                    # O count (contador) incrementa em 1 toda vez que for removido uma coluna, logo
                    # o contador sempre deverá ser igual ao valor do aux (index auxiliar, que começa em 0)
                    # mais 1, de maneira resumida, se for percorrido um elemento de labels, então
                    # o contador deverá ser igual a 1, visto que 1 valor deveria ser removido
                    if count != aux+1 and errors == "raise":
                        return "Erro: Linha " + str(labels[aux]) + " não foi encontrada."

            elif axis == 1: # Remoção em coluna
                for aux in range(len(labels)):
                    for j in range(len(new_col)):
                        if j < len(new_col) and new_col[j] == labels[aux]:
                            for i in range(ind_len):
                                if i < len(new_ind):
                                    new_df[i].pop(j)
                            new_col.pop(j)
                            count += 1

                    # Verifica se alguma coluna não foi encontrada no DataFrame
                    if count != aux+1 and errors == "raise":
                        return "Erro: Coluna " + str(labels[aux]) + " não foi encontrada."

        elif not isinstance(labels, list): # Verifica se não é lista
            if axis == 0:
                for i in range(ind_len):

                    if i < len(new_ind) and new_ind[i] == labels:
                        new_df.pop(i)
                        new_ind.pop(i)

            elif axis == 1:
                for j in range(ind_len):
                    if j < len(new_col) and new_col[j] == labels:

                        for i in range(ind_len):
                            if i < len(new_ind):
                                new_df[i].pop(j)

                        new_col.pop(j)

        if columns != None:
            labels = columns
            axis = 1

    if labels == None:
        # Remove linha por linha
        for i in range(ind_len-1, -1,-1):
            new_df.pop(i)

        for i in range(len(new_col)-1, -1, -1):
            new_col.pop(i)

        for i in range(len(new_ind)-1, -1, -1):
            new_ind.pop(i)

    return new_df, new_col, new_ind

def eval_expr(df, col, ind, node):

    """
    Função recursiva que avalia uma expressão
    Seus parâmetros são:
     - df: Matriz com os dados (DataFrame) que serão filtrados
     - col: Lista com os rótulos das colunas do DataFrame
     - ind: Lista com os indexes das linhas do DataFrame
     - node: Uma expressão/nó que será avaliada para efetuar as respectivas operações
    Retorna: Uma "máscara" (lista com valores do tipo bool, que indica qual linha do DataFrame será
    filtrada)

    """

    if not isinstance(node, ast.Expression):
        node = ast.parse(node, mode='eval')

    dictionary = {}

    for c in range(len(col)):
        coluna = []

        for i in range(len(df)):
            coluna.append(df[i][c])

        dictionary.update({col[c]:coluna})

    # Ambiente com variáveis disponíveis
    env = {
        'df': dictionary,  # Simula o DataFrame
        **dictionary  # Adiciona acesso direto às colunas como variáveis
    }

    # Mapeamento dos operadores
    ops = {
        # Comparações
        ast.Gt: operator.gt,        # >
        ast.Lt: operator.lt,        # <
        ast.GtE: operator.ge,        # >=
        ast.LtE: operator.le,        # <=
        ast.Eq: operator.eq,         # ==
        ast.NotEq: operator.ne,      # !=

        # Operadores binários (soma, subtração, etc.)
        ast.Add: operator.add,       # +
        ast.Sub: operator.sub,       # -
        ast.Mult: operator.mul,      # *
        ast.Div: operator.truediv,   # /
        ast.FloorDiv: operator.floordiv, # //
        ast.Mod: operator.mod,       # %

        # Operadores booleanos
        ast.And: operator.and_,      # and (lógico)
        ast.Or: operator.or_,        # or (lógico)
        ast.BitAnd: operator.and_,   # &
        ast.BitOr: operator.or_,     # |

        # Outros
        ast.Not: operator.not_,      # not
        ast.USub: operator.neg,      # - (unário negativo)
        ast.UAdd: operator.pos,      # + (unário positivo)

        # Subscripting
        ast.Subscript: lambda val, key: val[key],

        # Nomes e carregamento
        ast.Name: lambda node: env[node.id],
        ast.Load: lambda _: None
    }

    if isinstance(node, ast.Expression):
        return eval_expr(df, col, ind, node.body)

    elif isinstance(node, ast.Compare): # Para comparações
        left = eval_expr(df, col, ind, node.left)
        for op, comp in zip(node.ops, node.comparators):
            right = eval_expr(df, col, ind, comp)

            # Verificar se a comparação envolve uma lista (coluna) ou um valor fixo (inteiro)
            if isinstance(left, list) and isinstance(right, list):  # Comparação entre listas (colunas)
                left = [ops[type(op)](l, r) for l, r in zip(left, right)]
            elif isinstance(left, list):  # Comparação de lista com valor fixo
                left = [ops[type(op)](l, right) for l in left]
            elif isinstance(right, list):  # Comparação de valor fixo com lista
                left = [ops[type(op)](left, r) for r in right]
            else:  # Comparação entre valores individuais
                left = ops[type(op)](left, right)

            if isinstance(left, list):
                return filter_df(df, col, ind, left) # "Filtra" os valores do DataFrame (coloca os valores normais)

        return left

    elif isinstance(node, ast.BoolOp):
        values = [eval_expr(df, col, ind, v) for v in node.values]
        return ops[type(node.op)](values[0], values[1])

    elif isinstance(node, ast.BinOp):  # Para & ou | entre listas
        left = eval_expr(df, col, ind, node.left)
        right = eval_expr(df, col, ind, node.right)

        if isinstance(left, list) and isinstance(right, list):  # Para listas (colunas)
            return [ops[type(node.op)](l, r) for l, r in zip(left, right)]
        elif isinstance(left, list):  # Para operação de lista com valor fixo
            return [ops[type(node.op)](l, right) for l in left]
        elif isinstance(right, list):  # Para operação de valor fixo com lista
            return [ops[type(node.op)](left, r) for r in right]
        else:  # Para valores individuais
            return ops[type(node.op)](left, right)

    elif isinstance(node, ast.Name):  # Retorna a variável ou coluna
        return env[node.id]

    elif isinstance(node, ast.Constant):  # Se for uma constante literal (string, número, etc)
        return node.value

    elif isinstance(node, ast.Subscript):  # Modificado para lidar com df['A']
        val = eval_expr(df, col, ind, node.value)
        key = eval_expr(df, col, ind, node.slice)
        return val[key]

    elif isinstance(node, ast.Index):  # para versões < Python 3.9
        return eval_expr(df, col, ind, node.value)

    elif isinstance(node, ast.Slice):
        return slice(eval_expr(df, col, ind, node.lower), eval_expr(df, col, ind, node.upper))

    elif isinstance(node, ast.Str):  # Compatibilidade com strings
        return node.s

    else:
        raise TypeError(f"Unsupported type: {type(node)}")

def compare_columns(df, col, ind, col_1, col_2, op):

    """
    Função que compara os valores de duas colunas diferentes
    Seus parâmetros são:
     - df: Matriz com os valores do DataFrame
     - col: Lista com os rótulos das colunas
     - ind: Lista com os indexes das linhas
     - col_1: Primeira coluna
     - col_2: Segunda coluna, que será comparada com a primeira
     - op: A comparação que será realizada
    Retorna: Uma DataFrame com as linhas filtradas a partir do específicado nos argumentos
    """

    operation = ('==', '!=', '>', '>=', '<', '<=')

    df_result = []
    ind_result = []

    """ ================== VERIFICAÇÕES ================== """

    if not col_1 in col:
        return "Erro: Coluna " + str(col_1) + " não encontrada"

    if not col_2 in col:
        return "Erro: Coluna " + str(col_2) + " não encontrada"

    if not op in operation:
        return "Erro: Operação não reconhecida"

    """ ------------------------------------------------- """

    oper = operation[operation.index(op)]
    c1 = col.index(col_1)
    c2 = col.index(col_2)

    for i in range(len(ind)):
        add = False # Variável utilizada para saber se será adicionada a linha ao resultado

        v1 = df[i][c1]
        v2 = df[i][c2]

        if oper == '==' and v1 == v2:
            add = True
        elif oper == '!=' and v1 != v2:
            add = True
        elif oper == '>' and v1 > v2:
            add = True
        elif oper == '>=' and v1 >= v2:
            add = True
        elif oper == '<' and v1 < v2:
            add = True
        elif oper == '<=' and v1 <= v2:
            add = True

        if add:
            df_result.append(df[i])
            ind_result.append(ind[i])

    return df_result, col, ind_result

def isin(df, col, ind, values, col_v=None, ind_v=None, value_return='default'):

    """
    Função que filtra por valores específicos
    Seus parâmetros são:
     - df: Matriz com os valores que serão filtrados
     - col: Lista com os rótulos das colunas
     - ind: Lista com os indexes das linhas
     - values: Lista/Dicionário/DataFrame/Series que será utilizado como o parâmetro de filtragem
     - col_v: Lista com os rótulos das colunas de 'values'
     - ind_v: Lista com os indexes das linhas de 'values'
     - value_return: Define se será retornado um DataFrame com os valores no tipo 'bool' (True caso corresponda
       e False caso contrário) ou com os valores padrão ('default') do DataFrame
    Retorna: Um DataFrame com valores padrão ou bool, que específica os valores que serão "mantidos" como nan (Not a Number)
    ou True

    Parâmetro value_return foi definido para simular o efeito de colocar o DataFrame com os valores do tipo bool
    nele mesmo ( df[df.isin([1, 3])] )
    """

    if value_return != 'default' and value_return != 'bool':
        return "Erro: Argumento de 'value_return' não reconhecido, informe um valor válido ('default', 'bool')"

    df_copy = []

    for i in range(len(df)):
        df_copy.append([False]*len(df[i]))

    if isinstance(values, dict): # Dicionário ============================

        keys = list(values.keys()) # Pega a lista das chaves do dicionário (converte em lista, pois a função keys()
                                    # retorna um objeto do tipo dict_keys)

        for k in range(len(keys)):

            if keys[k] in col:
                c = col.index(keys[k])

                for i in range(len(df)):
                    if df[i][c] in values.get(keys[k]):
                        df_copy[i][c] = True
                    else:
                        df_copy[i][c] = False

    else:

        if col_v == None and ind_v == None: # Lista ========================
            for i in range(len(df)):
                for j in range(len(df[i])):

                    # Verifica se cada elemento do DataFrame corresponde a um dos valores da lista
                    if df[i][j] in values: # Se sim, define como True
                        df_copy[i][j] = True
                    else: # Caso contrário, define como False
                        df_copy[i][j] = False

        elif col_v != None: # DataFrame ====================================

            if ind_v == None:
                return "Erro: Informe os indexes do DataFrame"

            else:
                for i in range(len(df)):
                    for j in range(len(df[i])):

                        if (ind[i] in ind_v) and (col[j] in col_v):
                            l = ind_v.index(ind[i])
                            c = col_v.index(col[j])

                            if df[i][j] == values[l][c]:
                                df_copy[i][j] = True
                            else:
                                df_copy[i][j] = False

                        else:
                            df_copy[i][j] = False

        elif col_v == None and ind_v != None: # Series =====================

            for i in range(len(df)):

                if ind[i] in ind_v: # Verifica se o index i está presente na lista de indexes ind_v
                    l = ind_v.index(ind[i])

                    for j in range(len(df[i])):
                        if df[i][j] == values[l]:
                            df_copy[i][j] = True
                        else:
                            df_copy[i][j] = False

    if value_return == 'default':

        for i in range(len(df_copy)):
            for j in range(len(df_copy[i])):

                if df_copy[i][j] == True:
                    df_copy[i][j] = df[i][j]
                else:
                    df_copy[i][j] = float('nan')

    return df_copy, col, ind

def reset_index(df, col, ind, drop=False, inplace=False, allow_duplicates=None, names=None):

    """
    Função que reseta os indexes de um DataFrame
    Seus parâmetros são:
     - df: Matriz com os valores do DataFrame
     - col: Lista com os rótulos das colunas do DataFrame
     - ind: Lista com os indexes das linhas do DataFrame
     - drop: Define se os indexes antigos serão removidos por completo, se for False serão mantidos como uma nova coluna
     - inplace: Determina se a operação será realizada no DataFrame original ou em uma cópia
     - allow_duplicates: Valor bool que define se será permitido ou não a repetição de rótulos nas colunas
     - names: Nome da coluna adicional gerada pelo drop=False
    Retorna: DataFrame com os indexes resetados
    """

    # Verifica o argumento de inplace
    if inplace == False: # Se False, a operação será realizada a partir de uma cópia
        df_result = copy.deepcopy(df)
        col_result = copy.deepcopy(col)
        ind_result = copy.deepcopy(ind)

        if len(ind_result) != len(df_result) and len(df_result) - len(ind_result) > 0:
            for i in range(len(df_result)-len(ind_result)):
                ind_result.append(None)

    else: # Caso contrário, a operação será realizada a partir do DataFrame original
        df_result = df
        col_result = col
        ind_result = ind

        if len(ind_result) != len(df_result) and len(df_result) - len(ind_result) > 0:
            for i in range(len(df_result)-len(ind_result)):
                ind_result.append(None)

    # Verifica o argumento de drop e names
    if drop == False: # Se drop for falso, insere-se uma nova coluna com os indexes antigos

        if names == None: # Verifica o argumento de names, se for igual None, utiliza-se o nome padrão (index)
            name = "index"

            if name in col_result: # Verifica se o rótulo index já está presente no DataFrame, se já estiver então
                                   # utiliza-se outro
                aux = True
                num = 0

                while aux: # Verifica se o rótulo "level_<número>" já está presente, de forma a incrementar o número
                           # até que encontre-se um que não está presente no DataFrame

                    if not "level_"+str(num) in col_result:
                        name = "level_"+str(num)
                        aux = False

                    num += 1

            col_result.insert(0, name)

        else: # Caso contrário, utiliza-se o valor informado no parâmetro names
            col_result.insert(0, names)


        for i in range(len(df_result)):
            df_result[i].insert(0, ind[i]) # Insere no DataFrame os antigos indexes como uma coluna nova adicional

    # Verifica o argumento de allow_duplicates, se False não será permitido a existência de duas ou mais colunas de
    # mesmo rótulo, de forma a retornar um erro caso haja
    if allow_duplicates == False:
        for i in range(len(col_result)):
            for j in range(len(col_result)):

                if i != j and col_result[i] == col_result[j]:
                    return "Erro: Existe uma ou mais colunas com o rótulo '" + str(col_result[i]) + "'"

    # Cria os novos indexes
    for i in range(len(df_result)):
        ind_result[i] = i

    return df_result, col_result, ind_result

def reindex(df, col, ind, labels=None, index=None, columns=None, axis=None, method=None, copy_p=True, fill_value=float("nan"), limit=None, tolerance=0):

    """
    Função que altera ou adapta os indexes de um DataFrame seguindo uma lógica de preenchimento.
    Seus parâmetros são:
     - df: Matriz com os valores do DataFrame
     - col: Lista com os rótulos das colunas
     - ind: Lista com os indexes das linhas
     - labels: Lista com os novos identificadores das colunas/linhas
     - index: Lista com os novos indexes das linhas
     - columns: Lista com os novos rótulos das colunas
     - axis: Define o eixo da operação, onde 0 indica que a operação será realizada a partir das linhas
       e 1 a partir das colunas
     - method: Determina o método de preenchimento para as brechas (elementos sem valores) do DataFrame
       reindexado, no qual:
        - None: Não aplicará nenhum tipo de preenchimento
        - 'pad'/'ffill': Replicará o último valor válido até encontrar outro valor
        - 'backfill'/'bfill': Utilizará o próximo valor válido que encontrar como preenchimento
        - 'nearest': Aplicará o valor válido mais próximo que encontrar
     - copy_p (copy_parameter): Define se a operação será realizada a partir do DataFrame original ou não, nesse caso em uma cópia
     - fill_value: Valor que será colocado nos elementos que não apresentava valores na indexação prévia
     - limit: Número inteiro que restringirá a quantidade máxima de elementos consecutivos que serão preenchidos
       a partir de um valor válido
     - tolerance: Específica a tolerância máxima permitida para o alinhamento dos indexes ao efetuar a
       reindexação

    OBS: Deve-se utilizar apenas 1 (um) forma para determinar o eixo da operação, sendo este apenas com labels
    e axis, ou apenas com index/columns

    OBS 2: Para que a operação seja realizada no DataFrame original, a lista com os novos rótulos/indexes deve
    apresentar a mesma quantidade de elementos do original e copy_p deve estar assinalado com False
    """

    """ ================= VERIFICAÇÕES DE ERROS ================= """

    if (labels != None or axis != None) and (index != None or columns != None):
        return "Erro: Informe apenas uma das maneiras de chamada (labels e axis) ou (index/columns)"
    if index != None and columns != None:
        return "Erro: Não é possível especificar index e columns ao mesmo tempo"
    if labels != None and axis == None:
        return "Erro: Informe o eixo de operação (axis=0 ou axis=1)"
    if limit != None and not str(limit).isnumeric():
        return "Erro: Informe um limite válido (valor inteiro)"
    if isinstance(tolerance, list) or isinstance(tolerance, tuple):
        if ((axis == 0 or axis == 1) and len(tolerance) != len(labels)) or (index != None and len(tolerance) != len(index)) or (columns != None and len(tolerance) != len(columns)):
            return "Erro: A quantidade de elementos de tolerance deve corresponder a quantidade de linhas/colunas"

    """ ========================================================= """


    """ ===================== PARÂMETRO COPY ===================== """

    if index != None:
        labels = index
        axis = 0

    elif columns != None:
        labels = columns
        axis = 1

    if copy_p == False and ((axis == 0 and len(ind) == len(labels)) or (axis == 1 and len(col) == len(labels))):
        df_result = df
        col_result = col
        ind_result = ind

    else:
        df_result = []

        if axis == 0:
            for i in range(len(labels)):
                lst = []

                for j in range(len(col)):
                    lst.append(None)

                df_result.append(lst)
        else:
            for i in range(len(ind)):
                lst = []

                for j in range(len(labels)):
                    lst.append(None)

                df_result.append(lst)

        col_result = []
        ind_result = []

    # Cópia do DataFrame original para consultas posteriores
    df_copy = copy.deepcopy(df)
    col_copy = copy.deepcopy(col)
    ind_copy = copy.deepcopy(ind)

    """ ========================================================== """

    list_ind = []

    """ ===== VERIFICA EIXO DA OPERAÇÃO ===== """

    if axis == 0: # Linha
        # Verifica se é realizado a partir do original ou de uma cópia do DataFrame
        if copy_p == False and len(ind) == len(labels):
            for i in range(len(labels)):
                ind_result[i] = labels[i]

        else:
            ind_result = labels
            col_result = col.copy()

        for i in range(len(labels)):

            if labels[i] in ind_copy:
                aux_ind = ind_copy.index(labels[i])

                if copy_p == False and len(ind) == len(labels):
                    for j in range(len(df_result[aux_ind])):
                        df_result[i][j] = df_copy[aux_ind][j]

                else:
                    df_result[i] = df_copy[aux_ind]

            elif str(labels[i]).replace('.', '', 1).isnumeric() and tolerance != 0:
                if isinstance(tolerance, list):
                    t = tolerance[i]
                else:
                    t = tolerance

                verify = verify_tolerance(labels[i], ind_copy, t)

                if verify != -1: # Verifica se está dentro da tolerância permitida (-1 é False)

                    if copy_p == False and len(ind) == len(labels): # Verifica se copy_p == False
                        for j in range(len(df_result[verify])): # Se sim, então altera os valores da linha, coluna por coluna
                            df_result[i][j] = df_copy[verify][j]

                    else: # se não for uma cópia, a linha i recebe diretamente a linha
                        df_result[i] = df_copy[verify]

                else:
                    for j in range(len(df_result[i])):
                        df_result[i][j] = fill_value

                    list_ind.append(i)

            else:
                for j in range(len(df_result[i])):
                    df_result[i][j] = fill_value

                list_ind.append(i)

    else: # Coluna
        # Verifica se é realizado a partir do original ou de uma cópia do DataFrame
        if copy_p == False and len(col) == len(labels):
            for i in range(len(labels)):
                col_result[i] = labels[i]

        else:
            col_result = labels
            ind_result = ind.copy()

        for j in range(len(labels)):

            if labels[j] in col_copy:
                aux_ind = col_copy.index(labels[j])

                for i in range(len(df_result)):
                    df_result[i][j] = df_copy[i][aux_ind]

            elif str(labels[j]).replace('.', '', 1).isnumeric() and tolerance != 0:
                if isinstance(tolerance, list):
                    t = tolerance[j]
                else:
                    t = tolerance

                verify = verify_tolerance(labels[j], col_copy, t)

                if verify != -1: # Verifica se está dentro da tolerância permitida (-1 é False)
                    for i in range(len(df_result)):
                        df_result[i][j] = df_copy[i][verify]

                else:
                    for i in range(len(df_result)):
                        df_result[i][j] = fill_value

                    list_ind.append(j)

            else:
                for i in range(len(df_result)):
                    df_result[i][j] = fill_value

                list_ind.append(j)

    if method != None:
        fill_method(df_result, list_ind, axis, method, limit)

    return df_result, col_result, ind_result

def groupby(df, col, ind, by=None, axis=0, as_index=True, sort=True, group_keys=True, dropna=True, func=None, *args, **kwargs):

    """
    Função que permite o agrupamento de dados e aplicação de funções sobre os grupos.
    Seus parâmetros são:
     - df: Matriz que representa os elementos de um DataFrame
     - col: Vetor que representa os rótulos das colunas
     - ind: Vetor que representa os indexes das linhas
     - by: Define como os dados serão agrupados
     - axis: Define o eixo da operação (apenas axis=0 está configurado, axis=1 foi descontinuado a partir da versão 2.1.0 do pandas)
     - as_index: Indica se as chaves de agrupamento serão utilizados como index no DataFrame resultante ou não
     - sort: Ordena as chaves de agrupamento, sem afetar a ordem dos elementos de cada grupo
     - group_keys: Determina se as chaves de agrupamento serão adicionadas ao index para identificação dos grupos ao que pertencem com a aplicação de funções
     - dropna: Define se os grupos que possuírem NaN como chave de agrupamento serão mantidos ou removidos da operação
    Retorna: Um dicionário, com as chaves de agrupamento como chave e os indexes das linhas que fazem parte do grupo como valores associados para quando não é especificado
    nenhuma aplicação de função. Caso contrário, seja específicado uma função, retorna-se um DataFrame

    Parâmetro func, *args e **kwargs não estão na função do pandas. Foram definidas nesta função para simular a aplicação de uma função em DataFrame por agrupamento
    """

    # VERIFICAR: axis=1 e observed
    #   axis=1 -> Deprecated - Justificar e não fazer - RESOLVIDO
    #   observed -> Utiliza colunas/linhas do tipo Categoricals (funciona de forma similar a uma entidade criada para categoria no BD, vinculando a partir de seu ID)
    #   by -> Aceita um objeto do tipo grouper
    #   group_keys -> Trabalha com a multi indexação (se True e for utilizado juntamente com a função apply, inclui os nomes das chaves de agrupamento como um nível
    #                 superior (hierárquico) no índice do resultado, mantendo ao mesmo tempo os indexes originais)

    """ ========================== VERIFICAÇÕES ========================== """
    aux_bool = False

    # Verifica se existe uma função nativa do Python ou presente no escopo global com o nome específicado
    # Caso não exista, retorna um erro
    if func != None and isinstance(func, str) and not verify_function(func) and not (globals().get(func) and callable(globals().get(func))):
        return "Erro: Não foi encontrado nenhuma função existente com o nome de " + str(func)

    if by != None and isinstance(by, list):

        for i in range(len(by)):
            if (axis == 0 or axis == 'index') and not by[i] in col:
                aux_bool = True
            elif (axis == 1 or axis == 'columns') and not by[i] in ind:
                aux_bool = True

    if by != None and isinstance(by, (str, int, float)) and (((axis == 0 or axis == 'index') and not by in col) or ((axis == 1 or axis == 'columns') and not by in ind)) or aux_bool:
        return "Erro: Não foi encontrado nenhuma linha/coluna(s) com o nome correspondente ao específicado em 'by'"

    """ ================================================================== """


    """ ============== RETORNO SEM UTILIZAÇÃO DE FUNÇÃO ============== """

    # dictionary = {"__dataFrame__":df,
    #               "__columns__":col,
    #               "__index__":ind,
    #               "__groupedBy__":by,
    #               "__axis__":axis
    #              }

    dictionary = {}

    for i in range(len(ind)):

        aux_list = []

        if isinstance(by, (str, int, float)):
            if not df[i][col.index(by)] in dictionary:
                dictionary.update({df[i][col.index(by)]:[]})

            dictionary[df[i][col.index(by)]].append(ind[i])

        elif isinstance(by, list):
            for j in range(len(by)):
                aux_list.append(df[i][col.index(by[j])])

            aux_list = tuple(aux_list)

            if not aux_list in dictionary.keys():
                dictionary.update({aux_list:[]})

            dictionary[aux_list].append(ind[i])

    """ ============ DROPNA ============ """

    if dropna == True:
        key = list(dictionary.keys())

        for i in range(len(key)):
            if nan_list(key[i]):
                dictionary.pop(key[i])

    """ ================================ """

    if func == None:
        return dictionary

    elif func != None: # RETORNO COM UTILIZAÇÃO DE FUNÇÃO

        df_result = []
        col_result = []
        ind_result = []

        for key, value in dictionary.items():
            if as_index == True and not key in ind_result:
                ind_result.append(key)

            for j in range(len(col)):
                if isinstance(by, (str, int, float)) and not col[j] in col_result:
                    if (as_index == True and col[j] != by) or as_index == False:
                        col_result.append(col[j])
                elif isinstance(by, list) and not col[j] in col_result:
                    if (as_index == True and not col[j] in by) or as_index == False:
                        col_result.append(col[j])

            row = []

            for j in range(len(col_result)):
                aux_list = []

                for i in range(len(value)):
                    aux_ind = ind.index(value[i])
                    c = col.index(col_result[j])

                    if as_index == True or (as_index == False and ((isinstance(by, list) and not col[c] in by) or (isinstance(by, (str, int, float)) and col[c] != by))):
                        aux_list.append(df[aux_ind][c])

                if as_index == True or (as_index == False and ((isinstance(by, list) and not col[c] in by) or (isinstance(by, (str, int, float)) and col[c] != by))):
                    row.append(apply_function(aux_list, func, *args, **kwargs))

            if as_index == False:
                if isinstance(key, tuple):
                    for i in range(len(key)):
                        row.insert(i, key[i])

                elif isinstance(key, (str, int, float)):
                    row.insert(0, key)

            df_result.append(row)


    """ ======================= SORT ======================= """ # Bubble Sort

    if sort == True:
        for i in range(len(df_result)):
            for j in range(i+1, len(df_result), 1):
                if as_index == False and largest_group(df_result[i], df_result[j], col_result, by, as_index):
                    aux = df_result[i]
                    df_result[i] = df_result[j]
                    df_result[j] = aux
                elif as_index == True and largest_group(ind_result[i], ind_result[j], col_result, by, as_index):
                    aux = df_result[i]
                    df_result[i] = df_result[j]
                    df_result[j] = aux

                    aux = ind_result[i]
                    ind_result[i] = ind_result[j]
                    ind_result[j] = aux

    """ ==================================================== """

    return df_result, col_result, ind_result

def merge(left, col_l, ind_l, right, col_r, ind_r, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False,
          suffixes=('_x', '_y'), copy=True, indicator=False, validate=None):

    """
    Função que mescla dois objetos (DataFrame ou Series)
    Seus parâmetros são:
     - left: Primeiro DataFrame
     - col_l: Lista com os rótulos das colunas do primeiro DataFrame
     - ind_l: Lista com os indexes das linhas do primeiro DataFrame
     - right: Segundo DataFrame que será mesclado com o primeiro
     - col_r: Lista com os rótulos das colunas do segundo DataFrame
     - ind_r: Lista com os indexes das linhas do segundo DataFrame
     - how: Tipo de junção que será realizada, em que:
        - 'left': Mantêm as linhas do primeiro DataFrame (left) e adiciona os dados do segundo (right)
          quando houver correspondência
        - 'right': Mantêm as linhas do segundo DataFrame e adiciona os dados do primeiro quando houver
          correspondência
        - 'outer': Retém todas as linhas de ambos os objetos (left e right), preenchendo valores
          ausentes quando não há correspondência
        - 'inner': Apresenta apenas as linhas que aparecem em ambos os objetos
        - 'cross': Cria o produto cartesiano de ambos os objetos
     - on: Rótulo da coluna ou lista de rótulos que serão usados como referência para combinar os dois
       objetos
     - left_on: Rótulo da coluna ou lista de rótulos do primeiro DataFrame que será utilizado como
       referência juntamente com right_on para a junção
     - right_on: Rótulo da coluna ou lista de rótulos do segundo DataFrame que será utilizado como
       referência juntamente com left_on para a junção
     - left_index e right_index: Definem se os indexes serão utilizados como chave de junção
     - sort: Determinará se o resultado será organizado em ordem lexicográfica a partir do valor das
       chaves usadas na junção
     - suffixes: Sequência de dois elementos, no qual cada será utilizado como sufixo nos rótulos das
       colunas de mesmo nome presentes em ambos os objetos
     - copy: Define se será realizado uma cópia
     - indicator: Adiciona uma nova coluna ao resultado que indica a fonte de cada linha
     - validate: Verifica se a junção é de um tipo
     Retorna: Um DataFrame
    """

    # Verifica se os argumentos de on, left_on e right_on são listas ou não, se não for, os "tranforma" para uma lista de único elemento
    if not isinstance(on, list) and on != None:
        on = [on]
    elif (not isinstance(left_on, list) and left_on != None) and (not isinstance(right_on, list) and right_on != None):
        left_on = [left_on]
        right_on = [right_on]

    # Verifica se foi passado um valor em on:
    if on != None: # Padroniza as variáveis, ou seja, não será necessário ficar fazer derivações devido a esses parãmetros
        left_on = on.copy()
        right_on = on.copy()

        on = None # Para não lançar um erro

    """ ======== VERIFICAÇÕES QUE RETORNAM ERROS ======== """

    # Verifica se passou valores em on, left_on e right_on com how='cross', se sim, retorna um erro
    if (on != None or (left_on != None and right_on != None)) and how == 'cross':
        return "Erro: Não pode passar valores em on, left_on ou right_on quando how='cross'"

    # Verifica se foram passados valores em on, left_on e right_on ao mesmo tempo, se for, retorna um erro
    if on != None and left_on != None and right_on != None:
        return "Erro: Pode passar um valor apenas em on OU left_on e right_on, nunca a combinação de ambos"

    # Verifica se o comprimento de left_on e right_on são iguais, caso não for, retorna um erro
    if left_on != None and right_on != None and len(left_on) != len(right_on):
        return "Erro: left_on e right_on devem possuir a mesma quantidade de colunas"

    # Verifica se foram passados valores em on, left_on e right_on juntamente com left_index = True e right_index = True
    if (left_index == True or right_index == True) and (on != None or left_on != None or right_on != None):
        return "Erro: Pode passar um valor apenas em on/left_on/right_on OU left_index/right_index, nunca a combinação de ambos"

    # Verifica se left_index é True e right_index False e vice-versa, caso for, retorna um erro
    if (left_index == True and right_index == False) or (left_index == False and right_index == True):
        return "Erro: Ambos os parâmetros left_index e right_index devem ser verdadeiros se ao menos um for informado como verdadeiro"

    # Verifica se os tipos de cada coluna correspondem
    if left_on != None and right_on != None:
        for i in range(len(left_on)):
            if type(left[0][col_l.index(left_on[i])]) != type(right[0][col_r.index(right_on[i])]):
                return "Erro: Não é possível realizar a junção de valores de tipos diferentes"

    # Verifica se o argumento de indicator não é bool e nem String, se não for, retorna um erro
    if not isinstance(indicator, bool) and isinstance(indicator, str):
        return "Erro: O argumento de indicator aceita apenas valores de tipo booleano ou String"

    """ ------------------------------------------------- """

    if copy == True:
        df_result = []
        col_result = []
        ind_result = []
    else:
        df_result = left
        col_result = col_l
        ind_result = ind_l

    # Caso on=None, left_on=None e right_on=None, o programa deverá encontrar as colunas em comum dos dois DataFrames
    if how == 'cross' and on == None and left_on == None and right_on == None:
        on = []

        # Percorre as colunas de left
        for i in range(len(col_l)):

            # Verifica se a coluna está presente no outro DataFrame
            if col_l[i] in col_r:
                on.append(col_l[i])


    """ ================ SUFIXOS ================ """

    # Verifica se há colunas com nomes iguais, caso haja coloca o sufixo definido em suffixes
    for i in range(len(col_l)):

        if col_l[i] in col_r:
            col_l = col_l.copy()
            col_r = col_r.copy()

            if suffixes[0] == None and suffixes[1] == None:
                return "Erro: Há coluna(s) com nomes iguais porém sem um sufixo especificado"
            if suffixes[1] != None and (right_on == None or not col_l[i] in right_on or (col_l[i] in right_on and not col_l[i] in left_on)):
                col_r[col_r.index(col_l[i])] = str(col_r[col_r.index(col_l[i])]) + str(suffixes[1])
            if suffixes[0] != None and (left_on == None or not col_l[i] in left_on or (col_l[i] in left_on and not col_l[i] in right_on)):
                col_l[i] = str(col_l[i]) + str(suffixes[0])

    """ ----------------------------------------- """

    # Verifica se left_index=True e right_index=True
    # Se for, realizará a mescla a partir dos indexes, em que apenas juntará as colunas quando estiver presente
    # em ambos os DataFrames
    if left_index == True and right_index == True:

        col_result = col_l + col_r

        # Percorre os indexes do primeiro DataFrame
        for i in range(len(ind_l)):
            row = []

            if ind_l[i] in ind_r: # Verifica se aquele index está presente nos indexes do outro DataFrame
                ind = ind_r.index(ind_l[i])
                ind_result.extend([ind_l[i]])

                for j in range(len(col_result)):
                    if col_result[j] in col_l:
                        row.extend([left[i][col_l.index(col_result[j])]])
                    elif col_result[j] in col_r:
                        row.extend([right[ind][col_r.index(col_result[j])]])

            if len(row) != 0:
                df_result.extend([row])

        return df_result, col_result, ind_result


    """ ================ COLUNAS ================ """

    for i in range(len(col_l)): # Adiciona as colunas de left ao resultado
        if not col_l[i] in col_result:
            col_result.extend([col_l[i]])

    for i in range(len(col_r)): # Adiciona as colunas de right ao resultado
        if not col_r[i] in col_result:
            col_result.extend([col_r[i]])

    if indicator == True: # Se True troca o valor de indicator para o nome padrão
        indicator = "_merge"

    if indicator != False and isinstance(indicator, str): # Se String adiciona uma nova coluna com o nome armazenado em indicator
        col_result.extend([indicator])

    """ ----------------------------------------- """


    """ =========== PARÂMETROS DE HOW =========== """

    list_aux = []

    # Verifica o argumento de how
    if how == 'outer': # Se outer, então será incluído ao resultado todas as linhas de ambos os DataFrames

        for i in range(len(left)): # Percorre o primeiro DataFrame (left)
            row = []
            cont = 0

            for j in range(len(right)): # Percorre o segundo DataFrame (right)

                if verify_correspondence(left[i], col_l, right[j], col_r, left_on, right_on, suffixes):
                    ind_result.extend([ind_r[j]]) # Adiciona o index ao ind_result para salvar as linhas do segundo DataFrame que já
                                                # foram adicionados ao resultado, assim evitando possíveis repetições

                    list_aux.extend([ind_l[i]]) # Utilizado para auxiliar na verificação de validate juntamente com ind_result

                    for k in range(len(col_l)):
                        row.extend([left[i][k]])

                    for k in range(len(col_r)):
                        if not col_r[k] in right_on:
                            row.extend([right[j][k]])

                else:
                    cont += 1

                if len(row) != 0:
                    if isinstance(indicator, str): # Adiciona o indicador de "both", pois se a linha tiver comprimento maior que 0
                                                   # significa que houve correspondência nas chaves
                        row.extend(["both"])

                    df_result.extend([row])
                    row = []

            if cont == len(right):
                row = [None]*len(col_result)

                for j in range(len(col_result)):
                    if col_result[j] in col_l:
                        row[j] = left[i][col_l.index(col_result[j])]
                    else:
                        row[j] = "NaN"

                if isinstance(indicator, str): # Adiciona o indicador de "left_only", pois se o contador (cont) for igual a quantidade
                                               # de linhas do segundo DataFrame (right) significa que não houve nenhuma correspondência
                                               # nas chaves da linha i do primeiro DataFrame com todas as linhas do outro DataFrame
                    row.extend(["left_only"])

                df_result.extend([row])

        for i in range(len(ind_r)):

            if not ind_r[i] in ind_result:
                row = [None]*len(col_result)

                for j in range(len(col_result)):
                    if col_result[j] in col_r:
                        row[j] = right[i][col_r.index(col_result[j])]
                    else:
                        row[j] = "NaN"

                if isinstance(indicator, str): # Adiciona o indicador de "right_only", pois se o index da linha i do segundo DataFrame
                                               # não estiver na lista de ind_result, significa que essa linha ainda não foi adicionada ao
                                               # resultado e portanto não apresenta nenhuma correspondência de chave com as linhas do
                                               # primeiro DataFrame
                    row.extend(["right_only"])

                df_result.extend([row])

    elif how == 'inner': # Se inner, então será incluído apenas as linhas que apresentam correspondência dos dois DataFrames

        for i in range(len(left)): # Percorre o primeiro DataFrame (left)
            row = []

            for j in range(len(right)): # Percorre o segundo DataFrame (right)

                if verify_correspondence(left[i], col_l, right[j], col_r, left_on, right_on, suffixes):
                    ind_result.extend([ind_r[j]]) # Adiciona o index ao ind_result para salvar as linhas do segundo DataFrame que já
                                                # foram adicionados ao resultado, assim evitando possíveis repetições

                    list_aux.extend([ind_l[i]]) # Utilizado para auxiliar na verificação de validate juntamente com ind_result

                    for k in range(len(col_l)):
                        row.extend([left[i][k]])

                    for k in range(len(col_r)):
                        if not col_r[k] in right_on:
                            row.extend([right[j][k]])

                if len(row) != 0:

                    if isinstance(indicator, str): # Adiciona o indicador de "both" visto que 'inner' apenas incluí linhas em
                                                   # que as chaves correspondem
                        row.extend(["both"])
                    df_result.extend([row])
                    row = []

    elif how == 'cross': # Se cross, será criado o produto cartesiano

        for i in range(len(left)): # Percorre o primeiro DataFrame
            for j in range(len(right)): # Percorre o segundo DataFrame
                ind_result.extend([ind_r[j]]) # Adiciona o index ao ind_result para salvar as linhas do segundo DataFrame que já
                                         # foram adicionados ao resultado, assim evitando possíveis repetições

                list_aux.extend([ind_l[i]]) # Utilizado para auxiliar na verificação de validate juntamente com ind_result

                row = []
                row = left[i]+right[j] # Compõe uma linha pela concatenação da linha i do primeiro DataFrame com
                                         # uma linha j do segundo DataFrame

                if isinstance(indicator, str): # Adiciona o indicador de "both" visto que 'cross' é a "mistura" de linhas
                                               # do primeiro DataFrame com as do segundo
                    row.extend(["both"])

                df_result.extend([row])

    else: # Se left ou right, mantêm as linhas do primeiro/segundo DataFrame e adiciona os dados do outro quando
          # houver correspondência

        if how == 'left':
            d1 = left
            d2 = right

            c1 = col_l
            c2 = col_r

            i1 = ind_l
            i2 = ind_r

            lo = left_on
            ro = right_on

            suf = [suffixes[0], suffixes[1]]

            idt = "left_only"

        else:
            d1 = right
            d2 = left

            c1 = col_r
            c2 = col_l

            i1 = ind_r
            i2 = ind_l

            lo = right_on
            ro = left_on

            suf = [suffixes[1], suffixes[0]]

            idt = "right_only"

        for i in range(len(d1)): # Percorre o primeiro DataFrame
            row = []
            cont = 0

            for j in range(len(d2)): # Percorre o segundo DataFrame
                if verify_correspondence(d1[i], c1, d2[j], c2, lo, ro, suf):
                    ind_result.extend([i2[j]]) # Adiciona o index ao ind_result para salvar as linhas do segundo DataFrame que já
                                                # foram adicionados ao resultado, assim evitando possíveis repetições

                    list_aux.extend([i1[i]]) # Utilizado para auxiliar na verificação de validate juntamente com ind_result

                    if how == 'left':

                        for k in range(len(col_l)):
                            row.extend([left[i][k]])

                        for k in range(len(col_r)):
                            if not col_r[k] in right_on:
                                row.extend([right[j][k]])

                    else:

                        for k in range(len(c2)):
                            if not c2[k] in ro:
                                row.extend([d2[j][k]])

                        for k in range(len(c1)):
                            row.extend([d1[i][k]])

                else:
                    cont += 1

                if len(row) != 0:

                    if isinstance(indicator, str):
                        row.extend(["both"])

                    df_result.extend([row])
                    row = []

            if cont == len(d2):
                row = [None]*len(col_result)

                for j in range(len(col_result)):
                    if col_result[j] in c1:
                        row[j] = d1[i][c1.index(col_result[j])]
                    else:
                        row[j] = "NaN"

                if isinstance(indicator, str):
                    row.extend([idt])

                df_result.extend([row])

    """ ---------------------------------------------- """


    """ ==================== SORT ==================== """

    # Se sort=True ou how='outer', reorganiza o DataFrame em ordem lexicográfica por meio do Bubble Sort
    if sort == True or how == 'outer':

        for i in range(len(df_result)):
            for j in range(len(df_result)-1-i):

                if verify_row(df_result[i], df_result[j+1], col_result, col_l, suffixes):
                    aux = df_result[i]
                    df_result[i] = df_result[j+1]
                    df_result[j+1] = aux

    """ ---------------------------------------------- """


    """ ================== VALIDATE ================== """

    if validate != None:
        aux_1 = 0
        aux_2 = 0

        for i in range(len(list_aux)):
            aux_1 += list_aux.count(list_aux[i])-1

        for i in range(len(ind_result)):
            aux_2 += ind_result.count(ind_result[i])-1

        if validate == "one_to_one" or validate == "1:1":
            if aux_1 != 0 and aux_2 != 0:
                return "Erro: As chaves de junção não são únicas em ambos os conjuntos de dados"
            elif aux_1 != 0:
                return "Erro: As chaves de junção não são únicas no primeiro conjunto de dados"
            elif aux_2 != 0:
                return "Erro: As chaves de junção não são únicas no segundo conjunto de dados"

        elif validate == "one_to_many" or validate == "1:m":
            if aux_1 != 0:
                return "Erro: As chaves de junção não são únicas no primeiro conjunto de dados"

        elif validate == "many_to_one" or validate == "m:1":
            if aux_2 != 0:
                return "Erro: As chaves de junção não são únicas no segundo conjunto de dados"

        elif validate == "many_to_many" or validate == "m:m": # Não resulta em nenhuma verificação
            aux_1 = 0
            aux_2 = 0

        else:
            return "Erro: palavra-chave '" + str(validate) + "' desconhecida" # Melhorar

    """ ---------------------------------------------- """


    """ ================== INDEXES ================== """

    if left_index == False and right_index == False:
        ind_result = []

        for i in range(len(df_result)):
            ind_result.extend([i])

    """ --------------------------------------------- """

    # Refaz os indexes de maneira sequencial

    return df_result, col_result, ind_result

# Renomeado para df_map devido a existência de uma função nativa do Python de mesmo nome (map)
def df_map(df, col, ind, func, axis=0, na_action=None, **kwargs):

    """
    Função que aplica uma ou mais funções individualmente para cada elemento de uma DataFrame.
    Seus parâmetros são:
     - df: Matriz com os valores do DataFrame
     - col: Lista com os rótulos das colunas
     - ind: Lista com os indexes das linhas
     - func: Objeto do tipo chamável que será aplicada em cada elemento do DataFrame
     - axis: Eixo da aplicação das funções
     - na_action: Define como lidar com os valores NaN (Not a Number)
     - **kwargs: São argumento nomeados adicionais que serão utilizados na chamada da função
    Retorna: Um DataFrame de mesmo tamanho (df, col, ind) com seus valores atualizados.
    """

    """ ============================= VERIFICAÇÕES ============================= """

    if not isinstance(func, (list, dict)) and not callable(func):
        return "Erro: o argumento de func deve ser um objeto do tipo chamável"

    """ ======================================================================== """

    if not isinstance(func, (list, dict)):
        for i in range(len(df)):
            for j in range(len(df[i])):
                df[i][j] = apply_function(df[i][j], func, **kwargs)

    else:
        if isinstance(func, list):
            for i in range(len(df)):
                for j in range(len(df[i])):
                    aux = []

                    for k in range(len(func)):
                        if not callable(func[k]):
                            return "Erro: o argumento de func deve ser um objeto do tipo chamável", None, None
                        else:
                            aux.append(apply_function(df[i][j], func[k], **kwargs))

                    df[i][j] = aux

        else:
            keys = tuple(func.keys())

            if axis == 0 or axis == 'index':
                for j in range(len(keys)):
                    if not keys[j] in col:
                        return "Erro: Coluna " + str(keys[j]) + " não existe!", None, None
            elif axis == 1 or axis == 'columns':
                for i in range(len(keys)):
                    if not keys[i] in ind:
                        return "Erro: Coluna " + str(keys[i]) + " não existe!", None, None

            for i in range(len(df)):
                for j in range(len(df[i])):
                    aux = []

                    if axis == 0 or axis == 'index':
                        functions = func.get(col[j])
                    elif axis == 1 or axis == 'columns':
                        functions = func.get(ind[i])

                    if isinstance(functions, list):
                        for k in range(len(functions)):
                            if not callable(functions[k]):
                                return "Erro: o argumento de func deve ser um objeto do tipo chamável", None, None
                            else:
                                aux.append(apply_function(df[i][j], functions[k], **kwargs))

                        df[i][j] = aux

                    elif functions != None:
                        df[i][j] = apply_function(df[i][j], functions, **kwargs)

    return df, col, ind

def agg(df, col, ind, func=None, axis=0, *args, **kwargs):

    """
    Função que permite a aplicação de uma ou mais operações sobre um determinado eixo (linha/coluna).
    Seus parâmetros são:
     - df: Matriz com os elementos do DataFrame
     - col: Vetor com os rótulos das colunas
     - ind: Vetor com os indexes das linhas
     - func: Função a ser aplicada sobre as linhas/colunas
     - axis: eixo de aplicação das funções
     - *args: Argumentos posicionais adicionais para a aplicação da função
     - **kwargs: Argumentos nomeados adicionais para a aplicação da função
    Retorna: Um DataFrame com o resultado da aplicação das funções.
    """

    """ ============================= VERIFICAÇÕES ============================= """

    # Verifica se existe uma função nativa do Python ou presente no escopo global com o nome específicado
    # Caso não exista, retorna um erro
    if isinstance(func, str) and not verify_function(func) and not (globals().get(func) and callable(globals().get(func))):
        return "Erro: Não foi encontrado nenhuma função existente com o nome de " + str(func)

    """ ======================================================================== """

    df_result = []
    col_result = []
    ind_result = []

    if callable(func) or isinstance(func, str): # Verifica se foi informado uma única função ou o nome de uma função
        length = 1 # Se sim, então será retornado um DataFrame de uma única linha
    elif isinstance(func, list): # Verifica se foi passado uma lista de funções
        length = len(func) # O tamanho do resultado será relativo à quantidade de funções que foram passadas
    elif isinstance(func, dict): # Verifica se foi passado um dicionário
        if axis == 1 or axis == 'columns':
            for list_f in func.values():
                if isinstance(list_f, list):
                    for i in range(len(list_f)):
                        if not list_f[i] in col_result:
                            col_result.append(list_f[i].__name__ if callable(list_f[i]) else list_f[i])
                elif not list_f in col_result:
                    col_result.append(list_f.__name__ if callable(list_f) else list_f)

            length = len(col_result)

        elif axis == 0 or axis == 'index':
            for list_f in func.values():
                if isinstance(list_f, list):
                    for i in range(len(list_f)):
                        if not list_f[i] in ind_result:
                            ind_result.append(list_f[i].__name__ if callable(list_f[i]) else list_f[i])
                elif not list_f in ind_result:
                    ind_result.append(list_f.__name__ if callable(list_f) else list_f)

            length = len(ind_result)

    if axis == 1 or axis == 'columns':
        for i in range(len(df)):
            aux_list = [float('nan')]*length
            df_result.append(aux_list)

    elif axis == 0 or axis == 'index':
        for i in range(length):
            aux_list = [float('nan')]*len(df[0])
            df_result.append(aux_list)

    aux = []

    if isinstance(func, dict):
        dict_copy = func.copy()

    if axis == 1 or axis == "columns":
        ind_result = ind.copy()

        for i in range(len(df)):
            if callable(func):
                if not func.__name__ in col_result:
                    col_result.append(func.__name__)

                df_result[i][col_result.index(func.__name__)] = apply_function(df[i], func, *args, **kwargs)

            elif isinstance(func, str):
                if not func in col_result:
                    col_result.append(func)

                df_result[i][col_result.index(func)] = apply_function(df[i], func, *args, **kwargs)

            elif isinstance(func, list):
                for f in range(len(func)):
                    if callable(func[f]) and not func[f].__name__ in col_result:
                        col_result.append(func[f].__name__)
                    if isinstance(func[f], str) and not func[f] in col_result:
                        col_result.append(func[f])

                    df_result[i][col_result.index(func[f].__name__ if callable(func[f]) else func[f])] = apply_function(df[i], func[f], *args, **kwargs)

            elif isinstance(func, dict):
                functions = func.get(ind_result[i])

                if isinstance(functions, list):
                    for f in range(len(functions)):
                        df_result[i][col_result.index(functions[f].__name__ if callable(functions[f]) else functions[f])] = apply_function(df[i], functions[f], *args, **kwargs)
                else:
                    df_result[i][col_result.index(functions.__name__ if callable(functions) else functions)] = apply_function(df[i], functions, *args, **kwargs)

    elif axis == 0 or axis == 'index':
        col_result = col.copy()

        for j in range(len(df[0])):
            for i in range(len(df)):
                aux.append(df[i][j])

            if len(aux) > 0:
                if callable(func):
                    if not func.__name__ in ind_result:
                        ind_result.append(func.__name__)

                    df_result[ind_result.index(func.__name__)][j] = apply_function(aux, func, *args, **kwargs)

                elif isinstance(func, str):
                    if not func in ind_result:
                        ind_result.append(func)

                    df_result[ind_result.index(func)][j] = apply_function(aux, func, *args, **kwargs)

                elif isinstance(func, list):
                    for f in range(len(func)):
                        if callable(func[f]) and not func[f].__name__ in ind_result:
                            ind_result.append(func[f].__name__)
                        if isinstance(func[f], str) and not func[f] in ind_result:
                            ind_result.append(func[f])

                        df_result[ind_result.index(func[f].__name__ if callable(func[f]) else func[f])][j] = apply_function(aux, func[f], *args, **kwargs)

                elif isinstance(func, dict):
                    functions = func.get(col_result[j])

                    if isinstance(functions, list):
                        for f in range(len(functions)):
                            df_result[ind_result.index(functions[f].__name__ if callable(functions[f]) else functions[f])][j] = apply_function(aux, functions[f], *args, **kwargs)
                    else:
                        df_result[ind_result.index(functions.__name__ if callable(functions) else functions)][j] = apply_function(aux, functions, *args, **kwargs)

            aux = []

    return df_result, col_result, ind_result

def df_apply(df, col, ind, func, axis=0, raw=False, result_type=None, args=(), by_row='compat', **kwargs):

    """
    Função que permite a aplicações de funções um determinado eixo do DataFrame. Pode ser aplicado diretamente em linhas/colunas
    ou em cada elemento individualmente.
    Seus parâmetros são:
     - df: DataFrame (matriz) no qual será a aplicada as funções
     - col: Lista com os rótulos das colunas do DataFrame
     - ind: Lista com os indexes das linhas do DataFrame
     - func: Função ou lista/dicionário de funções a serem aplicadas
     - axis: Eixo para a aplicação das funções
     - raw: Define se a operação será realizada normalmente (False) ou se será a operação será realizada com objetos ndarray
            do módulo NumPy
     - result_type: Controla como o resultado será formatado, no qual apenas o 'broadcast' apresenta uma mudança significativa
     - args: Tupla que recebe os argumentos de posição extras para a aplicação da função
     - by_row: Determina como as funções serão aplicadas, por linha/coluna ou individualmente para cada elemento
     - kwargs**: Argumentos adicionais a serem passados como argumentos nomeados para a função
    Retorna: Um DataFrame com os resultados da aplicação das funções
    """

    if axis == 'index':
        axis = 0
    elif axis == 'columns':
        axis = 1

    df_result = []
    col_result = []
    ind_result = []

    if raw:
        for i in range(len(df)):
            df[i] = numpy.array(df[i], dtype=object) # Transforma a linha para um ndarray do módulo NumPy

    if by_row == 'compat': # Verifica qual o melhor tipo de aplicação (em série ou para cada elemento individualmente)
        try:
            result_format = apply_function([1, 2, 3], func, **kwargs)
            by_row = False
        except Exception:
            result_format = apply_function(123, func, **kwargs)
            by_row = True

    if by_row:
        df_result, col_result, ind_result = df_map(df, col, ind, func, axis, **kwargs)
    elif not by_row:
        df_result, col_result, ind_result = agg(df, col, ind, func, axis, **kwargs)
    else:
        df_result, col_result, ind_result = df_map(df, col, ind, func, axis, **kwargs)

    if isinstance(df_result, str):
        return df_result

    if isinstance(result_format, (list, numpy.ndarray)):
        if axis == 1:
            for i in range(len(df_result)):
                df_result[i] = df_result[i][0]
        else:
            df_result = df_result[0]

    if not isinstance(func, (list, dict)):
        if isinstance(result_format, (list, numpy.ndarray)) and axis == 0:
            temp = copy.deepcopy(df_result)
            df_result = []

            for j in range(len(temp[0])):
                aux = []

                for i in range(len(temp)):
                    aux.append(temp[i][j])

                df_result.append(aux)

    if isinstance(result_format, (list, numpy.ndarray)):
        if axis == 0 and len(df_result) != len(df):
            return "Erro: Formato dos valores passados é (" + str(len(df_result)) + ", " + str(len(df_result[0])) + "), porém os indexes implicam o formato ("  + str(len(df)) + ", " + str(len(df[0])) + ")"
        elif axis == 1 and len(df_result[0]) != len(df[0]):
            return "Erro: Formato dos valores passados é (" + str(len(df_result)) + ", " + str(len(df_result[0])) + "), porém os indexes implicam o formato ("  + str(len(df)) + ", " + str(len(df[0])) + ")"
        else:
            col_result = copy.deepcopy(col)
            ind_result = copy.deepcopy(ind)

    if result_type == 'broadcast':
        if not isinstance(func, (list, dict)):
            if not isinstance(result_format, (list, dict, numpy.ndarray)):
                col_result = copy.deepcopy(col)
                ind_result = copy.deepcopy(ind)
                value = df_result[0][0]

                for i in range(len(df_result)):
                    for j in range(len(df_result[i])):
                        if len(df_result[i]) < len(df[i]):
                            df_result[i].append(value)

                if len(df_result) < len(df):

                    for i in range(len(df)-1):
                        df_result.append(df_result[0])

    return df_result, col_result, ind_result

def to_csv(df, col, ind, arq=None, sep=',', na_rep='', float_format=None, columns=None, header=True, index=True):

    """
    Grava os dados de um DataFrame em um arquivo no formato CSV
    Seus parâmetros são:
     - df: DataFrame que será convertida para o formato CSV (em string ou arquivo)
     - col: Rótulos das colunas do DataFrame
     - ind: Nome dos indexes das linhas do DataFrame
     - arq: Arquivo que será salvo o DataFrame convertido
     - sep: Caractere que será utilizado como separador
     - na_rep: String que será utilizado para definir como lidar com dados faltantes, o que será colocado
               para preencher esses valores
     - float_format: String que determinará como os valores de ponto flutuantes serão formatados
     - columns: String ou lista de colunas que serão escritas
     - header: Lista ou bool que define se serão incluídos os rótulos das colunas
     - index: Lista ou bool que define ser serão incluídos os indexes das linhas
    Retorna: Uma string ou None, dependendo do argumento de arq
    """

    if columns != None: # Chama a função verify_columns para pegar os indexes
        if header == True or header == False:
            index_columns = verify_columns(col, columns)
        else:
            index_columns = verify_columns(header, columns)

        if index_columns == None:
            return None

    # String que armazenará os dados do DataFrame no formato CSV
    string_csv = ''

    # Auxiliares para caso sejam incluídos os indexes das linhas ou das colunas
    il = 0
    ic = 0
    auxl = 0
    auxc = 0

    # Verifica se os nomes virão do df original ou dos outros parâmetros (header/index)
    if header == True:
        name_col = col
    else:
        name_col = header

    if index == True:
        name_ind = ind
    else:
        name_ind = index

    if header != False: # Os rótulos serão incluídos na string
        il = 1 # Define com 1 o auxiliar para as linhas, pois como será adicionado os rótulos,
               # necessitará de uma linha a mais (loop)

    if index != False: # Os indexes serão incluídos na string
        ic = 1 # Define com 1 o auxiliar para as colunas, pois como será adicionado os indexes,
               # necessitará de uma coluna a mais (loop)

    for i in range(len(df)+il): # Acessando as linhas do DataFrame
        for j in range(len(df[0])+ic): # Acessando as colunas do DataFrame

            if header != False:
                if index != False: # header == True (ou lista) e index == True (ou lista)
                    if (i == 0 and j == 0):
                        string_csv += ' '
                    elif i == 0:
                        if columns == None or (j-ic in index_columns): # Caso columns possua um argumento, verifica se a coluna faz parte da lista de colunas
                            string_csv += str(name_col[auxc])
                            auxc += 1
                    elif j == 0:
                        string_csv += str(name_ind[auxl])
                        auxl += 1
                    else:
                        if columns == None or (j-ic in index_columns):
                            string_csv = verify_condition(df[i-il][j-ic], na_rep, float_format, string_csv)

                else: # header == True (ou lista) e index == False
                    if i == 0:
                        if columns == None or (j-ic in index_columns):
                            string_csv += str(name_col[auxc])
                            auxc += 1
                    else:
                        if columns == None or (j-ic in index_columns):
                            string_csv = verify_condition(df[i-il][j-ic], na_rep, float_format, string_csv)

            else: # header == False
                if index != False: # header == False e index == True (ou lista)

                    if j == 0:
                        string_csv += str(name_ind[auxl])
                        auxl += 1
                    else:
                        if columns == None or (j-ic in index_columns):
                            string_csv = verify_condition(df[i-il][j-ic], na_rep, float_format, string_csv)
                else: # header == False e index == False
                    if columns == None or (j-ic in index_columns):
                        string_csv = verify_condition(df[i-il][j-ic], na_rep, float_format, string_csv)

            if j < len(df[0])+ic-1: # Verifica se não é a última coluna
                if columns == None or j < len(columns)+ic-1:
                    string_csv += str(sep)

            elif i < len(df)+il-1: # Verifica se não é a última linha, e como está
                                   # sendo utilizado elif, é garantido que é a última coluna
                string_csv += '\n'


    # Verifica o que foi passado como argumento em arq
    if arq == None: # Valor padrão, retornará o CSV como uma string em vez de arquivo
        return string_csv

    else: # Caso contrário, significa que passou o caminho de um arquivo

        if isinstance(arq, str): # Verifica se é passado um caminho em string
            # Abre um arquivo no modo de escrita
            arquivo = open(arq, 'w')

        elif not arq.closed and arq.writable(): # Verifica se o arquivo está aberto e se é possível escrever nele
            arquivo = arq

        # Escreve a string previamente formatada em CSV no arquivo
        arquivo.write(string_csv)

        # Fecha o arquivo
        arquivo.close()

        return None

def read_csv(fl, sep=',', header='infer', names=None, index_col=None, usecols=None, dtype=None, quotechar='"'):

    """
    Função que lê os dados de um arquivo CSV
    Seus parâmetros são:
     - fl: Arquivo (file) que será lido
     - sep: Caractere que será utilizado como separador/delimitador
     - header: Inteiro que definirá a linha em que se encontra os rótulos das colunas
     - names: Lista que contêm os rótulos das colunas
     - index_col: Index numérico ou rótulo da coluna em que se encontra os indexes das linhas
     - usecols: Lista com as colunas que serão lidas
     - dtype: Determina qual o tipo de dado que os valores do DataFrames serão formatados, podendo receber um dicionário
     - quotechar: Recebe uma string de tamanho 1 que será utilizado como um delimitador de campos
    Retorna: Um DataFrame (matriz, coluna, índice)
    """

    try:
        req = requests.get(fl)
        req.raise_for_status()
        file_read = req.text
        fl_open = False
    except requests.exceptions.RequestException:
        try:
            file = open(fl, 'r', encoding='utf-8')
            fl_open = True

            file_read = file.read()
        except Exception:
            return "Erro: Falha ao abrir arquivo"

    df = []
    col = []
    ind = []

    string = ''
    aux = []
    quote = False

    for i in range(len(file_read)):

        if file_read[i] == sep and not quote:
            aux.append(string) # Adiciona um elemento (string) na linha aux
            string = ''
        elif file_read[i] == "\n" and not quote:
            if len(string) == 0:
                string = float('nan')
            aux.append(string) # Adiciona um elemento (string) na linha (aux)
            string = ''
            df.append(aux) # Adiciona uma linha (aux) no DataFrame
            aux = []
        elif file_read[i] == quotechar:
            if quote:
                quote = False
            else:
                quote = True
        else:
            string += str(file_read[i])

    if names != None and not isinstance(header, int):
        if len(names) != len(df[0]):
            print("Erro: names apresenta " + str(len(names)) + " campos enquanto que o DataFrame possui " + str(len(df[0])) + " colunas")
            return None

        for i in range(len(names)):
            for j in range(len(names)):
                if i != j and names[i] == names[j]:
                    print("Erro: Coluna " + str(names[i]) + " está duplicada")
                    return None

        else:
            col = names.copy()

    elif header == 'infer' or (header == None and names == None):
        col = df[0]
        df.pop(0)

    elif isinstance(header, int):
        if header < len(df):
            col = df[header]
            df.pop(header)
        else:
            return "Erro: header está fora dos limites das colunas" # Pensar em uma mensagem melhor

    # Pega o índice numérico da coluna que contêm os indexes
    if not isinstance(index_col, bool) and (isinstance(index_col, int) or isinstance(index_col, str)):
        if isinstance(index_col, str):
            if index_col in col:
                index_col = col.index(index_col)
            else:
                return "Erro: Coluna não encontrada"

        c = index_col

        if c >= len(df): # Se for uma coluna que não está contido na lista, retorna um erro
            return "Erro: index_col está fora dos limites das colunas" # Pensar em uma mensagem melhor

        else:
            ind.insert(0, col[c])
            col.pop(c)

            for i in range(len(df)):
                ind.append(df[i][c])
                df[i].pop(c)

    else: # Se não for informado nenhum valor no parâmetro index_col, cria-se um novo index sequencial
        seq = 0

        for i in range(len(df)):
            ind.append(seq)
            seq += 1

    if len(df) < len(ind):
        df.insert(0, [None]*len(col))

    if usecols != None:

        count = 0
        aux = []

        for i in range(len(usecols)):
            if isinstance(usecols, int):
                count += 1

        if count == len(usecols): # Verifica se usecols é uma lista de índices numéricos
            for j in range(len(usecols)):

                if j in usecols:
                    aux.append(col[j])

            usecols = aux # Transforme a lista de índices numéricos para uma lista de rótulos

        for j in range(len(col)-1, -1, -1):
            if j < len(col) and not col[j] in usecols:
                col.pop(j)

                for i in range(len(df)):
                    df[i].pop(j)

    list_float = []
    list_str = []

    for i in range(len(df)): # Conversão dos números para seus respectivos tipos
        for j in range(len(df[i])):
            if df[i][j] != None:
                if isinstance(df[i][j], str) and df[i][j].replace('.', '', 1).isnumeric(): # Utiliza replace para remover um ponto (.), pois isnumeric
                                                                                           # não identifica valores com ponto como um valor numérico
                    df[i][j] = float(df[i][j])

                    if df[i][j] - int(df[i][j]) == 0:
                        df[i][j] = int(df[i][j])
                    elif not j in list_float:
                        list_float.append(j)

                elif not j in list_str:
                    list_str.append(j)

    for c in range(len(list_str)): # Conversão para string
        for i in range(len(df)):
            if list_str[c] < len(df[i]) and df[i][list_str[c]] != None:
                df[i][list_str[c]] = str(df[i][list_str[c]])

    for c in range(len(list_float)): # Conversão para float das colunas que tenham no mínimo um valor do tipo float
        if not list_float[c] in list_str:
            for i in range(len(df)):
                if list_float[c] < len(df[i]) and df[i][list_float[c]] != None:
                    df[i][list_float[c]] = float(df[i][list_float[c]])

    if dtype != None: # Caso seja informado um valor diferente de None, realiza a conversão dos valores numéricos
        if isinstance(dtype, dict): # Verifica se é um dicionário
            keys = list(dtype.keys()) # Pega a lista das chaves do dicionário (converte em lista, pois a função keys()
                                        # retorna um objeto do tipo dict_keys)

            for i in range(len(keys)): # Percorre a lista de chaves
                if keys[i] in col: # Verifica se a chave está presente na lista de colunas
                    c = col.index(keys[i])

                    for l in range(len(df)):
                        if df[l][c] != None:
                            key_type = dtype.get(keys[i])

                            if isinstance(key_type, str): # Se receber uma string, converte-a em sua respectiva classe para a
                                                      # conversão posterior
                                if key_type == "int":
                                    key_type = int
                                elif key_type == "float":
                                    key_type = float

                            if not isinstance(df[l][c], str):
                                df[l][c] = key_type(df[l][c])
                            else:
                                return "Erro: Não é possível converter uma String para um valor numérico."
                else:
                    return "Erro: Coluna não encontrada"
        else:
            if isinstance(dtype, str): # Se receber uma string, converte-a em sua respectiva classe para a conversão posterior
                if dtype == "int":
                    dtype = int
                elif dtype == "float":
                    dtype = float

            for i in range(len(df)):
                for j in range(len(df[i])):
                    if (dtype == int or dtype == float or dtype == complex) and isinstance(df[i][j], str):
                        return "Erro: Não é possível converter uma String para um valor numérico"
                    else:
                        if df[i][j] != None:
                            df[i][j] = dtype(df[i][j])

    if fl_open:
        file.close()

    return df, col, ind

def concat(objs, axis=0, join='outer', ignore_index=False, verify_integrity=False, sort=False, copy_p=True):

    """
    Função que realiza a concatenação de duas ou mais DataFrames/Series
    Seus parâmetros são:
     - objs: Lista com os DataFrames/Series que serão concatenados
     - axis: Eixo da operação de concatenação
     - join: Define quais colunas/linhas irão para o resultado
        - 'outer': Todas as colunas/linhas serão incluídas na concatenação
        - 'inner': Apenas as colunas/linhas que estão presentes em todos os DataFrames/Series serão incluídas na concatenação
     - ignore_index: Determina se será criado uma nova indexação sequencial para o resultado
     - verify_integrity: Verifica se há colunas/linhas com nomes repetidos, em que:
        - True: Retorna um erro caso houver
        - False: Não faz nada
     - sort: Define se as colunas/linhas serão organizadas em ordem lexicográfica
     - copy: Realiza a cópia quando possível

    Importante: Os elementos do DataFrame (matriz, coluna, index) e da Series (vetor, index) devem estar
    dentro de uma lista para a identificação e separação dos mesmos.
    """

    df_result = []
    col_result = []
    ind_result = []

    seq = -1 # Rótulos (sequência) para Series, pois não apresentam rótulos, apenas indexes
    pointer = 0 # Variável auxiliar que será utilizado para apontar a última posição (index da linha/coluna) do DataFrame/Series a
                # adicionado

    if axis == 0 or axis == 'index': # Concatenação em linhas
        if join == 'outer': # Todas as linhas/colunas serão incluídas

            if copy_p: # Se for copy == True, então realiza a operação em uma cópia
                if check_type(objs[0]): # Se True, então é um DataFrame
                    df_result = copy.deepcopy(objs[0][0])
                    col_result = copy.deepcopy(objs[0][1])
                    ind_result = copy.deepcopy(objs[0][2])
                else: # Se False, então é uma Series
                    seq += 1
                    col_result.append(seq)

                    for i in range(len(objs[0][0])):
                        df_result.append([objs[0][0][i]])

                    ind_result.append = objs[0][1]

            else:
                if check_type(objs[0]): # Se True, então é um DataFrame
                    df_result = objs[0][0]
                    col_result = objs[0][1]
                    ind_result = objs[0][2]
                else: # Se False, então é uma Series
                    seq += 1
                    col_result.extend([seq])

                    for i in range(len(objs[0][0])):
                        df_result.extend([[objs[0][0][i]]])

                    ind_result = objs[0][1]

        for o in objs: # Percorre a lista de objetos (DataFrames/Series) - axis == 0
            if check_type(o): # DataFrame
                df = o[0]
                col = o[1]
                ind = o[2]
            else:
                df = o[0]
                ind = o[1]
                seq += 1
                col = [seq] # Em formato de lista para funcionar como se fosse um DataFrame

            if join == 'inner': # Se for inner, será realizado a verificação para cada coluna entre todos os objetos, em que
                                # apenas aqueles que aparacem em todos os objetos serão adicionados ao resultado

                columns = inner_join(objs, axis) # Pega os rótulos das colunas que irão para o resultado

                for i in range(len(ind)): # Independente do caso (DataFrame ou Series), percorre-se as linhas
                    row = []

                    for j in range(len(col)): # Percorre as colunas
                        if col[j] in columns: # Se estiver presente na lista de coluna que serão incluídas no resultado
                            if col[j] in col_result and verify_integrity: # Verifica se a coluna já não está presente e se verify_integrity == True
                                return "Erro: Coluna apresenta rótulos repetidos"

                            row.extend([float('nan')])

                            if col[j] not in col_result:
                                col_result.extend([col[j]])

                            if col[j] in col_result:
                                index = col_result.index(col[j])

                                if check_type(o): # DataFrame
                                    row[index] = df[i][col.index(col[j])]
                                else: # Series
                                    row[index] = df[i]

                    if len(row) > 0:
                        df_result.extend([row])
                        ind_result.extend([ind[i]])

            elif join == 'outer':
                if objs.index(o) != 0: # Pula o primeiro elemento
                    for j in range(len(col)): # Percorre as colunas
                        if col[j] in col_result and verify_integrity == True: # Verifica se a coluna já não está presente e se verify_integrity == True
                            return "Erro: Coluna apresenta rótulos repetidos"

                        elif col[j] not in col_result:
                            col_result.extend([col[j]]) # Adiciona as colunas que não em presentes em col_result

                            for i in range(len(df_result)): # Para cada coluna adicionada, adiciona mais um elemento NaN para cada linha
                                df_result[i].extend([float('nan')])

                    for i in range(len(ind)):
                        ind_result.extend([ind[i]])

                    for i in range(len(ind)): # Percorre as linhas do df que será adicionado ao resultado
                        row = ["NaN"]*len(col_result)

                        for j in range(len(col)): # Percorre as colunas do df que será adicionado
                            if col[j] in col_result: # Se a coluna estiver presente busca a posição dela
                                index = col_result.index(col[j])

                                if check_type(o): # DataFrame
                                    row[index] = df[i][col.index(col[j])] # Altera o valor da posição correspondente
                                else: # Series
                                    row[index] = df[i] # Altera o valor da posição correspondente

                        df_result.extend([row])

    elif axis == 1 or axis == 'columns': # Concatenação em colunas
        if join == 'inner':
            indexes = inner_join(objs, axis)

            for o in objs:
                if check_type(o): # DataFrame
                    df = o[0]
                    col = o[1]
                    ind = o[2]
                else: # Series
                    df = o[0]
                    ind = o[1]
                    seq += 1
                    col = [seq] # Em formato de lista para funcionar como um DataFrame

                for j in range(len(col)): # Percorre as colunas do objeto o
                    col_result.extend([col[j]]) # Adiciona todas as colunas do objeto o ao resultado

                for i in range(len(ind)): # Percorre as linhas de o
                    if ind[i] in indexes:
                        if ind[i] not in ind_result: # Se o index ainda não estiver incluído no resultado, inclui-se ele e uma nova linha
                            ind_result.extend([ind[i]])
                            df_result.extend([[]])

                        if ind[i] in ind_result: # Verifica se o index já foi incluído e caso for, procura a linha correspondente
                            if verify_integrity == True:
                                return "Erro: Linha apresenta indexes repetidos"
                            else:
                                if not check_type(o):
                                    df[i] = [df[i]]

                                df_result[ind_result[pointer:].index(ind[i])] += df[i]

        elif join == 'outer':
            for o in objs:
                if check_type(o): # DataFrame
                    df = o[0]
                    col = o[1]
                    ind = o[2]
                else: # Series
                    df = o[0]
                    ind = o[1]
                    seq += 1
                    col = [seq] # Em formato de lista para funcionar como um DataFrame

                for i in range(len(ind)): # Percorre os indexes do objeto o
                    if ind[i] not in ind_result: # Verifica se tal index ainda não foi adicionado ao resultado
                        ind_result.extend([ind[i]]) # Se ainda não estiver, adiciona
                        df_result.extend([[float('nan')] * len(col_result)]) # Para cada index incluído, adiciona-se uma
                                                                             # nova linha, com a quantidade de suas colunas
                                                                             # dependendo das colunas já incluídas no resultado

                    elif ind[i] in ind_result and verify_integrity == True:
                        return "Erro: Linha apresenta indexes repetidos"

                for j in range(len(col)): # Percorre cada coluna de o
                    col_result.extend([col[j]]) # Adiciona cada coluna ao resultado

                for i in range(len(df_result)): # Percorre as linhas do DataFrame resultante
                    for j in range(len(col)): # Em cada linha, percorre suas colunas
                        df_result[i].extend([float('nan')]) # Adiciona mais um elemento NaN na linha, em função da quantidade
                                                            # de colunas

                for i in range(len(ind)):
                    row = df_result[ind_result.index(ind[i])]

                    for j in range(len(col)):
                        if col[j] in col_result:
                            if col[j] in col_result[pointer:len(col_result)]:
                                index = col_result[pointer:len(col_result)].index(col[j]) + pointer
                            else:
                                index = col_result.index(col[j])

                            if check_type(o): # DataFrame
                                row[index] = df[i][j]
                            else: # Series
                                row[index] = df[i]

                pointer += len(col)

    """ ============== IGNORE_INDEX ============== """

    i_seq = 0

    if ignore_index == True: # Caso ignore_index == True, cria uma nova indexação para o DataFrame resultante
        if axis == 0:
            for i in range(len(ind_result)):
                ind_result[i] = i_seq
                i_seq += 1

        elif axis == 1:
            for j in range(len(col_result)):
                col_result[j] = i_seq
                i_seq += 1


    """ ================= SORT  ================= """

    if sort == True:
        if axis == 0: # Em linha

            # Bubble Sort
            for c1 in range(len(col_result)):
                for c2 in range(len(col_result)-1-c1):
                    if str(col_result[c2]) > str(col_result[c2+1]):
                        aux = col_result[c2]
                        col_result[c2] = col_result[c2+1]
                        col_result[c2+1] = aux

                        for i in range(len(df_result)):
                            aux = df_result[i][c2]
                            df_result[i][c2] = df_result[i][c2+1]
                            df_result[i][c2+1] = aux

        elif axis == 1:
            for l1 in range(len(ind_result)):
                for l2 in range(len(ind_result)-1-l1):
                    if str(ind_result[l2]) > str(ind_result[l2+1]):
                        aux = ind_result[l2]
                        ind_result[l2] = ind_result[l2+1]
                        ind_result[l2+1] = aux

                        for j in range(len(df_result[l2])):
                            aux = df_result[l2][j]
                            df_result[l2][j] = df_result[l2+1][j]
                            df_result[l2+1][j] = aux

    return df_result, col_result, ind_result

def maiorTamanho (v):
    """
    Encontra o elemento com maior tamanho no vetor v.
    """
    maior = 0

    for i in range(len(v)):
        tamanho = len(str(v[i]))
        if tamanho > maior:
            maior = tamanho
    
    return maior

def head(df, col, ind, n=5):

    """
    Função que recebe um DataFrame para imprimir as suas n primeiras linhas
    Seus parâmetros são:
     - df: Matriz com os elementos do DataFrame
     - col: Vetor com os rótulos das colunas do DataFrame
     - ind: Vetor com os indexes das linhas do DataFrame
     - n: Quantidade de linhas que serão impressas
    Retorna: Nada
    """

    dict_columns = {}
    dtype_columns = [None]*len(col)

    for i in range(len(df)):
        for j in range(len(df[i])):
            if dtype_columns[j] != float:
                dtype_columns[j] = type(df[i][j])

    for j in range(len(col)):
        for i in range(len(df) if n > len(df) else n):
            if col[j] not in dict_columns.keys():
                dict_columns.update({col[j]:[len(str(col[j]))]})

            if j < len(df[i]):
                if isinstance(df[i][j], (int, float)) and dtype_columns[j] == float and not math.isnan(df[i][j]):
                    dict_columns.get(col[j]).append(len(str(int(df[i][j])))+6)
                else:
                    dict_columns.get(col[j]).append(len(str(df[i][j])))

    list_ind = []

    for i in range(len(ind)):
        list_ind.append(len(str(ind[i])))

    keys = list(dict_columns.keys())

    for i in range(len(keys)):
        dict_columns[keys[i]] = max(dict_columns.get(keys[i]))

    # Impressão

    string = "{:^" + str(max(list_ind)) + "} "

    col_str = string

    for j in range(len(col)):
        col_str = col_str + "{:>" + str(dict_columns.get(col[j])) + "}"

        if isinstance(df[0][j], float):
            string = string + "{:>" + str(dict_columns.get(col[j])) + ".5f}"
        else:
            string = string + "{:>" + str(dict_columns.get(col[j])) + "}"

        if j < len(col)-1:
            string = string + "  "
            col_str = col_str + "  "

    print(col_str.format("", *col))
    
    df_copy = copy.deepcopy(df)

    for i in range(len(df_copy)):
        for j in range(len(df_copy[i])):
            if type(df_copy[i][j]) != int and type(df_copy[i][j]) != float:
                df_copy[i][j] = str(df_copy[i][j])

    for i in range(len(df_copy) if n > len(df_copy) else n):
        print(string.format(str(ind[i]), *df_copy[i]))
