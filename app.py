from openai import OpenAI
import streamlit as st
from modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import re
import extra_streamlit_components as stx

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
    if 'mp3_audio_path' not in st.session_state:
      st.success("¡Autenticado con éxito!")
      
      if st.button("Cargar información predeterminada", type = "primary", key = "Charge"):
        with open('demo.txt', "r",encoding="utf-8") as archivo:
          content = archivo.read()
        exec(content)
        st.rerun()
        
      col1, col2 = st.tabs(["Grabar audio", "Subir audio"])
      with col1:
        st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia.")
        archivo = st.file_uploader("Cargar archivo de audio")
        
        if st.button("Siguiente", type = "primary", key = "upload"):
          with st.spinner("Cargando audio... ⌛"):
            if archivo is not None:
                # Convierte el audio a formato MP3
                mp3_bytes = audio_a_bytes(archivo)
                          
                st.session_state.mp3_audio_path = bytes_a_audio(mp3_bytes, formato_destino="mp3")
              
                st.rerun()


      with col2:
        st.info("Puedes empezar a grabar un audio directamente desde aquí")
        
        audio=mic_recorder(start_prompt="Empezar a grabar",stop_prompt="Parar de grabar",key='recorder')
        if audio is not None:
          if st.button("Siguiente", type = "primary", key = "record"):
            with st.spinner("Cargando audio... ⌛"):            
                st.session_state.mp3_audio_path = bytes_a_audio(audio['bytes'], formato_destino="mp3")
              
                st.rerun()

  
    if 'mp3_audio_path' in st.session_state and 'topics' not in st.session_state:
      chosen_id = stx.tab_bar(data=[
          stx.TabBarItemData(id=1, title="Audio", description = ''),
          stx.TabBarItemData(id=2, title="Contexto", description = '')
      ], default=2)
              
      if chosen_id == "1":
        st.info("Aquí tienes el audio que hemos procesado")
        st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
      
      if chosen_id == "2":
      
        st.info("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
        if 'X' in st.session_state:
          X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", value = st.session_state.X)
          Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", value = st.session_state.Y)
          Z = st.text_input(":blue[¿Cuál es el tema más relevante del que ha hablado?]", value = st.session_state.Z)
          A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", value = st.session_state.A)
          B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", value = st.session_state.B)
        
        else:
          X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'Entrenador Real Madrid')
          Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", placeholder = 'Ancelotti')
          Z = st.text_input(":blue[¿Cuál es el tema más relevante del que ha hablado?]", placeholder = 'Partido vs Atletico de Madrid')
          A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'Rueda de Prensa')
          B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", placeholder = 'Martes 12')

        izq = st.number_input(label="izq")
        der = st.number_input(label="der")
        col1, col2 = st.columns([izq,der])
        
        with col2:
          if st.button("Siguiente", type = "primary", key = "Enviar"):
              with st.spinner("Enviando información... ⌛"):
                st.warning("Este proceso puede tardar unos minutos.")
                st.session_state.X = X
                st.session_state.Y = Y
                st.session_state.Z = Z
                st.session_state.A = A
                st.session_state.B = B
    
                
                st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
                st.session_state.transcription2, st.session_state.lista_transcription = dialoguer(st.session_state.transcription1, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                st.session_state.topics, st.session_state.dialogos_topics = topicer(st.session_state.lista_transcription)
                st.rerun()
              
        with col1:
          if st.button("Atrás", type = "primary", key = "atras"):
            del st.session_state['mp3_audio_path']
            st.rerun()
              
          
    if 'topics' in st.session_state and 'new_dialogos' not in st.session_state:
      
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Audio", description = ''),
            stx.TabBarItemData(id=2, title="Contexto", description = ''),
            stx.TabBarItemData(id=3, title="Transcripción", description = ''),
            stx.TabBarItemData(id=4, title="Temas seleccionados", description = ''),
        ], default=4)
              
        if chosen_id == "1":
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")

        if chosen_id == "2":
          st.info("Aquí tienes el contexto que nos has proporcionado sobre las declaraciones")
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
          
        if chosen_id == "3":
          st.info("Aquí tienes la transcripción del audio")
          lista_transcription = st.session_state.lista_transcription
          texto = '\n\n- '.join(lista_transcription)
          texto = '- ' + texto
          
          patron = r'- (.+):'
          coincidencias = re.findall(patron, texto)
          
          for elemento in coincidencias:
              texto_formateado = f'<u><b>{elemento}</u></b>'
              texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                    
          # Mostrar el texto formateado
          st.write(texto, unsafe_allow_html=True)
      
        if chosen_id == "4":
          st.info("Ahora puedes seleccionar fragmentos de la transcripción para indicar que partes son más importantes a la hora de generar la noticia.")
  
          for i in range(len(st.session_state.topics)):
              st.session_state[f'on_{st.session_state.topics[i]}'] = st.toggle(st.session_state.topics[i], key=f"{st.session_state.topics[i]}", value = True)
  
              with st.expander('Ver diálogos'):
                  texto = '\n\n- '.join(st.session_state.dialogos_topics[st.session_state.topics[i]])
                  texto = '- ' + texto
                  
                  patron = r'- (.+):'
                  coincidencias = re.findall(patron, texto)
                  
                  for elemento in coincidencias:
                      texto_formateado = f'<u><b>{elemento}</u></b>'
                      texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                            
                  # Mostrar el texto formateado
                  st.write(texto, unsafe_allow_html=True)         
          
          if st.button("Siguiente", type = "primary"):
            with st.spinner("Procesando la información... ⌛"):
              st.session_state.new_dialogos = {}
              for i in range(len(st.session_state.topics)):
                if st.session_state[f'on_{st.session_state.topics[i]}']:
                  st.session_state.new_dialogos[st.session_state.topics[i]] = st.session_state.dialogos_topics[st.session_state.topics[i]]
  
              st.rerun()
          elif st.button("Atrás", type = "primary", key = "atras"):
            del st.session_state['topics']
            st.rerun()
      
    if 'new_dialogos' in st.session_state and 'anotaciones' not in st.session_state:
      
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Audio", description = ''),
            stx.TabBarItemData(id=2, title="Contexto", description = ''),
            stx.TabBarItemData(id=3, title="Transcripción", description = ''),
            stx.TabBarItemData(id=4, title="Temas seleccionados", description = ''),
            stx.TabBarItemData(id=5, title="Anotaciones", description = ''),
        ], default=5)
              
        if chosen_id == "1":
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")

        if chosen_id == "2":
          st.info("Aquí tienes el contexto que nos has proporcionado sobre las declaraciones")
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

        if chosen_id == "3":
          st.info("Aquí tienes la transcripción del audio")
          lista_transcription = st.session_state.lista_transcription
          texto = '\n\n- '.join(lista_transcription)
          texto = '- ' + texto
          
          patron = r'- (.+):'
          coincidencias = re.findall(patron, texto)
          
          for elemento in coincidencias:
              texto_formateado = f'<u><b>{elemento}</u></b>'
              texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                    
          # Mostrar el texto formateado
          st.write(texto, unsafe_allow_html=True)

        if chosen_id == "4":
          st.info("Estos son los asuntos más importantes de las declaraciones")
          lista_claves = list(st.session_state.new_dialogos.keys())

          for i in range(len(lista_claves)):
            st.write(f"### {lista_claves[i]}")
            with st.expander('Ver diálogo'):
              texto = '\n\n- '.join(st.session_state.new_dialogos[lista_claves[i]])
              texto = '- ' + texto
              
              patron = r'- (.+):'
              coincidencias = re.findall(patron, texto)
              
              for elemento in coincidencias:
                  texto_formateado = f'<u><b>{elemento}</u></b>'
                  texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                        
              # Mostrar el texto formateado
              st.write(texto, unsafe_allow_html=True)
        
        if chosen_id == "5":
          st.info("Subraya aquellas frases que quieras mencionar explícitamente en la noticia")
    
          lista_claves = list(st.session_state.new_dialogos.keys())
    
          for i in range(len(lista_claves)):  
            st.session_state[f'anotaciones_{lista_claves[i]}'] = text_highlighter(" ".join(st.session_state.new_dialogos[lista_claves[i]]))
    
          if st.button("Siguiente", type = "primary"):
            with st.spinner("Procesando información... ⌛"):
              st.session_state.anotaciones = {}
              
              lista_claves = list(st.session_state.new_dialogos.keys())
    
              for i in range(len(lista_claves)):
                st.session_state.anotaciones[lista_claves[i]] = []
                for elemento in st.session_state[f'anotaciones_{lista_claves[i]}']:
                  for item in elemento:
                    st.session_state.anotaciones[lista_claves[i]].append(item['label'])
                    
              st.rerun()
              
          elif st.button("Atrás", type = "primary", key = "atras"):
            del st.session_state['new_dialogos']
            st.rerun()

    if 'anotaciones' in st.session_state and not 'noticia_generada' in st.session_state:
        st.write("# Resumen de la información recopilada")
      
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Audio", description = ''),
            stx.TabBarItemData(id=2, title="Contexto", description = ''),
            stx.TabBarItemData(id=3, title="Transcripción", description = ''),
            stx.TabBarItemData(id=4, title="Temas seleccionados", description = ''),
            stx.TabBarItemData(id=5, title="Anotaciones", description = ''),
        ], default=5)
              
        if chosen_id == "1":
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")

        if chosen_id == "2":
          st.info("Aquí tienes el contexto que nos has proporcionado sobre las declaraciones")
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

        if chosen_id == "3":
          st.info("Aquí tienes la transcripción del audio")
          lista_transcription = st.session_state.lista_transcription
          texto = '\n\n- '.join(lista_transcription)
          texto = '- ' + texto
          
          patron = r'- (.+):'
          coincidencias = re.findall(patron, texto)
          
          for elemento in coincidencias:
              texto_formateado = f'<u><b>{elemento}</u></b>'
              texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                    
          # Mostrar el texto formateado
          st.write(texto, unsafe_allow_html=True)

        if chosen_id == "4":
          st.info("Estos son los asuntos más importantes de las declaraciones")
          lista_claves = list(st.session_state.new_dialogos.keys())

          for i in range(len(lista_claves)):
            st.write(f"### {lista_claves[i]}")
            with st.expander('Ver diálogo'):
              texto = '\n\n- '.join(st.session_state.new_dialogos[lista_claves[i]])
              texto = '- ' + texto
              
              patron = r'- (.+):'
              coincidencias = re.findall(patron, texto)
              
              for elemento in coincidencias:
                  texto_formateado = f'<u><b>{elemento}</u></b>'
                  texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                        
              # Mostrar el texto formateado
              st.write(texto, unsafe_allow_html=True)
        
        if chosen_id == "5":
          st.info("Aquí tienes las declaraciones que marcastes")
          lista_anotaciones = list(st.session_state.anotaciones.keys())
 
          for i in range(len(lista_anotaciones)):
            if len(st.session_state.anotaciones[lista_anotaciones[i]]) > 0:
              st.write(f"### {lista_anotaciones[i]}")
              with st.expander('Ver anotaciones'):
                for j in range(len(st.session_state.anotaciones[lista_anotaciones[i]])):
                  st.write(f"- {st.session_state.anotaciones[lista_anotaciones[i]][j]}")

        if st.button("Generar noticia", type = "primary"):
          with st.spinner("Generando noticia... ⌛"):

            st.session_state.noticia_generada = generar_noticia(st.session_state.new_dialogos, st.session_state.anotaciones, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
            st.rerun()
            
        elif st.button("Atrás", type = "primary", key = "atras"):
          del st.session_state['anotaciones']
          st.rerun()

    if 'noticia_generada' in st.session_state:
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Audio", description = ''),
            stx.TabBarItemData(id=2, title="Contexto", description = ''),
            stx.TabBarItemData(id=3, title="Transcripción", description = ''),
            stx.TabBarItemData(id=4, title="Temas seleccionados", description = ''),
            stx.TabBarItemData(id=5, title="Anotaciones", description = ''),
            stx.TabBarItemData(id=6, title="Noticia", description = ''),       
        ], default=6)
              
        if chosen_id == "1":
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")

        if chosen_id == "2":
          st.info("Aquí tienes el contexto que nos has proporcionado sobre las declaraciones")
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

        if chosen_id == "3":
          st.info("Aquí tienes la transcripción del audio")
          lista_transcription = st.session_state.lista_transcription
          texto = '\n\n- '.join(lista_transcription)
          texto = '- ' + texto
          
          patron = r'- (.+):'
          coincidencias = re.findall(patron, texto)
          
          for elemento in coincidencias:
              texto_formateado = f'<u><b>{elemento}</u></b>'
              texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                    
          # Mostrar el texto formateado
          st.write(texto, unsafe_allow_html=True)

        if chosen_id == "4":
          st.info("Estos son los asuntos más importantes de las declaraciones")
          lista_claves = list(st.session_state.new_dialogos.keys())

          for i in range(len(lista_claves)):
            st.write(f"### {lista_claves[i]}")
            with st.expander('Ver diálogo'):
              texto = '\n\n- '.join(st.session_state.new_dialogos[lista_claves[i]])
              texto = '- ' + texto
              
              patron = r'- (.+):'
              coincidencias = re.findall(patron, texto)
              
              for elemento in coincidencias:
                  texto_formateado = f'<u><b>{elemento}</u></b>'
                  texto = re.sub(f'- {elemento}:', f'- {texto_formateado}:', texto)      
                        
              # Mostrar el texto formateado
              st.write(texto, unsafe_allow_html=True)
        
        if chosen_id == "5":
          st.info("Aquí tienes las declaraciones que marcastes")
          lista_anotaciones = list(st.session_state.anotaciones.keys())
 
          for i in range(len(lista_anotaciones)):
            if len(st.session_state.anotaciones[lista_anotaciones[i]]) > 0:
              st.write(f"### {lista_anotaciones[i]}")
              with st.expander('Ver anotaciones'):
                for j in range(len(st.session_state.anotaciones[lista_anotaciones[i]])):
                  st.write(f"- {st.session_state.anotaciones[lista_anotaciones[i]][j]}")

        if chosen_id == "6":
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


