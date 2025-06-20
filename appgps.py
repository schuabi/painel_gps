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

    resultado = merged[(merged['hora_viagem'] >= merged['hora_inicio']) & (merged['hora_viagem'] <= merged['hora_fim'])]
    resultado = resultado[['Início da Viagem', 'Faixa_Horaria']]

    gps_nucleo = gps_nucleo.merge(resultado, on='Início da Viagem', how='left')
    gps_nucleo = gps_nucleo.drop_duplicates()

    partidas_executadas = gps_nucleo.groupby(['Linha', 'Faixa_Horaria']).size().reset_index(name='Executado')
    partidas_executadas = partidas_executadas.sort_values(by=['Linha', 'Faixa_Horaria'])

    programacao.columns = programacao.columns.str.strip()
    partidas_executadas.columns = partidas_executadas.columns.str.strip()

    programacao = programacao.rename(columns={'Faixa': 'Faixa_Horaria', 'linha': 'Linha'})

    comparativo = pd.merge(
        partidas_executadas,
        programacao.rename(columns={'Viagens Programadas': 'Programado'}),
        how='left',
        on=['Linha', 'Faixa_Horaria']
    )

    comparativo['Programado'] = comparativo['Programado'].fillna(0).astype(int)
    comparativo['% Execução'] = (comparativo['Executado'] / comparativo['Programado'].replace(0, 1)) * 100
    comparativo['% Execução'] = comparativo['% Execução'].round(1)
    comparativo.loc[comparativo['Programado'] == 0, '% Execução'] = 0

    del comparativo['Tipo Linha']

    df_merged = pd.merge(
        comparativo,
        linhas[['Linha', 'Núcleo']],
        on='Linha',
        how='left'
    )

    # ✅ Preparar colunas para Plotly
    df_merged['Execucao_num'] = df_merged['% Execução'] / 100
    df_merged['cor'] = df_merged['Execucao_num'].apply(lambda x: 'green' if x >= 0.8 else 'red')

    # ✅ Filtro por Núcleo
    nucleos_disponiveis = df_merged['Núcleo'].unique().tolist()
    nucleo_selecionado = st.sidebar.radio(
        'Selecione o Núcleo:',
        options=nucleos_disponiveis
    )

    # ✅ Hora de última atualização
    file_path = r'dados/dados_gps.csv'
    if os.path.exists(file_path):
        timestamp_modificacao = os.path.getmtime(file_path)
        utc_time = datetime.datetime.utcfromtimestamp(timestamp_modificacao)
        fuso_rio = pytz.timezone('America/Sao_Paulo')
        hora_local = utc_time.replace(tzinfo=pytz.utc).astimezone(fuso_rio)
        hora_minuto = hora_local.strftime('%H:%M')

        
    else:
        st.error('Arquivo dados.csv não encontrado no caminho especificado!')

    st.markdown(f"""
    <div style='
        background-color: #f0f2f6;
        padding: 10px 20px;
        margin-bottom: 10px;
        margin-top: -25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    '>
        <h2 style='margin: 0; color: #31333F;'>% de Partidas Executadas {nucleo_selecionado}</h2>
        <div style='text-align: right;'>
            <span style='font-size: 14px; font-weight: bold;'>Última atualização</span><br>
            <span style='font-size: 16px; font-weight: bold;'>{hora_minuto}</span>
        </div>
    </div>
""", unsafe_allow_html=True)


    

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
                'Programado': True,
                'Executado': True,
                '% Execução': True,
                'cor': False,
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

    # ✅ Exibição dos gráficos
    for i in range(0, len(faixas_horarias), 4):
        cols = st.columns(4)
        for idx, (faixa_codigo, faixa_label) in enumerate(faixas_horarias[i:i+4]):
            with cols[idx]:
                faixa_df = df_merged[
                    (df_merged['Faixa_Horaria'] == faixa_codigo) &
                    (df_merged['Núcleo'] == nucleo_selecionado)
                ].sort_values(by='Execucao_num', ascending=False)

                if not faixa_df.empty:
                    fig = plot_faixa_plotly(faixa_df, faixa_label)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f'Nenhum dado disponível para a faixa {faixa_label}.')
