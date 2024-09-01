# Importações necessárias para o streamlit, api do google, leitura em json, lottie e etc.
import streamlit as st
import requests
from PIL import Image
import google.generativeai as genai
import PIL.Image
import pathlib
import tqdm
import os
import time
import json
import fitz
import tempfile
import PyPDF2
from io import BytesIO
from streamlit_lottie import st_lottie #Import de arquivos lottie animados
from dotenv import load_dotenv

# ? Configuración de la página
st.set_page_config(page_title="Soporte ChatBot - TURISMO VERDE", layout="centered")

# ?Cargar variables de entorno

load_dotenv()

API_KEY = os.getenv("API_KEY");
genai.configure(api_key = API_KEY);
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

messages = []
image_messages = []
pdf_messages = []

### Variáveis Globais de state
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "English"

if "selected_font_size" not in st.session_state:
    st.session_state["selected_font_size"] = "medium"

if "selected_background" not in st.session_state:
    st.session_state["selected_background"] = "Estándar"

if "selected_background_messages" not in st.session_state:
    st.session_state["selected_background_messages"] = "Estándar"
    
    

# Importando pasta de CSS para estilizações globais
def local_css(file_name):
    with open(file_name) as f:
        
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("./styles.css");

def set_language(language):
    st.session_state["selected_language"] = language
    st.session_state["messages"] = [] 

def update_chat_container():
    chat_message_html = '<div id="chat-area" class="chat-container">'
    
    for message, sender in st.session_state.get("messages", []):
        message_class = 'user' if sender == 'user' else 'bot'
        chat_message_html += f'<div class="message {message_class}">{message}</div>'
    
    chat_message_html += '</div>'
    
    st.markdown(chat_message_html, unsafe_allow_html=True)
    
    
    
def process_chat_message(user_input):
    if user_input:
        try:
            response = chat.send_message(user_input)  # Asumiendo que tienes esta función definida
            pronome = "Tú" if st.session_state["selected_language"] == "Español" else "You"
            
            # Agrega el mensaje del usuario a la sesión de estado
            st.session_state["messages"].append((
                f'<div class="message user"><img src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExdHdtMnU3ejk5ZzhvZ3Fha2hlZnVyaWRjYmdma2hxbzNudjNnbzc2YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/clM6fzkkgbAUU/giphy.gif" class="icon" alt="User Icon">{user_input}</div>', 
                'user'))
            
            # Agrega la respuesta del bot a la sesión de estado
            st.session_state["messages"].append((
                f'<div class="message bot"><img src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExajZ6dXN3OW9rODdocnp1cGsxdm95b3Q3cHhwaGlnYTN4ZnNmazZsNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/v0cofVoA6l5KPwtA8x/giphy.gif" class="icon" alt="Bot Icon">{response.text}</div>', 
                'bot'))
            
            update_chat_container()
        except Exception as e:
            st.markdown(f'<span id="error">Error: {e}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span id="error">Por favor, ingresa un mensaje.</span>', unsafe_allow_html=True)



# Función principal
def set_font_size(font_size):
    if font_size == "Small":
        st.markdown('<style>body { font-size: small; }</style>', unsafe_allow_html=True)
    elif font_size == "Medium":
        st.markdown('<style>body { font-size: medium; }</style>', unsafe_allow_html=True)
    elif font_size == "Large":
        st.markdown('<style>body { font-size: large; }</style>', unsafe_allow_html=True)




def set_background(color):
    if color == "white":
        st.markdown('''
            <style>
                [data-testid="stSidebarContent"] { background-color: #D7D5CD; }
                [data-testid="stAppViewContainer"] { background-color: white; }
                [data-testid="stHeader"] { background-color: white; }
                [data-testid="stSidebarCollapseButton"] { background-color: #D7D5CD; }
                [data-testid="stMainMenu"] { background-color: #D7D5CD; }
                [data-testid="main-menu-list"] { background-color: #D7D5CD; }
                [data-testid="stImageCaption"] { color: black; }
                p, li, ul, h3, h1, h2, button { color: black; }
            </style>''', unsafe_allow_html=True)
        
    elif color == "Default": 
        st.markdown('<style></style>', unsafe_allow_html=True)


