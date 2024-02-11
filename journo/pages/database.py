import streamlit as st
from journo.utils.modules import *
import pandas as pd
import extra_streamlit_components as stx

def show_database():
    
    st.write('## 📊 Tus noticias')
    if st.session_state.database.isna().all().all():
        st.info('Actualmente no has generado ninguna noticia. Adelante, prueba Journo y guarda tu primera noticia asistida por IA')
        
        if st.button("Crear nueva noticia", type = "primary", key = "start"):
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
            
    return
