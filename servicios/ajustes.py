"""Ajustes compartidos por todas las páginas: idioma, voz, claves y actividad."""
from datetime import datetime

import streamlit as st

IDIOMAS = {"Español": "es", "English": "en", "Français": "fr", "Português": "pt"}
BROKER_POR_DEFECTO = "157.230.214.127"
PREFIJO_POR_DEFECTO = "puerta_CAMBIAME"
PUERTO_MQTT = 1883


def _secreto(nombre: str, defecto: str = "") -> str:
    try:
        return st.secrets[nombre]
    except Exception:
        return defecto


def barra_lateral() -> None:
    """Dibuja la barra lateral común y deja los ajustes en st.session_state."""
    with st.sidebar:
        st.header("⚙️ Ajustes")
        nombre = st.selectbox(
            "Idioma de descripciones y lectura", list(IDIOMAS), key="nombre_idioma"
        )
        st.session_state["idioma"] = IDIOMAS[nombre]
        st.toggle("🔊 Responder también con voz", value=True, key="voz_activa")

        clave = _secreto("OPENAI_API_KEY")
        if clave:
            st.caption("🔑 API key cargada desde secrets")
        else:
            clave = st.text_input("OpenAI API Key", type="password", key="clave_manual")
        st.session_state["api_key"] = clave

        with st.expander("Conexión de la puerta (MQTT)"):
            st.session_state["broker"] = st.text_input(
                "Broker", value=_secreto("MQTT_BROKER", BROKER_POR_DEFECTO), key="in_broker"
            )
            st.session_state["prefijo"] = st.text_input(
                "Prefijo de topics",
                value=_secreto("MQTT_PREFIJO", PREFIJO_POR_DEFECTO),
                key="in_prefijo",
            )


def registrar(icono: str, texto: str) -> None:
    """Añade un evento al historial compartido por todas las páginas."""
    historial = st.session_state.setdefault("historial", [])
    historial.insert(0, f"{datetime.now():%H:%M:%S} · {icono} {texto}")
    del historial[20:]
