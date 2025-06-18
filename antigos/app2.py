import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from unidecode import unidecode

# ===== 1. Carregar os dados =====
df = pd.read_csv('comparativo_programado_executado.csv', sep=';')
linhas_nucleos = pd.read_csv('linhas_e_nucleos.csv', sep=';')

# ===== 2. Padronizar nomes das colunas =====
df.columns = [unidecode(col.strip().lower()) for col in df.columns]
linhas_nucleos.columns = [unidecode(col.strip().lower()) for col in linhas_nucleos.columns]

# ===== 3. Remover núcleos em branco =====
linhas_nucleos = linhas_nucleos.dropna(subset=['nucleo'])

# ===== 4. Filtrar linhas válidas =====
linhas_validas = linhas_nucleos['linha'].unique().tolist()
df = df[df['linha'].isin(linhas_validas)]

# ===== 5. Criar lista de núcleos =====
nucleos = sorted(linhas_nucleos['nucleo'].unique().tolist())

# ===== 6. Configuração da página =====
st.set_page_config(page_title="% de Partidas Executadas", layout="wide")

# ===== 7. Cabeçalho =====
st.markdown(f"### {datetime.now().strftime('%d/%m/%Y %H:%M')}  \n**Última Atualização**")
st.markdown("<h1 style='text-align: center; color: black;'>% de Partidas Executadas por Faixa Horária</h1>", unsafe_allow_html=True)

# ===== 8. Filtro de Núcleo =====
nucleo_selecionado = st.radio("Selecione o Núcleo:", nucleos, horizontal=True)

# ===== 9. Filtrar linhas do núcleo selecionado =====
linhas_nucleo = linhas_nucleos[linhas_nucleos['nucleo'] == nucleo_selecionado]['linha'].unique().tolist()
df = df[df['linha'].isin(linhas_nucleo)]

# ===== 10. Filtrar faixas horárias =====
faixas = df['faixa_horaria'].dropna().unique()
faixas = sorted(faixas, key=lambda x: int(x.split('-')[0]) if '-' in x else 99)

# ===== 11. Criar grid de gráficos =====
cols = st.columns(4)
contador = 0

for faixa in faixas:
    df_faixa = df[df['faixa_horaria'] == faixa]

    if df_faixa.empty:
        contador += 1
        continue

    faixa_label = f"Partidas {faixa.replace('-', 'h às ')}h"

    with cols[contador % 4]:
        st.markdown(f"#### {faixa_label}")

        fig = px.bar(
            df_faixa,
            x='linha',
            y='% execucao',
            text=df_faixa['% execucao'].apply(lambda x: f"{x:.1f}%"),
            color_discrete_sequence=['#FF7F7F'],
        )

        fig.update_traces(textposition='inside', textfont_size=12)
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
            yaxis=dict(range=[0, 100]),
        )

        st.plotly_chart(fig, use_container_width=True, key=f"{faixa}_{contador}")

    contador += 1
    if contador % 4 == 0:
        cols = st.columns(4)
