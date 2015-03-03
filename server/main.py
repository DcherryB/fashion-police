import socketserver
import argparse

class MyTCPHandler(socketserver.BaseRequestHandler):
	"""
	The RequestHandler class for our server.

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""

	def handle(self):
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024).strip()
		print ("{} wrote:".format(self.client_address[0]))
		print (self.data)
		# just send back the same data, but upper-cased
		self.request.sendall(self.data.upper())

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