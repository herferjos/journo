import streamlit as st
from journo.pages.inicio import show_inicio
from journo.pages.journo import show_journo
from journo.pages.chatbot import show_bot
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import load_database, reset_variables, img_to_html
from streamlit_option_menu import option_menu
import time


st.set_page_config(page_title="Journo", page_icon="🗞️") #layout="wide"

from boton_stripe import boton_stripe
value = boton_stripe()



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
if 'generacion' not in st.session_state:
    st.session_state.generacion = False
if 'extra' not in st.session_state:
    st.session_state.extra = False

st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)


add_auth(required=True, login_sidebar = False)

load_database()

with st.sidebar:
    st.markdown(
        "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 180, 180) + "</p>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div style='text-align: center;'>
            <h4>Una nueva forma de hacer periodismo</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.session_state.selected = option_menu("", ["Crea tu noticia", "Chatbot", "¿Qué es Journo?"], 
        icons=['pencil-fill', 'robot', 'house'], menu_icon="", default_index=0)
    
    st.write('---')
    
    c,d = st.columns(2)

    with c:
        if st.button("Empezar nueva noticia", type = "primary", key = "restart"):
            reset_variables()
    with d:
        if st.button("Guardar progreso", type = "primary"):
            guardar_info()
            st.rerun()
        

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
        
    
