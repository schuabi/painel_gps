#!/usr/bin/env python
# coding: utf-8

# In[44]:


import pandas as pd
import datetime
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title= 'Partidas GPS', layout='wide')

# In[45]:


gps_nucleo = pd.read_csv("C:/dashboard_onibus/dados/dados_gps.csv", sep=";")
faixas = pd.read_csv("C:/dashboard_onibus/dados/faixas_horarias.csv", sep=";")
linhas = pd.read_csv("C:/dashboard_onibus/dados/linhas_e_nucleos.csv", sep=";")
programacao = pd.read_csv("C://dashboard_onibus/dados/programacao_partidas.csv", sep=";")


# In[46]:


del gps_nucleo['Linha Informada a SMTR']
del gps_nucleo['Linha Realizada pela SMTR']
del gps_nucleo['Veículo Consolidado pela SMTR']
del gps_nucleo ['Início da Viagem pela SMTR']
del gps_nucleo ['Término da Viagem pela SMTR']
del gps_nucleo ['Viagem Reconhecida']


# In[47]:


gps_nucleo = pd.merge(gps_nucleo, linhas, on="Linha", how="left")


# In[48]:


del gps_nucleo ['Tipo Linha']
del gps_nucleo ['Nome_Linha']


# In[49]:


gps_nucleo['Início da Viagem'] = pd.to_datetime(gps_nucleo['Início da Viagem'], dayfirst=True)
gps_nucleo['Término da Viagem'] = pd.to_datetime(gps_nucleo['Término da Viagem'], format='%d/%m/%Y %H:%M:%S', errors='coerce')


# In[50]:


gps_nucleo['hora_viagem'] = gps_nucleo['Início da Viagem'].dt.time


# In[51]:


gps_nucleo['_key'] = 1
faixas['_key'] = 1


# In[52]:


merged = pd.merge(gps_nucleo, faixas, on='_key')


# In[53]:


merged['hora_inicio'] = pd.to_datetime(merged['hora_inicio'], format='%H:%M:%S').dt.time
merged['hora_fim'] = pd.to_datetime(merged['hora_fim'], format='%H:%M:%S').dt.time


# In[54]:


resultado = merged[(merged['hora_viagem'] >= merged['hora_inicio']) & (merged['hora_viagem'] <= merged['hora_fim'])]


# In[55]:


resultado = resultado[['Início da Viagem', 'Faixa_Horaria']]


# In[56]:


gps_nucleo = gps_nucleo.merge(resultado, on='Início da Viagem', how='left')


# In[57]:


gps_nucleo = gps_nucleo.drop_duplicates()


# In[58]:


partidas_executadas = gps_nucleo.groupby(['Linha', 'Faixa_Horaria']).size().reset_index(name='Total_Partidas')


# In[59]:


partidas_executadas = partidas_executadas.sort_values(by=['Linha', 'Faixa_Horaria'])


# In[60]:


programacao.columns = programacao.columns.str.strip()
partidas_executadas.columns = partidas_executadas.columns.str.strip()


# In[61]:


partidas_executadas = partidas_executadas.rename(columns={'Total_Partidas': 'Executado'})


# In[62]:


programacao = programacao.rename(columns={'Faixa': 'Faixa_Horaria', 'linha': 'Linha'})


# In[63]:


comparativo = pd.merge(
    partidas_executadas,
    programacao.rename(columns={'Viagens Programadas': 'Programado'}),
    how='left',
    on=['Linha', 'Faixa_Horaria']
)


# In[64]:


comparativo['Programado'] = comparativo['Programado'].fillna(0).astype(int)


# In[65]:


comparativo['% Execução'] = (comparativo['Executado'] / comparativo['Programado'].replace(0, 1)) * 100
comparativo['% Execução'] = comparativo['% Execução'].round(1)


# In[66]:


comparativo.loc[comparativo['Programado'] == 0, '% Execução'] = 0


# In[67]:


del comparativo ['Tipo Linha']


# In[68]:


#saida = "comparativo_programado_executado_com_nucleo.csv"


# In[69]:


df_merged = pd.merge(
    comparativo,
    linhas[['Linha', 'Núcleo']],  # Mantém só a coluna necessária do núcleo
    on='Linha',
    how='left'  # Faz um left join para manter todas as linhas do comparativo
)



#df_merged['% Execução'] = df_merged['% Execução'].apply(lambda x: f"{x:.1%}")

#---------------------------------------------------------------------------------------------------------

#INICIA CRIAÇÃO DO VISUAL



#EXTRAI HORA MODIFICAÇÃO ARQUIVO DADOS

# Caminho do arquivo
file_path = r'C:\dashboard_onibus\dados\dados_gps.csv'

# Verificar se o arquivo existe
if os.path.exists(file_path):
    # Timestamp da última modificação
    timestamp_modificacao = os.path.getmtime(file_path)

    # Converter para datetime
    ultima_modificacao = datetime.datetime.fromtimestamp(timestamp_modificacao)

    # Extrair hora:minuto
    hora_minuto = ultima_modificacao.strftime('%H:%M')

    # Exibir no Streamlit
    st.info(f'Dados atualizados às: {hora_minuto}')
else:
    st.error('Arquivo dados.csv não encontrado no caminho especificado!')



import streamlit as st
import matplotlib.pyplot as plt

# Sidebar - Filtro por Núcleo (agora radio buttons - seleção única)
nucleos_disponiveis = df_merged['Núcleo'].unique().tolist()
nucleo_selecionado = st.sidebar.radio(
    'Selecione o Núcleo:',
    options=nucleos_disponiveis
)

st.title(f'% de Partidas Executadas por Faixa Horária -  {nucleo_selecionado}')

# Preparar os dados
df_merged['Execucao_num'] = df_merged['% Execução'] / 100
df_merged['% Execução'] = df_merged['Execucao_num'].apply(lambda x: f"{x:.1%}")



# Criar colunas lado a lado
col1, col2, col3, col4 = st.columns(4)


