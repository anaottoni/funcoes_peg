# -*- coding: utf-8 -*-

import math
import numpy
import sys
import io
from pympler import asizeof

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

def reshape(df, dimensao, order='C', copy=True):
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
      for i in range(dimensao[0]):
        linha = []

        for j in range(dimensao[1]):
          if ind_coluna == shape_ant[1]:
            ind_linha +=1
            ind_coluna = 0

          linha.append(df[ind_linha][ind_coluna])

          ind_coluna += 1
        novo_df.append(linha)

    # caso a ordem seja F, os valores de df serão redimensionados por coluna

    if order == 'F':

      # Pra facilitar, vamos criar as linhas e colunas de novo_df e só depois inserir todos os valores coluna por coluna
      for i in range(dimensao[0]):
        linha = [None]*dimensao[1]

        novo_df.append(linha)

      for j in range(dimensao[1]):
        for i in range(dimensao[0]):
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
      if(shape_ant[0] < dimensao[0]):
        for i in range(shape_ant[0], dimensao[0]):
          df.append([None])

      if order == 'C':
        for i in range(dimensao[0]):
          linha = []

          for j in range(dimensao[1]):
            if ind_coluna == shape_ant[1]:
              ind_linha +=1
              ind_coluna = 0

            linha.append(copia[ind_linha][ind_coluna])

            ind_coluna += 1
          df[i] = linha

      # caso a ordem seja F, os valores de df serão redimensionados por coluna

      if order == 'F':
        for i in range(dimensao[0]):
          linha = [None]*dimensao[1]

          df[i] = linha

        for j in range(dimensao[1]):
          for i in range(dimensao[0]):
            if ind_coluna == shape_ant[1]:
              ind_linha +=1
              ind_coluna = 0

            df[i][j] = copia[ind_linha][ind_coluna]

            ind_coluna += 1

      # Depois de modificar as linhas necess
      if dimensao[0] < shape_ant[0]:
        for i in range(dimensao[0], shape_ant[0]):
          df.remove(df[dimensao[0]])

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
  if type(loc_ind) != list:
      new_index.append(loc_ind)
  else:
      new_index = loc_ind.copy()


  if type(loc_col) != list:
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

def iloc(df, index, columns, *, loc_ind=None, loc_col=None):
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

    if type(loc_ind) != list:
        int_index.append(loc_ind)
    else:
        int_index = loc_ind.copy()


    if type(loc_col) != list:
        int_col.append(loc_col)
    else:
        int_col = loc_col.copy()

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

def rename (mapper=None, *, index=None, columns=None, axis=None, inplace=False):
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

def verifica_se_nulo(valor):
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
            if verifica_se_nulo(df[i][j]):
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
            if verifica_se_nulo(df[i][j]):
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

