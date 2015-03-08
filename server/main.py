import socketserver
import argparse
import json
from tracker import Tracker

class Response:
	def __init__(self):
		self.statusCode = True
		self.value = None
		
	def __str__(self):
		s = str("Response Information:\n"
				"	Status: {0}\n"
				"	Value: {1}\n").format(self.statusCode,
										  self.value)
		return s
		
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

class MyTCPHandler(socketserver.BaseRequestHandler):
	"""
	The RequestHandler class for our server.

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""
	
	tracker = Tracker()

	def handle(self):
		recieved = (self.request.recv(1024).strip()).decode()
		
		print ("{0} wrote: {1}".format(self.client_address[0], recieved))
		
		self.data = {}
		response = Response()
		
		try:
			self.data = json.loads(recieved)
			response.value = self.data
		except:
			print ("Bad JSON")
			response.statusCode = False
			response.value = "invalid"
			
		
		# just send back the same data
		self.request.sendall(bytes(response.to_JSON(), 'UTF-8'))

parser = argparse.ArgumentParser()
parser.add_argument('-port', dest='port', type=int, required=False, default=9999)
args = parser.parse_args()
		
host = "localhost"

# Create the server, binding to HOST:PORT
server = socketserver.TCPServer((host, args.port), MyTCPHandler)

# Activate the server; this will keep running until you
# interrupt the program with Ctrl-C
print ('Server running on ' + str(host) + ':' + str(args.port))
server.serve_forever()