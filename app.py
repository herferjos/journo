import streamlit as st
from journo.pages.journo import show_journo
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import *
import time


st.set_page_config(page_title="Journo", page_icon="🗞️") #layout="wide"



import streamlit as st

st.markdown(
    """
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
    .google-button a {
        color: #000000;
        text-decoration: none;
    }
    .google-icon {
        margin-right: 8px;
        fill: #000000;
        width: 24px;
        height: 24px;
    }
    </style>
    """
    , unsafe_allow_html=True
)

st.markdown(
    """
    <a href="http://www.google.com" class="google-button">
        <span class="google-icon">
            <svg viewBox="0 0 24 24" class="google-icon">
                <path fill="#000000" d="M6 3c3.309 0 5.977 2.691 5.977 6 0 2.263-1.17 4.204-2.936 5.329l-.023.02 1.116 1.484c1.283-1.037 3.448-2.422 3.448-4.838C13.582 5.691 10.914 3 7.605 3c-1.17 0-2.238.445-3.054 1.18l1.346 1.602C5.075 5.383 6 4.276 6 3zm9 4a4.482 4.482 0 0 1-1.027 2.861c-.241.357-.634.872-1.109 1.398-1.256 1.256-2.654 2.665-2.654 5.188h2c0-1.635.724-2.635 1.557-3.468l1.857-1.857c.459-.459 1.248-.459 1.707 0 .236.236.365.547.365.854 0 .307-.129.618-.365.854l-1.428 1.428 1.442 1.442c1.318-1.318 2.901-2.891 2.901-5.824 0-3.309-2.691-6-6-6z"></path>
            </svg>
        </span>
        <span>Ir a Google</span>
    </a>
    """
    , unsafe_allow_html=True
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
