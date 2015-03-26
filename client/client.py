import socketserver
import socket
import json
import threading

class ClientTCPHandler(socketserver.BaseRequestHandler):

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
			
			# send back the response
			self.request.sendall(bytes(response.to_JSON(), 'UTF-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

class Client:
	def __init__(self, port):
		host = socket.gethostbyname(socket.gethostname())

		# Create the server, binding to HOST:PORT
		server = ThreadedTCPServer((host, port), ClientTCPHandler)

		# Activate the server; this will keep running until you
		# interrupt the program with Ctrl-C
		print ('Client running on ' + str(host) + ':' + str(port))
		thread = threading.Thread(target=server.serve_forever)
		thread.daemon = True
		thread.start()

		self.torrents = []

	def addTorrent(self, info):
		for torrent in self.torrents:
			if info["name"] == torrent.info["name"]:
				return False

		newTorrent = TorrentInstance(info)
		self.torrents.append(newTorrent)
		thread = threading.Thread(target=newTorrent.run)
		thread.daemon = True
		thread.start()
		return True

class TorrentInstance:
	def __init__(self, info):
		self.info = info

	def run(self):
		pass

