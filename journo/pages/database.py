import streamlit as st
from journo.utils.modules import *
import pandas as pd
import extra_streamlit_components as stx

def show_database():
    if 'database' not in st.session_state:
      st.session_state.sheet = load_sheet()
      try:
        st.session_state.database = st.session_state.sheet.read(worksheet=st.session_state.email)
      except:
        nuevo_df = pd.DataFrame({'Transcripción': [None]*5, 'Cargo': [None]*5, 'Nombre': [None]*5, 'Tema': [None]*5, 'Donde': [None]*5, 'Cuando': [None]*5, 'Transcripción filtrada': [None]*5, 'Anotaciones': [None]*5, 'Noticia': [None]*5, 'Sesion': [None]*5}, index=range(5))
        st.session_state.sheet.create(worksheet=st.session_state.email,data=nuevo_df)
        st.session_state.database = st.session_state.sheet.read(worksheet=st.session_state.email)
    
    
    st.write('## 📊 Tus noticias')
    if st.session_state.database.isna().all().all():
        st.info('Actualmente no has generado ninguna noticia. Adelante, prueba Journo y guarda tu primera noticia asistida por IA')
        
        if st.button("Crear nueva noticia", type = "primary", key = "start"):
            reset_variables()
    else:
        st.info('Aquí tienes las noticias que has generado con el asistente Journo. Puedes cargar una noticia directamente, explorar la información o crear una nueva.')
        df_copia = st.session_state.database.copy()
        df_copia = df_copia.iloc[:, :-1]
        dataframetipo(df_copia)

        
        st.download_button(
            label='Descargar noticias',
            data=df_copia.to_csv(index=False),
            file_name='noticias_journo.csv',
            mime='text/csv',
            type = 'primary'
        )
                
        if 'noticia_generada' in st.session_state and st.session_state.noticia_cargada == True:
            
            st.success(f"👍🏻 Noticia cargada correctamente. Puedes ir a la sección 'Journo' para continuar modificando la noticia")
            
            phase = stx.stepper_bar(steps=["Contexto", "Transcripción", "Selección/descarte", "Noticia generada"])
    
            if phase == 0:
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
    
            if phase == 1:
              st.info("Aquí tienes la transcripción del audio completa")
              st.write(st.session_state.transcription2, unsafe_allow_html=True)
    
            if phase == 2:
              st.info("Aquí tienes los párrafos descartados (aparecen desmarcados) y los momentos de mayor relevancia en las declaraciones.")
                
              for i in range(len(st.session_state.lista)):
                  on = st.toggle('', key=i, value = st.session_state[f'on_{i}'])
                  frases = []
                  for item in st.session_state[f'anotaciones_{i}']:
                      for x in item:
                        frases.append(x['label'])
                  st.write(generar_html_con_destacados(st.session_state.lista[i], frases), unsafe_allow_html=True)
    
            if phase == 3:
                st.info('Esta es la noticia generada por Journo')
                st.write(st.session_state.noticia_generada)
            
    return