def normalizar_df(df, feature_range=(0,1), *,copy=True, clip=False):
    """
    Recebe uma amtriz df e padroniza seus valores com a técnica min-max,
    de forma que todos os seus elementos serão padronizados para o intervalo dado pela tupla feature_range
    (que possui valor padrão de 0 e 1). A matriz df padronizada será o valor de retorno da função caso
    copy = True, caso contrário a função não terá valor de retorno e as mudanças serão feitas diretamente em df.
    Caso clip=True, todos os valores resultantes da padronização que não estiverem no intervalo de feature_range serão
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

def media_col(df):
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

def desvio_padrao_col (df):
    """
    Recebe uma matriz df e retorna um vetor lista_dp com n valores, onde o
    i-esimo elemento de lista_dp corresponde ao desvio padrão da i-esima
    coluna de df
    """

    lista_dv = []

    medias = media_col(df)

    dimensao = shape(df)

    for j in range(dimensao[1]):
        somatoria = 0

        for i in range(dimensao[0]):
            somatoria += (df[i][j]-medias[j])**2

        lista_dv.append(math.sqrt(somatoria/dimensao[0]))

    return lista_dv

def padronizar_df(df, *, copy=True,with_mean=True, with_std=True):
    """
    Recebe uma matriz df e padroniza os dados de acordo com os parâmetros with_mean
    e with_std, podendo retornar uma matriz com os dados padronizados caso copy = True,
    caso contrário não possui valor de retorno, fazendo as modificações nos elementos da matriz original.
    Por padrão, obedece a formula z = (x - media_coluna) / desvio_padrao_coluna,
    onde z é o valor padronizado e x o valor orginal na matriz
    """

    dimensao = shape(df)

    lista_media = media_col(df)
    lista_dv = desvio_padrao_col(df)

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

def procura_coluna(matriz, coluna, valor):
    """
    Recebe uma matriz e verifica se o valor já está presente na coluna
    recebida por parâmetro.
    """

    if dtype(valor) != 'str' and math.isnan(valor):
        for i in range(len(matriz)):
            if math.isnan(float(matriz[i][coluna])):
                return True
    else:
        for i in range(len(matriz)):
            if matriz[i][coluna] == valor:
                return True
    return False

def conta_valor_vetor (vetor, valor):
    """
    Recebe um vetor e retorna a quantidade de vezes que o valor recebido por parâmetro
    aparece no vetor.
    """

    cont = 0

    if dtype(valor) != 'str' and math.isnan(valor):
        for i in range(len(vetor)):
            if math.isnan(vetor[i]):
                cont+=1
    else:
        for i in range(len(vetor)):
            if vetor[i] == valor:
                cont+=1

    return cont

def chave_series(m):
    """
    Função auxiliar para ordenação em series_value_counts.
    """
    return m[1]

def menor_valor(v):
    """
    Recebe um vetor v e retorna o menor valor desse vetor.
    """

    menor = v[0]

    for i in range(len(v)):
        if v[i] < menor:
            menor = v[i]

    return menor

def maior_valor(v):
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
            if procura_coluna(valor_qtd, 0, v[i]) == False:

                # se dropna for verdadeiro e v[i] igual a nan, então sua contagem não será incluida
                if dropna == True and math.isnan(v[i]):
                    continue

                # caso contrário, usamos o vetor auxiliar linha para inserir o elemento e sua respectiva contagem

                linha.append(v[i])

                # se normalize é igual a false, então a frequência absoluta simples do elemento será inseida no vetor
                if normalize == False:
                    linha.append(conta_valor_vetor(v, v[i]))

                # caso contrário, a frequência relativa (freq. absoluta/freq. total) será inserida no vetor
                else:
                    linha.append(conta_valor_vetor(v, v[i])/freq_total)

                # depois, inserimos o vetor auxiliar como uma nova linha de valor_qtd
                valor_qtd.append(linha)

    else:
        amplitude = (maior_valor(v)-menor_valor(v))/bins

        inferior = menor_valor(v)-0.005
        superior = menor_valor(v) + amplitude

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
        valor_qtd.sort(reverse=True,key=chave_series)
    elif sort == True and ascending == True:
        valor_qtd.sort(key=chave_series)

    return valor_qtd

def acha_elemento (vetor, e):
    """
    Recebe vetor e um elemento e que pode ou não estar em vetor.
    Retorna True se e estiver em vetor e False caso contrário.
    """
    for i in range(len(vetor)):
        if vetor[i] == e:
            return True

    return False

def conta_linha (df, linha, col, subset):
    """
    Conta quantas vezes uma linha de df aparece na matriz.
    """

    cont = 0
    aux = False
    for i in range(shape(df)[0]):
        for j in range(shape(df)[1]):

            if acha_elemento(subset, col[j]):
                if dtype(linha[j]) != 'str' and math.isnan(linha[j]):
                    if math.isnan(df[i][j]):
                        aux = True
                    else:
                        aux = False

                else:
                    if df[i][j] == linha[j]:
                        aux = True
                    else:
                        aux = False
                        continue

        if aux == True:
            cont+=1

    return cont

def chave_df(m):
    return m[len(m)-1]

def df_value_counts(df, col, subset=None, normalize=False, sort=True, ascending=False, dropna=True):
    """
    Função recebe uma amtriz df e retorna uma matriz contendo a contagem de cada
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
            if dropna == True and math.isnan(df[i][j]):
                linha = [] # se for, deixar a linha vazia
                break

            if acha_elemento(subset, col[j]):
                linha.append(df[i][j])

        # verifica se a linha i de v já está presente ou não na matriz e se está vazia
        if (linha in aux) == False and linha != []:

            aux.append(linha.copy())

            if normalize == False:
                linha.append(conta_linha(df,df[i], col, subset))

            else:
                linha.append(conta_linha(df,df[i], col, subset)/num_linhas)

            linhas_qtd.append(linha)

    if sort == True and ascending == False:
        linhas_qtd.sort(reverse=True,key=chave_df)
    elif sort == True and ascending == True:
        linhas_qtd.sort(key=chave_df)

    return linhas_qtd

