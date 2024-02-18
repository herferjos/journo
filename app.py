import streamlit as st
from journo.pages.journo import show_journo
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import *
import time


st.set_page_config(page_title="Journo", page_icon="🗞️") #layout="wide"


import streamlit as st

# Definir el estilo del botón de Google
google_button_style = """
    <style>
    .google-button {
        background-color: #ffffff;
        color: #000000;
        padding: 10px 20px;
        border: 2px solid #cccccc;
        border-radius: 5px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s ease;
        text-decoration: none;
    }
    .google-button:hover {
        background-color: #f2f2f2;
    }
    .google-icon {
        margin-right: 8px;
        fill: #000000;
        width: 24px;
        height: 24px;
    }
    </style>
"""

# Mostrar el botón de Google
st.markdown(google_button_style, unsafe_allow_html=True)

st.markdown(
    """
    <a href="http://www.google.com" class="google-button">
        <span class="google-icon">
            <svg viewBox="0 0 24 24" class="google-icon">
                <path fill="#000000" d="M21.39 11.57h-8.02v2.86h4.6c-.19 1.27-1.05 3.08-2.86 4.09l-.13.08c-1.64 1.02-3.71 1.04-5.36 0l-.13-.08c-1.8-1.02-2.67-2.82-2.86-4.09H2.63v-2.86h4.08c-.38-1.1-.59-2.27-.59-3.48 0-1.21.21-2.38.59-3.48H2.63v-2.86h4.62c.2-1.27 1.06-3.07 2.86-4.09l.13-.08c1.65-1.02 3.72-1.04 5.36 0l.13.08c1.8 1.02 2.67 2.82 2.86 4.09h4.62v2.86h-4.08c.38 1.1.59 2.27.59 3.48 0 1.21-.21 2.38-.59 3.48h4.08v2.86z"></path>
            </svg>
        </span>
        Ir a Google
    </a>
    """,
    unsafe_allow_html=True
)


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
    
    show_journo()


#except Exception as e:
    #st.write(e)
    #st.error('Ha habido un error en Journo. La página será recargada en 3 segundos, si el error persiste contácta con el equipo de atención al cliente de Journo')
    #time.sleep(3)
    #st.rerun()
