#!/usr/bin/python
# -*- coding: utf-8 -*-

from gpiozero import Button
import RPi.GPIO as GPIO
import smtplib
import datetime
import time
import MySQLdb as mdb
import logging
import os
import fnmatch
import json
from home_network import find_network_nodes
from pprint import pprint
import sys
import logging
import paho.mqtt.client as mqtt

# To avoid the error on rc.local execution envirotment: 
#WARNING urllib3.connectionpool Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
# so that any debug messages are written to the file /home/pi/event_error.log.
logging.basicConfig(filename='/home/pi/door_event_error.log',
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Read the configuration file
DEFAULT_CONFIG_PATH = '/home/pi/config.json'
with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
  config = json.load(config_file)

# Function for storing readings into MySQL
def insertDB(plaptime,p_whois):
  try:
    con = mdb.connect('localhost',
                      config['db_update_user'],
                      config['db_update_password'],
                      'measurements');
    cursor = con.cursor()
    sql = "INSERT INTO main_door(laptime,name) VALUES ('%s','%s')" % (plaptime,p_whois)
    cursor.execute(sql)
    sql = []
    con.commit()
    con.close()
  except mdb.Error as e:
    logger.error(e)

# Function for send an email notifing the door is open and who did
def send_email_open_door(p_whois):
  # Specifying the from and to addresses
  fromaddr = config['mail']['fromaddr']
  toaddr = config['mail']['toaddr']
  cc = config['mail']['cc']
# bcc = ['mail@dominio.com']
  message_subject = "[DOOR] Home main door open alert"
  message_text = "The door was opened at: %s\r\n" % time.strftime("%c") + "And %s" % p_whois + " are in the house." 
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

# Function for publish MQTT messages
def publish_MQTT_messages (p_whois):
  try:
    client = mqtt.Client()
    # compose the message of who are in the house when the door is open
    topic = config['domohome_door']['topic']
    payload = p_whois
#    print ("Publishing " + payload + " to topic: " + topic + " ...")
    client.connect(config['MQTT']['broker_server_ip'],1883,60)
    client.publish(topic, payload)

    client.disconnect();
  except Exception as e:
    print ("exception")
    logger.error("Exception MQTT sending message: %s\n"+" "+e.__str__())

# Get readings from sensors and store them in MySQL
whois = " "

GPIO.setmode(GPIO.BCM)
GPIO.setup(config['domohome_door']['gpio_pin'], GPIO.IN)
count = 0
while True:
  inputValue = GPIO.input(18)
  if (inputValue == True):
    print("Door open")
    whois = find_network_nodes(" ")
    print(whois)
    if (whois == " "):
      whois = " NOBODY"
      send_email_open_door(whois)
    else:
      if "Carlos" not in whois: 
        send_email_open_door(whois)
    # Store the event in the DDBB
    insertDB(1,whois)
    # publish MQTT message
    publish_MQTT_messages(whois)
    time.sleep(50)
  time.sleep(.01)
