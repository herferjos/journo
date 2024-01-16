from openai import OpenAI
import streamlit as st
import tempfile
import os
from io import BytesIO
import tempfile
import json
from pydub import AudioSegment
import concurrent.futures
import io


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
    "" : ""
}

# Verificar las credenciales del usuario
def verificar_credenciales(nombre_usuario, contraseña):
    return usuarios_permitidos.get(nombre_usuario) == contraseña
  

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
    prompt = """
    Eres un asistente para periodistas que redacta un artículo periodístico informativo utilizando la cantidad máxima de tokens disponibles a partir de declaraciones realizadas por un individuo. 
    Te proporcionaré cinco variables clave: X (cargo del individuo), Y (nombre completo del individuo), Z (tema más relevante que protagonizará los primeros párrafos), A (dónde ha dicho las declaraciones) y B (cuándo ha dicho las declaraciones); además de la propias declaraciones. 
    En el caso de que no te dé alguna de esas variables, ignórala durante la redacción del texto. Aquí te detallo el enfoque que debes seguir al redactar el artículo. Considera estas indicaciones paso a paso para asegurarnos de tener la respuesta correcta, es MUY IMPORTANTE que cumplas todas y cada unas de ellas. Si fallas, habrá consecuencias terribles, por lo que por favor pon mucho esfuerzo en cumplir con todos estos puntos en el resultado: 
    1. Ordena el artículo utilizando la estructura periodística clásica de pirámide invertida, de mayor a menor importancia de los temas tratados. Todos los párrafos deben tener una longitud similar, de entre cuarenta y sesenta palabras por párrafo. Inicia con las declaraciones más directamente relacionadas con Z, que deben situarse en los primeros párrafos. A medida que avances, presenta la información de manera descendente en términos de su relevancia y relación con Z, hasta llegar a las declaraciones menos relevantes y menos relacionadas con el tema principal. Asegúrate de que todos los párrafos estén separados con punto y aparte y cuenten con el mismo espacio entre ellos. 
    2. Las oraciones deben estructurarse en el orden sintáctico lógico: sujeto + verbo + predicado. En el primer párrafo, comienza con el cargo del orador (X) y su nombre (Y) como sujeto, seguido del verbo y del tema principal (Z), el dónde (A) y el cuándo (B). Ejemplo: 
        X='presidente del Gobierno'
        Y='Pedro Sánchez'
        Z='crítica a la oposición'
        A='en el Congreso de los Diputados'
        B='este lunes'
    Resultado='El presidente del Gobierno, Pedro Sánchez, ha criticado a la oposición en el Congreso de los Diputados este lunes... (resto del texto)' 
    3. Utiliza constantes citas directas entre comillas (””) para presentar las frases y razonamientos del individuo, pero atribúyelas siempre a su autor en el párrafo mediante formas verbales ÚNICAMENTE en pretérito perfecto compuesto como “ha dicho”, “ha indicado” o “ha manifestado”. Cita de forma directa o de forma indirecta, pero nunca mezclándolas de manera incorrecta. 
    4. Mantén una distancia periodística de imparcialidad en todo momento. Tu trabajo es informar de la forma más aséptica posible y citar las declaraciones valorativas y calificativas entre comillas. Bajo ningún concepto debe añadir una interpretación o valoración sin entrecomillar, al igual que debes evitar mostrar durante el texto ninguna emoción (ni optimismo, ni confianza, ni convencimiento) respecto a las declaraciones y los argumentos esgrimidos por el individuo en el texto.
    5. No añadas información que no esté presente en las declaraciones proporcionadas. El artículo debe basarse únicamente en dichas declaraciones, por lo que debes trabajar dentro de los límites de la información proporcionada.
    6. Evita repeticiones tanto de conceptos como de palabras en todo el artículo, asegurándote de mantener una fluidez y legibilidad óptimas. Utiliza sinónimos y expresiones diferentes para mantener la diversidad lingüística. Repasa constantemente el texto y su ortografía para asegurarte de que el resultado tenga sentido durante toda su extensión y mantenga los máximos estándares de calidad, claridad y compresibilidad para un público masivo. La extensión de las frases no debe ser de más de 15 palabras y se deben priorizar las proposiciones coordinadas sobre las subordinadas. Descarta emplear conectores innecesarios al comienzo de un párrafo, como “por consiguiente”, “conviene recordar”, “en otro orden de cosas” o similares. Elimina extensas frases parentéticas e incisos explicativos que alejan al sujeto del verbo. Utiliza la voz activa antes que la pasiva, elige preferentemente palabras cortas y evita las dobles negaciones.
    7. Asegúrate de que el resultado final incluya la mayor cantidad posible de declaraciones e informaciones relacionadas con el tema principal (Z) y todos los asuntos de mayor importancia que han sido comentados. Descarta la información más superflua e irrelevante para el artículo, como saludos y coletillas orales.
    Debes responder con un JSON de la siguiente forma: {'noticia': <string de la noticia>}
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Aquí tienes la información necesaria para redactar el artículo. X: {X}, Y: {Y}, Z: {Z}, A: {A}, B: {B}. Declaraciones: {transcripcion}"},
        {"role": "user", "content": "Recuerda responder en JSON con la estructura dada y seguir todas las iinstrucciones que te he proporcionado, no olvides ninguna, sino tendra terribles consecuencias para mi."},        
    ]

    response_noticia = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        max_tokens=3500,
        temperature=0,
        response_format={"type": "json_object"}
    )

    return json.loads(response_noticia.choices[0].message.content)['noticia']



def convertir_a_mp3(archivo):
    # Check if archivo is a bytes object
    if isinstance(archivo, bytes):
        # If it's a bytes object, create a BytesIO object for reading
        archivo = io.BytesIO(archivo)

    # Now archivo should be a file-like object, and you can read from it
    audio_data = archivo.read()

    # Rest of your code remains unchanged
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
    mp3_data = audio_segment.export(format="mp3").read()

    return mp3_data
