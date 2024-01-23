from openai import OpenAI
import streamlit as st
from modules import *
from streamlit_annotation_tools import text_highlighter
from streamlit_mic_recorder import mic_recorder
import re

st.set_page_config(page_title="Journo.AI", page_icon="🗞️", layout="wide")

st.markdown(
  """
  <div style='text-align: center;'>
      <h1>🗞️ Journo 🗞️</h1>
      <h4>Tu asistente periodístico de inteligencia artificial</h4>
  </div>
  """,
    unsafe_allow_html=True
)
st.write("---")


# Inicio de sesión
if 'autenticado' not in st.session_state:
    nombre_usuario = st.text_input("Nombre de usuario")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión", type = "primary"):
        if verificar_credenciales(nombre_usuario, contraseña):
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

if 'autenticado' in st.session_state:
  with st.expander("Informacion recopilada"):
    if 'mp3_audio_path' in st.session_state and not 'transcription2' in st.session_state:
        st.info("Aquí tienes el audio que hemos procesado")
        st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
        st.write("---")
      
    if 'mp3_audio_path' in st.session_state and 'transcription2' in st.session_state and not 'noticia_generada' in st.session_state:
        audio, transcripcion = st.tabs(["Audio", "Transcripción"])
        with audio:
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
        with transcripcion:
          st.info("Aquí tienes la transcripción del audio")
          lista_transcription = st.session_state.lista_transcription
          # lista_transcription[0] = '- ' + lista_transcription[0]
          texto = '\n\n- '.join(lista_transcription)
          
          patron = re.compile(r'\n\n- ([^:]+):|-\s*([^:]+):')
          
          # Buscar coincidencias en el string
          coincidencias = patron.findall(texto)
          
          # Procesar las coincidencias
          for match in coincidencias:
              # Check which group matched
              texto_a_formatear = match[0] if match[0] else match[1]
              texto_formateado = f"<u><b>{texto_a_formatear.strip()}</b></u>"
              
              # Replace the matched text with the formatted text
              texto = texto.replace(match[0] or match[1], texto_formateado)
          
          # Mostrar el texto formateado
          st.markdown(texto, unsafe_allow_html=True)
            
        st.write("---")
      
    if 'noticia_generada' in st.session_state:
        audio, transcripcion, anotacions = st.tabs(["Audio", "Transcripción", "Anotaciones"])
        with audio:
          st.info("Aquí tienes el audio que hemos procesado")
          st.audio(st.session_state.mp3_audio_path, format="audio/mpeg")
        with transcripcion:
          st.info("Aquí tienes la transcripción del audio")
          lista_transcription = st.session_state.lista_transcription
          lista_transcription[0] = '- ' + lista_transcription[0]
          st.write('\n\n- '.join(lista_transcription))

        with anotaciones:
          st.info("Aquí tienes tus anotaciones")
          st.write(st.session_state.anotaciones)
       
  st.write("---")


