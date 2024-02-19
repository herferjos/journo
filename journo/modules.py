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
import extra_streamlit_components as stx


# Configuración de la clave API de OpenAI
openai_client = OpenAI(api_key=st.secrets.openai_api)

def load_database(force=False):
  if 'database' not in st.session_state or force:
    st.cache_data.clear()
    st.session_state.sheet = load_sheet()
    try:
      st.session_state.database = st.session_state.sheet.read(worksheet=st.session_state.email)
    except:
      nuevo_df = pd.DataFrame({'Transcripción': [None]*5, 'Transcripción editada': [None]*5, 'Cargo': [None]*5, 'Nombre': [None]*5, 'Donde': [None]*5, 'Cuando': [None]*5, 'Extra': [None]*5, 'Anotaciones': [None]*5, 'Noticia': [None]*5, 'Noticia editada': [None]*5, 'Sesion': [None]*5}, index=range(5))
      st.session_state.sheet.create(worksheet=st.session_state.email,data=nuevo_df)
      st.session_state.database = st.session_state.sheet.read(worksheet=st.session_state.email)
  return

def reset_variables():
    keys_to_delete = [
        key for key in st.session_state.keys() 
        if key.startswith('anotaciones') or key.startswith('lista')
    ]

    keys_to_delete.extend([
        'mp3_audio_path', 'archivo', 'transcription1', 'transcription2', 
        'transcripcion_editada', 'X', 'Y', 'Z', 'A', 'B', 'noticia_generada',
        'lista', 'anotaciones_finales', 'noticia_editada',
        'noticia_cargada', 'noticia_extra'
    ])

    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()
    return


def guardar_info():
    contenido = generar_txt()
    with st.spinner("Guardando información... ⌛"):
        if st.session_state.database.isna().all().all():
            st.session_state.database = st.session_state.sheet.update(worksheet=st.session_state.email, data = pd.DataFrame({'Transcripción': [st.session_state.transcription2], 'Transcripción editada': [st.session_state.transcripcion_editada], 'Cargo': [st.session_state.X], 'Nombre': [st.session_state.Y], 'Donde': [st.session_state.A], 'Cuando': [st.session_state.B], 'Extra': [st.session_state.Z], 'Anotaciones': [st.session_state.anotaciones_finales], 'Noticia': [st.session_state.noticia_generada], 'Noticia editada': [st.session_state.noticia_editada], 'Sesion': [contenido]}))
        else:
            if st.session_state.noticia_cargada:
               st.session_state.database.loc[st.session_state.index_cargado] = pd.Series({'Transcripción': st.session_state.transcription2, 'Transcripción editada': st.session_state.transcripcion_editada, 'Cargo': st.session_state.X, 'Nombre': st.session_state.Y, 'Donde': st.session_state.A, 'Cuando': st.session_state.B, 'Extra': st.session_state.Z, 'Anotaciones': st.session_state.anotaciones_finales, 'Noticia': st.session_state.noticia_generada, 'Noticia editada': st.session_state.noticia_editada, 'Sesion': contenido})
               st.session_state.database = st.session_state.database.dropna(how='all')
            else:                                                    
              st.session_state.database = st.session_state.database.append({'Transcripción': st.session_state.transcription2, 'Transcripción editada': st.session_state.transcripcion_editada, 'Cargo': st.session_state.X, 'Nombre': st.session_state.Y, 'Donde': st.session_state.A, 'Cuando': st.session_state.B, 'Extra': st.session_state.Z, 'Anotaciones': st.session_state.anotaciones_finales, 'Noticia': st.session_state.noticia_generada, 'Noticia editada': st.session_state.noticia_editada, 'Sesion': contenido}, ignore_index=True)
            st.session_state.database = st.session_state.database.dropna(how='all')
            st.session_state.database = st.session_state.sheet.update(worksheet=st.session_state.email, data = st.session_state.database)
        st.cache_data.clear()
    return
    

