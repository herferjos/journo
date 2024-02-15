import streamlit as st
from journo.utils.modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import extra_streamlit_components as stx
import pandas as pd
import subprocess 
from openai import OpenAI

openai_client = OpenAI(api_key=st.secrets.openai_api)

def show_journo():
    
    st.session_state.phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Destacado", "Noticia"])

    if st.session_state.phase == 0:
                      
        col1, col2 = st.tabs(["📼 Subir", "🎙️ Grabar"])
        with col1:
            if 'mp3_audio_path' not in st.session_state:
                st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia.")
                st.session_state.archivo = st.file_uploader("Cargar archivo de audio")

            if  st.session_state.archivo is not None and 'mp3_audio_path' not in st.session_state:       
                if st.button("Guardar audio", type = "primary", key = "upload"):
                    with st.spinner("Transcribiendo audio... ⌛"):
                        st.warning('Estamos transcribiendo el audio, no cambies de pestaña para no perder el progreso')
                        mp3_bytes = audio_a_bytes(st.session_state.archivo)
                        cargar_y_transcribir_audio(mp3_bytes)
                    
    
        with col2:
            if 'mp3_audio_path' not in st.session_state:
                st.info("Puedes empezar a grabar un audio directamente desde aquí")
        
            audio=mic_recorder(start_prompt="Empezar a grabar",stop_prompt="Parar de grabar",key='recorder')
            if audio is not None:
                if st.button("Guardar audio", type = "primary", key = "record"):
                    with st.spinner("Transcribiendo audio... ⌛"):
                        st.warning('Estamos transcribiendo el audio, no cambies de pestaña para no perder el progreso')
                        cargar_y_transcribir_audio(audio['bytes'])
                        
        if 'mp3_audio_path' in st.session_state:
            st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
            st.success(f"Audio cargado correctamente. Ve a la pestaña de 'Contexto' para continuar")

        with st.expander('**📊 Tus noticias**'):
            if st.session_state.database.isna().all().all():
                st.info('Actualmente no has generado ninguna noticia. Adelante, prueba Journo y guarda tu primera noticia asistida por IA')
    
                if st.button("Crear nueva noticia", type = "primary", key = "start"):
                    st.warning('¿Estás seguro de que quieres comenzar a crear una nueva noticia desde cero? Perderás la noticia que estás editando ahora mismo')
                    if st.button("¡Sí, adelante!", type = "primary", key = "yes"): 
                        reset_variables()
            
            else:
                st.info('Aquí tienes las noticias que has generado con el asistente Journo. Puedes cargar una noticia directamente, explorar la información o crear una nueva.')
                df_copia = st.session_state.database.copy()
                df_copia = df_copia.iloc[:, :-1]
                st.session_state.index_cargado = dataframetipo(df_copia)
    
                if st.button("Cargar noticia seleccionada", type = "primary", key = "start"):
                    cargar_noticia()
                        
                if st.session_state.noticia_cargada == True:
                    
                    st.success(f"👍🏻 Noticia cargada correctamente. Ahora puedes seguir modificando la noticia más abajo.")      
    
    if st.session_state.phase == 1:
        st.info(f"Una vez acabes de rellenar los campos, ve a la pestaña de 'Transcripción' para continuar")
        st.session_state.X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'Entrenador Real Madrid', value = st.session_state.X)
        st.session_state.Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", placeholder = 'Ancelotti', value = st.session_state.Y)
        st.session_state.A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'Rueda de Prensa', value = st.session_state.A)
        st.session_state.B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", placeholder = 'Martes 12', value = st.session_state.B)
        st.session_state.Z = st.text_area(":blue[Añade más contexto]", value = st.session_state.Z)

            

    if st.session_state.phase == 2:
        if 'transcription2' in st.session_state:
            st.info("Transcripción generada correctamente. Puedes editarla y darle a guardar o ir directamente a la pestaña de 'Selección' para continuar")
            
            st.session_state.transcripcion_editada = st.text_area(label = ":blue[Transcripción generada]", value = st.session_state.transcripcion_editada, height = int(len(st.session_state.transcription2)/4))
            
            if st.button("Guardar transcripción editada", type = "primary"):
                st.rerun()

        else:
            st.warning('Aún no has generado ninguna transcripción')
    
    if st.session_state.phase == 3:
        if 'anotaciones_0' in st.session_state:
            with st.expander('✍🏼Ver anotaciones'):
                  st.info("Aquí los momentos de mayor relevancia en las declaraciones.")
                    
                  for i in range(len(st.session_state.lista)):
                      frases = []
                      if f'anotaciones_{i}' in st.session_state:
                          if st.session_state[f'anotaciones_{i}'] == None:
                              pass
                          else:         
                              for item in st.session_state[f'anotaciones_{i}']:
                                  for x in item:
                                    frases.append(x['label'])
                              st.write(generar_html_con_destacados(st.session_state.lista[i], frases), unsafe_allow_html=True)


        if 'transcription2' in st.session_state:
            st.info("Aquí puedes subrayar los momentos más importantes de las declaraciones a la hora de generar la noticia.")
            st.session_state.lista = st.session_state.transcripcion_editada.split('\n\n')
            
            for i in range(len(st.session_state.lista)):
              st.session_state[f'anotaciones_{i}'] = text_highlighter(st.session_state.lista[i])


            if st.button("Guardar anotaciones", type = "primary"):
              with st.spinner("Guardando anotaciones... ⌛"):
                st.session_state.anotaciones_finales = []
                  
                for i in range(len(st.session_state.lista)):
                    for item in st.session_state[f'anotaciones_{i}']:
                        for x in item:
                            st.session_state.anotaciones_finales.append(x['label'])
                                                
                st.rerun()


            if 'anotaciones_finales' in st.session_state:
                st.success(f"Anotaciones guardadas correctamente. Ve a la pestaña de 'Noticia' para continuar")
            
        else:
            st.warning('Aún no has generado ninguna transcripción. Vuelve al paso de contexto y guarda la información para que la transcripción se genere correctamente.')

    if st.session_state.phase == 4:
        if 'noticia_generada' in st.session_state:
            st.write("""## ✅ ¡Ya está lista tu noticia!""")
            with st.expander('Editar noticia'):
                st.session_state.noticia_editada = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_editada, height = int(len(st.session_state.noticia_editada)/5))
                if st.button("Guardar noticia", type = "primary"): 
                   st.session_state.mensajes_noticias.append({"role": "user", "content": f'Esta es la nueva noticia editada por mi: {st.session_state.noticia_editada}'})
                   st.session_state.mensajes.append({"role": "user", "content": st.session_state.noticia_editada})


        else:
            st.warning('Aún no has generado ninguna noticia, dale click a "Generar noticia"')
            if st.button("Generar noticia", type = "primary"):
              with st.spinner("Generar noticia... ⌛"):
                st.session_state.mensajes_noticias = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)

        with st.container():
            for message in st.session_state.messages:
                if message["role"] == "system":
                    pass
                else:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            
            if prompt := st.chat_input("Pregunta lo que quieras"):
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                with st.chat_message("assistant"):
                            
                    response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=st.session_state.messages,
                    temperature = 0,
                    stream = True
                    )
                    
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
        
                              
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()

                
    if st.button("Volver a generar noticia", type = "primary"): 
      with st.spinner("Generando noticia... ⌛"):
        st.session_state.messages = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
        st.rerun()
                  
    return