if 'autenticado' in st.session_state:
    if 'mp3_audio_path' not in st.session_state:
      st.success("¡Autenticado con éxito!")
      col1, col2 = st.columns(2)
      with col1:
        st.info("Sube aquí tu archivo de audio con las declaraciones que deseas convertir en una noticia.")
        archivo = st.file_uploader("Cargar archivo de audio")
        
        if st.button("Siguiente", type = "primary", key = "upload"):
          with st.spinner("Cargando audio... ⌛"):
            if archivo is not None:
                # Convierte el audio a formato MP3
                mp3_bytes = audio_a_bytes(archivo)
                          
                st.session_state.mp3_audio_path = bytes_a_audio(mp3_bytes, formato_destino="mp3")
              
                st.rerun()


      with col2:
        st.info("Puedes empezar a grabar un audio directamente desde aquí")
        
        audio=mic_recorder(start_prompt="Empezar a grabar",stop_prompt="Parar de grabar",key='recorder')
        
        if st.button("Siguiente", type = "primary", key = "record"):
          with st.spinner("Cargando audio... ⌛"):            
              st.session_state.mp3_audio_path = bytes_a_audio(audio['bytes'], formato_destino="mp3")
            
              st.rerun()

  
    if 'mp3_audio_path' in st.session_state and 'X' not in st.session_state:
        st.info("Completa los siguientes campos para proporcionar contexto y detalles específicos que ayudarán a generar la noticia.")
        X = st.text_input(":blue[¿Cuál es el cargo de la persona que habla?]", value = 'Entrenador Real Madrid')
        Y = st.text_input(":blue[¿Cuál es el nombre de la persona que habla?]", value = 'Ancelotti')
        Z = st.text_input(":blue[¿Cuál es el tema más relevante del que ha hablado?]", value = 'Partido vs Atletico de Madrid')
        A = st.text_input(":blue[¿Dónde ha dicho las declaraciones?]", value = 'Rueda de Prensa')
        B = st.text_input(":blue[¿Cuándo ha dicho las declaraciones?]", value = 'Martes 12')
      
 
        if st.button("Enviar información", type = "primary", key = "Enviar"):
            with st.spinner("Enviando información... ⌛"):
              st.warning("Este proceso puede tardar unos minutos.")
              st.session_state.X = X
              st.session_state.Y = Y
              st.session_state.Z = Z
              st.session_state.A = A
              st.session_state.B = B
  
              
              st.session_state.transcription1 = transcribe_audio(st.session_state.mp3_audio_path)
              st.session_state.transcription2, st.session_state.lista_transcription = dialoguer(st.session_state.transcription1, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
              st.rerun()
        elif st.button("Cargar transcripcion predeterminada", type = "primary", key = "Charge"):
          st.session_state.transcription2 = 'Ancelotti: Por el partido de mañana, obviamente es un partido más que un partido, una competición importante que haremos, como siempre, intentar de hacer lo máximo para para ganarla. Creo que el equipo está bien, llega con gana, con ilusión, recuperando a los jugadores y creo que podemos plantear un partido bueno, teniendo en cuenta que el Atlético nos ha hecho daño en el primer partido que hemos jugado esto lo tenemos que tener en cuenta el Atlético, como siempre, es un equipo que compite que lucha, que tiene calidad entonces, el partido va a ser un partido competido e igualado Miguel Ángel Díaz: Hola míster, buenas tardes. ¿Nos puede dar alguna información más sobre quién va a jugar en la portería? Ancelotti: Uno de los dos va a jugar mañana, no quiero decirlo hoy. Antonio Romero: ¿Cómo se toma el entrenador del Real Madrid este carrusel de partidos contra el Atlético de Madrid? Ancelotti: Creo que nunca se puede descartar ninguna competición. Hay que ir a revienta calderas desde el principio hasta el final. Nos ha tocado el Atlético de Madrid, vamos a jugar otra vez. Personalmente, no es que me guste encontrarme al Atlético de Madrid porque es uno de los mejores equipos. Siempre es complicado jugar contra ellos. Creo que va a disfrutar la afición, sea del Real Madrid que del Atlético de Madrid, de estos partidos. Alberto Pérez: ¿Has tenido alguna vez jugadores tan completos que te pueden abarcar en tantas posiciones como Valverde? Ancelotti: Valverde es un jugador completo, un medio completo. Puede jugar a fútbol de muchas maneras. Es muy raro encontrar un medio en el mercado con este perfil y la suerte que tenemos es que lo tenemos nosotros. Pienso que él puede mejorar todavía. José Félix Díaz: ¿Crees que Simeone y tú son los entrenadores más indicados o que reúnen esa identificación con los clubes? Ancelotti: Yo me encuentro muy bien en este ambiente que es el ambiente blanco y creo también como observatorio desde fuera que Simeone se encuentra muy bien en el ambiente del Atlético de Madrid. Gonzalo de Martorell: ¿Qué le parece la decisión de escuchar los audios del VAR tras los partidos de la Supercopa? Ancelotti: Creo que se puede mejorar el VAR. Tiene que ser un soporte para el árbitro para tomar las decisiones. Si la comunicación puede mejorar al árbitro, bien, a nosotros no cambia absolutamente nada. Carlos Juanma Sánchez: ¿Ahora que ya se han recuperado Camavinga y Suamení, va a romper la pareja que ha dado consistencia al centro del campo con el doble pivote Cross-Valverde? Ancelotti: Obviamente se puede romper esta pareja porque vuelve Suamení, vuelve Camavinga. Tengo muchas más opciones en el medio del campo que en los últimos partidos. Rubén Cañizares: ¿Considera que el Barcelona ha iniciado una nueva era y que está por encima del Madrid? Ancelotti: El Barcelona es un rival que tenemos que respetar porque es el rival en la Liga Doméstica. Este año también creo que va a ser rival en la Champions. Es un rival bastante normal para nosotros que siempre lo ha sido y siempre lo será. Olivia Lorenzo: ¿Qué le ofrece Rudiger por sus cualidades como central respecto al resto de jugadores en esa posición que tiene la plantilla? Ancelotti: Rudiger es un defensa muy atento, concentrado, fuerte de cabeza, con experiencia y carácter. Es un defensa completo. Abraham Romero: ¿Cómo ha sido la relación con Simeone a lo largo de los años? Ancelotti: Nos respetamos, nos conocemos y nos hemos enfrentado muchas veces. Tenemos una relación de respeto y cercanía. Periodista 1: ¿Ha tenido ofertas de clubes saudíes y otras ofertas? Ancelotti: No, no he tenido oferta. Periodista 2: ¿El último partido jugado contra el Atlético de Madrid va a influir al equipo? Ancelotti: La verdad es que el último partido jugado nos ha hecho mucho daño. Creo que mañana podemos sacar una versión mejor que la del primer partido de la temporada contra el Atlético de Madrid.'
          


    if 'transcription2' in st.session_state and 'noticia_generada' not in st.session_state:
        st.info("Ahora puedes seleccionar fragmentos de la transcripción para indicar que partes son más importantes a la hora de generar la noticia.")
        st.session_state.anotaciones = text_highlighter(st.session_state.transcription2)
        if st.button("Generar noticia", type = "primary"):
          with st.spinner("Generando noticia... ⌛"):
            
            anotaciones = []
            
            for elemento in st.session_state.anotaciones:
              for item in elemento:
                anotaciones.append(item['label'])
                                   
            st.session_state.anotaciones = anotaciones
            st.session_state.noticia_generada = generar_noticia(st.session_state.transcription2, st.session_state.anotaciones, st.session_state.X, st.session_state.Y, st.session_state.Z, st.session_state.A, st.session_state.B)
            
            st.rerun()
              

    if 'noticia_generada' in st.session_state:
        st.write("""## ✔️¡Listo! Aquí tienes tu noticia:""")

        estilo_bordes_redondeados = """
            <style>
                .bordes-redondeados {
                    border-radius: 10px;
                    padding: 10px;
                    border: 2px solid #ccc; /* Puedes ajustar el color del borde según tus preferencias */
                }
            </style>
        """

        # Aplicar el estilo CSS
        st.markdown(estilo_bordes_redondeados, unsafe_allow_html=True)

        # Mostrar el texto con bordes redondeados
        st.markdown(f'<div class="bordes-redondeados">{st.session_state.noticia_generada}</div>', unsafe_allow_html=True)

