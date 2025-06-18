import pandas as pd
import streamlit as st
import plotly.express as px

# Carrega os dados
arquivo = 'dados.csv'  # Troque pelo caminho do seu arquivo CSV
df = pd.read_csv(arquivo)

# Converta a coluna de horário, se necessário
# df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time

# Lista de faixas de horário
faixas = [
    '00h às 03h', '03h às 06h', '06h às 09h',
    '09h às 12h', '12h às 15h', '15h às 18h',
    '18h às 21h', '21h às 00h'
]

# Título geral
st.title('Indicador de Partidas por Faixa Horária')

# Loop pelas faixas
for i, faixa in enumerate(faixas):
    # Filtra os dados da faixa atual
    df_faixa = df[df['faixa_horaria'] == faixa]

    # Só cria gráfico se houver dados para a faixa
    if not df_faixa.empty:
        # Define a cor por linha: verde se % >= 100, vermelho se < 100
        cores = df_faixa['%'].apply(lambda x: 'green' if x >= 100 else 'red')

        # Cria o gráfico
        fig = px.bar(
            df_faixa,
            x='linha',
            y='%',
            text=df_faixa['%'].apply(lambda x: f"{x:.1f}%"),
            color_discrete_sequence=['green'] * len(df_faixa)  # Default verde, mas vamos sobrescrever abaixo
        )

        # Ajusta a cor individual de cada barra
        for idx, color in enumerate(cores):
            fig.data[0].marker.color = list(cores)

        # Layout
        fig.update_traces(textposition='inside', marker_line_color='black', marker_line_width=0.5)
        fig.update_layout(
            title=f"Partidas {faixa}",
            xaxis_title="Linha",
            yaxis_title="%",
            yaxis_range=[0, max(120, df_faixa['%'].max() + 20)],
            height=300,
            margin=dict(l=20, r=20, t=50, b=40)
        )

        # Plot no Streamlit - adicionando key única por faixa
        st.plotly_chart(fig, use_container_width=True, key=f'plot_{i}')
    else:
        st.warning(f"Sem dados para a faixa: {faixa}")
