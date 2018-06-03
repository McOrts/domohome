#!/usr/bin/python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json
from pprint import pprint
import logging
import RPi.GPIO as GPIO
from gpiozero import Button

# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
# so that any debug messages are written to the file /home/pi/event_error.log.
logging.basicConfig(filename='/home/pi/o_irrigation.log',
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Read the configuration file
DEFAULT_CONFIG_PATH = '/home/pi/config.json'
with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
  config = json.load(config_file)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings (False)
GPIO.setup(config['domohome_irrigation']['gpio_pin_output'], GPIO.OUT)
GPIO.output(config['domohome_irrigation']['gpio_pin_output'], GPIO.HIGH)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
#	print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	topic = config['domohome_irrigation']['topic']
	client.subscribe (topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	if str(msg.payload) == 'on':
		print(str(msg.payload))
		GPIO.output(config['domohome_irrigation']['gpio_pin_output'], GPIO.LOW)
	else:
		print(str(msg.payload))
		GPIO.output(config['domohome_irrigation']['gpio_pin_output'], GPIO.LOW)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(config['MQTT']['broker_server_ip'],1883,60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
