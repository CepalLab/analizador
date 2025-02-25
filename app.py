import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Configurar página
st.set_page_config(page_title="Analizador de Artículos Web", page_icon="📝")

# Título de la aplicación
st.title("📝 Analizador de Artículos Web")

def get_text_from_url(url):
    """
    Obtiene el texto principal de una URL utilizando BeautifulSoup
    """
    try:
        # Realizar la petición HTTP
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Verificar si hay errores en la respuesta
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eliminar scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Obtener el texto
        text = soup.get_text()
        
        # Limpiar el texto (eliminar espacios extra y líneas en blanco)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    except Exception as e:
        return f"Error al obtener el texto de la URL: {str(e)}"

# Obtener la API key de Gemini desde st.secrets
@st.cache_resource
def configure_genai():
    try:
        api_key = st.secrets["GEMMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.error(f"Error al configurar la API: {str(e)}")
        return None

# Sidebar para información
with st.sidebar:
    st.header("Sobre esta app")
    st.markdown("""
    Esta aplicación analiza el contenido de cualquier artículo o página web.
    
    Simplemente introduce la URL y tu pregunta específica, y la IA analizará 
    el contenido para proporcionarte una respuesta.
    
    Powered by Google Gemini 1.5 Flash
    """)

# Interfaz principal
url = st.text_input("URL a analizar:", placeholder="https://ejemplo.com/articulo")
prompt = st.text_area(
    "¿Qué quieres saber sobre este contenido?", 
    placeholder="Ejemplo: Haz un resumen de los puntos principales del artículo",
    height=100
)

analyze_button = st.button("Analizar", type="primary")

# Procesar cuando se hace clic en el botón
if analyze_button and url and prompt:
    # Crear contenedor para el status
    status_container = st.empty()
    
    with status_container.status("Procesando...", expanded=True) as status:
        st.write("⏳ Obteniendo contenido de la URL...")
        texto = get_text_from_url(url)
        
        if texto.startswith("Error"):
            st.error(texto)
            status.update(label="Error", state="error")
        else:
            st.write("🧠 Analizando el contenido con IA...")
            model = configure_genai()
            
            if model:
                try:
                    response = model.generate_content(
                        [prompt, texto],    
                        generation_config=genai.GenerationConfig(
                            max_output_tokens=2000,
                            temperature=0,
                        )
                    )
                    status.update(label="Análisis completado", state="complete")
                except Exception as e:
                    status.update(label="Error", state="error")
                    st.error(f"Error al generar la respuesta: {str(e)}")
                    st.stop()
            else:
                status.update(label="Error de configuración", state="error")
                st.stop()
    
    # Mostrar resultados - FUERA del bloque status
    st.subheader("Resultado del análisis")
    st.markdown(response.text)
    
    # Mostrar información sobre el texto extraído - FUERA del bloque status
    with st.expander("Ver texto extraído"):
        st.text_area("Contenido de la página", texto, height=300)
        
elif analyze_button:
    st.warning("Por favor, introduce una URL y una pregunta.")