import socketserver
import socket
import json
import threading
import os
import hashlib
from math import ceil
import hashlib

BUFFER_SIZE = 1024

class Message:
        def __init__(self):
                self.command = ""
                self.args = None

        def __str__(self):
                s = str("Response Information:\n"
                        "       Command: {0}\n"
                        "       Args: {1}\n").format(self.command,
                                                     self.args)
                return s

        def to_JSON(self):
                return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

class Response:
        def __init__(self):
                self.statusCode = True
                self.value = None

        def __str__(self):
                s = str("Response Information:\n"
                        "       Status: {0}\n"
                        "       Value: {1}\n").format(self.statusCode,
                                                      self.value)
                return s

        def to_JSON(self):
                return json.dumps(self, default=lambda o: o.__dict__)

class ClientTCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		while True:
			request = self.request.recvfrom(BUFFER_SIZE)
			received = request[0].strip().decode()
			addr = request[1]
			if received == '':
				break
			
			#print ("{0} wrote: {1}".format(self.client_address[0], received))
			
			data = {}
			command = ""
			args = None
			
			response = Response()

			try:
				data = json.loads(received)
				command = data["command"]
				args = data["args"]
			except:
				print ("Invalid Message Format")
				response.statuscode = False
				response.value = "invalid"
				self.request.sendall(bytes(response.to_JSON(), 'UTF-8'))
			
			if command == 'get':
				readTotal = 0
				info = args['info']
				f = open('file/'+info['name']+'.'+info['extension'],'rb')
				f.seek(info['chunksize']*args['startChunk'])
				while readTotal != info['chunksize']:
					readBuf = f.read(BUFFER_SIZE)
					if readBuf.decode() == "": #end of file
						break
					readBuf = self.generatePrefix(readBuf) + readBuf
					self.request.sendall(readBuf)
					readTotal += BUFFER_SIZE
				
				f.close()

				response.statusCode = True
				response.value = 'done'
				message = bytes(response.to_JSON(),'UTF-8')
				message = self.generatePrefix(message) + message
				self.request.sendall(message)

	def generatePrefix(self, message):
		size = str(len(message))
		size = ("0" * (4 - len(size))) + size
		size = bytes(size, 'UTF-8')
		return size


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

class Client:
	def __init__(self, port, serverIP, serverPort):
		self.host = socket.gethostbyname(socket.gethostname())
		self.port = port

		self.serverIP = serverIP
		self.serverPort = serverPort

		# Create the server, binding to HOST:PORT
		server = ThreadedTCPServer((self.host, self.port), ClientTCPHandler)

		# Activate the server; this will keep running until you
		# interrupt the program with Ctrl-C
		print ('Client running on ' + str(self.host) + ':' + str(self.port))
		thread = threading.Thread(target=server.serve_forever)
		thread.daemon = True
		thread.start()

		self.torrents = []

	def addTorrent(self, info):
		for torrent in self.torrents:
			if info[0]["name"] == torrent.info["name"]:
				return False

		newTorrent = TorrentInstance(info, self)
		self.torrents.append(newTorrent)
		thread = threading.Thread(target=newTorrent.run)
		thread.daemon = True
		thread.start()
		return True

class TorrentInstance:
	def __init__(self, info, client):
		self.writeLock = threading.Lock()
		self.info = info[0]
		self.peers = info[1]
		self.client = client

	def run(self):
		fname = 'file/' + self.info['name'] + '.'+ self.info['extension']
		nchunks = ceil(self.info['size'] / self.info['chunksize'])
		print (nchunks)
		if os.access(fname,os.F_OK):
			finfo = os.stat(fname)
			if finfo.st_size == self.info['size']:
				h = hashlib.sha1()
				f = open(fname)
				while True:
					chunk = f.read(BUFFER_SIZE)
					if len(chunk) == 0:
						break
					h.update(chunk.encode('utf-8'))
				fileHash = h.hexdigest()
				if fileHash == self.info["full_hash"]:
					print ("File already downloaded")
					self.sendAddressToTracker()
					return
			else:
				pass

		self.fid = open(fname,'wb')
		self.currentHash = [None]*nchunks

		peerConnections = []
		for i in self.peers:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				sock.connect((i['ip'],i['port']))
				peerConnections.append(sock)
			except:
				print ("Unable to connect to " + i['ip'] + ":" + str(i['port']))
				pass

		if not peerConnections:
			print ("No peers available. Download failed.")#FIXME
			return
		
		threadList = []
		for i in range(len(peerConnections)):
			startChunk = ceil(nchunks/len(peerConnections))*i
			thread = threading.Thread(target = self.download, args = [peerConnections[i],startChunk])
			threadList.append(thread)
			thread.start()

		for i in threadList:
			i.join()

		print ('Download Complete')

		#fileinfo.create_file_info(fname,self.info['name'])

		

	def download(self,sock,startChunk):
		current = startChunk
		while (True):

			if current >= ceil(self.info['size'] / self.info['chunksize'])-1:
				current = 0

			message = Message()
			message.command = 'get'
			message.args = TorrentDownloadRequest(self.info,current)

			sock.send(bytes(message.to_JSON(), 'UTF-8'))

			in_buffer = ''

			while (True):
				replySize = int(sock.recv(4))
				reply = sock.recv(replySize)

				if reply == b'':
					continue

				try:
					r = reply.strip().decode()
					r = json.loads(r)
					if r['value'] == 'done':
						break
				
				except:
					in_buffer = in_buffer + reply.decode()

			with self.writeLock:
				in_buffer = bytes(in_buffer,'UTF-8')
				self.fid.seek(self.info['chunksize'] * current)
				self.fid.write(in_buffer)

			#update chunk hashes
			h = hashlib.sha1()
			h.update(in_buffer)
			self.currentHash[current] = h.hexdigest()		
			
			current +=1
			
			#If all chunks loaded
			if self.currentHash == self.info['chunk_hashes']:
				break
		
		sock.close()

		self.sendAddressToTracker()

	def sendAddressToTracker(self):
		trackerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			# Connect to server
			trackerSock.connect((self.client.serverIP, self.client.serverPort))
		except:
			print('Couldn\'t connect to server.')
			return

		message = Message()
		
		message.command = "upload"
		message.args = {}
		message.args["name"] = self.info["name"]
		message.args["ip"] = self.client.host
		message.args["port"] = self.client.port

		trackerSock.sendall(bytes(message.to_JSON(), 'UTF-8'))

		received = trackerSock.recv(BUFFER_SIZE)
		response = json.loads(received.decode())
				
		if response["statusCode"] == True:
			print ("Client's address successfully sent to tracker for seeding")
		else:
			print ("Something went horribly wrong when sending address to tracker")
		

class TorrentDownloadRequest:
	def __init__(self,info,startChunk):
		self.info = info
		self.startChunk = startChunk

	def startByte(self):
		return self.info.chunkSize * self.startChunk
