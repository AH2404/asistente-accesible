import streamlit as st

from servicios.ajustes import barra_lateral, registrar
from servicios.vision import ESTILOS, describir_imagen
from servicios.voz import hablar, texto_a_audio

st.set_page_config(page_title="Asistente", page_icon="🖼️")
barra_lateral()
ss = st.session_state

st.title("🖼️ Asistente de visión y lectura")
st.write("Entiende lo que ves y escucha lo que lees. Las respuestas se leen en voz alta.")

tab_imagen, tab_texto = st.tabs(["🖼️ Describir una imagen", "📖 Leer un texto"])

with tab_imagen:
    origen = st.radio("Origen", ["Subir archivo", "Cámara"], horizontal=True)
    if origen == "Subir archivo":
        imagen = st.file_uploader("Imagen", type=["png", "jpg", "jpeg", "webp"])
    else:
        imagen = st.camera_input("Toma una foto")
    estilo = st.selectbox("Tipo de descripción", list(ESTILOS), index=2)

    if imagen:
        st.image(imagen)

    if st.button("Describir imagen", type="primary", disabled=imagen is None):
        if not ss.get("api_key"):
            st.warning("Falta la API key de Gemini en la barra lateral.")
        else:
            try:
                with st.spinner("Analizando la imagen..."):
                    ss["descripcion"] = describir_imagen(
                        ss["api_key"], imagen.getvalue(), imagen.type or "image/jpeg",
                        estilo, ss["idioma"],
                    )
                registrar("🖼️", f"Describí una imagen (estilo {estilo.lower()})")
                hablar(ss["descripcion"])
            except Exception as e:
                st.error(f"No se pudo describir la imagen: {e}")

    if ss.get("descripcion"):
        st.subheader("Descripción")
        st.write(ss["descripcion"])
        if st.button("🔊 Escuchar de nuevo"):
            hablar(ss["descripcion"], forzar=True)

with tab_texto:
    archivo = st.file_uploader("Opcional: sube un archivo .txt", type=["txt"])
    inicial = archivo.getvalue().decode("utf-8", errors="ignore") if archivo else ""
    texto = st.text_area("Texto a leer", value=inicial, height=200).strip()
    lento = st.checkbox("Lectura lenta")

    if st.button("Leer en voz alta", type="primary"):
        if not texto:
            st.warning("Escribe o sube un texto primero.")
        else:
            registrar("📖", f"Leí en voz alta un texto de {len(texto)} caracteres")
            hablar(texto, forzar=True, lento=lento)
            try:
                st.download_button(
                    "Descargar MP3", texto_a_audio(texto[:5000], ss["idioma"], lento),
                    file_name="lectura.mp3", mime="audio/mpeg",
                )
            except Exception:
                pass
