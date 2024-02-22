import streamlit as st
from journo.aggregate_auth import auth
from journo.modules import *
import time
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import extra_streamlit_components as stx
import pandas as pd
from openai import OpenAI

openai_client = OpenAI(api_key=st.secrets.openai_api)

st.set_page_config(page_title="Journo", page_icon='files/logo-removebg-preview.png')

if 'messages' in st.session_state:
    for i in range(len(st.session_state.messages)):
        st.write(st.session_state.messages[i])
    

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

if 'noticia_cargada' not in st.session_state:
    st.session_state.noticia_cargada = False
if 'messages' not in st.session_state:
     st.session_state.messages = []

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
if 'anotaciones' not in st.session_state:   
    st.session_state.anotaciones = {}
if 'anotaciones_state' not in st.session_state:   
    st.session_state.anotaciones_state = {}

st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)


auth()

load_database()

with st.sidebar:

    st.markdown(
        "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 180, 180) + "</p>",
        unsafe_allow_html=True
    )
    
    #st.markdown("""<div style='text-align: center;'><h2>Una nueva forma de hacer periodismo</h2></div>""",unsafe_allow_html=True)

    st.write('')
    with st.expander('**📰 Tu hemeroteca**'):
        if st.session_state.database.isna().all().all():
            st.info('¡Todavía no has creado ninguna noticia!')
        
        else:
            st.info('Estas son tus noticias guardadas. Puedes seleccionar alguna para volver a editarla con Journo')
            df_copia = st.session_state.database.copy()
            df_copia = df_copia.iloc[:, :-1]
            st.session_state.index_cargado = dataframetipo(df_copia)

            if st.button("Cargar noticia seleccionada", type = "primary", key = "start"):
                cargar_noticia()
                    
            if st.session_state.noticia_cargada == True:
                
                st.success(f"¡Ya puedes seguir modificando tu noticia!")   

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
    
    st.session_state.phase = stx.stepper_bar(steps=["Transcripción", "Contexto", "Destacados", "Tu noticia"])

    if st.session_state.phase == 0:
                      
        col1, col2 = st.tabs(["📼 Subir", "🎙️ Grabar"])
        with col1:
            if 'mp3_audio_path' not in st.session_state:
                st.info("Adjunta aquí tu audio con las declaraciones que deseas convertir en una noticia")
                st.session_state.archivo = st.file_uploader("Cargar archivo")

            if  st.session_state.archivo is not None and 'mp3_audio_path' not in st.session_state:       
                if st.button("Generar transcripción", type = "primary", key = "upload"):
                    with st.spinner("Transcribiendo... ⌛"):
                        st.warning('¡No cambies de pestaña para no perder el progreso!')
                        mp3_bytes = audio_a_bytes(st.session_state.archivo)
                        cargar_y_transcribir_audio(mp3_bytes)
                    
    
        with col2:
            if 'mp3_audio_path' not in st.session_state:
                st.info("También puedes grabar tu audio directamente desde Journo")
        
            audio=mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording",key='recorder')
            if audio is not None:
                if st.button("Generar transcripción", type = "primary", key = "record"):
                    with st.spinner("Transcribiendo... ⌛"):
                        st.warning('¡No cambies de pestaña para no perder el progreso!')
                        cargar_y_transcribir_audio(audio['bytes'])
                        
        if 'mp3_audio_path' in st.session_state:
            st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")

        if 'transcripcion_editada' in st.session_state:
            st.success("¡Aquí está la transcripción de tus declaraciones! Revísala y edítala si lo necesitas. Para continuar con la redacción, avanza a 2️⃣ Contexto")
            
            st.session_state.transcripcion_editada = st.text_area(label = ":blue[Tus declaraciones]", value = st.session_state.transcripcion_editada, height = int(len(st.session_state.transcripcion_editada)/4))
            st.session_state.lista_1 = st.session_state.transcripcion_editada.split('\n\n')
            
    if st.session_state.phase == 1:
        st.session_state.X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'El presidente de la Junta de Andalucía', value = st.session_state.X)
        st.session_state.Y = st.text_input(":blue[¿Cuál es el nombre del orador?]", placeholder = 'Juanma Moreno', value = st.session_state.Y)
        st.session_state.A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'en una rueda de prensa en el Palacio de San Telmo, en Sevilla', value = st.session_state.A)
        st.session_state.B = st.text_input(":blue[¿Cuándo las ha dicho?]", placeholder = 'tras el Consejo de Gobierno autonómico durante la mañana de este martes', value = st.session_state.B)
        st.session_state.Z = st.text_area(":blue[¿Qué más información de contexto es relevante para redactar la noticia?]", placeholder = 'Andalucía sufre desde hace meses una grave sequía, que ha llevado a la Junta a impulsar varios paquetes de medidas que...', value = st.session_state.Z)
        st.info(f"¿Lo tienes? Continúa en 3️⃣ Destacados")

    
    if st.session_state.phase == 2:
        if 'transcripcion_editada' in st.session_state:
            if 'anotaciones_finales' in st.session_state:
                 st.success("¡Ya tenemos los destacados! Avanaza a 4️⃣ Tu noticia para culminar la redacción")
            else:
                st.info('Aquí puedes seleccionar las frases más relevantes de las declaraciones para la redacción de tu noticia')

            if 'lista_2' not in st.session_state:
                st.session_state.lista_2 = st.session_state.lista_1
                
            if listas_iguales(st.session_state.lista_1, st.session_state.lista_2) == False:
                st.session_state.lista_2 = st.session_state.lista_1
                for i in range(len(st.session_state.lista_2)):
                    st.session_state.anotaciones[i] = [[]]
                    
            for i in range(len(st.session_state.lista_2)):
                if not st.session_state.anotaciones:
                    st.session_state.anotaciones_state[i] = text_highlighter(st.session_state.lista_2[i])
                else:
                    if len(st.session_state.anotaciones[i][0]) == 0:
                        st.session_state.anotaciones_state[i] = text_highlighter(st.session_state.lista_2[i])
                    else:
                        st.session_state.anotaciones_state[i] = text_highlighter(st.session_state.lista_2[i], st.session_state.anotaciones[i])


            c,v,g = st.columns(3)

            with v: 
                if st.button("Guardar destacados", type = "primary", key = "anotaciones_button"):
                    st.session_state.anotaciones_finales = []
                    for i in range(len(st.session_state.lista_2)):
                        st.session_state.anotaciones[i] = st.session_state.anotaciones_state[i]
                        for element in st.session_state.anotaciones[i]:
                            for item in element:
                                st.session_state.anotaciones_finales.append(item['label'])
                    st.rerun()

        else:
            st.warning('¡No tan rápido, Kapuściński! Vuelve a 1️⃣ Transcripción y asegúrate de que las declaraciones estén correctamente cargadas')

    if st.session_state.phase == 3:
        
       if 'noticia_editada' in st.session_state or st.session_state.generacion:
           with st.container():
                st.write("""""")
                for i in range(len(st.session_state.messages)):
                    if i == 0 or i == 1:
                        pass
                    elif i == 2:
                        st.session_state.noticia_editada = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_editada, height = int(len(st.session_state.noticia_editada)/4))
                    elif st.session_state.messages[i]['role'] == 'user':
                        st.info(st.session_state.messages[i]['content'])
                    else:
                        st.session_state.messages[i]['content'] = st.text_area(label = "", value = st.session_state.messages[i]['content'], height = int(len(st.session_state.messages[i]['content'])/4))
                
           if st.session_state.generacion:
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
                if st.session_state.generacion_noticia:
                    st.session_state.noticia_generada = full_response
                    st.session_state.noticia_editada = st.session_state.noticia_generada
                st.session_state.generacion = False
                st.session_state.generacion_noticia = False
               
                st.rerun()
                 
           a,b = st.columns([0.5,1])
           with a:
        
                if st.button("Volver a redactar noticia", type = "primary"): 
                  with st.spinner("Escribiendo... ⌛"):
                    st.session_state.messages = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                    st.session_state.generacion = True
                    st.session_state.generacion_noticia = True
                    st.rerun()
           with b:
                if prompt := st.chat_input("Haz que la noticia sea más larga / Propón tres titulares atractivos"):
                        
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.generacion = True
                    st.rerun()

       else:
           
            if 'anotaciones_finales' in st.session_state:
                if st.button("Redactar noticia", type = "primary"):
                  with st.spinner("Escribiendo... ⌛"):
                    st.session_state.messages = generar_noticia(st.session_state.transcripcion_editada, st.session_state.anotaciones_finales, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
                    st.session_state.generacion = True
                    st.session_state.generacion_noticia = True
                    st.rerun()
            else:
                st.warning('Journo no puede redactar tu noticia hasta que no le hayas dado toda la información que necesita :(')

 
#except Exception as e:
    #st.write(e)
    #st.error('Cargando...')
    #time.sleep(3)
    #st.rerun()