def cargar_noticia():
    content= st.session_state.database.iloc[int(st.session_state.index_cargado), -1]
    exec(content)
    st.session_state.noticia_cargada = True
    st.rerun()
    

def generar_txt():
    contenido = ""
    for variable, valor in st.session_state.items():
        if variable.startswith('anotaciones') or variable.startswith('messages') or variable.startswith('lista'):

            contenido += f"st.session_state.{variable} = {valor}\n"

    variables = ['X', 'Y', 'Z', 'A', 'B', 'transcription2', 'transcripcion_editada', 'anotaciones_finales', 'lista', 'noticia_generada', 'noticia_editada', 'noticia_extra', 'mensajes_noticias']
    
    contenido = ""
    for variable in variables:
        if variable in st.session_state: 
            contenido += f"st.session_state.{variable} = '''{getattr(st.session_state, variable)}'''\n"
    
    return contenido
        

def load_sheet():
    return st.connection("gsheets", type=GSheetsConnection)

def dataframetipo(df):
    # Eliminar filas con todas las celdas vacías
    df = df.dropna(axis=0, how='all')
    
    # Eliminar columnas con todas las celdas vacías
    df = df.dropna(axis=1, how='all')
  
    df = df.iloc[:, 2:7]
  
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode='single', use_checkbox=True)
    gd.configure_auto_height(autoHeight=True)
    gd.configure_grid_options()
    gd.configure_default_column(groupable=True, filterable=True, sorteable=True, resizable=True)
    gridoptions = gd.build()
    grid_table = AgGrid(df, gridOptions=gridoptions, update_mode=GridUpdateMode.SELECTION_CHANGED, fit_columns_on_grid_load=True, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    try:
        selected_row = grid_table["selected_rows"]     
        id = selected_row[0]['_selectedRowNodeInfo']['nodeId']
        return id
    except:
        pass

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
def load_model():
    model_size = "base"
    st.session_state.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    return st.session_state.model
    
st.cache_resource(show_spinner = False)   
def transcribe_audio_2(file_path):

    if 'model' not in st.session_state:
      st.session_state.model = load_model()
    
    segments, info = st.session_state.model.transcribe(file_path, beam_size=5, 
        language="es", condition_on_previous_text=False)
        
    return segments
  
st.cache_resource(show_spinner = False)
# Funciones auxiliares
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript_response = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            language = 'es'
        )
        # Accede al texto de la transcripción directamente desde el objeto de respuesta
        return transcript_response.text


