#!/usr/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
import time
import MySQLdb as mdb
import logging

# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
# so that any debug messages are written to the file /home/pi/event_error.log.
logging.basicConfig(filename='/home/webservice/mcortshome-api/ws_wind_error.log',
  level=logging.DEBUG,
  format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)


# Create MySQL connection and a DDBB handle
db = mdb.connect(host="localhost", port=3306, user="pi_select", passwd="", db="measurements")
cursor = db.cursor()

# Execute the querie
cursor.execute("SELECT speed, dtg FROM wind ORDER BY dtg DESC LIMIT 1")

for (speed,dtg) in cursor:
  print("The wind at {}Km/h".format(speed))

cursor.close()
db.close() 

#API description
app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@app.route('/mcortshome/ws_wind', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

if __name__ == '__main__':
    app.run(host='0.0.0.0')