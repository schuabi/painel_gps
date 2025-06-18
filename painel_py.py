import pandas as pd
import datetime
#import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import os


# In[45]:


gps_nucleo = pd.read_csv("C:/dashboard_onibus/dados_gps.csv", sep=";")
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











# ✅ Configuração inicial Streamlit
st.set_page_config(page_title='Partidas GPS', layout='wide')

# ✅ Dados de última modificação
file_path = r'C:\dashboard_onibus\dados\dados_gps.csv'
if os.path.exists(file_path):
    timestamp_modificacao = os.path.getmtime(file_path)
    ultima_modificacao = datetime.datetime.fromtimestamp(timestamp_modificacao)
    hora_minuto = ultima_modificacao.strftime('%H:%M')
    st.info(f'Dados atualizados às: {hora_minuto}')
else:
    st.error('Arquivo dados.csv não encontrado no caminho especificado!')

# ✅ Filtro por Núcleo (radio button - único)
nucleos_disponiveis = df_merged['Núcleo'].unique().tolist()
nucleo_selecionado = st.sidebar.radio(
    'Selecione o Núcleo:',
    options=nucleos_disponiveis
)

st.title(f'% de Partidas Executadas por Faixa Horária - Núcleo: {nucleo_selecionado}')

# ✅ Preparação dos dados
df_merged['Execucao_num'] = df_merged['% Execução'] / 100
df_merged['% Execução'] = df_merged['Execucao_num'].apply(lambda x: f"{x:.1%}")

# ✅ Função para criar gráfico por faixa
def plot_faixa(df, faixa_nome):
    fig, ax = plt.subplots(figsize=(6, 4))

    # Definir cores por % Execução
    colors = ['green' if x >= 0.8 else 'red' for x in df['Execucao_num']]
    bars = ax.bar(df['Linha'], df['Execucao_num'] * 100, color=colors, edgecolor='black', linewidth=0.5)

    # Títulos e fontes
    ax.set_title(f'Faixa {faixa_nome}', fontsize=12, fontweight='bold')
    ax.set_xlabel('Linha', fontsize=10)
    ax.set_ylabel('% Execução', fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    ax.tick_params(axis='y', labelsize=8)

    # Grid de fundo
    ax.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    ax.set_axisbelow(True)

    # Remover bordas (spines)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    # Adicionar os valores % no topo
    for bar, label in zip(bars, df['% Execução']):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            label,
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold'
        )

    return fig

# ✅ Lista das faixas horárias com títulos
faixas_horarias = [
    ('00-03', '00h às 03h'),
    ('03-06', '03h às 06h'),
    ('06-09', '06h às 09h'),
    ('09-12', '09h às 12h'),
    ('12-15', '12h às 15h'),
    ('15-18', '15h às 18h'),
    ('18-21', '18h às 21h'),
    ('21-00', '21h às 00h'),
]

# ✅ Exibir gráficos em grupos de 4 colunas
for i in range(0, len(faixas_horarias), 4):
    cols = st.columns(4)
    for idx, (faixa_codigo, faixa_label) in enumerate(faixas_horarias[i:i+4]):
        with cols[idx]:
            faixa_df = df_merged[
                (df_merged['Faixa_Horaria'] == faixa_codigo) &
                (df_merged['Núcleo'] == nucleo_selecionado)
            ].sort_values(by='Execucao_num', ascending=False)

            if not faixa_df.empty:
                fig = plot_faixa(faixa_df, faixa_label)
                st.pyplot(fig)
            else:
                st.info(f'Nenhum dado disponível para a faixa {faixa_label}.')
