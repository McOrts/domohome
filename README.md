# Un Mosquitto controla mi casa
Este es un proyecto del tipo de los que nunca se acaban, Pero he querido ordenar y documentar la parte principal de este sistema de domótica que he instalado en mi casa, para poder compartirlo con la comunidad. 

Construido bajo los principios del _Do It Yourselft_, [aquí encontraréis todo el código](https://github.com/McOrts/domohome) Python, NodeJS, SQL y node-red utilizado. Así como las referencias al open-hardware utilizado: [Raspberry Pi](https://www.raspberrypi.org).

## Mi implementación del IOT

Para montar un sistema de domótica en casa se pueden aplicar muchas soluciones. Y en como tantas otras cosas. Hay una fácil y cara. Y otra difícil y barata. La mía es más bien de estas últimas.

El componente principal de la arquitectura que he utilizado el un _Broker_ de mensajería basado en _topic_. Los sensores están conectados a puertos GPIO de una mini-CPU que ejecuta un programa específivo para cada uno. Este programa realiza las siguientes tareas:
- Lee el valor del sensor. 
- Graba el valor en una BBDD relacional.
- Envía el valor a:
	- Una plataforma de _Cloud_ via API Rest.
	- Un mensaje MQTT a un _topic_ especifico.

Por encima de esta gestión corre una aplicación _middleware_ que subscrita a los _topics_, toma decisiones acerca de:
- Activar un dispositivo a través de puertos GPIO.
- Enviar avisos a Twitter.
- Ofrece un interface de usuario web para operar el sistema.
![Arquitectura domohome](https://github.com/McOrts/domohome/blob/master/images/domohome_arquitectura.jpg?raw=true)
Lo sensores también se pueden construir incorporados en microcontroladores dedicados operando de forma autónoma. El valor entonces en enviado en un mensaje MQTT por un canal inalámbrico o físico a _broker_. En sucesivos artículos describiré otras muchas maneras de implementar sensores. 

## MQTT ¿Qué, cuándo y dónde?

En 1999 dos ingenieros, el Dr. Andy Stanford-Clark de IBM y Arlen Nipper de Eurotech. Estaban participando en la construcción de un oleoducto con el reto de conectar online sus 4.000 sensores a un sistema centralizado de SCADA. Utilizando un enlace de satélite como única comunicación posible.

Y así se diseñó este protocolo MQTT a fin de cumplir la restricción de utilizar una comunicación costosa, de banda estrecha y con latencias importantes. Siendo sus caracteristicas principales:
- __Simple y ligero__. Con menos requerimientos de proceso y ancho de banda.
- __Tolerancia a altas latencias__. Lo que permite utilizar canales de comunicacion poco óptimos para otros protocolos.
- __Fiabilidad__ de entrega de mensajes.

En 2012 Andy Stanford-Clark contó su experiencia y su visión del futuro de la IOT basado en MQTT en esta famosa conferencia TED:

[![TEDxWarwick](https://github.com/McOrts/domohome/blob/master/images/TedTalk_Andy_2012.png?raw=true)](https://youtu.be/s9nrm8q5eGg)
En 2011 IBM cedió el codigo a la fundacion Eclipse liberandolo a la comunidad. De manera que su popularización llevo a que en En 2014 se conviertiera en un estandard certificado por la Organización para la Adopcion del Estándas de Comercio Electrónico y Servicios Web ( [OASIS](https://www.oasis-open.org/news/announcements/mqtt-version-3-1-1-becomes-an-oasis-standard)).
 
## Manos a la obra 

Lo primero, definir la estructura de los _topic_ que necesito usar. Un _topic_ al fin y al cavo es un buzón público de correo que cualquiera puede luego leer. Con la caracteristica especial de que pueden organizarse gerárquimanente. En mi caso este es el árbol:
`-- home
    |-- meteo
    |   `-- solar
    `-- storageroom
        |-- humidity
        `-- temperature

Programación en Python

Buena libreria :paho-mqtt 1.3.1
https://pypi.python.org/pypi/paho-mqtt
Eclipse Paho MQTT Python client library, which implements versions 3.1 and 3.1.1 of the MQTT protocol.

## Agradecimientos y referencias
- [MQTT.org](http://mqtt.org)
- Una vez más a Luis del Valle de [ProgramarFacil](https://programarfacil.com) por su artículo ["Cómo conectar MQTT con ESP8266, Raspberry Pi y Mosquitto"](https://programarfacil.com/esp8266/mqtt-esp8266-raspberry-pi/)
- R. A. Light, "Mosquitto: server and client implementation of the MQTT protocol," The Journal of Open Source Software, vol. 2, no. 13, May 2017, DOI: [10.21105/joss.00265](http://dx.doi.org/10.21105/joss.00265)
- IBM Developers [MQTT: Enabling the Internet of Things](https://developer.ibm.com/messaging/2013/04/26/mqtt-enabling-internet-things/)
