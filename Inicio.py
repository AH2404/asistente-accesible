import streamlit as st

from servicios.ajustes import PUERTO_MQTT, barra_lateral
from servicios.puerta import obtener_puerta

st.set_page_config(page_title="Asistente accesible", page_icon="🦾")
barra_lateral()
ss = st.session_state

st.title("🦾 Asistente accesible")
st.subheader("Ver, escuchar y actuar sin usar las manos")
st.write(
    "Una sola app con una idea: que una persona sin brazos pueda entender su entorno "
    "y controlarlo con la voz. La app describe imágenes, lee textos en voz alta y "
    "abre una puerta inteligente, y siempre responde hablando."
)

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🖼️ Asistente\nDescribe imágenes y lee textos en voz alta.")
    st.page_link("pages/1_Asistente.py", label="Abrir el Asistente", icon="🖼️")
with col2:
    st.markdown(
        "#### 🚪 Puerta inteligente\nÁbrela y ciérrala con tu voz; el ESP32 simulado "
        "en Wokwi confirma cada orden."
    )
    st.page_link("pages/2_Puerta.py", label="Abrir la Puerta", icon="🚪")

st.divider()


@st.fragment(run_every=3)
def estado_puerta():
    puerta = obtener_puerta(ss["broker"], PUERTO_MQTT, ss["prefijo"])
    estado = puerta.estado_texto if puerta.conectado else None
    st.metric("Estado de la puerta", estado.capitalize() if estado else "Sin datos")


estado_puerta()

st.markdown("**Actividad reciente**")
historial = ss.get("historial", [])
if historial:
    st.markdown("\n".join(f"- {evento}" for evento in historial[:8]))
else:
    st.caption("Aún no hay actividad. Prueba el Asistente o la Puerta.")
