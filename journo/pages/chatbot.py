import streamlit as st
from openai import OpenAI

# Configuración de la clave API de OpenAI
openai_client = OpenAI(api_key=st.secrets.openai_api)

def show_bot():
    st.write('## 🤖 Chatea con Journo')
    st.info('Puedes chatear con una IA para ayudarte a formatear la noticia cómo desees. Importa fácilmente la noticia generada haciendo click en el siguiente botón:')
    
    if 'noticia_editada' in st.session_state:
        a, b, c = st.columns([0.5, 0.3, 0.5])
        
        with b:
            if st.button("Copiar noticia ", type = "primary"):
                st.session_state.messages.append({"role": "system", "content": f"Esta es la noticia del usuario: {st.session_state.noticia_editada}"})
                st.rerun()
    else:
        st.warning('Oh...! Parece que aún no has generado ninguna noticia. Ve a la pestaña de "Crea tu noticia" y regresa cuando hayas acabado')
        
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
            model="gpt-3.5-turbo-0125",
            messages=st.session_state.messages,
            temperature = 0,
            stream = True
            )
            
            message_placeholder = st.empty()
            full_response = ""
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

                      
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    return
