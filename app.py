import streamlit as st
from journo.pages.inicio import show_inicio
from journo.pages.journo import show_journo
from journo.pages.chatbot import show_bot
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import img_to_html, load_database
from streamlit_option_menu import option_menu
import time
import pandas as pd
from streamlit_gsheets import GSheetsConnection


st.set_page_config(page_title="Journo", page_icon="🗞️") #layout="wide"

st.markdown(
    "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo.png', 200, 200) + "</p>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='text-align: center;'>
        <h4>Tu asistente periodístico de inteligencia artificial</h4>
    </div>
    """,
    unsafe_allow_html=True
)


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres un asistente virtual de Journo, una webapp de asistencia con IA para periodistas y ahora podrás comunicarte con los usuarios de Journo. Trata de ayudar a los usuarios con sus peticiones e instrucciones para dar forma y estilo a una noticia periodística. Razona siempre paso por paso cualquier petición."}]

if 'guardado' not in st.session_state:
    st.session_state.guardado = False
    
if 'noticia_cargada' not in st.session_state:
    st.session_state.noticia_cargada = False

if 'X' not in st.session_state:
    st.session_state.X = None
if 'Y' not in st.session_state:
    st.session_state.Y = None
if 'Z' not in st.session_state:
    st.session_state.Z = None
if 'A' not in st.session_state:
    st.session_state.A = None
if 'B' not in st.session_state:
    st.session_state.B = None


st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)


add_auth(required=True, login_sidebar = False)

# load_database(force=True)

st.write(st.session_state.database)

if st.button('Crear nuevo df'):
    nuevo_df = pd.DataFrame({'Transcripción': ['_']*5, 'Transcripción editada': ['_']*5, 'Cargo': ['_']*5, 'Nombre': ['_']*5, 'Donde': ['_']*5, 'Cuando': ['_']*5, 'Extra': ['_']*5, 'Anotaciones': ['_']*5, 'Noticia': ['_']*5, 'Noticia editada': ['_']*5,'Sesion': ['_']*5}, index=range(5))
    st.session_state.sheet.create(worksheet='test', data=nuevo_df)
    st.session_state.sheet = st.connection("gsheets", type=GSheetsConnection)
    st.session_state.database = st.session_state.sheet.read(worksheet='test')
    st.rerun()

if st.button('Actualizar'):
    st.session_state.database.append({'Transcripción': 'xd', 'Transcripción editada': 'xd', 'Cargo': 'xd', 'Nombre': 'xd', 'Donde': 'xd', 'Cuando': 'xd', 'Extra': 'xd', 'Anotaciones':'xd', 'Noticia': 'xd', 'Noticia editada': 'xd', 'Sesion': 'xd'}, ignore_index=True)
    st.session_state.sheet.update(worksheet='test', data = st.session_state.database)

with st.sidebar:
    st.session_state.selected = option_menu("", ["Crea tu noticia", "Chatbot", "¿Qué es Journo?"], 
        icons=['pencil-fill', 'robot', 'house'], menu_icon="", default_index=0)

if 'email' in st.session_state and st.session_state.user_subscribed == True: 
    
    if st.session_state.selected == 'Crea tu noticia':
        show_journo()

    if st.session_state.selected == 'Chatbot':
        show_bot()
    
    if st.session_state.selected == '¿Qué es Journo?':
        show_inicio()


#except:
#    st.error('Ha habido un error en Journo. La página será recargada en 5 segundos, si el error persiste contácta con hola@journo-ai.com')
#    time.sleep(5)
 #   st.rerun()
        
    
