"""Descripción de imágenes con Gemini."""
from google import genai
from google.genai import types

from servicios.ajustes import MODELO_GEMINI

IDIOMA_NOMBRES = {"es": "español", "en": "inglés", "fr": "francés", "pt": "portugués"}

ESTILOS = {
    "Breve": "Describe la imagen en una o dos frases.",
    "Detallada": (
        "Describe la imagen con detalle: objetos, personas, colores, "
        "ambiente, texto visible y relaciones entre los elementos."
    ),
    "Accesible": (
        "Describe la imagen para una persona con discapacidad visual: "
        "empieza por lo más importante, indica la posición de los elementos "
        "y lee cualquier texto visible."
    ),
}


def describir_imagen(api_key: str, imagen: bytes, mime: str, estilo: str, idioma: str) -> str:
    nombre_idioma = IDIOMA_NOMBRES.get(idioma, "español")
    client = genai.Client(api_key=api_key)
    respuesta = client.models.generate_content(
        model=MODELO_GEMINI,
        contents=[
            types.Part.from_bytes(data=imagen, mime_type=mime),
            f"{ESTILOS[estilo]} Responde en {nombre_idioma}.",
        ],
    )
    return (respuesta.text or "").strip()
