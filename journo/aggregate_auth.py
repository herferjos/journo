import streamlit as st
from journo.google_auth import get_logged_in_user_email, show_login_button
from journo.stripe_auth import is_active_subscriber, redirect_button
from journo.modules import *

payment_provider = st.secrets.get("payment_provider", "stripe")


def auth():
    user_email = get_logged_in_user_email()

    if not user_email:
        
        xf, xd = st.columns([2,1])
        with xd:
            cabecera()
            show_login_button()
        with xf:
            with open("files/video_base64.txt", "r") as input_file:
                video_base64 = input_file.read()
        
            st.write(f'''
                <div style="display: flex; justify-content: center;">
                    <video width="1000" height="600" controls autoplay loop>
                        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    </video>
                </div>
            ''', unsafe_allow_html=True)

        
        show_inicio()
        
        st.stop()
        
    if 'subscriptions' in st.session_state:
        is_subscriber = user_email and len(st.session_state.subscriptions)>0
    else:
        is_subscriber = user_email and is_active_subscriber(user_email)

    if not is_subscriber:
        cabecera()
        
        redirect_button(customer_email=user_email)
        st.write(' ')
        st.markdown("""<div style='text-align: center;'> <h5>And if you are convinced, subscribe for 9,90€ per month</h5></div>""",unsafe_allow_html=True)
        
        #show_inicio()
        
        st.session_state.user_subscribed = False
        st.stop()
    elif is_subscriber:
        st.session_state.user_subscribed = True

def cabecera():
    st.markdown('#')
    st.markdown('#')
    st.markdown('#')
    st.markdown("<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 200, 200) + "</p>", unsafe_allow_html=True)

    st.markdown("""<div style='text-align: center;'> <h5>Your journalistic copilot</h5></div>""",unsafe_allow_html=True)

    return
    
