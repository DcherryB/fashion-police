import socket
import sys
import fileinfo
import json

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	# Connect to server and send data
	sock.connect((HOST, PORT))
	sock.sendall(bytes(data + "\n", 'UTF-8'))

	# Receive data from the server and shut down
	received = sock.recv(1024)

	#print stuff
	print ("Sent:     {}".format(data))
	print ("Received: {}".format(received))
except:
	print('Couldn\'t connect to server.')
finally:
	sock.close()

info = fileinfo.read_file(sys.argv[1], sys.argv[2])
print(info)

validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
filename = ''.join(c for c in sys.argv[2] if c in validchars) + '.' + info['extension']

f = open(filename + '.fashion', 'w')
f.write(json.dumps(info))
f.close()