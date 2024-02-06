import streamlit as st
from journo.google_auth import get_logged_in_user_email, show_login_button
from journo.stripe_auth import is_active_subscriber, redirect_button

payment_provider = st.secrets.get("payment_provider", "stripe")


def add_auth(
    required: bool = True,
    login_button_text: str = "Inicia sesión con Google",
    login_button_color: str = "#FD504D",
    login_sidebar: bool = True,

):
    if required:
        require_auth(
            login_button_text=login_button_text,
            login_sidebar=login_sidebar,
            login_button_color=login_button_color,
        )
    else:
        optional_auth(
            login_button_text=login_button_text,
            login_sidebar=login_sidebar,
            login_button_color=login_button_color,
        )


def require_auth(
    login_button_text: str = "Login with Google",
    login_button_color: str = "#FD504D",
    login_sidebar: bool = True,
):
    user_email = get_logged_in_user_email()

    if not user_email:
        st.info("Debes iniciar sesión con tu cuenta de google")
        show_login_button(
            text=login_button_text, color=login_button_color, sidebar=login_sidebar
        )
        st.stop()
    if payment_provider == "stripe":
        is_subscriber = user_email and is_active_subscriber(user_email)
    else:
        raise ValueError("payment_provider must be 'stripe'")

    if not is_subscriber:
        st.warning("Debes suscribirte al plan mensual para hacer uso de la app")
        redirect_button(
            text="¡Suscríbete!",
            customer_email=user_email,
            payment_provider=payment_provider,
        )
        st.session_state.user_subscribed = False
        st.stop()
    elif is_subscriber:
        st.session_state.user_subscribed = True

    # if st.button("Cerrar sesión", type="primary"):
    #     del st.session_state.email
    #     del st.session_state.user_subscribed
    #     st.rerun()


def optional_auth(
    login_button_text: str = "Login with Google",
    login_button_color: str = "#FD504D",
    login_sidebar: bool = True,
):
    user_email = get_logged_in_user_email()
    if payment_provider == "stripe":
        is_subscriber = user_email and is_active_subscriber(user_email)
    else:
        raise ValueError("payment_provider must be 'stripe'")

    if not user_email:
        show_login_button(
            text=login_button_text, color=login_button_color, sidebar=login_sidebar
        )
        st.session_state.email = ""
        st.markdown("")

    if not is_subscriber:
        redirect_button(
            text="¡Suscríbete!", customer_email="", payment_provider=payment_provider
        )
        st.markdown("")
        st.session_state.user_subscribed = False

    elif is_subscriber:
        st.session_state.user_subscribed = True

    if st.session_state.email != "":
        if st.button("Cerrar sesión", type="primary"):
            del st.session_state.email
            del st.session_state.user_subscribed
            st.rerun()
