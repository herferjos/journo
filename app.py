from openai import OpenAI
import streamlit as st
from modules import *
from streamlit_annotation_tools import text_highlighter
from audio_recorder_streamlit import audio_recorder

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
  with st.expander("Informacion recopilada"):
    if 'mp3_audio_path' in st.session_state and not 'transcription2' in st.session_state:
        st.info("Aquí tienes el audio que hemos procesado")
        st.audio(st.session_state.wav_audio_path)
        st.write("---")
      
    if 'mp3_audio_path' in st.session_state and 'transcription2' in st.session_state and not 'noticia_generada' in st.session_state:
        audio, transcripcion = st.tabs(["Audio", "Transcripción"])
        with audio:
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.wav_audio_path)
        with transcripcion:
          st.info("Aquí tienes la transcripción del audio")
          st.write(st.session_state.transcription2)
        st.write("---")
      
    if 'noticia_generada' in st.session_state:
        audio, transcripcion, anotacions = st.tabs(["Audio", "Transcripción", "Anotaciones"])
        with audio:
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.wav_audio_path)
        with transcripcion:
          st.info("Aquí tienes la transcripción del audio")
          st.write(st.session_state.transcription2)

        with anotaciones:
          st.info("Aquí tienes tus anotaciones")
          st.write(st.session_state.anotaciones)
       
  st.write("---")


if 'autenticado' in st.session_state:
    if 'mp3_audio_path' not in st.session_state:
      st.success("¡Autenticado con éxito!")
      col1, col2 = st.columns(2)
      with col1:
        st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia.")
        archivo = st.file_uploader("Cargar archivo de audio")

        if st.button("Siguiente", type = "primary", key = "upload"):
          with st.spinner("Cargando audio... ⌛"):
            if archivo is not None:
                # Convierte el audio a formato MP3
                mp3_bytes = audio_a_bytes(archivo)
              
                st.session_state.wav_audio_path = bytes_a_audio(mp3_bytes, formato_destino="wav")               
                st.session_state.mp3_audio_path = bytes_a_audio(mp3_bytes, formato_destino="mp3")
              
                st.rerun()


      with col2:
        st.info("Puedes empezar a grabar un audio directamente desde aquí")
        
        audio_bytes = audio_recorder()
        
        if st.button("Siguiente", type = "primary", key = "record"):
          with st.spinner("Cargando audio... ⌛"):
              st.session_state.wav_audio_path = bytes_a_audio(audio_bytes, formato_destino="wav")               
              st.session_state.mp3_audio_path = bytes_a_audio(audio_bytes, formato_destino="mp3")
            
              st.rerun()

  
    if 'mp3_audio_path' in st.session_state and 'X' not in st.session_state:
        st.info("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
        X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", value = 'Entrenador Real Madrid')
        Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", value = 'Ancelotti')
        Z = st.text_input(":blue[¿Cuál es el tema más relevante del que ha hablado?]", value = 'Partido vs Atletico de Madrid')
        A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", value = 'Rueda de Prensa')
        B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", value = 'Martes 12')
      
 
        if st.button("Enviar información", type = "primary", key = "Enviar"):
            with st.spinner("Enviando información... ⌛"):
              st.warning("Este proceso puede tardar unos minutos.")
              st.session_state.X = X
              st.session_state.Y = Y
              st.session_state.Z = Z
              st.session_state.A = A
              st.session_state.B = B
  
              
              st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
              st.session_state.transcription2 = dialoguer(st.session_state.transcription1, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
              st.rerun()


    if 'transcription2' in st.session_state and 'noticia_generada' not in st.session_state:
        st.info("Ahora puedes seleccionar fragmentos de la transcripción para indicar que partes son más importantes a la hora de generar la noticia.")
        st.session_state.anotaciones = text_highlighter(st.session_state.transcription2)
        if st.button("Generar noticia", type = "primary"):
          with st.spinner("Generando noticia... ⌛"):
            
            anotaciones = []
            
            for elemento in st.session_state.anotaciones:
              for item in elemento:
                anotaciones.append(item['label'])
                                   
            st.session_state.anotaciones = anotaciones
            st.session_state.noticia_generada = generar_noticia(st.session_state.transcription2, st.session_state.anotaciones, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
            
            st.rerun()
              

    if 'noticia_generada' in st.session_state:
        st.write("""## ✔️¡Listo! Aquí tienes tu noticia:""")

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

