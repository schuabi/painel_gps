#!/usr/bin/env python
# coding: utf-8

# In[160]:


import pandas as pd
from datetime import datetime


# In[161]:


gps = pd.read_csv("C:/dashboard_onibus/dados/dados_gps.csv", sep=";")
faixas = pd.read_csv("C:/dashboard_onibus/dados/faixas_horarias.csv", sep=";")
linhas = pd.read_csv("C:/dashboard_onibus/dados/linhas_e_nucleos.csv", sep=";")
programacao = pd.read_csv("C://dashboard_onibus/dados/programacao_partidas.csv", sep=";")


# In[162]:


del gps['Linha Informada a SMTR']
del gps['Linha Realizada pela SMTR']
del gps['Veículo Consolidado pela SMTR']
del gps ['Início da Viagem pela SMTR']
del gps ['Término da Viagem pela SMTR']
del gps ['Viagem Reconhecida']


# In[163]:


gps_nucleo = pd.merge(gps, linhas, on="Linha", how="left")


# In[164]:


del gps_nucleo['Tipo Linha']
del gps_nucleo['Nome_Linha']


# In[165]:


gps_nucleo['Início da Viagem'] = pd.to_datetime(gps_nucleo['Início da Viagem'], dayfirst=True)


# In[166]:


gps_nucleo['Término da Viagem'] = pd.to_datetime(gps_nucleo['Término da Viagem'], format='%d/%m/%Y %H:%M:%S', errors='coerce')


# In[167]:


# 1. Extrair a hora da viagem como time
gps_nucleo['hora_viagem'] = gps_nucleo['Início da Viagem'].dt.time


# In[168]:


# 2. Adicionar chave auxiliar para cross join
gps_nucleo['_key'] = 1
faixas['_key'] = 1


# In[169]:


# Cross join
merged = pd.merge(gps_nucleo, faixas, on='_key')


# In[170]:


# Converte hora_inicio e hora_fim para tipo time
merged['hora_inicio'] = pd.to_datetime(merged['hora_inicio'], format='%H:%M:%S').dt.time
merged['hora_fim'] = pd.to_datetime(merged['hora_fim'], format='%H:%M:%S').dt.time


# In[171]:


# Filtra registros com hora_viagem dentro do intervalo da faixa horária
resultado = merged[(merged['hora_viagem'] >= merged['hora_inicio']) & (merged['hora_viagem'] <= merged['hora_fim'])]


# In[172]:


# Selecionar colunas necessárias
resultado = resultado[['Início da Viagem', 'Faixa_Horaria']]


# In[173]:


# Mescla com gps_nucleo
gps_nucleo = gps_nucleo.merge(resultado, on='Início da Viagem', how='left')


# In[174]:


# Remove duplicatas com base em todas as colunas
gps_nucleo = gps_nucleo.drop_duplicates()


# In[175]:


# Exporta para CSV
#gps_nucleo.to_csv("C:/dashboard_onibus/gps_com_faixa_horaria.csv", sep=";", index=False, encoding='utf-8-sig')


# In[176]:


# Faz a contagem de partidas por linha e faixa horária
partidas_executadas = gps_nucleo.groupby(['Linha', 'Faixa_Horaria']).size().reset_index(name='Total_Partidas')


# In[177]:


# Ordena por Linha e Faixa_Horaria para melhor visualização
partidas_executadas = partidas_executadas.sort_values(by=['Linha', 'Faixa_Horaria'])


# In[178]:


# (Opcional) Exporta para CSV
#partidas_executadas.to_csv("C:/dashboard_onibus/partidas_executadas.csv", sep=";", index=False, encoding='utf-8-sig')


# In[179]:


# 2. Garantir que as colunas estejam sem espaços
programacao.columns = programacao.columns.str.strip()
partidas_executadas.columns = partidas_executadas.columns.str.strip()


# In[180]:


# 3. Renomear a coluna da contagem de executadas (se ainda não estiver)
# Supondo que partidas_executadas tenha as colunas: 'Linha', 'Faixa_Horaria', 'Partidas'
partidas_executadas = partidas_executadas.rename(columns={'Total_Partidas': 'Executado'})


# In[181]:


#partidas_executadas


# In[185]:


programacao = programacao.rename(columns={'Faixa': 'Faixa_Horaria', 'linha': 'Linha'})


# In[186]:


#programacao


# In[187]:


comparativo = pd.merge(
    partidas_executadas,
    programacao.rename(columns={'partidas_programadas': 'Programado'}),
    how='left',
    on=['Linha', 'Faixa_Horaria']
)


# In[188]:


#comparativo


# In[189]:


# 5. Corrigir possíveis NaN em Programado (caso tenha faixa que não existia na programação)
comparativo['Programado'] = comparativo['Programado'].fillna(0).astype(int)


# In[190]:


# Calcular o percentual de execução
comparativo['% Execução'] = (comparativo['Executado'] / comparativo['Programado'].replace(0, 1)) * 100
comparativo['% Execução'] = comparativo['% Execução'].round(1)


# In[191]:


# Se programado era zero, deixar o percentual em zero
comparativo.loc[comparativo['Programado'] == 0, '% Execução'] = 0


# In[198]:


del comparativo ['tipo_linha']


# In[199]:


#comparativo


# In[200]:


# Exportar para CSV
comparativo.to_csv('comparativo_programado_executado.csv', index=False, sep=';')