def set_background_messages(color_message):
    if color_message == "White and Dark Gray":
        st.markdown('''
            <style>
                div.message.user { background-color: white; color: black; }
                div.message.bot { background-color: #333; color: white; }
                .chat-container { display: flex; flex-direction: column; overflow-y: auto; max-height: 500px; }
            </style>''', unsafe_allow_html=True)
        
    elif color_message == "Navy Blue and Light Gray":
        st.markdown('''
            <style>
                div.message.user { background-color: #001f3f; color: white; }
                div.message.bot { background-color: #f5f5f5; color: black; }
                .chat-container { display: flex; flex-direction: column; overflow-y: auto; max-height: 500px; }
            </style>''', unsafe_allow_html=True)
        
    elif color_message == "Dark Green and Light Green":
        st.markdown('''
            <style>
                div.message.user { background-color: #004d00; color: white; }
                div.message.bot { background-color: #c8e6c9; color: black; }
                .chat-container { display: flex; flex-direction: column; overflow-y: auto; max-height: 500px; }
            </style>''', unsafe_allow_html=True)
        
    elif color_message == "Slate Gray and Light Gray":
        st.markdown('''
            <style>
                div.message.user { background-color: #2c3e50; color: white; }
                div.message.bot { background-color: #d0d3d4; color: black; }
                .chat-container { display: flex; flex-direction: column; overflow-y: auto; max-height: 500px; }
            </style>''', unsafe_allow_html=True)
        
    elif color_message == "Beige and Dark Brown":
        st.markdown('''
            <style>
                div.message.user { background-color: #f5f5dc; color: #3e2723; }
                div.message.bot { background-color: #3e2723; color: #f5f5dc; }
                .chat-container { display: flex; flex-direction: column; overflow-y: auto; max-height: 500px; }
            </style>''', unsafe_allow_html=True)
        
        
        
#!  audio enviado
def process_audio(audio_file_path, user_prompt):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content([user_prompt, audio_file])
    return response.text

# Función para guardar el archivo
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    
#? Sidebars - Filtros

#Linguagem
with st.sidebar:
    language_options = ["English", "Español"]
    st.markdown('''<style> [data-testid="stMarkdownContainer"] h1 { font-size: 45px; text-shadow: 2px -2px #466EFF; }</style>''', unsafe_allow_html=True)
    st.sidebar.title('SETTINGS ⚙️')

    with open('./img/Animation.json') as f:
        lottie_animation = json.load(f)
    
    st_lottie(lottie_animation)

    selected_language = st.selectbox("LANGUAGE 🌎", language_options)

    if selected_language != st.session_state.get("selected_language"):
        set_language(selected_language)
        st.session_state["selected_language"] = selected_language
#Fontes
with st.sidebar:
    font_size_options = ["Medium", "Small", "Large"]
    selected_font_size = st.selectbox("Font Size 🔍", font_size_options)
    st.sidebar.markdown("---")
    
    if selected_font_size != st.session_state.get("selected_font_size"):
        set_font_size(selected_font_size)
        st.session_state["selected_font_size"] = selected_font_size

#Background Color
with st.sidebar:
    background_options = ["Default", "White"]
    selected_background = st.radio("Background 🎨", background_options)

    if selected_background != st.session_state.get("selected_background"):
        set_background(selected_background)
        st.session_state["selected_background"] = selected_background

#Message-Colors
with st.sidebar:
    background_options_messages = ["Default", "White and Dark Gray", "Navy Blue and Light Gray", "Dark Green and Light Green", "Slate Gray and Light Gray", "Beige and Dark Brown"]
    selected_background_messages = st.radio("Message Background 🎨", background_options_messages)
    st.sidebar.markdown("---")
    st.image('./img/gemini.png', caption='Powered by Gemini AI')

    if selected_background_messages != st.session_state.get("selected_background_messages"):
        set_background_messages(selected_background_messages)
        st.session_state["selected_background_messages"] = selected_background_messages





col1, col2 = st.columns([1, 4])

with col1:
    st.image('https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExdW5nbWl4Z2VnY2gxYWI2MXl5OGxiejl6anprdW52bWJzcGo4cW00aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/xd22iKsu0Wn0Q/giphy.gif', 
            caption='', 
            use_column_width=False, 
            width=100)

