"""Cliente MQTT de la puerta: envía órdenes al ESP32 (Wokwi) y recibe su estado."""
import json
import time
import uuid

import paho.mqtt.client as mqtt
import streamlit as st


class Puerta:
    def __init__(self, broker: str, puerto: int, prefijo: str):
        self.topic_cmd = f"{prefijo}/cmd"
        self.topic_estado = f"{prefijo}/estado"
        self.estado = None  # último JSON recibido, p. ej. {"estado": "abierta", "angulo": 90}
        self.ultima_actualizacion = 0.0
        self.conectado = False

        self._cliente = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=f"streamlit_{uuid.uuid4().hex[:8]}"
        )
        self._cliente.on_connect = self._on_connect
        self._cliente.on_disconnect = self._on_disconnect
        self._cliente.on_message = self._on_message
        self._cliente.connect_async(broker, puerto)
        self._cliente.loop_start()

    def _on_connect(self, cliente, userdata, flags, reason_code, properties):
        self.conectado = not reason_code.is_failure
        if self.conectado:
            cliente.subscribe(self.topic_estado)

    def _on_disconnect(self, cliente, userdata, flags, reason_code, properties):
        self.conectado = False

    def _on_message(self, cliente, userdata, msg):
        try:
            self.estado = json.loads(msg.payload)
            self.ultima_actualizacion = time.time()
        except ValueError:
            pass

    @property
    def estado_texto(self):
        """'abierta', 'cerrada' o None si todavía no se conoce."""
        return self.estado.get("estado") if self.estado else None

    def ejecutar(self, accion: str, espera: float = 4.0) -> str:
        """Envía una orden y espera la confirmación del ESP32.

        Devuelve 'ok', 'sin_conexion', 'error_envio' o 'sin_respuesta'.
        """
        if not self.conectado:
            return "sin_conexion"
        inicio = time.time()
        info = self._cliente.publish(self.topic_cmd, json.dumps({"accion": accion}))
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            return "error_envio"
        while time.time() - inicio < espera:
            if self.ultima_actualizacion > inicio:
                return "ok"
            time.sleep(0.1)
        return "sin_respuesta"


@st.cache_resource(show_spinner=False)
def obtener_puerta(broker: str, puerto: int, prefijo: str) -> Puerta:
    """Una única conexión MQTT compartida por todas las páginas y recargas."""
    return Puerta(broker, puerto, prefijo)
