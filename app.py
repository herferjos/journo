import streamlit as st
from journo.pages.inicio import show_inicio
from journo.pages.database import show_database
from journo.pages.journo import show_journo
from journo.utils.aggregate_auth import add_auth
from journo.utils.modules import img_to_html
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Journo", page_icon="🗞️", layout="wide")

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

if 'guardado' not in st.session_state:
    st.session_state.guardado = False
    
if 'noticia_cargada' not in st.session_state:
    st.session_state.noticia_cargada = False


st.markdown("""
  <style>
  div.stLinkButton {text-align:center}
  </style>""", unsafe_allow_html=True)

x,y,z = st.columns(3)
with y:
  add_auth(required=True, login_sidebar = False)


with st.sidebar:
    st.session_state.selected = option_menu("Menu", ["Inicio", "Base de datos", "Journo", "Chatbot"], 
        icons=['house', 'clipboard-data', 'pencil-fill', 'robot'], menu_icon="cast", default_index=0)

if 'email' in st.session_state and st.session_state.user_subscribed == True: 
    
    if st.session_state.selected == 'Inicio':
        show_inicio()

    if st.session_state.selected == 'Base de datos':
        show_database()
        
    if st.session_state.selected == 'Journo':
        show_journo()

    if st.session_state.selected == 'Chatbot':
        st.write('## 🤖 Chatea con una IA y ayúdate')
        st.info('Puedes chatear con una IA para ayudarte a formatear la noticia cómo desees. Además, podrás importar fácilmente la noticia de la sección "Noticia generada" haciendo click en el siguiente botón:')
        if st.button("Copiar noticia ", type = "primary"):
            st.session_state.messages.append({"role": "system", "content": f"Esta es la noticia del usuario: {st.session_state.noticia_generada}"})
            st.rerun()
        
        for message in st.session_state.messages:
            if message["role"] == "system":
                pass
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        
        if prompt := st.chat_input("Pregunta lo que quieras")
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                        
                response = openai_client.chat.completions.create(
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


        
    