with col2:
    st.title("Chat Bot DE TURISMO VERDE")

## Configuración de las pestañas
if selected_language == "Español":
    tabs = ['Chat Bot General', 'Análisis de Imágenes', 'Análisis de PDFs', 'Análisis de Audio', 'Sobre']
elif selected_language == "English":
    tabs = ['General Chat Bot', 'Image Review', 'PDF Review', 'Audio Review', 'About']

aba1, aba2, aba3, aba4, aba5 = st.tabs(tabs)

# Sección de Chat Bot General
with aba1:
    if selected_language == "Español":
        st.write("### Chat Bot:")
        st.write(" 📍 **¡Pregunta lo que quieras!** Di hola, pregunta de dónde viene la ropa blanca en Año Nuevo, por qué es azul el cielo, deja volar tu creatividad (no uses el bot para consultas de investigación, busca una fuente confiable).")
        st.markdown('<p class = aviso>Nota: Dependiendo de la pregunta, el bot puede añadir mucho texto y no enviar la respuesta. Sé puntual. Si el bot da un error, pídele que resuma la respuesta, debería funcionar.</p>', unsafe_allow_html=True)

    elif selected_language == "English":
        st.write("### Chat Bot:")
        st.write(" 📍 **Ask anything you want!** Say hello, ask where the white clothes come from on New Year's Eve, why the sky is blue, let your creativity run wild (don't use the bot for research queries, go back and trust the information, it's always good to have a reliable source).")
        st.markdown('<p class = aviso>Note: Depending on the question, the bot may add a lot of text and not send the answer. Be punctual. If the bot gives an error, ask it to summarize the answer, it should work.</p>', unsafe_allow_html=True)

    chat_container = st.container()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for user, message in st.session_state.messages:
            message_class = "user" if user == ("Você" if selected_language == "Español" else "You") else "bot"
            st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Diga algo...", key="user_input" if selected_language == "Español" else "user_input")
    if user_input:
        with st.spinner('Procesando...'):
            process_chat_message(user_input)

    st.markdown("<div id='chat-area' style='overflow-y: auto; max-height: 500px;'></div>", unsafe_allow_html=True)


# Sección de Análisis de Imágenes
with aba2:
    if selected_language == "Español":
        st.write("### Análisis de Imágenes con IA")
        st.write("📍 **¡Envía una imagen!**: Envía una imagen y pregunta lo que quieras sobre ella a la IA.")
        st.markdown("<p class = aviso >Aviso: La IA admite imágenes de hasta 20MB.</p>", unsafe_allow_html=True)

    elif selected_language == "English":
        st.write("### Image Review with AI")
        st.write("📍 **Upload an image!**: Upload an image and ask the AI anything about it!")
        st.markdown("<p class = aviso>Note: IA supports up to 20MB upload</p>", unsafe_allow_html=True)

    model = genai.GenerativeModel('gemini-1.5-flash')
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="image")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image' if selected_language == "English" else 'Imagen Enviada', use_column_width=True)
        st.write("Analyzing the image..." if selected_language == "English" else "Analizando la imagen...")

        if 'image_messages' not in st.session_state:
            st.session_state.image_messages = []

        if len(st.session_state.image_messages) == 0:
            st.session_state.image_messages.append(("You" if selected_language == "English" else "Você", f"Analyze this image: {uploaded_file.name}" if selected_language == "English" else f"Analiza esta imagen: {uploaded_file.name}"))
            response = model.generate_content(["Analyze this image", image] if selected_language == "English" else ["Analiza esta imagen", image])
            response.resolve()
            st.session_state.image_messages.append(("Gemini", response.text))

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.image_messages:
                message_class = "user" if user == ("Você" if selected_language == "Español" else "You") else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Pergunte algo sobre a imagem..." if selected_language == "Español" else "Ask something about the image...", key="image_user_input")
        if user_input:
            st.session_state.image_messages.append(("You" if selected_language == "English" else "Você", user_input))
            response = model.generate_content([user_input, image])
            response.resolve()
            st.session_state.image_messages.append(("Gemini", response.text))
            st.rerun()

