#!/usr/bin/python
# -*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
import artikcloud
from artikcloud.rest import ApiException
import smtplib
import datetime
import time
import MySQLdb as mdb
import logging
import os
import fnmatch
import math
import json
from pprint import pprint
import sys

#PYTHON 3
#import asyncio
#PYTHON 2
import trollius as asyncio

import websocket
import Adafruit_DHT as dht
import paho.mqtt.client as mqtt

# To avoid the error on rc.local execution envirotment: 
#WARNING urllib3.connectionpool Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
# so that any debug messages are written to the file /home/pi/event_error.log.
logging.basicConfig(filename='/home/pi/humidity_event_error.log',
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Read the configuration file
DEFAULT_CONFIG_PATH = '/home/pi/config.json'
with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
  config = json.load(config_file)

# Function for storing readings into MySQL
def insertDB(humidity,temperature):
  try:
    con = mdb.connect(config['db_server_ip'],
                      config['db_update_user'],
                      config['db_update_password'],
                      'measurements');
    cursor = con.cursor()
    sql = "INSERT INTO humidity(humidity_percentage,temperature) VALUES ('%s', '%s')" % (humidity,temperature)
    cursor.execute(sql)
    sql = []
    con.commit()
    con.close()
  except mdb.Error as e:
    logger.error(e)

# Function for send an email notifing the humidity reach the maximum 
def send_email_humidity(p_cc, p_humidity, p_temperature):
    # Specifying the from and to addresses
    fromaddr = config['mail']['fromaddr']
    toaddr = config['mail']['toaddr']
    cc = config['mail']['cc']
#    bcc = ['mail@dominio.com']
    message_subject = "[HUMIDITY] Home humidity alert"
    message_text = "The humidity is: %s" % '{:3.2f}'.format(p_humidity / 1.) + " with a temperature of: %s" % '{:3.2f}'.format(p_temperature / 1.)+ "C"
    if p_cc:
      # cc version
      message = "From: %s\r\n" % fromaddr + "To: %s\r\n" % toaddr + "CC: %s\r\n" % ",".join(cc) + "Subject: %s\r\n" % message_subject + "\r\n"  + message_text
      toaddrs = [toaddr] + [cc] 
    else:
      message = "From: %s\r\n" % fromaddr + "To: %s\r\n" % toaddr + "Subject: %s\r\n" % message_subject + "\r\n"  + message_text
      toaddrs = [toaddr]
    # Sending the mail  
    try:
      server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
      server.ehlo()
      server.login(config['mail']['username'],config['mail']['password'])
      # ssl server doesn't support or need tls, so don't call server.starttls() 
      server.sendmail(fromaddr, toaddrs, message)
      server.close()
      # print 'successfully sent the mail'
    except:
      print ("failed to send mail")

# Function for send  the data to de IOT Cloud
def send_data_IOT_cloud(p_humidity, p_temperature):
  try:
    # SDK reference for more details
    # https://github.com/artikcloud/artikcloud-python

    # Configure Oauth2 access_token for the client application.  Here we have used
    # the device token for the configuration
    artikcloud.configuration = artikcloud.Configuration();
    artikcloud.configuration.access_token = config['domohome_storageroom_humidity']['device_token']

    # We create an instance of the Message API class which provides
    # the send_message() and get_last_normalized_messages() api call
    # for our example
    api_instance = artikcloud.MessagesApi()

    # Device_message - data that is sent to your device
    device_message = {}
    device_message['humidity']=int(round(p_humidity, 0))
    device_message['temp']=round(p_temperature, 1)

    # Set the 'device id' - value from your config.json file
    device_sdid = config['domohome_storageroom_humidity']['device_id']

    # set your custom timestamp
    ts = None

    # Construct a Message object for your request
    data = artikcloud.Message(device_message, device_sdid, ts)
    #print(data)

    #pprint(artikcloud.configuration.auth_settings())

    # Send Message
    api_response = api_instance.send_message(data)
    #pprint(api_response)

  except Exception as e:
    pprint("Exception when calling MessagesApi->send_message: %s\n" % e)
    logger.error("Exception when calling MessagesApi->send_message: %s\n" % e)

# Function for publish MQTT messages
def publish_MQTT_messages (p_humidity, p_temperature):
  try:
    client = mqtt.Client()
    # compose the message of humidity
    topic = config['domohome_storageroom_humidity']['topic_humidity']
    payload = '{:3.2f}'.format(p_humidity / 1.)
#    print ("Publishing " + payload + " to topic: " + topic + " ...")
    client.connect(config['MQTT']['broker_server_ip'],1883,60)
    client.publish (topic, payload)

    # compose the message of temperature
    topic = config['domohome_storageroom_humidity']['topic_temperature']
    payload = '{:3.2f}'.format(p_temperature / 1.)
#    print "Publishing " + payload + " to topic: " + topic + " ..."
    client.connect(config['MQTT']['broker_server_ip'],1883,60)
    client.publish (topic, payload)

    client.disconnect();
  except Exception as e:
    print ("exception")
    logger.error("Exception MQTT sending message: %s\n"+" "+e.__str__())

while True:
  # Read agein the configuration file for hot changes
  DEFAULT_CONFIG_PATH = '/home/pi/config.json'
  with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

  # Read the measurements
  humidity,temperature = dht.read_retry(dht.DHT22, config['domohome_storageroom_humidity']['gpio_pin'])
#  print('{:3.2f}'.format(humidity / 1.))
#  print('{:3.2f}'.format(temperature / 1.))

  # Store the measurements in the DDBB
  insertDB (humidity,temperature)

  # Send an warning email if the humidity reach at maximum
  if humidity > config['domohome_storageroom_humidity']['max_warning']:
    send_email_humidity(True,humidity,temperature)

  # send the data to de IOT Cloud
  send_data_IOT_cloud (humidity,temperature)

  # publish MQTT messages
  publish_MQTT_messages (humidity,temperature)

  time.sleep(3600)