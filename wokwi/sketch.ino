#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// ---------- Configuración ----------
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "157.230.214.127";
const int mqtt_port = 1883;

const char* TOPIC_CMD = "puerta_gato_q7x4m2/cmd";        // Streamlit -> ESP32
const char* TOPIC_ESTADO = "puerta_gato_q7x4m2/estado";  // ESP32 -> Streamlit
const char* TOPIC_PULSO = "puerta_gato_q7x4m2/pulso";    // latido para mantener la conexión
const char* CLIENT_ID = "puerta_gato_q7x4m2_esp32";      // identificador único en el broker

const int PIN_SERVO = 13;
const int PIN_LED = 2;
const int ANGULO_CERRADA = 0;
const int ANGULO_ABIERTA = 90;
const unsigned long INTERVALO_PULSO = 15000;  // ms de simulación

// ---------- Objetos y estado ----------
WiFiClient espClient;
PubSubClient client(espClient);
Servo servo;
bool puertaAbierta = false;
bool yaConecto = false;
unsigned long ultimoPulso = 0;

// ---------- Funciones ----------
void setup_wifi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void publicarEstado() {
  StaticJsonDocument<100> doc;
  doc["estado"] = puertaAbierta ? "abierta" : "cerrada";
  doc["angulo"] = puertaAbierta ? ANGULO_ABIERTA : ANGULO_CERRADA;
  char buffer[100];
  serializeJson(doc, buffer);
  client.publish(TOPIC_ESTADO, buffer, true);  // retained: Streamlit lo recibe al conectarse
  Serial.print("Estado publicado: ");
  Serial.println(buffer);
}

void moverPuerta(bool abrir) {
  puertaAbierta = abrir;
  servo.write(abrir ? ANGULO_ABIERTA : ANGULO_CERRADA);
  digitalWrite(PIN_LED, abrir ? HIGH : LOW);
  publicarEstado();
}

void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<128> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
    Serial.print("JSON inválido: ");
    Serial.println(error.c_str());
    return;
  }

  const char* accion = doc["accion"] | "";
  Serial.print("Comando recibido: ");
  Serial.println(accion);

  if (strcmp(accion, "abrir") == 0) {
    moverPuerta(true);
  } else if (strcmp(accion, "cerrar") == 0) {
    moverPuerta(false);
  } else if (strcmp(accion, "estado") == 0) {
    publicarEstado();
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT...");
    if (client.connect(CLIENT_ID)) {
      Serial.println("conectado");
      yaConecto = true;
      client.subscribe(TOPIC_CMD);
      publicarEstado();
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" reintentando en 5 s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  servo.setPeriodHertz(50);
  servo.attach(PIN_SERVO, 500, 2400);
  servo.write(ANGULO_CERRADA);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setKeepAlive(60);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    if (yaConecto) {
      Serial.print("Desconectado del broker, state=");
      Serial.println(client.state());
    }
    reconnect();
  }
  client.loop();

  // Latido: actividad frecuente para que el broker no cierre la conexión
  if (millis() - ultimoPulso > INTERVALO_PULSO) {
    ultimoPulso = millis();
    client.publish(TOPIC_PULSO, "1");
  }
}
