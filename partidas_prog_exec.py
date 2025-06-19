import pandas as pd
import datetime
import streamlit as st
import os
import pytz
import plotly.express as px

def app():

    # ✅ Leitura dos dados
    gps_nucleo = pd.read_csv("dados/dados_gps.csv", sep=";")
    faixas = pd.read_csv("dados/faixas_horarias.csv", sep=";")
    linhas = pd.read_csv("dados/linhas_e_nucleos.csv", sep=";")
    programacao = pd.read_csv("dados/programacao_partidas.csv", sep=";")

    # ✅ Limpeza inicial
    del gps_nucleo['Linha Informada a SMTR']
    del gps_nucleo['Linha Realizada pela SMTR']
    del gps_nucleo['Veículo Consolidado pela SMTR']
    del gps_nucleo['Início da Viagem pela SMTR']
    del gps_nucleo['Término da Viagem pela SMTR']
    del gps_nucleo['Viagem Reconhecida']

    gps_nucleo = pd.merge(gps_nucleo, linhas, on="Linha", how="left")
    del gps_nucleo['Tipo Linha']
    del gps_nucleo['Nome_Linha']

    gps_nucleo['Início da Viagem'] = pd.to_datetime(gps_nucleo['Início da Viagem'], dayfirst=True)
    gps_nucleo['Término da Viagem'] = pd.to_datetime(gps_nucleo['Término da Viagem'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    gps_nucleo['hora_viagem'] = gps_nucleo['Início da Viagem'].dt.time

    gps_nucleo['_key'] = 1
    faixas['_key'] = 1

    merged = pd.merge(gps_nucleo, faixas, on='_key')
    merged['hora_inicio'] = pd.to_datetime(merged['hora_inicio'], format='%H:%M:%S').dt.time
    merged['hora_fim'] = pd.to_datetime(merged['hora_fim'], format='%H:%M:%S').dt.time

    merged[['Data','Linha','Veículo','Início da Viagem','Término da Viagem', 'Núcleo', 'Faixa_Horaria']]













    # ✅ Configuração inicial Streamlit

    st.set_page_config(page_title='Partidas GPS Real', layout='wide')

    # ✅ Filtro por Núcleo
    nucleos_disponiveis = merged['Núcleo'].unique().tolist()
    nucleo_selecionado = st.sidebar.radio(
        'Selecione o Núcleo:',
        options=nucleos_disponiveis
    )


    st.title(f'% de Partidas Executadas {nucleo_selecionado}')

    # ✅ Hora de última atualização
    file_path = r'dados/dados_gps.csv'
    if os.path.exists(file_path):
        timestamp_modificacao = os.path.getmtime(file_path)
        utc_time = datetime.datetime.utcfromtimestamp(timestamp_modificacao)
        fuso_rio = pytz.timezone('America/Sao_Paulo')
        hora_local = utc_time.replace(tzinfo=pytz.utc).astimezone(fuso_rio)
        hora_minuto = hora_local.strftime('%H:%M')

        st.markdown(f"""
        <div style='text-align:left; padding:8px 0;'>
            <span style='font-size:16px; font-weight:bold;'>Última atualização</span><br>
            <span style='font-size:20px; font-weight:bold;'>{hora_minuto}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error('Arquivo dados.csv não encontrado no caminho especificado!')



    # ✅ Função para gerar gráfico com Plotly
    def plot_faixa_plotly(df, faixa_nome):
        fig = px.bar(
            df,
            x='Linha',
            y='Execucao_num',
            color='cor',
            color_discrete_map={'green': 'green', 'red': 'red'},
            text=df['Execucao_num'].apply(lambda x: f'{x*100:.1f}%'),
            hover_data={
                'Linha': True,
                'Executado': True,
                'Programado': True,
                '% Execução': True,
                'cor': False,
                #'text': False,
                'Execucao_num': False
            },
            title=f'Faixa {faixa_nome}',
        )

        fig.update_layout(
            yaxis_title='',
            xaxis_title='',
            xaxis_type='category',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            bargap=0.1
        )

        fig.update_traces(textposition='outside')

        return fig

    # ✅ Lista das faixas
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


