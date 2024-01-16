from openai import OpenAI
import streamlit as st
import tempfile
import os
from modules import *
from io import BytesIO
import re
import html2text
from simple_diarizer.diarizer import Diarizer

st.set_page_config(page_title="Journo.AI", page_icon="🗞️", layout="wide")

st.markdown(
  """
  <div style='text-align: center;'>
      <h1>🗞️ Journo 🗞️</h1>
      <h4>Tu asistente periodístico de inteligencia artificial</h4>
  </div>
  """,
    unsafe_allow_html=True
)
st.write("---")

if 'diarization' not in st.session_state:
  count = 0
  while count == 0:
    try:
      st.session_state.diarization = Diarizer(embed_model='xvec', cluster_method='sc')
      break
    except:
      pass


# Inicio de sesión
if 'autenticado' not in st.session_state:
    nombre_usuario = st.text_input("Nombre de usuario")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión", type = "primary"):
        if verificar_credenciales(nombre_usuario, contraseña):
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")


if 'autenticado' in st.session_state:
    if 'path' not in st.session_state:
        st.success("¡Autenticado con éxito!")
        st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia. Asegúrate de que sea un archivo en formato MP3.")
        archivo = st.file_uploader("Cargar archivo de audio")
        if st.button("Siguiente", type = "primary"):
          mp3_data = convertir_a_mp3(archivo)
          # wav_data = convertir_mp3_a_wav_16khz_mono(mp3_data)
          
          with open('/mount/src/journo/audio.mp3', "wb") as f:
              f.write(mp3_data)
            
          st.session_state.path = '/mount/src/journo/audio.mp3'
          st.rerun()
        
    if 'path' in st.session_state and 'X' not in st.session_state:
        st.info("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
        X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]")
        Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]")
        Z = st.text_input(":blue[¿Cuál es el tema más relevante del que ha hablado?]")
        A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]")
        B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]")

        st.session_state.list_paths = dividir_audio(st.session_state.path, st.session_state.diarization)
      
        if st.button("Enviar", type = "primary"):
            st.session_state.X = X
            st.session_state.Y = Y
            st.session_state.Z = Z
            st.session_state.A = A
            st.session_state.B = B

            with st.spinner("Cargando tu noticia... ⌛"):
                st.warning("Este proceso puede tardar unos minutos. ¡Recuerda revisarla antes de publicar!")
                st.session_state.transcription = generar_transcripcion_conjunta(st.session_state.list_paths)
                st.session_state.noticia_generada = generar_noticia(st.session_state.transcription, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                st.rerun()
              

    if 'noticia_generada' in st.session_state:
        st.write("## ✔️¡Listo! Aquí tienes tu noticia:")

        estilo_bordes_redondeados = """
            <style>
                .bordes-redondeados {
                    border-radius: 10px;
                    padding: 10px;
                    border: 2px solid #ccc; /* Puedes ajustar el color del borde según tus preferencias */
                }
            </style>
        """

        # Aplicar el estilo CSS
        st.markdown(estilo_bordes_redondeados, unsafe_allow_html=True)

        # Mostrar el texto con bordes redondeados
        st.markdown(f'<div class="bordes-redondeados">{st.session_state.noticia_generada}</div>', unsafe_allow_html=True)
