import streamlit as st
from journo.google_auth import get_logged_in_user_email, show_login_button
from journo.stripe_auth import is_active_subscriber, redirect_button
from journo.modules import show_inicio, img_to_html

payment_provider = st.secrets.get("payment_provider", "stripe")


def auth():
    user_email = get_logged_in_user_email()

    if not user_email:
        cabecera()
        
        show_login_button()
        
        #show_inicio()
        st.stop()
        
    if 'subscriptions' in st.session_state:
        is_subscriber = user_email and len(st.session_state.subscriptions)>0
    else:
        is_subscriber = user_email and is_active_subscriber(user_email)

    if not is_subscriber:
        cabecera()
        
        redirect_button(customer_email=user_email)
        st.write(' ')
        st.markdown("""<div style='text-align: center;'> <h5>Y si te convence, suscríbete por 9,90€ al mes</h5></div>""",unsafe_allow_html=True)
        
        show_inicio()
        
        st.session_state.user_subscribed = False
        st.stop()
    elif is_subscriber:
        st.session_state.user_subscribed = True

def cabecera():
    st.markdown("<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 200, 200) + "</p>", unsafe_allow_html=True)
    
    st.markdown("""<div style='text-align: center;'> <h5>Tu copiloto periodístico</h5></div>""",unsafe_allow_html=True)

    return
    
