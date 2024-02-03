from openai import OpenAI
import streamlit as st
import tempfile
import os
from io import BytesIO
import json
from pydub import AudioSegment
import concurrent.futures
import io
import base64
from faster_whisper import WhisperModel
import base64
from pathlib import Path
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_gsheets import GSheetsConnection

# Configuración de la clave API de OpenAI
openai_client = OpenAI(api_key=st.secrets.openai_api)

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
    "" : ""
}

def reset_variables():
    st.session_state.inicio = True
    
    del st.session_state.mp3_audio_path
    del st.session_state.X
    del st.session_state.Y
    del st.session_state.Z
    del st.session_state.A
    del st.session_state.B
    del st.session_state.transcription2 
    del st.session_state.lista_transcription 
    del st.session_state.topics
    del st.session_state.dialogos_topics
    
    st.rerun()

def cargar_noticia(df):
    st.session_state.transcription2 = df.iloc[0, 0]
    st.session_state.X = df.iloc[0, 1]
    st.session_state.Y = df.iloc[0, 2]
    st.session_state.Z = df.iloc[0, 3]
    st.session_state.A = df.iloc[0, 4]
    st.session_state.B = df.iloc[0, 5]
    
    
        

@st.cache_resource(show_spinner = False)
def load_sheet():
    return st.experimental_connection("gsheets", type=GSheetsConnection)

def dataframetipo(df):
    # Eliminar filas con todas las celdas vacías
    df = df.dropna(axis=0, how='all')
    
    # Eliminar columnas con todas las celdas vacías
    df = df.dropna(axis=1, how='all')
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode='single', use_checkbox=True)
    gd.configure_auto_height(autoHeight=True)
    gd.configure_grid_options()
    gd.configure_default_column(groupable=True, filterable=True, sorteable=True, resizable=True)
    gridoptions = gd.build()
    grid_table = AgGrid(df, gridOptions=gridoptions, update_mode=GridUpdateMode.SELECTION_CHANGED, fit_columns_on_grid_load=True, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    
    selected_row = grid_table["selected_rows"]
    selected_row_json = json.dumps(selected_row)
    selected_row_dict = json.loads(selected_row_json)
    
    if len(selected_row_dict) > 0:
      for elemento in selected_row_dict:
          elemento.pop('_selectedRowNodeInfo')
      df = pd.DataFrame(selected_row_dict)
        
      return df, selected_row

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path, width=None, height=None):
    style = ""
    if width:
        style += f"width:{width}px;"
    if height:
        style += f"height:{height}px;"
    img_html = "<img src='data:image/png;base64,{}' style='{}' class='img-fluid'>".format(
        img_to_bytes(img_path),
        style
    )
    return img_html

st.cache_resource(show_spinner = False)
# Verificar las credenciales del usuario
def verificar_credenciales(nombre_usuario, contraseña):
    return usuarios_permitidos.get(nombre_usuario) == contraseña

st.cache_resource(show_spinner = False)
def load_model():
    model_size = "base"
    st.session_state.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    return st.session_state.model
    
st.cache_resource(show_spinner = False)   
def transcribe_audio_2(file_path):
    
    st.session_state.model = load_model()
    
    segments, info = st.session_state.model.transcribe(file_path, beam_size=5, 
        language="es", condition_on_previous_text=False)
    
    texto = ''
    for segment in segments:
      texto += segment.text
        
    return texto
  
st.cache_resource(show_spinner = False)
# Funciones auxiliares
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript_response = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        # Accede al texto de la transcripción directamente desde el objeto de respuesta
        return transcript_response.text


