#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from gpiozero import Button
from random import randint
import RPi.GPIO as GPIO
import smtplib
import time
import MySQLdb as mdb
import logging
import os
import fnmatch
import json
from pprint import pprint

# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
# so that any debug messages are written to the file /home/pi/event_error.log.
logging.basicConfig(filename='/home/pi/xmas_error.log',
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Read the configuration file
DEFAULT_CONFIG_PATH = '/home/pi/config.json'
with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
  config = json.load(config_file)
#pprint(config)
#print(config['db_password'])

# Function for readings into MySQL the last Sunset
def read_last_sunset():
  try:
    global last_sunset
    con = mdb.connect('localhost',
                     config['db_read_user'],
                     config['db_read_password'],
                     'measurements');
    cursor = con.cursor()
    sql = "SELECT event, dtg FROM solar WHERE event = 'Sunset' ORDER BY dtg DESC LIMIT 1"
    cursor.execute(sql)
    for (event,dtg) in cursor:
      if event == 'Sunset':
        last_sunset = dtg
#        print (dtg.strftime("%c"))
    sql = []
    con.commit()
    con.close()
  except mdb.Error, e:
    logger.error(e)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings (False)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, GPIO.HIGH)

est_pre = 'OFF'
delay_time = randint(0,90)
print (delay_time)

while True:
  read_last_sunset()
  #print (datetime.time(last_sunset))

  current_time=datetime.time(datetime.now())
  start_time=datetime.time(last_sunset + timedelta(minutes=delay_time))
  end_time=datetime.time(last_sunset + timedelta(minutes=delay_time + 120))
  print (current_time)
  print (start_time)
  print (end_time)

  if  current_time >= start_time:
    if current_time < end_time:
      GPIO.output(13, GPIO.LOW)
      print ("Switch-ON")
      # if est_pre == 'OFF':
        # send_email_irrigation('ON')
      est_pre = 'ON'
    else:
      GPIO.output(13, GPIO.HIGH)
      print ("Switch-OFF")
      #if est_pre == 'ON':
        # send_email_irrigation('OFF')
        # insertDB(start_time,end_time)
      est_pre = 'OFF'
  time.sleep(60)
 

