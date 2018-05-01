import os
import time
import MySQLdb as mdb
import logging
import fnmatch

def find_network_nodes(nodes_found):
	# Then the code sets up the logging module. We are going to use the basicConfig() function to set up the default handler 
	# so that any debug messages are written to the file find_network_nodes_error.log
	logging.basicConfig(filename='/home/pi/find_network_nodes_error.log',
	  level=logging.DEBUG,
	  format='%(asctime)s %(levelname)s %(name)s %(message)s')
	logger=logging.getLogger(__name__)

	# Read the configuration file
	DEFAULT_CONFIG_PATH = '/home/pi/config.json'
	with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
  	config = json.load(config_file)

  	# obtain the list of MacAddress of the devices connected to the LAN
	os.system('sudo nmap -sP 192.168.1.* > nmap_results.txt')

	# Find users of the devices
	try:
		con = mdb.connect('localhost',
                     config['db_read_user'],
                     config['db_read_password'],
	                      'configurations');
		cursor = con.cursor()
		sql = "SELECT name,mac_address FROM net_devices"
		cursor.execute(sql)
		for (name,mac_address) in cursor:
			f = open('nmap_results.txt', 'r')
			for line in f:
				if mac_address in line: 
					nodes_found += name + ", "
			f.close()
		sql = []
		con.commit()
		con.close()
	except mdb.Error, e:
		logger.error(e)
	return nodes_found