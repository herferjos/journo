import streamlit as st
from openai import OpenAI

# Configuración de la clave API de OpenAI
openai_client = OpenAI(api_key=st.secrets.openai_api)

def show_bot():
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
    
    
    if prompt := st.chat_input("Pregunta lo que quieras"):
        
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
    return
