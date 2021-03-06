# Name of the mongodb server
DATABASE_HOST = "127.0.0.1"

# port of the mongodb service
DATABASE_PORT = 27017
# database that we will be playing with
DATABASE_NAME = "recordkeeper"

# enable for DEBUG messages to be printed
DEBUG=False

# IP that the basic webserver will start on
WEBSERVER_HOST = '0.0.0.0'
# PORT that the basic webserver will listen on
WEBSERVER_PORT = 5000

try:
	from local_settings import *
except ImportError:
	pass

