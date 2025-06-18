#!/usr/bin/env python
# coding: utf-8

# In[122]:


import pandas as pd
from datetime import datetime


# In[123]:


gps = pd.read_csv("C:/dashboard_onibus/dados/dados_gps.csv", sep=";")
faixas = pd.read_csv("C:/dashboard_onibus/dados/faixas_horarias.csv", sep=";")
linhas = pd.read_csv("C:/dashboard_onibus/dados/linhas_e_nucleos.csv", sep=";")
programacao = pd.read_csv("C://dashboard_onibus/dados/programacao_partidas.csv", sep=";")


# In[124]:


del gps['Linha Informada a SMTR']
del gps['Linha Realizada pela SMTR']
del gps['Veículo Consolidado pela SMTR']
del gps ['Início da Viagem pela SMTR']
del gps ['Término da Viagem pela SMTR']
del gps ['Viagem Reconhecida']


# In[125]:


gps_nucleo = pd.merge(gps, linhas, on="Linha", how="left")


# In[126]:


del gps_nucleo['Tipo Linha']
del gps_nucleo['Nome_Linha']


# In[127]:


gps_nucleo['Início da Viagem'] = pd.to_datetime(gps_nucleo['Início da Viagem'], dayfirst=True)


# In[128]:


gps_nucleo['Término da Viagem'] = pd.to_datetime(gps_nucleo['Término da Viagem'], format='%d/%m/%Y %H:%M:%S', errors='coerce')


# In[129]:


# 1. Extrair a hora da viagem como time
gps_nucleo['hora_viagem'] = gps_nucleo['Início da Viagem'].dt.time


# In[130]:


# 2. Adicionar chave auxiliar para cross join
gps_nucleo['_key'] = 1
faixas['_key'] = 1


# In[131]:


# Cross join
merged = pd.merge(gps_nucleo, faixas, on='_key')


# In[132]:


# Converte hora_inicio e hora_fim para tipo time
merged['hora_inicio'] = pd.to_datetime(merged['hora_inicio'], format='%H:%M:%S').dt.time
merged['hora_fim'] = pd.to_datetime(merged['hora_fim'], format='%H:%M:%S').dt.time


# In[133]:


# Filtra registros com hora_viagem dentro do intervalo da faixa horária
resultado = merged[(merged['hora_viagem'] >= merged['hora_inicio']) & (merged['hora_viagem'] <= merged['hora_fim'])]


# In[134]:


# Selecionar colunas necessárias
resultado = resultado[['Início da Viagem', 'Faixa_Horaria']]


# In[135]:


# Mescla com gps_nucleo
gps_nucleo = gps_nucleo.merge(resultado, on='Início da Viagem', how='left')


# In[136]:


# Remove duplicatas com base em todas as colunas
gps_nucleo = gps_nucleo.drop_duplicates()


# In[137]:


# Exporta para CSV
gps_nucleo.to_csv("C:/dashboard_onibus/gps_com_faixa_horaria.csv", sep=";", index=False, encoding='utf-8-sig')


# In[138]:


# Faz a contagem de partidas por linha e faixa horária
contagem_partidas = gps_nucleo.groupby(['Linha', 'Faixa_Horaria']).size().reset_index(name='Total_Partidas')


# In[139]:


# Ordena por Linha e Faixa_Horaria para melhor visualização
contagem_partidas = contagem_partidas.sort_values(by=['Linha', 'Faixa_Horaria'])


# In[140]:


# Exibe o resultado
print(contagem_partidas)


# In[141]:


# (Opcional) Exporta para CSV
contagem_partidas.to_csv("C:/dashboard_onibus/contagem_partidas_por_faixa.csv", sep=";", index=False, encoding='utf-8-sig')


# In[ ]:





# In[ ]:





# In[ ]:




