import streamlit as st
from journo.utils.google_auth import get_logged_in_user_email, show_login_button
from journo.utils.stripe_auth import is_active_subscriber, redirect_button
from journo.pages.inicio import show_inicio
from journo.utils.modules import img_to_html

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
        st.markdown(
            "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 180, 180) + "</p>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Una nueva forma de hacer periodismo</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        show_login_button(
            text=login_button_text, color=login_button_color, sidebar=login_sidebar
        )
        show_inicio()
        st.stop()
    if payment_provider == "stripe":
        if 'subscriptions' in st.session_state:
            is_subscriber = user_email and len(st.session_state.subscriptions)>0
        else:
            is_subscriber = user_email and is_active_subscriber(user_email)
    else:
        raise ValueError("payment_provider must be 'stripe'")

    if not is_subscriber:
        st.markdown(
            "<p style='text-align: center; color: grey;'>" + img_to_html('files/logo-removebg-preview.png', 180, 180) + "</p>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Una nueva forma de hacer periodismo</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Lee el contenido del archivo SVG
        with open("files/pago.svg", "r") as file:
            svg_content = file.read()
        
        # Modificar el tamaño del SVG
        svg_content = svg_content.replace('<svg ', '<svg width="35" height="35" ')
        
        # Muestra el estilo del botón de Google
        st.markdown("""
            <style>
            .pago-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 10vh; /* Ajusta la altura según necesites */
            }
            .pago-button {
                background-color: #ffffff;
                color: #000000;
                padding: 10px 20px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
            }
            .pago-icon {
                margin-right: 10px;
            }
            .pago-button:hover {
                border-color: #000000;
            }
            .pago-text {
                margin-left: 10px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Muestra el botón de Google con el SVG cargado centrado en la página
        st.markdown(
            f"""
            <div class="pago-container">
                <a href={url} class="pago-button">
                    <span class="pago-icon">
                        {svg_content}
                    </span>
                    Suscríbete
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        show_inicio()
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
