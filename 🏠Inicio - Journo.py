from openai import OpenAI
import streamlit as st
from journo.modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import re
import extra_streamlit_components as stx
from journo.aggregate_auth import add_auth
import pandas as pd

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


if 'email' in st.session_state and st.session_state.user_subscribed == True:
  
    if 'inicio' not in st.session_state:
        st.success(f"🥳 ¡Bienvenido {st.session_state.email}!")
        st.write("## ¿Qué es Journo?")
        st.markdown(
            """
            <h4>Journo es una <strong>Inteligencia Artificial</strong> que te ayudará en tu día a día a la hora de redactar noticias. Con Journo podrás:</h4>
            <ul>
                <li><strong>Automatizar</strong> la transcripción de audios</li>
                <li><strong>Guíar</strong> a la Inteligencia Artificial a redactar la noticia a tu gusto</li>
                <li><strong>Modificar</strong> las noticias y darle el toque final</li>
                <li><strong>Recibirás</strong> toda la información en un correo electrónico</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        
        st.write("")
         
        st.link_button("Ver video tutorial", "https://streamlit.io/gallery", type = "primary")
        
        st.write("---")
            
        st.write("## ¿Cómo funciona Journo?")
        
        with open('files/demo.txt', "r",encoding="utf-8") as archivo:
            content = archivo.read()
      
        exec(content)
      
        phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Selección/descarte", "Noticia"])
      
        if phase == 0:
            st.write("### 1) Cargar o subir audio")
            st.info("En esta primera etapa deberemos aportar al sistema el audio a transcribir. Podemos subir un audio ya grabado o grabarlo directamente desde la app")
            with st.expander("*Ver ejemplo*"):
                try:
                    st.audio('files/audio.mp3', format="audio/mpeg")
                except:
                    st.error("Error al cargar el audio. Recuerda que si cargas una noticia de la base de datos, no está disponible el audio para escuchar")
        
        if phase == 1:
            st.write("### 2) Describir el contexto de las declaraciones")
            st.info("Ahora deberemos de aportar información a la Inteligencia Artificial para que sepa en qué contexto se han producido las declaraciones que has aportado")
            with st.expander("*Ver ejemplo*"):
                st.write("#### :blue[¿Cuál es el cargo de la persona que habla?]")
                st.write(st.session_state.X)
                st.write("#### :blue[¿Cuál es el nombre de la persona que habla?]")
                st.write(st.session_state.Y)
                st.write("#### :blue[¿Cuál es el tema más relevante del que ha hablado?]")
                st.write(st.session_state.Z)
                st.write("#### :blue[¿Dónde ha dicho las declaraciones?]")
                st.write(st.session_state.A)
                st.write("#### :blue[Cuándo ha dicho las declaraciones?]")
                st.write(st.session_state.B)
                
        if phase == 2:
            st.write("### 3) Transcripción de las declaraciones")
            st.info("Journo entonces nos generará la transcripción completa del audio.")
            with st.expander("*Ver ejemplo*"):
                st.write(st.session_state.transcription2, unsafe_allow_html=True)
        
            
        if phase == 3:
          st.write("### 4) Selección/descarte de temas mencionados")
          st.info("En este paso tendrás que descartar los párrafos que no te interesen (aparecerán desmarcados) y subrayar los momentos de mayor relevancia en las declaraciones.")
          with st.expander("*Ver ejemplo*"):    
              for i in range(len(st.session_state.lista)):
                  on = st.toggle('', key=i, value = st.session_state[f'on_{i}'])
                  frases = []
                  for item in st.session_state[f'anotaciones_{i}']:
                      for x in item:
                        frases.append(x['label'])
                  st.write(generar_html_con_destacados(st.session_state.lista[i], frases), unsafe_allow_html=True)
              
        if phase == 4:
            st.info('Finalmente, Journo nos dará una primera versión de nuestra noticia a partir del audio y la información proporcionada. Posteriormente podremos editarla manualmente o con ayuda de Journo.')
            with st.expander("*Ver ejemplo*"):
                st.write(st.session_state.noticia_generada)





        
    
