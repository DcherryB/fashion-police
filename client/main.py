import socket
import sys
import fileinfo
import json
import argparse

class Message:
	def __init__(self):
		self.command = ""
		self.args = None
		
	def __str__(self):
		s = str("Response Information:\n"
				"	Command: {0}\n"
				"	Args: {1}\n").format(self.command,
										  self.args)
		return s
		
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

parser = argparse.ArgumentParser()
parser.add_argument('-host', dest='host', type=str, required=False, default='localhost')
parser.add_argument('-port', dest='port', type=int, required=False, default=9999)
parser.add_argument('-data', dest='data', type=str, required=True)
parser.add_argument('-path', dest='path', type=str, required=True)
parser.add_argument('-name', dest='name', type=str, required=True)
args = parser.parse_args()

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	# Connect to server and send data
	sock.connect((args.host, args.port))
	
	message = Message()
	message.command = "test"
	message.args = args.data
	
	sock.sendall(bytes(message.to_JSON(), 'UTF-8'))

	# Receive data from the server and shut down
	received = sock.recv(1024)

	#print stuff
	print ("Sent:     {}".format(message.to_JSON()))
	print ("Received: {}".format(received))
except:
	print('Couldn\'t connect to server.')
finally:
	sock.close()

torrent = fileinfo.read_file(args.path, args.name)
print(torrent)

validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
filename = ''.join(c for c in args.name if c in validchars) + '.' + torrent.extension

f = open(filename + '.fashion', 'w')
f.write(torrent.to_JSON())
f.close()