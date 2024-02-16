import streamlit as st
from journo.pages.journo import show_journo
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import *
import time


st.set_page_config(page_title="Journo", page_icon="🗞️") #layout="wide"


try:
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
 
        clicked = clickable_logo():
        if clicked == 0:
            reset_variables()
            clicked = None
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
    
        st.write('')
        
        c,d = st.columns(2)
    
        with c:
            if st.button("Nueva noticia", type = "primary", key = "restart"):
                reset_variables()
        with d:
            if st.button("Guardar progreso", type = "primary"):
                guardar_info()
                st.rerun()
            
    
    if 'email' in st.session_state and st.session_state.user_subscribed == True: 
        
        show_journo()


except Exception as e:
    st.error('Ha habido un error en Journo. La página será recargada en 5 segundos, si el error persiste contácta con el equipo de atención al cliente de Journo')
    time.sleep(5)
    st.rerun()
