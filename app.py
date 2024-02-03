from openai import OpenAI
import streamlit as st
from rsc.modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import re
import extra_streamlit_components as stx
from rsc.aggregate_auth import add_auth

st.set_page_config(page_title="Journo", page_icon="🗞️", layout="wide")

prueba = text_highlighter("jeje esto es una prueba. muy larga")

st.write(prueba)

st.markdown(
    "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo.png', 200, 200) + "</p>",
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style='text-align: center;'>
        <h4>Tu asistente periodístico de inteligencia artificial</h4>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("---")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres un asistente virtual de Journo, una webapp de asistencia con IA para periodistas y ahora podrás comunicarte con los usuarios de Journo. Trata de ayudar a los usuarios con sus peticiones e instrucciones para dar forma y estilo a una noticia periodística. Razona siempre paso por paso cualquier petición."}]
    
st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)

x,y,z = st.columns(3)
with y:
  add_auth(required=True, login_sidebar = False)


if 'email' in st.session_state and st.session_state.user_subscribed == True:
    if 'inicio' not in st.session_state:
        st.success(f"🥳 ¡Bienvenido {st.session_state.email}!")
        st.write("## ¿Qué es Journo?")
        st.markdown(
            """
            <h4>Journo es una <strong>Inteligencia Artificial</strong> que te ayudará en tu día a día a la hora de redactar noticias. Con Journo podrás:</h4>
            <ul>
                <li><strong>Automatizar</strong> la transcripción de audios</li>
                <li><strong>Guíar</strong> a la Inteligencia Artificial a redactar la noticia a tu gusto</li>
                <li><strong>Modificar</strong> las noticias y darle el toque final</li>
                <li><strong>Recibirás</strong> toda la información en un correo electrónico</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        
        st.write("")
        
        a,b,c = st.columns([1,0.7,5])
        with b:
            if st.button("Probar Journo", type = "primary", key = "start"):
                st.session_state.inicio = True
                
                del st.session_state.mp3_audio_path
                del st.session_state.X
                del st.session_state.Y
                del st.session_state.Z
                del st.session_state.A
                del st.session_state.B
                del st.session_state.transcription2 
                del st.session_state.lista_transcription 
                del st.session_state.topics
                del st.session_state.dialogos_topics
                
                st.rerun()
        with c:   
            st.link_button("Ver video tutorial", "https://streamlit.io/gallery", type = "primary")

        st.write("---")
            
        st.write("## ¿Cómo funciona Journo?")
        
        with open('files/demo.txt', "r",encoding="utf-8") as archivo:
            content = archivo.read()
      
        exec(content)
      
        phase = stx.stepper_bar(steps=["Audio", "Contexto", "Selección temática", "Destacar momentos", "Noticia"])
      
        if phase == 0:
            st.write("### 1) Cargar o subir audio")
            st.info("En esta primera etapa deberemos aportar al sistema el audio a transcribir. Podemos subir un audio ya grabado o grabarlo directamente desde la app")
            with st.expander("*Ver ejemplo*"):
                st.audio('files/audio.mp3', format="audio/mpeg")
        
        if phase == 1:
            st.write("### 2) Describir el contexto de las declaraciones")
            st.info("Ahora deberemos de aportar información a la Inteligencia Artificial para que sepa en qué contexto se han producido las declaraciones que has aportado")
            with st.expander("*Ver ejemplo*"):
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
        
        if phase == 2:
            st.write("### 3) Selección/descarte de temas mencionados")
            st.info("A continuación deberemos deseleccionar aquellos asuntos que no queremos incluir en la noticia final y fueron mencionados en las declaraciones.")
            with st.expander("*Ver ejemplo*"):
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

            
    if 'mp3_audio_path' not in st.session_state and 'inicio' in st.session_state:
        
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

  
    if 'mp3_audio_path' in st.session_state and 'transcription2' not in st.session_state and 'inicio' in st.session_state:
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
          
        col1, col2 = st.columns([0.07,1])
        
        with col2:
          boton_adelante = st.button("Siguiente", type = "primary", key = "Enviar")
              
        with col1:
          if st.button("Atrás", type = "primary", key = "atras"):
            del st.session_state['mp3_audio_path']
            st.rerun()
              
        if boton_adelante:
              with st.spinner("Enviando información... ⌛"):
                st.warning("Este proceso puede tardar unos minutos.")
                st.session_state.X = X
                st.session_state.Y = Y
                st.session_state.Z = Z
                st.session_state.A = A
                st.session_state.B = B
    
                
                st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
                st.session_state.transcription2, st.session_state.lista_transcription = parrafer(st.session_state.transcription1)
                st.rerun()
          
    if 'transcription2' in st.session_state and 'transcripcion_final' not in st.session_state and 'inicio' in st.session_state:
      
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Audio", description = ''),
            stx.TabBarItemData(id=2, title="Contexto", description = ''),
            stx.TabBarItemData(id=3, title="Transcripción", description = ''),
            stx.TabBarItemData(id=4, title="Selección/descarte", description = ''),
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
          st.info("Aquí tienes la transcripción del audio completa")
          st.write(st.session_state.transcription2, unsafe_allow_html=True)
      
        if chosen_id == "4":
          st.info("Ahora puedes eliminar fragmentos de la transcripción desmarcando el párrafo y subrayar en aquellos que desees incluir, indicando así que partes son más importantes a la hora de generar la noticia.")
          st.session_state.lista = st.session_state.transcription2.split('\n\n')
            
          for i in range(len(st.session_state.lista)):
              st.session_state[f'on_{i}'] = st.toggle('', key=i, value = True)
              st.session_state[f'anotaciones_{i}'] = text_highlighter(st.session_state.lista[i])
           
          
          col1, col2 = st.columns([0.07,1])
          
          with col2:
            if st.button("Siguiente", type = "primary"):
              with st.spinner("Procesando la información... ⌛"):
                st.session_state.anotaciones_finales = []
                st.session_state.transcripcion_final = ''
                for i in range(len(st.session_state.lista)):
                  if st.session_state[f'on_{i}']:
                    st.session_state.transcripcion_final += st.session_state.lista[i] + '\n\n'
                    st.session_state.anotaciones_finales.append( st.session_state[f'anotaciones_{i}'])
                st.rerun()
                  
          with col1:
            if st.button("Atrás", type = "primary", key = "atras"):
              del st.session_state['topics']
              st.rerun()
      

    if 'transcripcion_final' in st.session_state and not 'noticia_generada' in st.session_state and 'inicio' in st.session_state:
        st.write("# Resumen de la información recopilada")
      
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id=1, title="Audio", description = ''),
            stx.TabBarItemData(id=2, title="Contexto", description = ''),
            stx.TabBarItemData(id=3, title="Transcripción", description = ''),
            stx.TabBarItemData(id=4, title="Selección/descarte", description = ''),
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
          st.info("Aquí tienes la transcripción del audio completa")
          st.write(st.session_state.transcription2, unsafe_allow_html=True)

        if chosen_id == "4":
          st.info("Aquí tienes los párrafos descartados (aparecen desmarcados) y los momentos de mayor relevancia en las declaraciones.")
            
          for i in range(len(st.session_state.lista)):
              on = st.toggle('', key=i, value = st.session_state[f'on_{i}'])
              st.write(generar_html_con_destacados(st.session_state.lista[i], st.session_state[f'anotaciones_{i}']), unsafe_allow_html=True)

        col1, col2 = st.columns([0.07,1])
        
        with col2:
          if st.button("Generar noticia", type = "primary"):
            with st.spinner("Generando noticia... ⌛"):
  
              st.session_state.noticia_generada = generar_noticia(st.session_state.new_dialogos, st.session_state.anotaciones, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
              st.rerun()
        with col1:    
          if st.button("Atrás", type = "primary", key = "atras"):
            del st.session_state['anotaciones']
            st.rerun()

    if 'noticia_generada' in st.session_state and 'inicio' in st.session_state:
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
            st.info("Podrás editar la noticia directamente aquí para adaptarla a tu gusto. Si lo prefieres, puedes pedirle a la IA que lo haga por ti. Dale click a chatear")
            
            st.session_state.noticia_generada = st.text_area(label = ":blue[Noticia generada]", value = st.session_state.noticia_generada)

            with st.expander('Chatea con una IA y ayúdate'):
                if len(st.session_state.messages) == 1:
                    st.session_state.messages.append({"role": "system", "content": f"Esta es la noticia del usuario: {st.session_state.noticia_generada}"})
                
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
                                
                        response = openai.ChatCompletion.create(
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



