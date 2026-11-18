"""Descripción de imágenes con un modelo de visión."""
import base64

from openai import OpenAI

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
    b64 = base64.b64encode(imagen).decode("utf-8")
    nombre_idioma = IDIOMA_NOMBRES.get(idioma, "español")
    respuesta = OpenAI(api_key=api_key).chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{ESTILOS[estilo]} Responde en {nombre_idioma}."},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ],
    )
    return respuesta.choices[0].message.content