def contar_nao_nulos_coluna(df, col):
    """
    Recebe uma matriz df e retorna a quantidade de valores não nulos da coluna de índice col.
    """

    numlin, numcol = shape(df)
    cont = 0

    for j in range(numlin):
        if df[j][col] != None:
            cont = cont + 1

    return cont

def lista_tipos (df):
    """
    Recebe uma matriz df e retorna um vetor contendo todos os tipos dos valores
    presentes em df.
    """

    numlin, numcol = shape(df)

    tipos = []

    for i in range(numcol):
        linha = []

        tipo = dtype(df[0][i])

        if  procura_coluna(tipos, 0, tipo) == False:
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
            print("RangeIndex:", numlin, "entries, 0 to", numlin-1)

            if (verbose == None or verbose == True):
                print("Data columns (total",numcol,"columns):")

                if show_counts == None or show_counts == True:

                    print('{0:^3} {1:10} {2:14} {3:10}'.format('#','Column','Non-Null Count','Dtype'))

                    print('{0:^3} {1:10} {2:14} {3:10}'.format('---','------','--------------','-----'))

                for i in range(numcol):
                    print('{0:^3} {1:<10} {2:<14} {3:<10}'.format(i,col[i],str(contar_nao_nulos_coluna(df,i))+' non-null',dtype(df[0][i])))

            else:
                print("Columns:", numcol, "entries,", col[0], "to", col[numcol-1])

            print("dtypes: ", end="")

            tipos = lista_tipos(df)
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
            buf.write("RangeIndex:"+ str(numlin)+ " entries, 0 to "+ str(numlin-1)+"\n")

            if (verbose == None or verbose == True):
                buf.write("Data columns (total "+str(numcol)+" columns):"+"\n")

                if show_counts == None or show_counts == True:

                    buf.write('{0:^3} {1:10} {2:14} {3:10}'.format('#','Column','Non-Null Count','Dtype')+"\n")

                    buf.write('{0:^3} {1:10} {2:14} {3:10}'.format('---','------','--------------','-----')+"\n")

                for i in range(numcol):
                    buf.write('{0:^3} {1:<10} {2:<14} {3:<10}'.format(i,col[i],str(contar_nao_nulos_coluna(df,i))+' non-null',dtype(df[0][i]))+"\n")

            else:
                buf.write("Columns:", numcol, "entries,", col[0], "to", col[numcol-1]+"\n")

            buf.write("dtypes: ")

            tipos = lista_tipos(df)
            numtipos = len(tipos)

            for i in range(numtipos-1):
                buf.write(str(tipos[i][0])+"("+str(tipos[i][1])+") + ")
            buf.write(str(tipos[numtipos-1][0])+"("+str(tipos[numtipos-1][1])+")"+"\n")

            if memory_usage == True or memory_usage == None:
                buf.write("memory usage: "+str((sys.getsizeof(df)+sys.getsizeof(index)+sys.getsizeof(col)))+"+ bytes"+"\n")
            elif memory_usage == 'deep':
                buf.write("memory usage: "+str(asizeof.asizeof(df)+asizeof.asizeof(index)+asizeof.asizeof(col))+"+ bytes"+"\n")

def contar_nao_nulos_coluna(df, col):
    """
    Recebe uma matriz df e retorna a quantidade de valores não nulos da coluna de índice col
    """
    numlin, numcol = shape(df)
    cont = 0.0

    for j in range(numlin):
        if df[j][col] != None:
            cont = cont + 1

    return cont

