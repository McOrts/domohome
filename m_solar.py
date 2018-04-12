#!/usr/bin/python
# -*- coding: utf-8 -*-

import artikcloud
from gpiozero import Button
from artikcloud.rest import ApiException
import RPi.GPIO as GPIO
import smtplib
import datetime
import time
import MySQLdb as mdb
import os
import fnmatch
import json
from pprint import pprint
import sys
import logging
import paho.mqtt.client as mqtt

# To avoid the error on rc.local execution envirotment: 
#WARNING urllib3.connectionpool Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
# so that any debug messages are written to the file /home/pi/event_error.log.
logging.basicConfig(filename='/home/pi/solar_event_error.log',
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Read the configuration file
DEFAULT_CONFIG_PATH = '/home/pi/config.json'
with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
  config = json.load(config_file)

# Function for storing readings into MySQL
def insertDB(p_event):
  try:
    con = mdb.connect('localhost',
                      config['db_update_user'],
                      config['db_update_password'],
                      'measurements');
    cursor = con.cursor()
    sql = "INSERT INTO solar(event) VALUES ('%s')" % (p_event)
    cursor.execute(sql)
    sql = []
    con.commit()
    con.close()
  except mdb.Error as e:
    logger.error(e)

# Function for readings into MySQL the last Sunrise
def read_last_sunrise():
  try:
    global g_last_sunrise
    con = mdb.connect('localhost',
                      config['db_read_user'],
                      config['db_read_password'],
                      'measurements');
    cursor = con.cursor()
    sql = "SELECT event, dtg FROM solar WHERE event = 'Sunrise' ORDER BY dtg DESC LIMIT 1"
    cursor.execute(sql)
    for (event,dtg) in cursor:
      if event == 'Sunrise':
        g_last_sunrise = dtg
#        print (dtg.strftime("%c"))
    sql = []
    con.commit()
    con.close()
  except mdb.Error as e:
    logger.error(e)

# Function for publish MQTT messages
def publish_MQTT_messages (p_event):
  try:
    client = mqtt.Client()
    # compose the message of humidity
    topic = config['domohome_solar']['topic']
    payload = p_event
#    print ("Publishing " + payload + " to topic: " + topic + " ...")
    client.connect(config['MQTT']['broker_server_ip'],1883,60)
    client.publish (topic, payload)

    client.disconnect();
  except Exception as e:
    print ("exception")
    logger.error("Exception MQTT sending message: %s\n"+" "+e.__str__())

# Function for send  the data to de IOT Cloud
def send_data_IOT_cloud(p_sunrise, p_sunset, p_insolation):
  try:
    # SDK reference for more details
    # https://github.com/artikcloud/artikcloud-python

    # Configure Oauth2 access_token for the client application.  Here we have used
    # the device token for the configuration
    artikcloud.configuration = artikcloud.Configuration();
    artikcloud.configuration.access_token = config['domohome_solar']['device_token']

    # We create an instance of the Message API class which provides
    # the send_message() and get_last_normalized_messages() api call
    # for our example
    api_instance = artikcloud.MessagesApi()

    # Device_message - data that is sent to your device
    device_message = {}
    device_message['insolation'] = p_insolation    
    device_message['sunrise'] = p_sunrise
    device_message['sunset'] = p_sunset
    
    # Set the 'device id' - value from your config.json file
    device_sdid = config['domohome_solar']['device_id']

    # set your custom timestamp
    ts = None

    # Construct a Message object for your request
    data = artikcloud.Message(device_message, device_sdid, ts)
    #print(data)

    #pprint(artikcloud.configuration.auth_settings())

    # Send Message
    api_response = api_instance.send_message(data)
    #pprint(api_response)

  except ApiException as e:
    pprint("Exception when calling MessagesApi->send_message: %s\n" % e)
    logger.error("Exception when calling MessagesApi->send_message: %s\n" % e)
    

# Get readings from sensors and store them in MySQL
button = Button(5)

est_pre = 'D'
interval = 300

while True:
    if button.is_pressed:
        if est_pre == 'D':
#          print("Sunrise")
          est_pre = 'L'
          insertDB('Sunrise')
          publish_MQTT_messages('Sunrise')
        time.sleep(interval)
    else:
        if est_pre == 'L':
#          print("Sunset")
          est_pre = 'D'
          insertDB('Sunset')
          publish_MQTT_messages('Sunset')
          # calculate the sunset time 
          sunset_time_decimal = float(time.strftime("%-H"))+float(time.strftime("%-M"))/60
          # calculate the daylight duration
          read_last_sunrise ()
          sunrise_time_decimal = float(g_last_sunrise.strftime("%-H"))+float(g_last_sunrise.strftime("%-M"))/60
          insolation_time_decimal = sunset_time_decimal - sunrise_time_decimal
 #         print (sunrise_time_decimal)
 #         print (sunset_time_decimal)
 #         print (insolation_time_decimal)
          send_data_IOT_cloud(sunrise_time_decimal,sunset_time_decimal,insolation_time_decimal)
        time.sleep(interval)
