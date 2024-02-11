import streamlit as st
from journo.pages.inicio import show_inicio
from journo.pages.journo import show_journo
from journo.pages.chatbot import show_bot
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import img_to_html, load_database
from streamlit_option_menu import option_menu
import time


st.set_page_config(page_title="Journo", page_icon="🗞️") #layout="wide"

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


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres un asistente virtual de Journo, una webapp de asistencia con IA para periodistas y ahora podrás comunicarte con los usuarios de Journo. Trata de ayudar a los usuarios con sus peticiones e instrucciones para dar forma y estilo a una noticia periodística. Razona siempre paso por paso cualquier petición."}]

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


st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)


import streamlit as st

# Define el estilo CSS para el subrayado
css = """
<style>
.underline {
    position: relative;
    text-decoration: none;
}

.underline::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 100%;
    height: 2px;
    background-color: blue; /* Puedes cambiar el color del subrayado aquí */
}
</style>
"""

# Define el script JavaScript para capturar la selección del usuario
javascript = """
<script type="text/javascript">
document.addEventListener("mouseup", function() {
    var selection = window.getSelection().toString();
    if (selection !== "") {
        // Envía la selección al backend de Streamlit
        Shiny.setInputValue('selected_text', selection);
    }
});
</script>
"""

# Agrega el estilo CSS al Streamlit
st.markdown(css, unsafe_allow_html=True)

# Agrega el script JavaScript al Streamlit
st.markdown(javascript, unsafe_allow_html=True)

# Título de la aplicación
st.title("Subrayar Texto")

# Entrada de texto
text_input = st.text_area("Escribe o pega tu texto aquí:")

# Muestra el texto subrayado con la clase CSS "underline"
subrayado = f'<div class="underline">{text_input}</div>'
st.markdown(subrayado, unsafe_allow_html=True)

# Botón para guardar el texto subrayado
if st.button("Guardar Texto Subrayado"):
    selected_text = st.session_state.selected_text
    if selected_text:
        st.success("Texto subrayado guardado exitosamente!")
        st.write("Texto subrayado:", selected_text)
    else:
        st.warning("Por favor, selecciona un texto subrayado antes de guardar.")







add_auth(required=True, login_sidebar = False)

load_database()

with st.sidebar:
    st.session_state.selected = option_menu("", ["Crea tu noticia", "Chatbot", "¿Qué es Journo?"], 
        icons=['pencil-fill', 'robot', 'house'], menu_icon="", default_index=0)

if 'email' in st.session_state and st.session_state.user_subscribed == True: 
    
    if st.session_state.selected == 'Crea tu noticia':
        show_journo()

    if st.session_state.selected == 'Chatbot':
        show_bot()
    
    if st.session_state.selected == '¿Qué es Journo?':
        show_inicio()


"""except:
    st.error('Ha habido un error en Journo. La página será recargada en 5 segundos, si el error persiste contácta con hola@journo-ai.com')
    time.sleep(5)
    st.rerun()"""
        
    