def maior_elemento_col (df, col):
    """
    Recebe uma matriz df e retorna o maior elemento da coluna de índice col
    """
    dimensao = shape(df)

    maior = df[0][col]
    for i in range(dimensao[0]):
        if df[i][col] > maior:
            maior = df[i][col]

    return maior

def menor_elemento_col (df, col):
    """
    Recebe uma matriz df e retorna o menor elemento da coluna de índice col
    """
    dimensao = shape(df)

    menor = df[0][col]
    for i in range(dimensao[0]):
        if df[i][col] < menor:
            menor = df[i][col]

    return menor

def desvio_padrao_col(df, col):
    """
    Recebe uma matriz df e retorna o desvio padrão da coluna de índice col
    """
    dimensao = shape(df)

    somatoria = 0

    for i in range(dimensao[0]):
        somatoria += (df[i][col]-calcula_media_colunas(df,col))**2

    return math.sqrt(somatoria/(dimensao[0]-1))

def calcula_media_colunas(df, col):
    """
    Recebe uma matriz df e retorna a média dos valores da coluna de índice col
    """
    numlin, numcol = shape(df)

    contador = 0

    for j in range(numlin):
        contador += df[j][col]

    return contador/numlin

def transforma_col_vetor(df,col):
    """
    Recebe uma matriz df e um índice col e retorna um vetor contendo os elementos
    da coluna col de df
    """
    vetor = []
    numlinhas, numcol = shape(df)

    for i in range(numlinhas):
        vetor.append(df[i][col])

    return vetor

def calcula_percentil(df,col, p):
    """
    Recebe uma matriz df, um índice col e um percentil p e retorna o valor do
    referido percentil na coluna col de df.
    """
    numlinhas, numcol = shape(df)
    pos = p * (numlinhas-1)

    v = transforma_col_vetor(df,col)

    v.sort()

    if(type(pos) == int):
        return v[pos]
    else:
        posinf = math.floor(pos)

        possup = math.ceil(pos)
        return v[posinf] + (pos - posinf) * (v[possup] - v[posinf])

def conta_aparicoes_col(df,col,e):
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

def valor_mais_comum_col(df,col):
    """
    Recebe uma matriz df e retorna o valor mais comum da coluna de índice col.
    """
    freq = 0
    top = df[0][col]
    aux = 0

    numlin, numcol = shape(df)

    for i in range(numlin):
       aux = conta_aparicoes_col(df,col,df[i][col])

       if aux > freq:
           freq = aux
           top = df[i][col]

    return top, freq

def conta_val_unicos(df, col):
    """
    Recebe uma matriz df e retorna a quantidade de valores únicos na coluna de índe col.
    """
    elementos_col = transforma_col_vetor(df, col)

    valores_unicos = set(elementos_col)

    return len(valores_unicos)

def tem_num(df):
    """
    Recebe uma matriz df e verifica se esta possui valores númericos.
    """
    numlin, numcol = shape(df)

    for i in range(numcol):
        if type(df[0][i]) == int or type(df[0][i]) == float:
            return True

    return False

def tem_obj(df):
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
        temnum = tem_num(df)
        temobj = tem_obj(df)

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
            saida[1].append(contar_nao_nulos_coluna(df,j))

            if obj == True:
                if eh_num == False:
                    saida[2].append(conta_val_unicos(df,j))
                    t, f = valor_mais_comum_col(df,j)
                    saida[3].append(t)
                    saida[4].append(f)
                else:
                    saida[2].append("NaN")
                    saida[3].append("NaN")
                    saida[4].append("NaN")
            if number == True:
                if eh_num == True:
                    saida[2+ind].append(calcula_media_colunas(df,j))
                    saida[3+ind].append(desvio_padrao_col(df,j))
                    saida[4+ind].append(menor_elemento_col(df,j))
                    for i in range(len(percentiles)):
                        saida[5+i+ind].append(calcula_percentil(df,j,percentiles[i]))
                    saida[5+len(percentiles)+ind].append(maior_elemento_col(df,j))
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

