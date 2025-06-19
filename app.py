import streamlit as st
from appgps import app as appgps_app
from partidas_prog_exec import app as partidas_app
from programacao import app as programacao_app

st.set_page_config(page_title='Dashboard GPS', layout='wide')

# ✅ Sidebar com Navegação
st.sidebar.title('Navegação')
pagina = st.sidebar.radio(
    'Escolha a página:',
    ['Gráficos', 'Partidas', 'Programação']
)

# ✅ Controle de navegação
if pagina == 'Gráficos':
    appgps_app()
elif pagina == 'Partidas':
    partidas_app()
elif pagina == 'Programação':
    programacao_app()
