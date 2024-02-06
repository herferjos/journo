import streamlit as st
from journo.utils.modules import *
from journo.pages.database import show_database
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import extra_streamlit_components as stx
import pandas as pd

def show_journo():
    st.write('## ✍🏼 Redacta con Journo')
    
    st.session_state.phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Selección/descarte", "Noticia generada"])
    if st.session_state.noticia_cargada == True:
        st.info('Se ha cargado la noticia de tu base de datos. Si quieres crear una nueva noticia, haz click en el siguiente botón de "Crear nueva noticia"')
        
    a, b, c = st.columns([0.5, 0.3, 0.5])
    
    with b:
        if st.button("Crear nueva noticia", type = "primary", key = "start"):
            reset_variables()
            st.rerun()

    st.write("---")

    if st.session_state.phase == 0:
        with st.expander('🔊 Audio cargado'):
            if 'mp3_audio_path' in st.session_state:
                try:
                    st.info("Aquí tienes el audio que hemos procesado previamente")
                    st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
                except:
                    st.error("Error al cargar el audio. Recuerda que si cargas una noticia de la base de datos, no está disponible el audio para escuchar")
            else:
                st.warning('Aún no has cargado ningún audio')
                
      
        col1, col2 = st.tabs(["Subir audio", "Grabar audio"])
        with col1:
            st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia.")
            archivo = st.file_uploader("Cargar archivo de audio")
        
        if st.button("Guardar audio", type = "primary", key = "upload"):
          with st.spinner("Cargando audio... ⌛"):
            if archivo is not None:
                # Convierte el audio a formato MP3
                mp3_bytes = audio_a_bytes(archivo)
                          
                st.session_state.mp3_audio_path = bytes_a_audio(mp3_bytes, formato_destino="mp3")
                st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
                st.session_state.transcription2 = parrafer(st.session_state.transcription1)          
                st.rerun()
        
        with col2:
            st.info("Puedes empezar a grabar un audio directamente desde aquí")
        
            audio=mic_recorder(start_prompt="Empezar a grabar",stop_prompt="Parar de grabar",key='recorder')
            if audio is not None:
              if st.button("Siguiente", type = "primary", key = "record"):
                with st.spinner("Cargando audio... ⌛"):            
                    st.session_state.mp3_audio_path = bytes_a_audio(audio['bytes'], formato_destino="mp3")
                    st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
                    st.session_state.transcription2 = parrafer(st.session_state.transcription1)
                  
                    st.rerun()
                    
        if 'mp3_audio_path' in st.session_state:
            st.success(f"Audio cargado correctamente. Ve a la pestaña de 'Contexto' para continuar")

    if st.session_state.phase == 1:
      
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
          
              
        if st.button("Guardar", type = "primary", key = "Enviar"):
              with st.spinner("Enviando información... ⌛"):
                st.warning("Este proceso puede tardar unos minutos.")
                st.session_state.X = X
                st.session_state.Y = Y
                st.session_state.Z = Z
                st.session_state.A = A
                st.session_state.B = B
    
                st.rerun()
                  
        if 'X' in st.session_state:
            st.success(f"Contexto cargado correctamente. Ve a la pestaña de 'Transcripción' para continuar")


    if st.session_state.phase == 2:
        if 'transcription2' in st.session_state:
            st.info("Aquí tienes la transcripción del audio completa")
            
            edited_transcription = st.text_area(label = ":blue[Transcripción generada]", value = st.session_state.transcription2, height = int(len(st.session_state.transcription2)/5))
            
            st.success(f"Transcripción generada correctamente. Puedes editarla y darle a guardar o ir directamente a la pestaña de 'Selección' para continuar")
            
            if st.button("Guardar transcripción editada", type = "primary"):
                st.session_state.transcription2 = edited_transcription
                st.rerun()

        else:
            st.warning('Aún no has generado ninguna transcripción')
    
    if st.session_state.phase == 3:
        with st.expander('✍🏼Ver anotaciones'):
            if 'on_0' in st.session_state:
              st.info("Aquí tienes los párrafos descartados (aparecen desmarcados) y los momentos de mayor relevancia en las declaraciones.")
                
              for i in range(len(st.session_state.lista)):
                  on = st.toggle('', key=i, value = st.session_state[f'on_{i}'])
                  frases = []
                  if st.session_state[f'anotaciones_{i}'] == None:
                      pass
                  else:         
                      for item in st.session_state[f'anotaciones_{i}']:
                          for x in item:
                            frases.append(x['label'])
                      st.write(generar_html_con_destacados(st.session_state.lista[i], frases), unsafe_allow_html=True)
            else:
                st.warning('Aún no has generado ninguna anotación sobre la transcripción')

        if 'transcription2' in st.session_state:
            st.info("Aquí puedes eliminar fragmentos de la transcripción desmarcando el párrafo y subrayar en aquellos que desees incluir, indicando así que partes son más importantes a la hora de generar la noticia.")
            st.session_state.lista = st.session_state.transcription2.split('\n\n')
            
            for i in range(len(st.session_state.lista)):
              st.session_state[f'on_{i}'] = st.toggle('', key=f'{i}_{i}', value = True)
              st.session_state[f'anotaciones_{i}'] = text_highlighter(st.session_state.lista[i])
        
            if 'transcripcion_final' in st.session_state:
                a,b = st.columns([0.2, 1])
                with a:
                    if st.button("Guardar", type = "primary"):
                      with st.spinner("Procesando la información... ⌛"):
                        st.session_state.anotaciones_finales = []
                        st.session_state.transcripcion_final = ''
                        for i in range(len(st.session_state.lista)):
                          if st.session_state[f'on_{i}']:
                            for item in st.session_state[f'anotaciones_{i}']:
                                for x in item:
                                    st.session_state.anotaciones_finales.append(x['label'])
                                    
                            st.session_state.transcripcion_final += st.session_state.lista[i] + '\n\n'
            
                            st.rerun()
        
                with b:
                    if st.button("Generar noticia", type = "primary"):
                      with st.spinner("Generando noticia... ⌛"):
                        st.session_state.noticia_generada = generar_noticia(st.session_state.transcripcion_final, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                        st.rerun()
            else:
                
                if st.button("Guardar", type = "primary"):
                  with st.spinner("Procesando la información... ⌛"):
                    st.session_state.anotaciones_finales = []
                    st.session_state.transcripcion_final = ''
                    for i in range(len(st.session_state.lista)):
                      if st.session_state[f'on_{i}']:
                        for item in st.session_state[f'anotaciones_{i}']:
                            for x in item:
                                st.session_state.anotaciones_finales.append(x['label'])
                                
                        st.session_state.transcripcion_final += st.session_state.lista[i] + '\n\n'
        
                        st.rerun()

            if 'noticia_generada' in st.session_state:
                if 'transcripcion_final' in st.session_state:
                    st.success(f"Anotaciones guardadas y noticia generada correctamente. Ve a la pestaña de 'Noticia' para continuar")
                else:
                    st.success(f"Noticia generada correctamente. Ve a la pestaña de 'Noticia' para continuar")
            else:
                if 'transcripcion_final' in st.session_state:
                    st.success(f"Anotaciones guardadas correctamente. Ve a la pestaña de 'Noticia' para continuar")
            
        else:
            st.warning('Aún no has generado ninguna transcripción. Vuelve al paso de contexto y guarda la información para que la transcripción se genere correctamente.')

    if st.session_state.phase == 4:
        if 'noticia_generada' in st.session_state:
            st.write("""## ✅ ¡Ya está lista tu noticia!""")
            st.info("Podrás editar la noticia directamente aquí para adaptarla a tu gusto. Si lo prefieres, puedes pedirle a la IA que lo haga por ti en la pestaña de 'Chatear con IA'")
            
            edited_noticia = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_generada, height = int(len(st.session_state.noticia_generada)/5))
            if st.button("Guardar noticia", type = "primary"):
                st.session_state.noticia_generada = edited_noticia
                guardar_info()
                st.rerun()
        else:
            st.warning('Aún no has generado ninguna noticia. Vuelve al paso anterior y genera la noticia.')

    return