def quick_sort_por_coluna(a, by, index, ascending, ini=0, fim=None):
    """
    Algoritmo quick sort recursivo que ordena as linhas de a por coluna.
    """
    fim = fim if fim is not None else len(a)
    if ini < fim:
        pp = particao_por_coluna(a, ini, fim, by, index, ascending)
        quick_sort_por_coluna(a, by, index, ascending, ini, pp)
        quick_sort_por_coluna(a, by, index, ascending, pp + 1, fim)
    return a

def particao_por_coluna(a, ini, fim, by, index, ascending):
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

def quick_sort_por_linha(a, by, columns, ascending, ini=0, fim=None):
    """
    Algoritmo quick sort recursivo que ordena as colunas de a por linha.
    """
    fim = fim if fim is not None else len(a[0])
    if ini < fim:
        pp = particao_por_linha(a, ini, fim, by, columns, ascending)
        quick_sort_por_linha(a, by, columns, ascending, ini, pp)
        quick_sort_por_linha(a, by, columns, ascending, pp + 1, fim)
    return a

def particao_por_linha(a, ini, fim, by, columns, ascending):
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

def procura_indice_por_rotulo(rotulos, nome):
    """
    Procura o valor do índice de um rótulo (parâmetro nome) em uma lista de
    rótulos (parâmetro rotulos).
    """
    tamanho = len(rotulos)
    for i in range(tamanho):
        if rotulos[i] == nome:
            return i

def organiza_nan(df, index, columns, by, axis, position):
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
                if verifica_se_nulo(df[i][by]) == False:
                    copy_df.append(df[i])
                    copy_ind.append(index[i])
                    cont+=1

            for i in range(numlin):
                if verifica_se_nulo(df[i][by]):
                    copy_df.append(df[i])
                    copy_ind.append(index[i])

            fim = cont
        else:

            for i in range(numlin):
                if verifica_se_nulo(df[i][by]):
                    cont+=1
                    copy_df.append(df[i])
                    copy_ind.append(index[i])

            for i in range(numlin):
                if verifica_se_nulo(df[i][by]) == False:
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
                if verifica_se_nulo(df[by][i]) == False:
                    cont+=1
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            for i in range(numcol):
                if verifica_se_nulo(df[by][i]):
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            fim = cont

        else:
            cont = 0
            for i in range(numcol):
                if verifica_se_nulo(df[by][i]):
                    cont+=1
                    for k in range(numlin):
                        copy_df[k].append(df[k][i])
                    copy_col.append(columns[i])

            for i in range(numcol):
                if verifica_se_nulo(df[by][i]) == False:
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
            pos_by = procura_indice_por_rotulo(columns, by)
            copy_df, copy_index, ini, fim = organiza_nan(df,index, columns, pos_by,axis,na_position)

            df.clear()
            index.clear()

            df.extend(copy_df)
            index.extend(copy_index)

            df = quick_sort_por_coluna(copy_df, by, index, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numlin):
                    index[i] = i
        else:
            pos_by = procura_indice_por_rotulo(index, by)
            copy_df, copy_columns, ini, fim = organiza_nan(df,index, columns, pos_by,axis,na_position)

            df.clear()
            columns.clear()

            df.extend(copy_df)
            columns.extend(copy_columns)

            df = quick_sort_por_linha(copy_df, pos_by, columns, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numcol):
                    columns[i] = i

    else:
        if axis == 0:
            pos_by = procura_indice_por_rotulo(columns, by)

            copy_df, copy_index, ini, fim = organiza_nan(df,index, columns, pos_by,axis,na_position)

            copy_df = quick_sort_por_coluna(copy_df, pos_by, copy_index, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numlin):
                    copy_index[i] = i

            copy_columns.extend(columns)
        else:
            pos_by = procura_indice_por_rotulo(index, by)
            copy_df, copy_columns, ini, fim = organiza_nan(df,index, columns, pos_by,axis,na_position)

            copy_df = quick_sort_por_linha(copy_df, pos_by, copy_columns, ascending, ini, fim)

            if ignore_index == True:
                for i in range(numcol):
                    copy_columns[i] = i

            copy_index.extend(index)

        return copy_df, copy_index, copy_columns
    