st.cache_resource(show_spinner = False)
def generar_noticia(declaraciones, anotaciones, X, Y, Z, A, B):
    my_texto = "Vas a actuar como un asistente de inteligencia artificial para periodistas, cuya tarea será redactar el cuerpo de texto de un artículo periodístico informativo de la mayor longitud posible utilizando la cantidad máxima de tokens disponibles a partir de declaraciones proporcionadas por un individuo. Te proporcionaré cinco variables clave: X (cargo del individuo), Y (nombre completo del individuo), Z (tema más relevante que protagonizará los primeros párrafos), A (dónde ha dicho las declaraciones) y B (cuándo ha dicho las declaraciones); además de la propias declaraciones. Aquí te detallo el enfoque que debes seguir al redactar el artículo. Considera estas indicaciones paso a paso para asegurarnos de tener la respuesta correcta: 1. Ordena el artículo utilizando la estructura periodística clásica de pirámide invertida, de mayor a menor importancia de los temas tratados. El primer párrafo debe explicar quién ha dicho qué (variable Z), cuándo (B) y dónde (A). Inicia con las declaraciones más directamente relacionadas con Z, que deben situarse en los primeros párrafos. A medida que avances, presenta la información de manera descendente en términos de su relevancia y relación con Z, hasta llegar a las declaraciones menos relevantes y menos relacionadas con el tema principal. 2. Utiliza citas directas entre comillas para presentar las frases y razonamientos del individuo, pero atribúyelas siempre a su autor en el párrafo mediante expresiones como “ha dicho”, “ha indicado” o “ha manifestado”. Mantén una distancia periodística de imparcialidad en todo momento. Tu trabajo es informar de la forma más aséptica posible y citar las declaraciones más valorativas y calificativas entre comillas. No añadas ninguna interpretación o valoración sin entrecomillar a las declaraciones. 3. Utiliza ÚNICAMENTE el pretérito perfecto compuesto durante todo el texto para referirte a las acciones del orador: “ha dicho”, “ha manifestado”, “ha indicado”... Evita en todo momento el uso del pretérito perfecto simple. 4. No añadas información que no esté presente en las declaraciones proporcionadas. El artículo debe basarse únicamente en dichas declaraciones, por lo que debes trabajar dentro de los límites de la información proporcionada. 5. Evita repeticiones tanto de conceptos como de palabras en todo el artículo, asegurándote de mantener una fluidez y legibilidad óptimas. Utiliza sinónimos y expresiones diferentes para mantener la diversidad lingüística"
    messages = [
        {"role": "user", "content": f"{my_texto} \n X: {X}, Y: {Y}, Z: {Z}, A: {A}, B: {B}. Declaraciones: {declaraciones}. Anotaciones de relevancia: {anotaciones}"}
    ]

    response_noticia = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        max_tokens=3500,
        temperature=0,
        seed = 42
    )

    return response_noticia.choices[0].message.content
    
st.cache_resource(show_spinner = False)
def parrafer(transcripcion):
    
    messages = [
      {"role": "system", "content": "Eres un asistente de periodistas. Ayúdame a separar en párrafos las siguientes declaraciones para que sea un texto legible. No elimines nada de información, solo dedicate a estructurar en párrafos la transcripción. Responde únicamente con la transcripcion separada en parrafos usando '\n\n', nada más:"},
      {"role": "user", "content": transcripcion}
    ]

    response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            seed = 42,
            temperature=0
        )
    
    return response.choices[0].message.content


st.cache_resource(show_spinner = False)
def audio_a_bytes(archivo_audio):
    # Obtener los bytes del archivo de audio
    contenido_bytes = archivo_audio.read()
    return contenido_bytes

st.cache_resource(show_spinner = False)
def bytes_a_audio(bytes_audio, formato_destino="mp3"):
    # Crear un objeto AudioSegment a partir de los bytes
    audio_segment = AudioSegment.from_file(BytesIO(bytes_audio))

    # Convertir el audio al formato deseado
    formato_destino = formato_destino.lower()
    if formato_destino not in ["mp3", "wav"]:
        print("Formato no compatible. Selecciona 'mp3' o 'wav'.")
        return None

    # Crear un archivo temporal con extensión deseada
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{formato_destino}") as temp_file:
        temp_path = temp_file.name

        # Exportar el audio en el nuevo formato
        audio_segment.export(temp_path, format=formato_destino)

    return temp_path

# Función para generar el HTML resaltando las frases
def generar_html_con_destacados(texto, frases_destacadas):
    html = ""
    inicio = 0
    for frase in frases_destacadas:
        ocurrencias = encontrar_ocurrencias(texto, frase)
        for ocurrencia in ocurrencias:
            html += texto[inicio:ocurrencia[0]]  # Agregar texto antes de la frase
            html += f"<span style='background-color: yellow'>{texto[ocurrencia[0]:ocurrencia[1]]}</span>"  # Resaltar la frase
            inicio = ocurrencia[1]
    html += texto[inicio:]  # Agregar el texto restante
    return html

# Función para encontrar todas las ocurrencias de una frase en el texto
def encontrar_ocurrencias(texto, frase):
    ocurrencias = []
    inicio = 0
    while inicio < len(texto):
        inicio = texto.find(frase, inicio)
        if inicio == -1:
            break
        ocurrencias.append((inicio, inicio + len(frase)))
        inicio += len(frase)
    return ocurrencias
