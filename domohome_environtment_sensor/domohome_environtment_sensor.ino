#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#include "settings.h"

// Configuración cliente WiFi
WiFiClient espClient;

// Configuración MQTT
PubSubClient clientMqtt(espClient);
long lastMsg = 0;
char msg[50];
String mqttcommand = String(14);

/* Configuración sensor NEOPIXEL */
#define PIN_STRIP_1 2
#define NUMPIXELS_STRIP_1 7
Adafruit_NeoPixel pixels_STRIP_1  = Adafruit_NeoPixel(NUMPIXELS_STRIP_1, PIN_STRIP_1, NEO_GRB + NEO_KHZ800);


/* Configuración sensor DHT22 */
#define DHTPIN            4  
#define DHTTYPE           DHT22     // DHT 22 (AM2302)
float temperature;
float humidity;
DHT_Unified dht(DHTPIN, DHTTYPE);
uint32_t delayMS;

void setup() {
  Serial.begin(115200);

  /* Iiniciar NEOPIXEL */
  pixels_STRIP_1.begin(); // This initializes the NeoPixel library. 
  for(int i=0;i<NUMPIXELS_STRIP_1;i++){
     pixels_STRIP_1.setPixelColor(i, pixels_STRIP_1.Color(0,0,0)); // black color.
     pixels_STRIP_1.show(); // This sends the updated pixel color to the hardware.
  }

  /* Iiniciar wifi */
  setup_wifi();
  clientMqtt.setServer(mqtt_server, mqtt_port);
  clientMqtt.setCallback(callback);

  /* Iiniciar sensor */
  dht.begin();
  Serial.println("DHT22 Unified Sensor initialization");
    // Print temperature sensor details.
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.println("Temperature");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" *C");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" *C");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" *C");  
  Serial.println("------------------------------------");
  // Print humidity sensor details.
  dht.humidity().getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.println("Humidity");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println("%");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println("%");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println("%");  
  Serial.println("------------------------------------");
  // Set delay between sensor readings based on sensor details.
  delayMS = sensor.min_delay / 1000;
}

void setup_wifi() {
  delay(10);

  // Comienza el proceso de conexión a la red WiFi
  Serial.println();
  Serial.print("[WIFI]Conectando a ");
  Serial.println(ssid);

  // Modo estación
  WiFi.mode(WIFI_STA);
  // Inicio WiFi
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("[WIFI]WiFi conectada");
  Serial.print("[WIFI]IP: ");
  Serial.print(WiFi.localIP());
  Serial.println("");
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("[MQTT]Mensaje recibido (");
  Serial.print(topic);
  Serial.print(") ");
  mqttcommand = "";
  for (int i = 0; i < length; i++) {
    mqttcommand += (char)payload[i];
  }
  Serial.print(mqttcommand);
  Serial.println();
  // Switch on the LED if an 1 was received as first character
  if (mqttcommand == "LightOn") {
    pixels_STRIP_1.setPixelColor(0, pixels_STRIP_1.Color(255,255,55));
    pixels_STRIP_1.setPixelColor(1, pixels_STRIP_1.Color(255,255,55));
    pixels_STRIP_1.setPixelColor(5, pixels_STRIP_1.Color(255,255,55));
    pixels_STRIP_1.setPixelColor(6, pixels_STRIP_1.Color(255,255,55));
    pixels_STRIP_1.setPixelColor(2, pixels_STRIP_1.Color(255,255,255));
    pixels_STRIP_1.setPixelColor(3, pixels_STRIP_1.Color(255,255,255));
    pixels_STRIP_1.setPixelColor(4, pixels_STRIP_1.Color(255,255,255));
    pixels_STRIP_1.show(); // This sends the updated pixel color to the hardware.
    Serial.println("LightOn");
  } else if (mqttcommand == "LightOff"){
    for(int i=0;i<NUMPIXELS_STRIP_1;i++){
      pixels_STRIP_1.setPixelColor(i, pixels_STRIP_1.Color(0,0,0)); // black color.
      pixels_STRIP_1.show(); // This sends the updated pixel color to the hardware.
    }
    Serial.println("LightOff");
  } else if (mqttcommand == "Alarm"){
    for (int q=0; q < 100; q++) {
      for(int i=0;i<NUMPIXELS_STRIP_1;i++){
        pixels_STRIP_1.setPixelColor(i, pixels_STRIP_1.Color(255,255,255)); // high bright white color.
        pixels_STRIP_1.show(); // This sends the updated pixel color to the hardware.
      }
      for(int i=0;i<NUMPIXELS_STRIP_1;i++){
        pixels_STRIP_1.setPixelColor(i, pixels_STRIP_1.Color(0,0,0)); // black color.
        pixels_STRIP_1.show(); // This sends the updated pixel color to the hardware.
      }
      delay(100);
    }
    Serial.println("Alarm");
  }
}

void reconnect() {
  Serial.print("[MQTT]Intentando conectar a servidor MQTT... ");
  // Bucle hasta conseguir conexión
  while (!clientMqtt.connected()) {
    Serial.print(".");
    // Intento de conexión
    if (clientMqtt.connect(mqtt_id)) { // Ojo, para más de un dispositivo cambiar el nombre para evitar conflicto
      Serial.println("");
      Serial.println("[MQTT]Conectado al servidor MQTT");
      // Once connected subscribe
      clientMqtt.subscribe(mqtt_sub_topic_operation);
    } else {
      Serial.print("[MQTT]Error, rc=");
      Serial.print(clientMqtt.state());
      Serial.println("[MQTT]Intentando conexión en 5 segundos");

      delay(5000);
    }
  }
}

void loop() {
  if (!clientMqtt.connected()) {
    reconnect();
  }
  clientMqtt.loop();

  long now = millis();
  if (now - lastMsg > update_time) {
    lastMsg = now;

    /* Publicación de temperatura y presión en cada topic */
    sensors_event_t event;  
    dht.temperature().getEvent(&event);
    if (isnan(event.temperature)) {
      Serial.println("Error reading temperature!");
    }
    else {
      Serial.print("Temperature: ");
      temperature = event.temperature;
      Serial.print(temperature);
      Serial.println(" *C");
      snprintf (msg, 6, "%2.1f", temperature);
      Serial.print("[MQTT]Enviando mensaje de temperatura: ");
      Serial.println(msg);
      clientMqtt.publish(mqtt_pub_topic_temperature, msg);
    }
    // Get humidity event and print its value.
    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
      Serial.println("Error reading humidity!");
    }
    else {
      Serial.print("Humidity: ");
      humidity = event.relative_humidity;
      Serial.print(humidity);
      Serial.println("%");
      snprintf (msg, 6, "%2.1f", humidity);
      Serial.print("[MQTT]Enviando mensaje de humedad: ");
      Serial.println(msg);
      clientMqtt.publish(mqtt_pub_topic_humidity, msg);
    }
  }
}

