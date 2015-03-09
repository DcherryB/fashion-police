import socketserver
import argparse
import json
from tracker import Tracker
from tracker import Response

class MyTCPHandler(socketserver.BaseRequestHandler):
	"""
	The RequestHandler class for our server.

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""
	
	tracker = Tracker()

	def handle(self):
		while True:
			recieved = (self.request.recv(1024).strip()).decode()
			if recieved == "":
				break
			
			print ("{0} wrote: {1}".format(self.client_address[0], recieved))
			
			data = {}
			command = ""
			args = None
			
			response = Response()
			
			try:
				data = json.loads(recieved)
				command = data["command"]
				args = data["args"]
			except:
				print ("Invalid Message Format")
				response.statusCode = False
				response.value = "invalid"
			
			if command == "post":
				response = MyTCPHandler.tracker.post(args) 
			else:
				response.statusCode = False
				response.value = "Unknown Command"
			
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