with aba3:
    if selected_language == "Español":
        st.write("### Análisis de PDFs con IA")
        st.write("📍 **¡Envía un archivo PDF!**: Envía tu currículum, un libro, revista y pregunta sobre él a la IA.")
        st.markdown("<p class = aviso> Si ocurre algún error en la lectura, asegúrate de que tu archivo PDF esté correctamente formateado. La IA leerá el contenido de tu PDF, ignorando imágenes.</p>", unsafe_allow_html=True)
    elif selected_language == "English":
        st.write("### PDF Review with AI")
        st.write("📍 **Upload a PDF file!**: Upload your resume, a book, magazine, and ask about it to the AI.")
        st.markdown("<p class = aviso> If an error occurs, make sure your PDF file is correctly formatted. The AI will read the content of your PDF, ignoring images.</p>", unsafe_allow_html=True)

    uploaded_file_pdf = st.file_uploader("Choose a PDF...", type=["pdf"], key="pdf")
    if uploaded_file_pdf is not None:
        pdf_bytes = BytesIO(uploaded_file_pdf.read())
        reader = PyPDF2.PdfReader(pdf_bytes)
        num_pages = len(reader.pages)
        full_text = ""

        for page_num in range(num_pages):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            full_text += page_text + "\n"

        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        if 'pdf_messages' not in st.session_state:
            st.session_state.pdf_messages = []

        if len(st.session_state.pdf_messages) == 0:
            st.session_state.pdf_messages.append(("You" if selected_language == "English" else "Você", f"Analyze this PDF: {uploaded_file_pdf.name}" if selected_language == "English" else f"Analiza este PDF: {uploaded_file_pdf.name}"))
            response = model.generate_content(["Analyze this PDF", full_text] if selected_language == "English" else ["Analiza este PDF", full_text])
            response.resolve()
            st.session_state.pdf_messages.append(("Gemini", response.text))

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.pdf_messages:
                message_class = "user" if user == ("Você" if selected_language == "Español" else "You") else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Pergunte algo sobre o PDF..." if selected_language == "Español" else "Ask something about the PDF...", key="pdf_user_input")
        if user_input:
            st.session_state.pdf_messages.append(("You" if selected_language == "English" else "Você", user_input))
            response = model.generate_content([user_input, full_text])
            response.resolve()
            st.session_state.pdf_messages.append(("Gemini", response.text))
            st.rerun()
            
# Ahora replicamos, pero cambiando el idioma
    elif selected_language == "Español":
        st.write("### Revisión de PDFs con IA")
        st.write("📍 **¡Envía un archivo PDF!**: Envía tu currículum, una revista, un libro, pregúntale a la IA sobre él, ¿quieres un resumen? ¿un consejo? ¡Pruébalo ahora!")
        st.markdown("<p class = aviso> Si hay un error al leer el archivo PDF, asegúrate de que tu archivo esté correctamente formateado. La IA leerá el contenido de tu PDF, ignorando las imágenes.</p>", unsafe_allow_html=True)
        uploaded_file_pdf = st.file_uploader("Elige un archivo PDF...", type=["pdf"])

        if uploaded_file_pdf is not None:
            pdf_bytes = BytesIO(uploaded_file_pdf.read())
            
            lector_pdf = PyPDF2.PdfReader(pdf_bytes)

            num_paginas = len(lector_pdf.pages)
            texto_completo = ""

            for num_pagina in range(num_paginas):
                pagina = lector_pdf.pages[num_pagina]

                texto_pagina = pagina.extract_text()
                texto_completo += texto_pagina + "\n"

            model = genai.GenerativeModel('gemini-1.5-pro-latest')

            if 'pdf_messages' not in st.session_state:
                st.session_state.pdf_messages = []

            if len(st.session_state.pdf_messages) == 0:
                st.session_state.pdf_messages.append(("Tú", f"Analiza este PDF: {uploaded_file_pdf.name}"))
                response = model.generate_content([f"Analiza este PDF", texto_completo])
                response.resolve()
                st.session_state.pdf_messages.append(("Gemini", response.text))

            chat_container = st.container()
            with chat_container:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                for user, message in st.session_state.pdf_messages:
                    message_class = "user" if user == "Tú" else "bot"
                    st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            user_input = st.chat_input("Pregunta algo sobre el PDF...", key="pdf_user_input")
            if user_input:
                st.session_state.pdf_messages.append(("Tú", user_input))
                response = model.generate_content([user_input, texto_completo])
                response.resolve()
                st.session_state.pdf_messages.append(("Gemini", response.text))
                st.rerun()