def minimo_col(df, col):
    """
    Encontra o índice da linha do menor valor presente na matriz df e coluna col.
    """
    cont = 0
    menor = None
    pos_menor = 0
    dimensao = shape(df)

    while(cont < dimensao[0]):
        if verifica_se_nulo(df[cont][col]) == False:
            menor = df[cont][col]
            break
        cont+=1

    pos_menor = cont

    if menor != None:
        for i in range(dimensao[0]):
            if verifica_se_nulo(df[i][col]) == False and df[i][col] < menor:
                menor = df[i][col]
                pos_menor = i

    return pos_menor

def verifica_nulo_coluna (df,col):
    """
    Recebe uma matriz df e um índice de coluna col e retorna o índice
    da linha que possuir valor nulo na referida coluna. Caso não houver, retorna -1.
    """
    dimensao = shape(df)

    for i in range(dimensao[0]):
        if verifica_se_nulo(df[i][col]) == True:
            return i
    return -1

def verifica_nulo_linha (df,ind):
    """
    Recebe uma matriz df e um índice de linha e retorna o índice
    da coluna que possuir valor nulo na referida linha. Caso não houver, retorna -1.
    """
    dimensao = shape(df)

    for i in range(dimensao[1]):
        if verifica_se_nulo(df[ind][i]) == True:
            return i
    return -1

def minimo_linha(df, ind):
    """
    Encontra o índice da coluna do menor valor presente na matriz df e linha ind.
    """
    cont = 0
    menor = None
    pos_menor = 0
    dimensao = shape(df)

    while(cont < dimensao[1]):
        if verifica_se_nulo(df[ind][cont]) == False:
            menor = df[ind][cont]
            break
        cont+=1

    pos_menor = cont

    if menor != None:

        for i in range(dimensao[1]):
            if verifica_se_nulo(df[ind][i]) == False and df[ind][i] < menor:
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
                aux = verifica_nulo_coluna(df,i)
                if aux != -1:
                    linha.append(index[aux])
                else:
                    linha.append(index[minimo_col(df,i)])
            else:
                linha.append(index[minimo_col(df,i)])
            new_df.append(linha)

    else:
        for i in range(numlin):
            linha = []
            linha.append(index[i])

            if skipna == True:
                aux = verifica_nulo_linha(df,i)
                if aux != -1:
                    linha.append(columns[aux])
                else:
                    linha.append(columns[minimo_linha(df,i)])
            else:
                linha.append(columns[minimo_linha(df,i)])
            new_df.append(linha)

    return new_df

def maximo_col(df, col):
    """
    Encontra o índice da linha do maior valor presente na matriz df e coluna col.
    """
    cont = 0
    maior = None
    pos_maior = 0
    dimensao = shape(df)

    while(cont < dimensao[0]):
        if verifica_se_nulo(df[cont][col]) == False:
            maior = df[cont][col]
            break
        cont+=1

    pos_maior = cont

    if maior != None:
        for i in range(dimensao[0]):
            if verifica_se_nulo(df[i][col]) == False and df[i][col] > maior:
                maior = df[i][col]
                pos_maior = i

    return pos_maior

def maximo_linha(df, ind):
    """
    Encontra o índice da coluna do maior valor presente na matriz df e linha ind.
    """
    cont = 0
    maior = None
    pos_maior = 0
    dimensao = shape(df)

    while(cont < dimensao[1]):
        if verifica_se_nulo(df[ind][cont]) == False:
            maior = df[ind][cont]
            break
        cont+=1

    pos_maior = cont

    if maior != None:

        for i in range(dimensao[1]):
            if verifica_se_nulo(df[ind][i]) == False and df[ind][i] > maior:
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
            linha.append(index[maximo_col(df,i)])
            new_df.append(linha)

    else:
        for i in range(numlin):
            linha = []
            linha.append(index[i])
            linha.append(columns[maximo_linha(df,i)])
            new_df.append(linha)

    return new_df
