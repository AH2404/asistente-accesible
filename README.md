# Asistente accesible

App multipágina en Streamlit para que una persona sin brazos pueda entender su entorno
y controlarlo con la voz: describe imágenes, lee textos en voz alta y abre una puerta
inteligente simulada en Wokwi. La app siempre responde hablando.

## Estructura

```
Inicio.py              Página de inicio (resumen, estado de la puerta, actividad)
pages/1_Asistente.py   Descripción de imágenes + lectura de textos en voz alta
pages/2_Puerta.py      Control de la puerta por voz y botones, con estado en vivo
servicios/             Lógica compartida: ajustes, voz, visión y MQTT
wokwi/sketch.ino       Firmware del ESP32 (servo + LED, MQTT bidireccional)
```

## Comunicación Streamlit ↔ Wokwi (MQTT)

| Dirección | Topic | Mensaje |
|---|---|---|
| Streamlit → ESP32 | `<prefijo>/cmd` | `{"accion": "abrir" \| "cerrar" \| "estado"}` |
| ESP32 → Streamlit | `<prefijo>/estado` | `{"estado": "abierta" \| "cerrada", "angulo": 90}` |
| ESP32 → broker | `<prefijo>/pulso` | `1` cada 15 s (latido para mantener la conexión) |

## Puesta en marcha

1. `pip install -r requirements.txt`
2. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y completa tu API key y un prefijo único.
3. En Wokwi: crea un proyecto ESP32 y copia `wokwi/sketch.ino`, `wokwi/diagram.json` y `wokwi/libraries.txt`.
   Usa el mismo prefijo en `TOPIC_CMD` y `TOPIC_ESTADO`.
4. Inicia la simulación y ejecuta `streamlit run Inicio.py`.
