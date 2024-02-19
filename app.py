import streamlit as st
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import *
import time
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import extra_streamlit_components as stx
import pandas as pd
from openai import OpenAI

openai_client = OpenAI(api_key=st.secrets.openai_api)

st.set_page_config(page_title="Journo", page_icon="🗞️")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 400px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if 'messages' not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'content': 'Hola, soy Journo y estoy aquí para ayudarte. Aún no has generado ninguna noticia. Te invito a rellenar toda la información necesaria y luego podrás volver aquí y generar tu noticia'}]

if 'guardado' not in st.session_state:
    st.session_state.guardado = False
    
if 'noticia_cargada' not in st.session_state:
    st.session_state.noticia_cargada = False

if 'X' not in st.session_state:
    st.session_state.X = None
if 'Y' not in st.session_state:
    st.session_state.Y = None
if 'Z' not in st.session_state:
    st.session_state.Z = None
if 'A' not in st.session_state:
    st.session_state.A = None
if 'B' not in st.session_state:
    st.session_state.B = None
if 'generacion' not in st.session_state:   
    st.session_state.generacion = False
if 'variables_dinamicas' not in st.session_state:   
    st.session_state.variables_dinamicas = {}  


st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)


add_auth(required=True, login_sidebar = False)

load_database()

with st.sidebar:

    st.markdown(
        "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 180, 180) + "</p>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div style='text-align: center;'>
            <h2>Una nueva forma de hacer periodismo</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write('---')
    with st.expander('**📊 Noticias generadas**'):
        if st.session_state.database.isna().all().all():
            st.info('Actualmente no has generado ninguna noticia. Adelante, prueba Journo y guarda tu primera noticia asistida por IA')

            if st.button("Crear nueva noticia", type = "primary", key = "start"):
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

    st.write('')
    
    c,d = st.columns(2)

    with c:
        boton_reset = st.button("Nueva noticia", type = "primary", key = "restart")
        
    if boton_reset:
        reset_variables()
        
    with d:
        boton_guardar = st.button("Guardar progreso", type = "primary")
        
    if boton_guardar:
        guardar_info()
        st.rerun()
        

if 'email' in st.session_state and st.session_state.user_subscribed == True: 
    
    st.session_state.phase = stx.stepper_bar(steps=["Transcripción", "Contexto", "Destacado", "Noticia"])

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

        if 'transcription2' in st.session_state:
            st.info("Transcripción generada correctamente. Puedes editarla y darle a guardar o ir directamente a la pestaña de 'Selección' para continuar")
            
            st.session_state.transcripcion_editada = st.text_area(label = ":blue[Transcripción generada]", value = st.session_state.transcripcion_editada, height = int(len(st.session_state.transcription2)/4))
    
    if st.session_state.phase == 1:
        st.info(f"Una vez acabes de rellenar los campos, ve a la pestaña de 'Transcripción' para continuar")
        st.session_state.X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'Entrenador Real Madrid', value = st.session_state.X)
        st.session_state.Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", placeholder = 'Ancelotti', value = st.session_state.Y)
        st.session_state.A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'Rueda de Prensa', value = st.session_state.A)
        st.session_state.B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", placeholder = 'Martes 12', value = st.session_state.B)
        st.session_state.Z = st.text_area(":blue[Añade más contexto]", value = st.session_state.Z)

    
    if st.session_state.phase == 2:
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
            
            anotaciones= []
            for i in range(len(st.session_state.lista)):
              anotaciones.append(text_highlighter(st.session_state.lista[i]))


            if st.button("Guardar anotaciones", type = "primary"):
              with st.spinner("Guardando anotaciones... ⌛"):
                st.session_state.anotaciones_finales = []
                  
                for i in range(len(st.session_state.lista)):
                    st.session_state[f'anotaciones_{i}'] = anotaciones[i]
                    for item in st.session_state[f'anotaciones_{i}']:
                        for x in item:
                            st.session_state.anotaciones_finales.append(x['label'])
                                                
                st.rerun()


            if 'anotaciones_finales' in st.session_state:
                st.success(f"Anotaciones guardadas correctamente. Ve a la pestaña de 'Noticia' para continuar")
            
        else:
            st.warning('Aún no has generado ninguna transcripción. Vuelve al paso de contexto y guarda la información para que la transcripción se genere correctamente.')

    if st.session_state.phase == 3:
        if 'noticia_generada' in st.session_state:
            st.write("""## ✅ ¡Ya está lista tu noticia!""")
            with st.expander('Editar noticia original'):
                st.session_state.noticia_editada = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_editada, height = int(len(st.session_state.noticia_editada)/5))
            a,b = st.columns([0.5,1])
            with a:
                boton_guardar = st.button("Guardar noticia", type = "primary")
                
            if boton_guardar: 
               st.session_state.messages.append({"role": "user", "content": f'Esta es la nueva noticia editada por mi: {st.session_state.noticia_editada}'})
            
            with b:
                boton_volver = st.button("Volver a generar noticia", type = "primary")
                
            if boton_volver: 
              with st.spinner("Generando noticia... ⌛"):
                st.session_state.messages = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                st.session_state.generacion = True
                st.rerun()

        else:
            st.warning('Aún no has generado ninguna noticia, dale click a "Generar noticia"')
            if st.button("Generar noticia", type = "primary"):
              with st.spinner("Generar noticia... ⌛"):
                st.session_state.messages = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                st.session_state.generacion = True
                st.rerun()
        if len(st.session_state.messages) > 1:
            with st.container(height = min(len(st.session_state.messages) * 150, 500)):
                for i in range(len(st.session_state.messages)):
                    if st.session_state.messages[i]["role"] == "system" or i == 1:
                        pass
                    else:
                        with st.chat_message(st.session_state.messages[i]["role"]):
                            st.markdown(st.session_state.messages[i]["content"])
                            
                    
                if prompt := st.chat_input("Pregunta lo que quieras") or st.session_state.generacion:
        
                    if st.session_state.generacion == False:
                    
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
                        if st.session_state.generacion:
                            st.session_state.noticia_generada = full_response
                            st.session_state.noticia_editada = st.session_state.noticia_generada
                        st.session_state.generacion = False
                        st.rerun()

#except Exception as e:
    #st.write(e)
    #st.error('Ha habido un error en Journo. La página será recargada en 3 segundos, si el error persiste contácta con el equipo de atención al cliente de Journo')
    #time.sleep(3)
    #st.rerun()
