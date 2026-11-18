import hashlib

import streamlit as st

from servicios.ajustes import PREFIJO_POR_DEFECTO, PUERTO_MQTT, barra_lateral, registrar
from servicios.puerta import obtener_puerta
from servicios.voz import audio_a_texto, hablar, interpretar_orden

st.set_page_config(page_title="Puerta inteligente", page_icon="🚪")
barra_lateral()
ss = st.session_state

st.title("🚪 Puerta inteligente")
st.write(
    "Abre y cierra la cerradura simulada en Wokwi con tu voz o con botones. "
    "El ESP32 confirma cada orden por MQTT y la app te responde hablando."
)

puerta = obtener_puerta(ss["broker"], PUERTO_MQTT, ss["prefijo"])
if ss["prefijo"] == PREFIJO_POR_DEFECTO:
    st.warning(
        "Estás usando el prefijo de topics por defecto. Cámbialo por uno único tuyo "
        "(barra lateral y sketch de Wokwi): el broker es público y compartido."
    )


@st.fragment(run_every=2)
def panel_estado():
    if not puerta.conectado:
        st.error("Sin conexión con el broker MQTT.")
    elif puerta.estado_texto == "abierta":
        st.success("🔓 Puerta abierta")
    elif puerta.estado_texto == "cerrada":
        st.info("🔒 Puerta cerrada")
    else:
        st.warning("Esperando el estado del ESP32. ¿Está corriendo la simulación en Wokwi?")


panel_estado()

ERRORES = {
    "sin_conexion": "No tengo conexión con la puerta.",
    "error_envio": "No pude enviar la orden.",
    "sin_respuesta": "Envié la orden pero la puerta no respondió. Revisa que la simulación esté corriendo.",
}


def ejecutar(accion: str, origen: str) -> None:
    resultado = puerta.ejecutar(accion)
    if resultado == "ok":
        if accion == "estado":
            texto = f"La puerta está {puerta.estado_texto}."
        else:
            texto = f"Listo, la puerta está {puerta.estado_texto}."
        ss["respuesta_puerta"] = ("ok", texto)
    else:
        texto = ERRORES[resultado]
        ss["respuesta_puerta"] = ("error", texto)
    registrar("🚪", f"Orden «{accion}» por {origen}: {resultado}")
    hablar(texto, idioma="es")


def procesar_voz(datos: bytes) -> None:
    if not ss.get("api_key"):
        ss["respuesta_puerta"] = ("error", "Falta la API key de OpenAI en la barra lateral.")
        return
    try:
        with st.spinner("Escuchando..."):
            ss["escuchado"] = audio_a_texto(datos, ss["api_key"], "es")
    except Exception as e:
        ss["respuesta_puerta"] = ("error", f"No pude transcribir el audio: {e}")
        return
    accion = interpretar_orden(ss["escuchado"])
    if accion is None:
        texto = "No entendí la orden. Prueba con «abre la puerta» o «cierra la puerta»."
        ss["respuesta_puerta"] = ("error", texto)
        registrar("🚪", "Orden de voz no reconocida")
        hablar(texto, idioma="es")
    else:
        ejecutar(accion, "voz")


st.subheader("🎙️ Por voz")
st.caption("Di, por ejemplo: «abre la puerta», «cierra la puerta» o «¿cuál es el estado?»")
grabacion = st.audio_input("Graba tu orden")
if grabacion is not None:
    datos = grabacion.getvalue()
    huella = hashlib.md5(datos).hexdigest()
    if huella != ss.get("ultima_grabacion"):  # procesa cada grabación una sola vez
        ss["ultima_grabacion"] = huella
        procesar_voz(datos)
if ss.get("escuchado"):
    st.caption(f"Escuché: «{ss['escuchado']}»")

st.subheader("🖱️ Con botones")
c1, c2, c3 = st.columns(3)
if c1.button("🔓 Abrir", type="primary"):
    ejecutar("abrir", "botón")
if c2.button("🔒 Cerrar"):
    ejecutar("cerrar", "botón")
if c3.button("❓ Estado"):
    ejecutar("estado", "botón")

tipo, mensaje = ss.get("respuesta_puerta", (None, None))
if mensaje:
    (st.success if tipo == "ok" else st.error)(mensaje)

with st.expander("Detalles técnicos"):
    st.write(f"Órdenes → `{puerta.topic_cmd}`  ·  Estado ← `{puerta.topic_estado}`")
    st.json(puerta.estado or {})
