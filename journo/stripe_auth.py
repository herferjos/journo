import streamlit as st
import stripe
import urllib.parse


def get_api_key() -> str:
    testing_mode = st.secrets.get("testing_mode", False)
    return (
        st.secrets["stripe_api_key_test"]
        if testing_mode
        else st.secrets["stripe_api_key"]
    )


def redirect_button(
    customer_email: str,
    color="#FD504D",
    payment_provider: str = "stripe",
):
    testing_mode = st.secrets.get("testing_mode", False)
    encoded_email = urllib.parse.quote(customer_email)
    if payment_provider == "stripe":
        stripe.api_key = get_api_key()
        stripe_link = (
            st.secrets["stripe_link_test"]
            if testing_mode
            else st.secrets["stripe_link"]
        )
        button_url = f"{stripe_link}?prefilled_email={encoded_email}"
    else:
        raise ValueError("payment_provider must be 'stripe' or 'bmac'")

    # Lee el contenido del archivo SVG
    with open("files/pago.svg", "r") as file:
        svg_content = file.read()
    
    # Modificar el tamaño del SVG
    svg_content = svg_content.replace('<svg ', '<svg width="50" height="50" ')
    
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
            padding: 15px 15px;
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
            <a href={button_url} class="pago-button">
                <span class="pago-icon">
                </span>
                🥳  Pruébalo gratis
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


def is_active_subscriber(email: str) -> bool:
    stripe.api_key = get_api_key()
    customers = stripe.Customer.list(email=email)
    try:
        customer = customers.data[0]
    except IndexError:
        return False

    subscriptions = stripe.Subscription.list(customer=customer["id"])
    st.session_state.subscriptions = subscriptions

    return len(subscriptions) > 0
