import asyncio
from typing import Optional

import jwt
import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token

testing_mode = st.secrets.get("testing_mode", False)


client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_url = (
    st.secrets["redirect_url_test"] if testing_mode else st.secrets["redirect_url"]
)

client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)


def decode_user(token: str):
    """
    :param token: jwt token
    :return:
    """
    decoded_data = jwt.decode(jwt=token, options={"verify_signature": False})

    return decoded_data


async def get_authorization_url(client: GoogleOAuth2, redirect_url: str) -> str:
    authorization_url = await client.get_authorization_url(
        redirect_url,
        scope=["email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


def markdown_button(url: str, text: Optional[str] = None, color="#FD504D", sidebar: bool = True):
    if sidebar:
        st.sidebar.link_button(label=text, url=url, help=None, type="primary", disabled=False, use_container_width=False)
    else:
        # Lee el contenido del archivo SVG
        with open("files/google.svg", "r") as file:
            svg_content = file.read()
        
        # Modificar el tamaño del SVG
        svg_content = svg_content.replace('<svg ', '<svg width="35" height="35" ')
        
        # Muestra el estilo del botón de Google
        st.markdown("""
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
                text-decoration: none;
            }
            .google-icon {
                margin-right: 10px;
            }
            .google-button:hover {
                border-color: #000000;
            }
            .google-text {
                margin-left: 10px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Muestra el botón de Google con el SVG cargado
        st.markdown(
            f"""
            <a href="http://www.google.com" class="google-button">
                <span class="google-icon">
                    {svg_content}
                </span>
                Iniciar Sesión
            </a>
            """,
            unsafe_allow_html=True
        )


async def get_access_token(
    client: GoogleOAuth2, redirect_url: str, code: str
) -> OAuth2Token:
    token = await client.get_access_token(code, redirect_url)
    return token


def get_access_token_from_query_params(
     client: GoogleOAuth2, redirect_url: str
 ) -> OAuth2Token:
     query_params = st.experimental_get_query_params()
     code = query_params["code"][0]
     token = asyncio.run(
         get_access_token(client=client, redirect_url=redirect_url, code=code)
     )
     # Clear query params
     st.experimental_set_query_params()
     return token


def show_login_button(
    text: Optional[str] = "Login with Google", color="#FD504D", sidebar: bool = True
):
    authorization_url = asyncio.run(
        get_authorization_url(client=client, redirect_url=redirect_url)
    )
    markdown_button(authorization_url, text, color, sidebar)


def get_logged_in_user_email() -> Optional[str]:
    if "email" in st.session_state:
        return st.session_state.email

    try:
        token_from_params = get_access_token_from_query_params(client, redirect_url)
    except KeyError:
        return None

    user_info = decode_user(token=token_from_params["id_token"])

    st.session_state["email"] = user_info["email"]

    return user_info["email"]
