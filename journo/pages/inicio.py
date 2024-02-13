import streamlit as st
from journo.utils.modules import generar_html_con_destacados
import extra_streamlit_components as stx

def show_inicio():
    st.write("## 🤔 ¿Qué es Journo?")
    st.markdown(
        """
        <h4>Journo es un asistente de redacción con el que podrás:</h4>
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
     
    st.link_button("Ver video tutorial", "https://streamlit.io/gallery", type = "primary")
    
    st.write("---")
        
    st.write("## ¿Cómo funciona Journo?")
    
    with open('files/demo.txt', "r",encoding="utf-8") as archivo:
        content = archivo.read()
  
    exec(content)
  
    phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Destacados", "Noticia"])
  
    if phase == 0:
        st.write("### 1) Cargar o subir audio")
        st.info("En esta primera etapa deberemos aportar al sistema el audio a transcribir. Podemos subir un audio ya grabado o grabarlo directamente desde la app")
        try:
            st.audio('files/audio.mp3', format="audio/mpeg")
        except:
            st.error("Error al cargar el audio. Recuerda que si cargas una noticia de la base de datos, no está disponible el audio para escuchar")
    
    if phase == 1:
        st.write("### 2) Describir el contexto de las declaraciones")
        st.info("Ahora deberemos de aportar información a la Inteligencia Artificial para que sepa en qué contexto se han producido las declaraciones que has aportado")

        X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'Entrenador Real Madrid', value = st.session_state.X_demo)
        Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", placeholder = 'Ancelotti', value = st.session_state.Y_demo)
        A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'Rueda de Prensa', value = st.session_state.A_demo)
        B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", placeholder = 'Martes 12', value = st.session_state.B_demo)
        Z = st.text_area(":blue[Añade más contexto]", value = st.session_state.Z_demo)
            
    if phase == 2:
        st.write("### 3) Transcripción de las declaraciones")
        st.info("Journo entonces nos generará la transcripción completa del audio.")

        st.write(st.session_state.transcription2_demo, unsafe_allow_html=True)
    
        
    if phase == 3:
      st.write("### 4) Selección/descarte de temas mencionados")
      st.info("En este paso tendrás que descartar los párrafos que no te interesen (aparecerán desmarcados) y subrayar los momentos de mayor relevancia en las declaraciones.")
      for i in range(len(st.session_state.lista_demo)):
          frases = []
          for item in st.session_state[f'anotaciones_demo_{i}']:
              for x in item:
                frases.append(x['label'])
          st.write(generar_html_con_destacados(st.session_state.lista_demo[i], frases), unsafe_allow_html=True)
          
    if phase == 4:
        st.info('Finalmente, Journo nos dará una primera versión de nuestra noticia a partir del audio y la información proporcionada. Posteriormente podremos editarla manualmente o con ayuda de Journo.')
        st.write(st.session_state.noticia_generada_demo)
    return 
