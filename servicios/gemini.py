"""Llamadas a Gemini con reintentos y modelo de respaldo."""
import time

from google import genai
from google.genai import errors

# El primero es el preferido; los siguientes son respaldo si no está disponible.
MODELOS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]
REINTENTOS = 3
ERRORES_TEMPORALES = (500, 503, 504)  # se reintenta con el mismo modelo
ERRORES_DE_MODELO = (404, 429)        # se pasa al siguiente modelo


def generar_texto(api_key: str, contenido: list) -> str:
    """Envía el contenido a Gemini y devuelve el texto de la respuesta."""
    client = genai.Client(api_key=api_key)
    ultimo_error = None
    for modelo in MODELOS:
        for intento in range(REINTENTOS):
            try:
                respuesta = client.models.generate_content(model=modelo, contents=contenido)
                return (respuesta.text or "").strip()
            except errors.APIError as e:
                ultimo_error = e
                if e.code in ERRORES_TEMPORALES:
                    time.sleep(1.5 * (intento + 1))
                    continue
                if e.code in ERRORES_DE_MODELO:
                    break
                raise
    raise ultimo_error