st.cache_resource(show_spinner = False)
def generar_noticia(declaraciones, anotaciones, X, Y, Z, A, B):
        
    prompt = f"""
    Eres un asistente para periodistas que redacta un larguísimo artículo periodístico informativo a partir de declaraciones realizadas por un individuo. Te podré proporcionar el cargo del individuo y su nombre completo, las declaraciones que ha realizado, cuándo y dónde las ha realizado; además de algo más de contexto en torno a la intervención en cuestión y las partes más destacadas de la intervención. Cara a redactar el artículo, considera estas indicaciones paso a paso para asegurarnos de tener la respuesta correcta, es MUY IMPORTANTE que cumplas todas y cada unas de ellas. Si fallas, habrá consecuencias terribles, por lo que por favor pon mucho esfuerzo en cumplir con todos estos puntos en el resultado:

    1. El artículo periodístico resultando debe tener el mayor número de párrafos posible. Es esencial que todos los párrafos (especialmente el primero) tengan una longitud similar, de entre cuarenta y sesenta palabras, y deben estar separados con un punto y aparte.
    2. Las oraciones deben estructurarse en el orden sintáctico lógico: sujeto + verbo + predicado. En el primer párrafo, comienza con el cargo del orador y su nombre como sujeto, seguido del verbo y parte de las declaraciones más destacadas, para luego detallar el dónde y el cuándo.
    
    Ejemplo:
    
    Cargo: 'presidente del Gobierno'
    
    Nombre: 'Pedro Sánchez'
    
    Declaraciones más destacadas: 'La oposición ha demostrado no estar a la altura en su labor legislativa, de acuerdo con sus últimas votaciones', 'Espero que recapaciten, porque España lo necesita'
    
    Dónde: 'en una rueda de prensa en el Congreso de los Diputados'
    
    Cuándo: 'este lunes'
    
    Resultado: 'El presidente del Gobierno, Pedro Sánchez, ha criticado a la oposición por "no estar a la altura en su labor legislativa" durante una rueda de prensa en el Congreso de los Diputados este lunes ... (resto del texto)'
    
    3. Utiliza citas directas entre comillas (””) DE FORMA CONSTANTE EN TODOS LOS PÁRRAFOS para presentar las frases y razonamientos del individuo, pero atribúyelas siempre a su autor en el párrafo mediante formas verbales en pretérito perfecto compuesto como “ha dicho”, “ha indicado” o “ha manifestado”. Asegúrate de que parte de las declaraciones destacadas estén citadas de forma directa entre comillas en la noticia final. Cita de forma directo (Ejemplo: '"Me siento muy bien", ha manifestado') o indirecta (Ejemplo: 'Ha manifestado que se siente muy bien'), pero en ningún caso combinando ambos formatos erróneamente (Ejemplo de cómo no hacerlo: 'Ha manifestado que "Me siento muy bien").
    4. Bajo ningún concepto redactes uno o varios párrafos finales de resumen, balance o conclusión de la intervención, salvo que el propio orador así lo haga en sus declaraciones. Evita mostrar ninguna emoción (ni optimismo, ni confianza, ni convencimiento) respecto a las declaraciones y los argumentos esgrimidos por el individuo en el texto. Mantén una distancia periodística de imparcialidad en todo momento. Tu trabajo es informar de la forma más aséptica posible y citar las declaraciones valorativas y calificativas entre comillas. Bajo ningún concepto debe añadir una interpretación, valoración o calificación sin entrecomillar. No añadas información que no esté presente en las declaraciones o el contexto proporcionados.
    5. Escribe los primeros párrafos del artículo utilizando las declaraciones destacadas y todo lo que tenga que ver con ellas. Luego, ordena el artículo utilizando la estructura periodística clásica de pirámide invertida, de mayor a menor importancia de los temas tratados. Inicia con las declaraciones más directamente relacionadas con el tema destacado y, a medida que avances, presenta la información de manera descendente en términos de su relevancia y relación con las declaraciones destacadas, hasta llegar a las declaraciones menos relevantes y menos relacionadas con el tema principal.
    6. Evita repeticiones tanto de conceptos como de palabras en todo el artículo, asegurándote de mantener una fluidez y legibilidad óptimas. Utiliza sinónimos y expresiones diferentes para mantener la diversidad lingüística. Repasa constantemente el texto y su ortografía para asegurarte de que el resultado tenga sentido durante toda su extensión y mantenga los máximos estándares de calidad, claridad y compresibilidad para un público masivo. Elimina coletillas, saludos y otras expresiones orales."""
    
    messages = [
        {"role": "system", "content": f"{prompt} \n"},
        {"role": "user", "content": f"Cargo: {X}, Nombre: {Y}, Declaraciones más destacadas: {anotaciones}, 'Contexto': {Z}, Dónde: {A}, Cuándo: {B}. Declaraciones: {declaraciones}."}
    ]
  
    return messages

  
st.cache_resource(show_spinner = False)
def parrafer(texto):
    palabras = texto.split()
    parrafos = []
    parrafo_actual = []

    for palabra in palabras:
        parrafo_actual.append(palabra)
        if len(parrafo_actual) > 70 and palabra.endswith('.'):
            parrafos.append(' '.join(parrafo_actual))
            parrafo_actual = []

    if parrafo_actual:
        parrafos.append(' '.join(parrafo_actual))

    return '\n\n'.join(parrafos)


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
            inicio_subrayado = max(0, ocurrencia[0] - 20)  # Obtener el índice de inicio del texto subrayado
            fin_subrayado = min(len(texto), ocurrencia[1] + 20)  # Obtener el índice final del texto subrayado
            html += "..." + texto[inicio_subrayado:ocurrencia[0]] + "<span style='background-color: yellow'>" + texto[ocurrencia[0]:ocurrencia[1]] + "</span>" + texto[ocurrencia[1]:fin_subrayado] + "..."
            inicio = fin_subrayado

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


