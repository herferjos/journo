import streamlit as st
from journo.utils.modules import *
from journo.pages.database import show_database
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import extra_streamlit_components as stx
import pandas as pd

def show_journo():
    st.write('## ✍🏼 Redacta con Journo')
    
    st.session_state.phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Selección/descarte", "Noticia generada", "Chatear con IA", "Enviar información"])

    a, b, c = st.columns([0.5, 0.3, 0.5])
    
    with b:
        if st.button("Crear nueva noticia", type = "primary", key = "start"):
            reset_variables()
            st.rerun()
            
    st.write('')

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
    
                
                st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
                st.session_state.transcription2 = parrafer(st.session_state.transcription1)
                st.rerun()


    if st.session_state.phase == 2:
        if 'transcription2' in st.session_state:
            st.info("Aquí tienes la transcripción del audio completa")
            st.write(st.session_state.transcription2, unsafe_allow_html=True)
        else:
            st.warning('Aún no has generado ninguna transcripción')
    
    if st.session_state.phase == 3:
        with st.expander('✍🏼Ver anotaciones'):
            if 'on_0' in st.session_state:
              st.info("Aquí tienes los párrafos descartados (aparecen desmarcados) y los momentos de mayor relevancia en las declaraciones.")
                
              for i in range(len(st.session_state.lista)):
                  on = st.toggle('', key=i, value = st.session_state[f'on_{i}'])
                  frases = []
                  for item in st.session_state[f'anotaciones_{i}']:
                      for x in item:
                        frases.append(x['label'])
                  st.write(generar_html_con_destacados(st.session_state.lista[i], frases), unsafe_allow_html=True)
            else:
                st.warning('Aún no has generado ninguna anotación sobre la transcripción')

        
        st.info("Aquí puedes eliminar fragmentos de la transcripción desmarcando el párrafo y subrayar en aquellos que desees incluir, indicando así que partes son más importantes a la hora de generar la noticia.")
        st.session_state.lista = st.session_state.transcription2.split('\n\n')
        
        for i in range(len(st.session_state.lista)):
          st.session_state[f'on_{i}'] = st.toggle('', key=f'{i}_{i}', value = True)
          st.session_state[f'anotaciones_{i}'] = text_highlighter(st.session_state.lista[i])
    
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


    if st.session_state.phase == 4:
        st.write("""## ✅ ¡Ya está lista tu noticia!""")
        st.info("Podrás editar la noticia directamente aquí para adaptarla a tu gusto. Si lo prefieres, puedes pedirle a la IA que lo haga por ti en la pestaña de 'Chatear con IA'")
        
        edited_noticia = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_generada, height = int(len(st.session_state.noticia_generada)/5))
        if st.button("Guardar noticia", type = "primary"):
            st.session_state.noticia_generada = edited_noticia
            st.rerun()
            
    if st.session_state.phase == 5:
        st.write('## 🤖 Chatea con una IA y ayúdate')
        st.info('Puedes chatear con una IA para ayudarte a formatear la noticia cómo desees. Además, podrás importar fácilmente la noticia de la sección "Noticia generada" haciendo click en el siguiente botón:')
        if st.button("Copiar noticia ", type = "primary"):
            st.session_state.messages.append({"role": "system", "content": f"Esta es la noticia del usuario: {st.session_state.noticia_generada}"})
        
        for message in st.session_state.messages:
            if message["role"] == "system":
                pass
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        prompt = st.chat_input("Pregunta lo que quieras")

        if st.button("Enviar ", type = "primary"):
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                        
                response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=st.session_state.messages,
                temperature = 0,
                stream = True
                )
                
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in response:
                    full_response += chunk.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
                          
                st.session_state.messages.append({"role": "assistant", "content": full_response})

    if st.session_state.phase == 6:
        st.write('## 📍Guardar información')
        st.info('Guardaremos la información y te haremos llegar la información que desees a tu correo electrónico.')
        contenido = generar_txt()

        if st.button("Guarda información", type = "primary"):
            with st.spinner("Guardando información... ⌛"):
                if st.session_state.database.isna().all().all():
                    st.session_state.sheet.update(worksheet=st.session_state.email, data = pd.DataFrame({'Transcripción': [st.session_state.transcription2], 'Cargo': [st.session_state.X], 'Nombre': [st.session_state.Y], 'Tema': [st.session_state.Z], 'Donde': [st.session_state.A], 'Cuando': [st.session_state.B], 'Transcripción filtrada': [st.session_state.transcripcion_final], 'Anotaciones': [st.session_state.anotaciones_finales], 'Noticia': [st.session_state.noticia_generada], 'Sesion': [contenido]}))
                else:
                    st.session_state.database.append({'Transcripción': st.session_state.transcription2, 'Cargo': st.session_state.X, 'Nombre': st.session_state.Y, 'Tema': st.session_state.Z, 'Donde': st.session_state.A, 'Cuando': st.session_state.B, 'Transcripción filtrada': st.session_state.transcripcion_final, 'Anotaciones': st.session_state.anotaciones_finales, 'Noticia': st.session_state.noticia_generada, 'Sesion': contenido}, ignore_index=True)
                    st.session_state.sheet.update(worksheet=st.session_state.email, data = st.session_state.database)
                    
                st.session_state.guardado = True
                st.rerun()
        if st.session_state.guardado:
            st.success(f"🎉 ¡Noticia guardada con éxito!")
    return
