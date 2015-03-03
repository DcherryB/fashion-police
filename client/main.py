import socket
import sys
import fileinfo
import json
import argparse

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
	sock.sendall(bytes(args.data + "\n", 'UTF-8'))

	# Receive data from the server and shut down
	received = sock.recv(1024)

	#print stuff
	print ("Sent:     {}".format(args.data))
	print ("Received: {}".format(received))
except:
	print('Couldn\'t connect to server.')
finally:
	sock.close()

info = fileinfo.read_file(args.path, args.name)
print(info)

validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
filename = ''.join(c for c in args.name if c in validchars) + '.' + info['extension']

f = open(filename + '.fashion', 'w')
f.write(json.dumps(info))
f.close()