import socketserver
import socket
import argparse
import json
from tracker import Tracker
from tracker import Response
from tracker import Torrent

class ServerTCPHandler(socketserver.BaseRequestHandler):
	"""
	The RequestHandler class for our server.

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""
	
	tracker = Tracker()

	def handle(self):
		while True:
			received = (self.request.recv(1024).strip()).decode()
			if received == "":
				break

			print ("{0} wrote: {1}".format(self.client_address[0], received))
			
			data = {}
			command = ""
			args = None
			
			response = Response()

			try:
				data = json.loads(received)
			except:
				print('NO NO NO')
			
			try:
				data = json.loads(received)
				command = data["command"]
				args = data["args"]
			except:
				print ("Invalid Message Format")
				response.statusCode = False
				response.value = "invalid"
			
			if command == "post":
				r = ServerTCPHandler.tracker.post(args[0])
				response = ServerTCPHandler.tracker.upload(args[0], args[1])
				if response.statusCode == False:
					response = r

			elif command == 'query':
				response = ServerTCPHandler.tracker.query(args)

			elif command == 'get':
				response = ServerTCPHandler.tracker.get(args)

			elif command == 'peer':
				response = ServerTCPHandler.tracker.peer(args)

			elif command == 'upload':
				response = ServerTCPHandler.tracker.upload(args[0]["name"], args[1])

			else:
				response.statusCode = False
				response.value = "Unknown Command"
			
			# just send back the same data
			self.request.sendall(bytes(response.to_JSON(), 'UTF-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-port', dest='port', type=int, required=False, default=9999)
	args = parser.parse_args()
		
	host = socket.gethostbyname(socket.gethostname())

	# Create the server, binding to HOST:PORT
	server = ThreadedTCPServer((host, args.port), ServerTCPHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	print ('Server running on ' + str(host) + ':' + str(args.port))
	server.serve_forever()

if __name__ == "__main__":
	main()
