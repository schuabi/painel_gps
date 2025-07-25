import streamlit as st
from appgps import app as appgps_app
from partidas import app as partidas_app
from programacao import app as programacao_app
import threading
import time



st.markdown("""
    <style>
    /* Ocultar os botões de ações do header (ex: Share, Config) */
    div[data-testid="stToolbarActions"] {
        display: none !important;
    }

    /* Ocultar o Menu (três pontinhos) */
    #MainMenu {
        visibility: hidden;
    }

    /* Ocultar o rodapé */
    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)




st.set_page_config(page_title='Dashboard GPS', layout='wide', initial_sidebar_state='expanded')

# ✅ Configurar Auto-Refresh a cada 5 minutos
def auto_refresh(interval=300):
    def refresh():
        time.sleep(interval)
        st.experimental_rerun()
    threading.Thread(target=refresh, daemon=True).start()

auto_refresh()

# ✅ Inicializar o estado se ainda não existir
if "pagina" not in st.session_state:
    st.session_state.pagina = "Gráficos"

# ✅ Sidebar com botões de navegação
st.sidebar.title('Navegação')

col1, col2, col3 = st.sidebar.columns(3)  # 1 coluna, mas para manter consistência visual

# ✅ Captura de clique de botões
clicou_graficos = st.sidebar.button('Gráficos 📊')
clicou_partidas = st.sidebar.button('Partidas 🚌')
clicou_programacao = st.sidebar.button('Programação 📅')

# ✅ Atualiza a página ativa se algum botão for clicado
if clicou_graficos:
    st.session_state.pagina = "Gráficos"
elif clicou_partidas:
    st.session_state.pagina = "Partidas"
elif clicou_programacao:
    st.session_state.pagina = "Programação"

# ✅ Exibir a página ativa
if st.session_state.pagina == 'Gráficos':
    appgps_app()
elif st.session_state.pagina == 'Partidas':
    partidas_app()
elif st.session_state.pagina == 'Programação':
    programacao_app()
