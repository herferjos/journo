import streamlit as st
from journo.utils.modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import extra_streamlit_components as stx
import pandas as pd

def show_journo():
    with st.expander('**Ver tus noticias**'):
        st.write('## 📊 Tus noticias')
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
            df_cargado = dataframetipo(df_copia)
            if st.button("Crear nueva noticia", type = "primary", key = "start"):
                cargar_noticia(df_cargado)
    
            if st.session_state.noticia_cargada == True:
                
                st.success(f"👍🏻 Noticia cargada correctamente. Puedes ir a la sección 'Journo' para continuar modificando la noticia")
    st.session_state.phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Destacar", "Noticia"])
    if st.session_state.noticia_cargada == True:
        st.info('Se ha cargado la noticia de tu base de datos. Si quieres crear una nueva noticia, haz click en el siguiente botón de "Crear nueva noticia"')


    import threading
    
    def cargar_y_transcribir_audio(audio):
        # Convierte el audio a formato MP3
        st.session_state.mp3_audio_path = bytes_a_audio(audio, formato_destino="mp3")
        st.session_state.transcription1 = transcribe_audio(mp3_audio_path)
        st.session_state.transcription2 = parrafer(transcription1)
        st.session_state.transcripcion_editada = st.session_state.transcription2

        st.rerun()    

    if st.session_state.phase == 0:
                      
        col1, col2 = st.tabs(["📼 Subir", "🎙️ Grabar"])
        with col1:
            if 'mp3_audio_path' not in st.session_state:
                st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia.")
                st.session_state.archivo = st.file_uploader("Cargar archivo de audio")
                
            if 'mp3_audio_path' in st.session_state:
                st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
                st.success(f"Audio cargado correctamente. Ve a la pestaña de 'Contexto' para continuar")
                
            if  st.session_state.archivo is not None and 'mp3_audio_path' not in st.session_state:       
                if st.button("Guardar audio", type = "primary", key = "upload"):
                    mp3_bytes = audio_a_bytes( st.session_state.archivo)
                    threading.Thread(target=cargar_y_transcribir_audio, args=(mp3_bytes,)).start()
    
        with col2:
            if 'mp3_audio_path' not in st.session_state:
                st.info("Puedes empezar a grabar un audio directamente desde aquí")
        
            audio=mic_recorder(start_prompt="Empezar a grabar",stop_prompt="Parar de grabar",key='recorder')
            if audio is not None:
                if 'mp3_audio_path' in st.session_state:
                    st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
                        
                    st.success(f"Audio cargado correctamente. Ve a la pestaña de 'Contexto' para continuar")
                if st.button("Guardar audio", type = "primary", key = "record"):
                    threading.Thread(target=cargar_y_transcribir_audio, args=(audio['bytes'],)).start()

        if 'mp3_audio_path' in st.session_state:
            st.success("Audio cargado correctamente. Ve a la pestaña de 'Contexto' para continuar")


    if st.session_state.phase == 1:
        
        if 'X' in st.session_state:
            st.session_state.X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", value = st.session_state.X)
            st.session_state.Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", value = st.session_state.Y)
            st.session_state.A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", value = st.session_state.A)
            st.session_state.B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", value = st.session_state.B)
            st.session_state.Z = st.text_area(":blue[Añade más contexto]", value = st.session_state.Z)

        
        else:
            st.info("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
            st.session_state.X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'Entrenador Real Madrid')
            st.session_state.Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", placeholder = 'Ancelotti')
            st.session_state.A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'Rueda de Prensa')
            st.session_state.B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", placeholder = 'Martes 12')
            st.session_state.Z = st.text_area(":blue[Añade más contexto]", placeholder = 'Partido vs Atletico de Madrid')
          
        if 'X' in st.session_state:
            st.success(f"Contexto cargado correctamente. Ve a la pestaña de 'Transcripción' para continuar")
            st.write(f'Aqui tienes el X: {st.session_state.X}')


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
                      if st.session_state[f'anotaciones_{i}'] == None:
                          pass
                      else:         
                          for item in st.session_state[f'anotaciones_{i}']:
                              for x in item:
                                frases.append(x['label'])
                          st.write(generar_html_con_destacados(st.session_state.lista[i], frases), unsafe_allow_html=True)


        if 'transcription2' in st.session_state:
            st.info("Aquí puedes subrayar los momentos más importantes de las declaraciones a la hora de generar la noticia.")
            st.session_state.lista = st.session_state.transcription2.split('\n\n')
            
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
            st.info("Podrás editar la noticia directamente aquí para adaptarla a tu gusto. Si lo prefieres, puedes pedirle a la IA que lo haga por ti en la pestaña de 'Chatear con IA'")
            st.session_state.noticia_editada = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_editada, height = int(len(st.session_state.noticia_generada)/5))
            a,b = st.columns([0.7,1])
            with a:
                if st.button("Guardar noticia", type = "primary"):
                    guardar_info()
                    st.rerun()
            with b:
                if st.button("Volver a generar noticia", type = "primary"):
                  with st.spinner("Generar noticia... ⌛"):
                    st.session_state.noticia_generada = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                    st.session_state.noticia_editada = st.session_state.noticia_generada
                    st.rerun()
        else:
            st.warning('Aún no has generado ninguna noticia, dale click a "Generar noticia"')
            if st.button("Generar noticia", type = "primary"):
              with st.spinner("Generar noticia... ⌛"):
                st.session_state.noticia_generada = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                st.session_state.noticia_editada = st.session_state.noticia_generada
                st.rerun()
                  
    return
