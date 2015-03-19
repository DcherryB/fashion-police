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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-host', dest='host', type=str, required=False, default='localhost')
	parser.add_argument('-port', dest='port', type=int, required=False, default=9999)
	args = parser.parse_args()

	# Create a socket (SOCK_STREAM means a TCP socket)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		# Connect to server
		sock.connect((args.host, args.port))
	except:
		print('Couldn\'t connect to server.')
		return

	while(True):
		
		print ("Choose an Action:")
		print ("0) Create a Torrent")
		print ("1) Query Torrents")
		print ("2) Download a torrent")
		print ("3) Quit")
	
		val = -1
		while val < 0:
			try:
				x = int(input(":"))
				if x >= 0 and x <= 3:
					val = x
			except:
				print ("Invalid Integer")
	
		if val == 0:
			print ("Enter the File's Path:")
			path = ""
			while len(path) == 0:
				path = input(":")
			
			print ("Enter the Torrent's Name:")
			name = ""
			while len(name) == 0:
				name = input(":")

			info = fileinfo.generate_torrent_info(path, name)
			print(info)
			
			message  = Message()
			message.command = "post"
			message.args = info
		
			sock.sendall(bytes(message.to_JSON(), 'UTF-8'))
		
			#Receive data from the server
			received = sock.recv(1024)
		
			#print stuff
			print ("Sent:     {}".format(message.to_JSON()))
			print ("Received: {}".format(received))
		
			response = json.loads(received.decode())
			if response["statusCode"] == True:
				print ("Torrent successfully created and sent to tracker")
		
				torrent = fileinfo.Torrent(info)
				torrent.save_info()
				torrent.save_status()
			else:
				print ("Torrent unsuccessfully sent to tracker, reason: " + response["value"])
	
		elif val == 1:
			message  = Message()
			message.command = "query"
			message.args = {}
		
			sock.sendall(bytes(message.to_JSON(), 'UTF-8'))
		
			#Receive data from the server
			received = sock.recv(1024)

			response = json.loads(received.decode())
			if response["statusCode"] == True:
				print ("Query Results:")
				print (response['value'])
			else:
				print ("Your query was shit, friend")
		elif val == 2:
			print ("Not Implemented")
		elif val == 3:
			break
		
		print ()
	
	sock.close()

if __name__ == "__main__":
	main()