### --- GRÁFICO FAIXA 00-03 ---
with col1:
    faixa0003 = df_merged[
        (df_merged['Faixa_Horaria'] == '00-03') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 00-03')

    if not faixa0003.empty:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        colors1 = ['green' if x >= 0.8 else 'red' for x in faixa0003['Execucao_num']]
        bars1 = ax1.bar(faixa0003['Linha'], faixa0003['Execucao_num'] * 100, color=colors1)

        ax1.set_xlabel('')
        ax1.set_ylabel('')
        ax1.set_title(f'Faixa de 0h às 03h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars1, faixa0003['% Execução']):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig1)
    else:
        st.info('Nenhum dado disponível para a faixa 00-03 com o núcleo selecionado.')




### --- GRÁFICO FAIXA 03-06 ---
with col2:
    faixa0306 = df_merged[
        (df_merged['Faixa_Horaria'] == '03-06') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 03-06')

    if not faixa0306.empty:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        colors2 = ['green' if x >= 0.8 else 'red' for x in faixa0306['Execucao_num']]
        bars2 = ax2.bar(faixa0306['Linha'], faixa0306['Execucao_num'] * 100, color=colors2)

        ax2.set_xlabel('')
        ax2.set_ylabel('')
        ax2.set_title(f'Faixa de 03h às 06h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars2, faixa0306['% Execução']):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig2)
    else:
        st.info('Nenhum dado disponível para a faixa 03-06 com o núcleo selecionado.')




### --- GRÁFICO FAIXA 06-09 ---
with col3:
    faixa0609 = df_merged[
        (df_merged['Faixa_Horaria'] == '06-09') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 06-09')

    if not faixa0609.empty:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        colors3 = ['green' if x >= 0.8 else 'red' for x in faixa0609['Execucao_num']]
        bars3 = ax3.bar(faixa0609['Linha'], faixa0609['Execucao_num'] * 100, color=colors3)

        ax3.set_xlabel('')
        ax3.set_ylabel('')
        ax3.set_title(f'Faixa de 06h às 09h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars3, faixa0609['% Execução']):
            height = bar.get_height()
            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig3)
    else:
        st.info('Nenhum dado disponível para a faixa 06-09 com o núcleo selecionado.')



### --- GRÁFICO FAIXA 09-12 ---
with col4:
    faixa0912 = df_merged[
        (df_merged['Faixa_Horaria'] == '09-12') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 09-12')

    if not faixa0912.empty:
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        colors4 = ['green' if x >= 0.8 else 'red' for x in faixa0912['Execucao_num']]
        bars4 = ax4.bar(faixa0912['Linha'], faixa0912['Execucao_num'] * 100, color=colors4)

        ax4.set_xlabel('')
        ax4.set_ylabel('')
        ax4.set_title(f'Faixa de 09h às 12h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars4, faixa0912['% Execução']):
            height = bar.get_height()
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig4)
    else:
        st.info('Nenhum dado disponível para a faixa 09-12 com o núcleo selecionado.')



        # Criar colunas lado a lado
col1, col2, col3, col4 = st.columns(4)

        
### --- GRÁFICO FAIXA 12-15 ---
with col1:
    faixa1215 = df_merged[
        (df_merged['Faixa_Horaria'] == '12-15') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 12-15')

    if not faixa1215.empty:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        colors1 = ['green' if x >= 0.8 else 'red' for x in faixa1215['Execucao_num']]
        bars1 = ax1.bar(faixa1215['Linha'], faixa1215['Execucao_num'] * 100, color=colors1)

        ax1.set_xlabel('')
        ax1.set_ylabel('')
        ax1.set_title(f'Faixa de 12h às 15h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars1, faixa1215['% Execução']):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig1)
    else:
        st.info('Nenhum dado disponível para a faixa 00-03 com o núcleo selecionado.')



### --- GRÁFICO FAIXA 15-18 ---
with col2:
    faixa1518 = df_merged[
        (df_merged['Faixa_Horaria'] == '15-18') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 15-18')

    if not faixa1518.empty:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        colors2 = ['green' if x >= 0.8 else 'red' for x in faixa1518['Execucao_num']]
        bars2 = ax2.bar(faixa1518['Linha'], faixa1518['Execucao_num'] * 100, color=colors2)

        ax2.set_xlabel('')
        ax2.set_ylabel('')
        ax2.set_title(f'Faixa de 15h às 18h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars2, faixa1518['% Execução']):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig2)
    else:
        st.info('Nenhum dado disponível para a faixa 03-06 com o núcleo selecionado.')



### --- GRÁFICO FAIXA 06-09 ---
with col3:
    faixa1821 = df_merged[
        (df_merged['Faixa_Horaria'] == '18-21') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 18-21')

    if not faixa1821.empty:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        colors3 = ['green' if x >= 0.8 else 'red' for x in faixa1821['Execucao_num']]
        bars3 = ax3.bar(faixa1821['Linha'], faixa1821['Execucao_num'] * 100, color=colors3)

        ax3.set_xlabel('')
        ax3.set_ylabel('')
        ax3.set_title(f'Faixa de 18h às 21h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars3, faixa1821['% Execução']):
            height = bar.get_height()
            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig3)
    else:
        st.info('Nenhum dado disponível para a faixa 06-09 com o núcleo selecionado.')        



### --- GRÁFICO FAIXA 21-00 ---
with col4:
    faixa2100 = df_merged[
        (df_merged['Faixa_Horaria'] == '21-00') &
        (df_merged['Núcleo'] == nucleo_selecionado)
    ].sort_values(by='Execucao_num', ascending=False)

    #st.subheader('Faixa 21-00')

    if not faixa2100.empty:
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        colors4 = ['green' if x >= 0.8 else 'red' for x in faixa0912['Execucao_num']]
        bars4 = ax4.bar(faixa2100['Linha'], faixa2100['Execucao_num'] * 100, color=colors4)

        ax4.set_xlabel('')
        ax4.set_ylabel('')
        ax4.set_title(f'Faixa de 21h às 00h')
        plt.xticks(rotation=45)

        for bar, label in zip(bars4, faixa2100['% Execução']):
            height = bar.get_height()
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                label,
                ha='center',
                va='bottom',
                fontsize=8,
                fontweight='bold'
            )

        st.pyplot(fig4)
    else:
        st.info('Nenhum dado disponível para a faixa 21-00 com o núcleo selecionado.')        