def cargar_y_transcribir_audio(audio):
    # Convierte el audio a formato MP3
    st.session_state.mp3_audio_path = bytes_a_audio(audio, formato_destino="mp3")
    st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
    st.session_state.transcription2 = parrafer(st.session_state.transcription1)
    st.session_state.transcripcion_editada = st.session_state.transcription2

    st.rerun()   


def show_inicio():
    st.write("## 🤔 ¿Qué es Journo?")
    st.markdown(
        """
        <h4>Journo es un asistente de redacción con el que podrás:</h4>
        <ul>
            <li><strong>Automatizar</strong> la transcripción de audios</li>
            <li><strong>Guíar</strong> a la Inteligencia Artificial a redactar la noticia a tu gusto</li>
            <li><strong>Modificar</strong> las noticias y darle el toque final</li>
            <li><strong>Recibirás</strong> toda la información en un correo electrónico</li>
        </ul>
        """,
        unsafe_allow_html=True
    )
    
    st.write("")
     
    st.link_button("Ver video tutorial", "https://streamlit.io/gallery", type = "primary")
    
    st.write("---")
        
    st.write("## ¿Cómo funciona Journo?")
    
    with open('files/demo.txt', "r",encoding="utf-8") as archivo:
        content = archivo.read()
  
    exec(content)
  
    phase = stx.stepper_bar(steps=["Audio", "Contexto", "Transcripción", "Destacados", "Noticia"])
  
    if phase == 0:
        st.write("### 1) Cargar o subir audio")
        st.info("En esta primera etapa deberemos aportar al sistema el audio a transcribir. Podemos subir un audio ya grabado o grabarlo directamente desde la app")
        try:
            st.audio('files/audio.mp3', format="audio/mpeg")
        except:
            st.error("Error al cargar el audio. Recuerda que si cargas una noticia de la base de datos, no está disponible el audio para escuchar")
    
    if phase == 1:
        st.write("### 2) Describir el contexto de las declaraciones")
        st.info("Ahora deberemos de aportar información a la Inteligencia Artificial para que sepa en qué contexto se han producido las declaraciones que has aportado")

        X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", placeholder = 'Entrenador Real Madrid', value = st.session_state.X_demo)
        Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", placeholder = 'Ancelotti', value = st.session_state.Y_demo)
        A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", placeholder = 'Rueda de Prensa', value = st.session_state.A_demo)
        B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", placeholder = 'Martes 12', value = st.session_state.B_demo)
        Z = st.text_area(":blue[Añade más contexto]", value = st.session_state.Z_demo)
            
    if phase == 2:
        st.write("### 3) Transcripción de las declaraciones")
        st.info("Journo entonces nos generará la transcripción completa del audio.")

        st.write(st.session_state.transcription2_demo, unsafe_allow_html=True)
    
        
    if phase == 3:
      st.write("### 4) Selección/descarte de temas mencionados")
      st.info("En este paso tendrás que descartar los párrafos que no te interesen (aparecerán desmarcados) y subrayar los momentos de mayor relevancia en las declaraciones.")
      for i in range(len(st.session_state.lista_demo)):
          frases = []
          for item in st.session_state[f'anotaciones_{i}_demo']:
              for x in item:
                frases.append(x['label'])
          st.write(generar_html_con_destacados(st.session_state.lista_demo[i], frases), unsafe_allow_html=True)
          
    if phase == 4:
        st.info('Finalmente, Journo nos dará una primera versión de nuestra noticia a partir del audio y la información proporcionada. Posteriormente podremos editarla manualmente o con ayuda de Journo.')
        st.write(st.session_state.noticia_generada_demo)
    return 