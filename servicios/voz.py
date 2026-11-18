"""Voz: texto a voz (gTTS), voz a texto (Whisper) e interpretación de órdenes."""
import io
import re
import unicodedata

import streamlit as st
from gtts import gTTS
from openai import OpenAI

MAX_CARACTERES = 5000


@st.cache_data(show_spinner=False)
def texto_a_audio(texto: str, idioma: str = "es", lento: bool = False) -> bytes:
    """Convierte texto en MP3 (cacheado por entrada)."""
    buffer = io.BytesIO()
    gTTS(text=texto, lang=idioma, slow=lento).write_to_fp(buffer)
    return buffer.getvalue()


def hablar(texto, forzar=False, autoplay=True, lento=False, idioma=None) -> None:
    """Reproduce el texto en voz alta si el ajuste global de voz está activo."""
    if not (forzar or st.session_state.get("voz_activa", True)):
        return
    idioma = idioma or st.session_state.get("idioma", "es")
    try:
        audio = texto_a_audio(texto[:MAX_CARACTERES], idioma, lento)
        st.audio(audio, format="audio/mpeg", autoplay=autoplay)
    except Exception as e:
        st.warning(f"No pude generar la voz: {e}")


def audio_a_texto(audio_bytes: bytes, api_key: str, idioma: str = "es") -> str:
    """Transcribe audio con Whisper."""
    client = OpenAI(api_key=api_key)
    respuesta = client.audio.transcriptions.create(
        model="whisper-1", file=("orden.wav", audio_bytes), language=idioma
    )
    return respuesta.text.strip()


ABRIR = {"abre", "abrir", "abras", "abra", "abrime"}
CERRAR = {"cierra", "cerrar", "cierres", "cierre"}
ESTADO = {"estado", "abierta", "cerrada"}
NEGACION = {"no", "nunca", "tampoco"}


def _palabras(texto: str) -> set:
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn"
    )
    return set(re.findall(r"[a-z]+", sin_tildes))


def interpretar_orden(texto: str):
    """Devuelve 'abrir', 'cerrar', 'estado' o None si la orden no es clara."""
    p = _palabras(texto)
    if p & NEGACION:
        return None
    abrir, cerrar = bool(p & ABRIR), bool(p & CERRAR)
    if abrir and cerrar:
        return None
    if abrir or cerrar:
        return "abrir" if abrir else "cerrar"
    return "estado" if p & ESTADO else None
