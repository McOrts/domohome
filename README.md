# Un Mosquitto controla mi casa
Este es un proyecto del tipo de los que nunca se acaban, Pero he querido ordenar y documentar la parte principal de este sistema de domótica para poder compartirlo con la comunidad. 

Construido bajo los principios del _Do It Yourselft_, encontraréis todo el código Python, NodeJS, SQL y node-red utilizado. Así como las referencias al open-hardware utilizado: [Raspberry Pi](https://www.raspberrypi.org).

## Mi implementación del IOT

Para montar un sistema de domótica en casa se pueden aplicar muchas soluciones. Y en como tantas otras cosas. Hay una fácil y cara. Y otra difícil y barata. La mía es más bien de estas últimas.

El componente principal de la arquitectura que he utilizado el un _Broker_ de mensajería basado en topic. Los sensores están conectados a puertos GPIO de una mini-CPU que ejecuta un programa específivo para cada uno. Este programa realiza estas tareas:
- Lee el valor del sensor.
- Graba el valor en una BBDD relacional.
- Envía el valor a:
-- Una plataforma de _Cloud_ via API Rest.
-- Un mensaje MQTT a un _topic_ especifico.

Por encima de esta gestión corre una aplicación _middleware_ que subscrita a los _topic_ que toma decisiones acerca de:
- Activar un dispositivo a través de puertos GPIO.
- Enviar avisos a Twitter
- Ofrece un interface de usuario web para operar el sistema

![Arquitectura domohome](https://github.com/McOrts/domohome/blob/master/images/domohome_arquitectura.jpg?raw=true)



Domotic project. Sustainable energy management and home control based on Raspberry Pi

MQTT 

Nace de la necesidad de crear un protocolo ligero y confiable para la comunicación Machine To Machine (M2M).
El significado de sus 
Caracteristicas:
	•	Simple y ligero. Menos requerimientos de proceso y ancho de banda.
	•	Tolerancia a altas latinices. Lo que permite utilizar canales de comunicacion poco óptimos para otros protocolos.
	•	Fiabilidad de entrega de mensajes


Creado en 1999 por Dr. Andy Stanford-Clark de IBM y Arlen Nipper de Eurotech ante la necesidad de orquestar las comunicaciones de un oleoducto. Este especial protocolo nacio por la necesidad de cumplir la restricción de utilizar una comunicaciones por satelite. De manera que en otras redes es muy optimo

En 2011 IBM cedio el codigo a la fundacion Eclipse liberandolo a la comunidad. De manera que su popularización llevo a que en En 2104 se convirtio en un estandard certificado por la organización  para la adopcion del estándares de comercio electrónico y servicios web  OASIS 

Programación en Python

Buena libreria :paho-mqtt 1.3.1
https://pypi.python.org/pypi/paho-mqtt
Eclipse Paho MQTT Python client library, which implements versions 3.1 and 3.1.1 of the MQTT protocol.

## Agradecimientos
* Una vez más a Luis del Valle de [ProgramarFacil](https://programarfacil.com) por su artículo ["Cómo conectar MQTT con ESP8266, Raspberry Pi y Mosquitto"](https://programarfacil.com/esp8266/mqtt-esp8266-raspberry-pi/)
* R. A. Light, "Mosquitto: server and client implementation of the MQTT protocol," The Journal of Open Source Software, vol. 2, no. 13, May 2017, DOI: [10.21105/joss.00265](http://dx.doi.org/10.21105/joss.00265)
