import socketserver
import socket
import json
import threading
import os
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
			request = self.request.recvfrom(1024)
			received = request[0].strip().decode()
			addr = request[1]
			if received == "":
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
					if readBuf == '': #end of file
						break
					readBuf = self.generatePrefix(readBuf) + readBuf
					self.request.sendall(readBuf)
					readTotal += BUFFER_SIZE
				
				f.close()

				response.statusCode = True
				response.value = 'done'
				message = bytes(response.to_JSON(), 'UTF-8')
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
		if os.access(fname,os.F_OK):
			finfo = os.stat(fname)
			if finfo.st_size == self.info['size']:
				return
			else:
				pass

		self.fid = open(fname,'wb')

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
		while (True):
			message = Message()
			message.command = 'get'
			message.args = TorrentDownloadRequest(self.info,current)

			sock.send(bytes(message.to_JSON(), 'UTF-8'))

			in_buffer = []

			while (True):
				replyLength = int(sock.recv(4))
				reply = sock.recv(replyLength)
				if reply == "":
					continue

				try:
					reply = reply.decode()
					print (reply)
					reply = json.loads(reply)
					print (reply)
					if reply['value'] == 'done':
						break
				except:
					in_buffer.append(reply)

			
			block = ""
			for i in in_buffer:
				if type(i) != str:
					i = str(i)
				block += i

			h = hashlib.sha1()
			h.update(block.encode('utf-8'))
			blockHash = h.hexdigest()
			print (blockHash)
			
			if blockHash != self.info['chunk_hashes'][current]:
				print ("BAD BLOCK HASH")
				continue	

			with self.writeLock:
				self.fid.seek(self.info['chunksize'] * current)
				self.fid.write(bytes(block,'UTF-8'))
				self.fid.flush()

			++current
			if current > ceil(self.info['size'] / self.info['chunksize']):
				current = 0			

			#TODO: do full file hash check
			fname = 'file/' + self.info['name'] + '.'+ self.info['extension']
			finfo = os.stat(fname)
			if finfo.st_size == self.info['size']:
				print ("Download Complete")
				break
			
		sock.close()
		

class TorrentDownloadRequest:
	def __init__(self,info,startChunk):
		self.info = info
		self.startChunk = startChunk

	def startByte(self):
		return self.info.chunkSize * self.startChunk
