import streamlit as st
import google.generativeai as genai
import tempfile
import os

# Configurar la página
st.set_page_config(
    page_title="Analizador de PDFs con Gemini",
    page_icon="📑",
    layout="wide"
)

# Título y descripción
st.title("📑 Analizador de Documentos PDF con Google Gemini")
st.markdown("""
Esta aplicación te permite analizar documentos PDF utilizando el modelo Gemini 1.5 Flash de Google.
Sube un archivo PDF y obtén respuestas detalladas sobre el contenido del documento.
""")

# Configurar Gemini API
@st.cache_resource
def configure_genai():
    try:
        api_key = st.secrets["GEMMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.error(f"Error al configurar la API: {str(e)}")
        return None

# Sidebar con información
with st.sidebar:
    st.header("Sobre esta app")
    st.markdown("""
    ### Funcionamiento
    1. Sube un archivo PDF
    2. Escribe tus preguntas o usa las predefinidas
    3. Haz clic en 'Analizar documento'
    
    ### Tecnología
    - Google Gemini 1.5 Flash
    - Streamlit
    
    ### Limitaciones
    - Tamaño máximo de archivo: 20MB
    - Solo analiza archivos PDF
    """)

# Área de carga de archivos
uploaded_file = st.file_uploader("Sube un documento PDF", type=["pdf"])

# Área de texto para preguntas
st.subheader("¿Qué quieres saber sobre este documento?")
default_prompt = """
Podrías responder a todas estas preguntas: 

1. ¿De qué trata el documento?
2. ¿Cuál es el nombre del documento?
3. ¿Quiénes son los autores del documento?
4. ¿Qué división elaboró el documento?
5. ¿Cuáles son los principales mensajes del documento?
6. ¿Cuáles son los principales tópicos que aborda el documento?
7. ¿A qué países hace referencia el documento?
8. ¿Cuáles son los principales datos que entrega el documento?
9. ¿Qué recomendaciones da el documento?
10. ¿Cuántos capítulos tiene el documento?
"""

user_prompt = st.text_area(
    "Preguntas:",
    value=default_prompt,
    height=250,
    help="Puedes modificar las preguntas predefinidas o escribir las tuyas propias"
)

# Botón para analizar
analyze_button = st.button("Analizar documento", type="primary", disabled=not uploaded_file)

# Procesar cuando se hace clic en el botón
if analyze_button and uploaded_file is not None:
    # Mostrar un spinner mientras se procesa
    with st.status("Procesando documento...", expanded=True) as status:
        try:
            st.write("⏳ Cargando modelo...")
            model = configure_genai()
            
            if not model:
                status.update(label="Error de configuración", state="error")
                st.stop()
            
            # Guardar temporalmente el archivo subido
            st.write("📄 Preparando archivo PDF...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Subir archivo a Gemini
            st.write("🚀 Enviando documento a Google Gemini...")
            pdf_file = genai.upload_file(tmp_file_path)
            
            # Generar la respuesta
            st.write("🧠 Analizando contenido...")
            response = model.generate_content(
                [user_prompt, pdf_file],
                generation_config=genai.GenerationConfig(
                    max_output_tokens=4000,  # Aumentado para respuestas más completas
                    temperature=0,
                )
            )
            
            # Limpiar el archivo temporal
            os.unlink(tmp_file_path)
            
            status.update(label="Análisis completado", state="complete")
            
            # Mostrar la respuesta
            st.subheader("Resultados del análisis")
            st.markdown(response.text)
            
            # Opción para descargar la respuesta
            st.download_button(
                label="Descargar resultados",
                data=response.text,
                file_name="analisis_documento.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            status.update(label="Error", state="error")
            st.error(f"Se produjo un error durante el análisis: {str(e)}")
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)  # Limpiar archivo temporal en caso de error
                except:
                    pass

# Instrucciones cuando no hay archivo
if not uploaded_file:
    st.info("👆 Sube un archivo PDF para comenzar el análisis")

# Footer
st.markdown("---")
st.caption("Desarrollado con ❤️ por el CEPAL Lab")