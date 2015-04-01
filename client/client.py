import socketserver
import socket
import json
import threading
import os
import hashlib
from math import ceil

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
			if received == b'':
				break
			
			print ("{0} wrote: {1}".format(self.client_address[0], received))
			
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
					print (readBuf)
					if readBuf == b'':
						break
					self.request.sendall(readBuf)
					readTotal += BUFFER_SIZE
				
				f.close()

				response.statusCode = True
				response.value = 'done'
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
		self.writeLock = threading.Lock()
		self.info = info[0]
		self.peers = info[1]

	def run(self):
		fname = 'file/' + self.info['name'] + '.'+ self.info['extension']
		nchunks = ceil(self.info['size'] / self.info['chunksize'])
		print (nchunks)
		if os.access(fname,os.F_OK):
			finfo = os.stat(fname)
			if finfo.st_size == self.info['size']:
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
				pass

		if not peerConnections:
			print ("No peers available. Download failed.")#FIXME
			return

		for i in range(len(peerConnections)):
			startChunk = ceil(nchunks/len(peerConnections))*i
			thread = threading.Thread(target = self.download, args = [peerConnections[i],startChunk])
			thread.start()

	def download(self,sock,startChunk):
		current = startChunk
		print (current)
		while (True):
			message = Message()
			message.command = 'get'
			message.args = TorrentDownloadRequest(self.info,current)

			sock.send(bytes(message.to_JSON(), 'UTF-8'))

			in_buffer = ''

			while (True):
				reply = sock.recv(BUFFER_SIZE)
				print (type(reply))
				if reply == "":
					continue

				try:
					r = reply.strip().decode()
					r = json.loads(r)
					if r['value'] == 'done':
						break
				
				except:
					#if type(reply) == str:
					print(type(reply))
					in_buffer = in_buffer + reply.decode()
					#in_buffer = in_buffer.join(reply)

			with self.writeLock:
				in_buffer = bytes(in_buffer,'UTF-8')
				self.fid.seek(self.info['chunksize'] * current)
				self.fid.write(in_buffer)

			#update chunk hashes
			h = hashlib.sha1()
			h.update(in_buffer)
			self.currentHash[current] = h.hexdigest()
			
			
			current +=1
			if current >= ceil(self.info['size'] / self.info['chunksize'])-1:
				current = 0
			
			#If all chunks loaded
			print (self.currentHash)
			print (self.info['chunk_hashes'])
			print (in_buffer)
			if self.currentHash == self.info['chunk_hashes']:
				break
			
		sock.close()
		

class TorrentDownloadRequest:
	def __init__(self,info,startChunk):
		self.info = info
		self.startChunk = startChunk

	def startByte(self):
		return self.info.chunkSize * self.startChunk
