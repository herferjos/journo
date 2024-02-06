from openai import OpenAI
import streamlit as st
import tempfile
import os

# Configuración de la clave API de OpenAI
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Credenciales de acceso permitidas
usuarios_permitidos = {
    "dpelagu": "Dpelagu.journoAI",
    "jorgepedrosa": "Jorgepedrosa.journoAI",
    "luciavillalba": "Luciavillalba.journoAI",
    "mariasanchez" : "Mariasanchez.journoAI",
    "albarosado" : "Albarosado.journoAI",
    "juanromera" : "Juanromera.journoAI",
    "anamontañez" : "Anamontañez.journoAI",
    "carlosguerrero" : "Carlosguerrero.journoAI",
    "daninuñez" : "Daninuñez.journoAI",
    "marmanrique" : "Marmanrique.journoAI",
    "joseluisherfer" : "Joseluisherfer.journoAI",
    "borjagutierrez" : "Borjagutierrez.journoAI",
    "javipachon" : "Javipachon.journoAI",
    "samuruiz" : "Samuruiz.journoAI",
    "martapachon" : "Martapachon.journoAI",
    "josemrodriguez" : "Josemrodriguez.journoAI",
    "analopez" : "Analopez.journoAI",
    "valeriaveiga" : "Valeriaveiga.journoAI",
    "alvarorafaelvl" : "Alvarorafaelvl.journoAI",
    # Puedes añadir más usuarios aquí
}

# Verificar las credenciales del usuario
def verificar_credenciales(nombre_usuario, contraseña):
    return usuarios_permitidos.get(nombre_usuario) == contraseña

# Título de la aplicación
st.title("Journo.AI: tu asistente periodístico de inteligencia artificial")

# Funciones auxiliares
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript_response = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        # Accede al texto de la transcripción directamente desde el objeto de respuesta
        return transcript_response.text

def generar_noticia(transcripcion, X, Y, Z, A, B):
    my_texto = "Vas a actuar como un asistente de inteligencia artificial para periodistas, cuya tarea será redactar un artículo periodístico informativo de la mayor longitud posible utilizando la cantidad máxima de tokens disponibles a partir de declaraciones proporcionadas por un individuo. Te proporcionaré cinco variables clave: X (cargo del individuo), Y (nombre completo del individuo), Z (tema más relevante que protagonizará los primeros párrafos), A (dónde ha dicho las declaraciones) y B (cuándo ha dicho las declaraciones); además de la propias declaraciones. Aquí te detallo el enfoque que debes seguir al redactar el artículo. Considera estas indicaciones paso a paso para asegurarnos de tener la respuesta correcta: 1. Ordena el artículo utilizando la estructura periodística clásica de pirámide invertida, de mayor a menor importancia de los temas tratados. El primer párrafo debe explicar quién ha dicho qué (variable Z), cuándo (B) y dónde (A). Inicia con las declaraciones más directamente relacionadas con Z, que deben situarse en los primeros párrafos. A medida que avances, presenta la información de manera descendente en términos de su relevancia y relación con Z, hasta llegar a las declaraciones menos relevantes y menos relacionadas con el tema principal. 2. Utiliza citas directas entre comillas para presentar las frases y razonamientos del individuo, pero atribúyelas siempre a su autor en el párrafo mediante expresiones como “ha dicho”, “ha indicado” o “ha manifestado”. Mantén una distancia periodística de imparcialidad en todo momento. Tu trabajo es informar de la forma más aséptica posible y citar las declaraciones más valorativas y calificativas entre comillas. No añadas ninguna interpretación o valoración sin entrecomillar a las declaraciones. 3. Utiliza ÚNICAMENTE el pretérito perfecto compuesto durante todo el texto para referirte a las acciones del orador: “ha dicho”, “ha manifestado”, “ha indicado”... Evita en todo momento el uso del pretérito perfecto simple. 4. No añadas información que no esté presente en las declaraciones proporcionadas. El artículo debe basarse únicamente en dichas declaraciones, por lo que debes trabajar dentro de los límites de la información proporcionada. 5. Evita repeticiones tanto de conceptos como de palabras en todo el artículo, asegurándote de mantener una fluidez y legibilidad óptimas. Utiliza sinónimos y expresiones diferentes para mantener la diversidad lingüística"
    messages = [
        {"role": "user", "content": f"{my_texto} \n X: {X}, Y: {Y}, Z: {Z}, A: {A}, B: {B}. Declaraciones: {transcripcion}."}
    ]

    response_noticia = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        max_tokens=3500,
        temperature=0
    )

    return response_noticia.choices[0].message.content

# Inicio de sesión
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Muestra las cajas de entrada solo si el usuario no está autenticado
if not st.session_state['autenticado']:
    nombre_usuario = st.text_input("Nombre de usuario")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if verificar_credenciales(nombre_usuario, contraseña):
            st.session_state['autenticado'] = True
            st.success("¡Autenticado con éxito!")
        else:
            st.error("Usuario o contraseña incorrectos")

# Si el usuario está autenticado, entonces muestra el resto de la aplicación
if st.session_state['autenticado']:
    # Todo el código que sigue debe estar indentado para que se ejecute después de la autenticación
    st.markdown("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia. Asegúrate de que sea un archivo en formato MP3.")
    # Control de flujos con session state
    if "stage" not in st.session_state:
        st.session_state.stage = "upload"

    if st.session_state.stage == "upload":
        uploaded_file = st.file_uploader("Cargar archivo de audio", type=['mp3'])

        if uploaded_file is not None:
            st.session_state.stage = "loading_transcription"
            st.text("Cargando...")

    # This stage happens in the background
    if st.session_state.stage == "loading_transcription":
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.transcription = transcribe_audio(temp_path)
        os.remove(temp_path)
        st.session_state.stage = "questions"

    if st.session_state.stage == "questions":
        st.markdown("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
        X = st.text_input("¿Cuál es el cargo de la persona que habla?")
        Y = st.text_input("¿Cuál es el nombre de la persona que habla?")
        Z = st.text_input("¿Cuál es el tema más relevante del que ha hablado?")
        A = st.text_input("¿Dónde ha dicho las declaraciones?")
        B = st.text_input("¿Cuándo ha dicho las declaraciones?")

        if st.button("Generar Noticia"):
            st.session_state.stage = "loading_news"

    if st.session_state.stage == "loading_news":
        st.text("Cargando tu noticia...\n\n¡Recuerda revisarla antes de publicar!\n\nEste proceso puede tardar unos minutos")
        st.session_state.noticia_generada = generar_noticia(st.session_state.transcription, X, Y, Z, A, B)
        st.session_state.stage = "result"

    if st.session_state.stage == "result":
        st.subheader("¡Listo! Aquí tienes tu noticia:")
        st.write(st.session_state.noticia_generada)
