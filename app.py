from openai import OpenAI
import streamlit as st
from journo.modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import re
import extra_streamlit_components as stx
from journo.aggregate_auth import add_auth
import pandas as pd
from streamlit_option_menu import option_menu

openai_client = OpenAI(api_key=st.secrets.openai_api)

st.set_page_config(page_title="Inicio - Journo", page_icon="🏠", layout="wide")

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

st.write("---")


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres un asistente virtual de Journo, una webapp de asistencia con IA para periodistas y ahora podrás comunicarte con los usuarios de Journo. Trata de ayudar a los usuarios con sus peticiones e instrucciones para dar forma y estilo a una noticia periodística. Razona siempre paso por paso cualquier petición."}]

if 'guardado' not in st.session_state:
    st.session_state.guardado = False

st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)

x,y,z = st.columns(3)
with y:
  add_auth(required=True, login_sidebar = False)


with st.sidebar:
    st.session_state.selected = option_menu("Menu", ["Inicio", "Base de datos", "Journo"], 
        icons=['house', 'gear'], menu_icon="cast", default_index=1)
    selected


if 'email' in st.session_state and st.session_state.user_subscribed == True: 
    
    if st.session_state.selected == 1:
      show_incio()






        
    
