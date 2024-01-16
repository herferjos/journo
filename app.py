from openai import OpenAI
import streamlit as st
import tempfile
import os
from modules import *
from io import BytesIO
import re
import html2text

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
    if 'temp_path' not in st.session_state:
        st.success("¡Autenticado con éxito!")
        st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia. Asegúrate de que sea un archivo en formato MP3.")
        archivo = st.file_uploader("Cargar archivo de audio", type=['mp3'])
        if st.button("Siguiente", type = "primary"):
          temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
          with open(temp_path, "wb") as f:
              f.write(archivo.read())
          st.session_state.temp_path = temp_path
          st.rerun()
        
    if 'temp_path' in st.session_state and 'X' not in st.session_state:
        st.info("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
        X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]")
        Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]")
        Z = st.text_input(":blue[¿Cuál es el tema más relevante del que ha hablado?]")
        A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]")
        B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]")
        if st.button("Enviar", type = "primary"):
            st.session_state.X = X
            st.session_state.Y = Y
            st.session_state.Z = Z
            st.session_state.A = A
            st.session_state.B = B

            with st.spinner("Cargando tu noticia... ⌛"):
                st.warning("Este proceso puede tardar unos minutos. ¡Recuerda revisarla antes de publicar!")
                st.session_state.transcription = transcribe_audio(st.session_state.temp_path)
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