# En la etapa de análisis de audio, fue necesario además de chequear la documentación, consultar algunos proyectos similares en GitHub, 
# ya que estaba ocasionando algunos problemas. Finalmente todo salió bien. Algunas partes similares a las pestañas anteriores.
with aba4:
    if selected_language == "Español":
        st.write("### Análisis de Audio")
        st.write("📍 **¡Envía un audio!**: Envía un audio y haz una pregunta sobre él, ¿quieres un resumen de un audio de 10 minutos? ¡Pruébalo!")
        st.markdown("<p class = aviso> El audio debe contener habla, el bot analizará principalmente la habla (¡que no contenga lenguaje explícito/obscenidades!). Los audios que contengan ruidos/música probablemente darán error.</p>", unsafe_allow_html=True)

        user_prompt = st.text_input("Escribe tu pregunta sobre el audio:", placeholder="Por ejemplo... 'Resúmeme este audio'")

        audio_file = st.file_uploader("Envía tu archivo", type=['wav', 'mp3'])
        if audio_file is not None:
            audio_path = save_uploaded_file(audio_file)
            st.audio(audio_path)

            if st.button('¡Procesar!'):
                with st.spinner('Procesando...'):
                    processed_text = process_audio(audio_path, user_prompt)
                    st.text_area("Respuesta: ", processed_text, height=300)

    elif selected_language == "English":
        st.write("### Audio Review")
        st.write("📍 **Send an audio!**: Send an audio and ask a question about it, want a summary of a 10-minute audio? Try it out!")
        st.markdown("<p class = aviso> The audio must contain speech, the bot will mainly analyse speech (that doesn't contain explicit language/obscenities!). Audio that contains noise/music is likely to give an error. </p>", unsafe_allow_html=True)

        user_prompt = st.text_input("Enter your custom AI prompt:", placeholder="E.g., 'Please summarize the audio:'")

        audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
        if audio_file is not None:
            audio_path = save_uploaded_file(audio_file)
            st.audio(audio_path)

            if st.button('Process Audio'):
                with st.spinner('Processing...'):
                    processed_text = process_audio(audio_path, user_prompt)
                    st.text_area("Processed Output", processed_text, height=300)


with aba5:
    #! Contenido Dinámico con Base en el Idioma
    if selected_language == "Español":
        st.write("### Sobre")
        st.write("Este sitio fue construido usando la biblioteca Streamlit de Python a través de la API de Google Gemini, la inteligencia artificial de Google.")

        # Gemini
        st.image('./img/gemini.png', caption='Gemini AI')
        # Streamlit
        st.image('./img/Streamlit.png', caption='Streamlit Logo')

        
        st.write("### Sobre el Proyecto")
        st.write("Este ChatBot es parte del proyecto TURISMO VERDE, diseñado para ofrecer soporte interactivo en tiempo real a los usuarios.")
        st.write("#### Desarrolladores:")
        st.write("- **Nombre del Desarrollador**: xennie")
        st.write("- **Nombre del Desarrollador**: xennie")
        st.write("#### Tecnologías Usadas:")
        st.write("- Python")
        st.write("- Streamlit")
        st.write("- Google Gemini AI")

    elif selected_language == "English":
        st.write("### About")
        st.write("This site was built using the Streamlit python library via the Google Gemini API, Google's artificial intelligence.")
        
        # Gemini
        st.image('./img/gemini.png', caption='Gemini AI')

        # Streamlit
        st.image('./img/Streamlit.png', caption='Streamlit Logo')

        # Additional Project Information
        st.write("### About the Project")
        st.write("This ChatBot is part of the TURISMO VERDE project, designed to offer real-time interactive support to users.")
        st.write("#### Developers:")
        st.write("- **Developer's Name**: Developer's Role")
        st.write("- **Developer's Name**: Developer's Role")
        st.write("#### Technologies Used:")
        st.write("- Python")
        st.write("- Streamlit")
        st.write("- Google Gemini AI")
