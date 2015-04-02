import socket
import sys
import fileinfo
import json
import argparse
from client import Client

BUF_SIZE = 1024

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
	parser.add_argument('-I', dest='serverIP', type=str, required=False, default='127.0.1.1')
	parser.add_argument('-P', dest='serverPort', type=int, required=False, default=9999)
	parser.add_argument('-p', dest='port', type=int, required=False, default=9998)
	args = parser.parse_args()

	# Create a socket (SOCK_STREAM means a TCP socket)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		# Connect to server
		sock.connect((args.serverIP, args.serverPort))
	except:
		print('Couldn\'t connect to server.')
		return

	client = Client(args.port, args.serverIP, args.serverPort)
	clientAddr = (socket.gethostbyname(socket.gethostname()),args.port)

	while(True):
		
		print ("Choose an Action:")
		print ("0) Create a Torrent")
		print ("1) Query Torrents")
		print ("2) Download a torrent")
		print ("3) Lookup peers (debug purposes)")
		print ("4) Quit")
	
		val = -1
		while val < 0:
			try:
				x = int(input(":"))
				if x >= 0 and x <= 4:
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
			if info != None:
				print(info)
			
				message  = Message()
				message.command = "post"
				message.args = (info,clientAddr)
		
				sock.sendall(bytes(message.to_JSON(), 'UTF-8'))
		
				#Receive data from the server
				received = sock.recv(BUF_SIZE)
		
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

			answer = ""
			wait = True
			print ("Would you like to use a search phrase? (y/n): ")
			while wait == True:
				answer = input(":")
				answer = answer.lower()
				if answer == "y" or answer == "n":
					wait = False
				else:
					print ("Please enter y or n")

			if answer == "y":
				print ("Enter the search phrase:")
				phrase = ""
				while len(phrase) == 0:
					phrase = input(":")
				message.args["name"] = phrase.strip()
		
			sock.sendall(bytes(message.to_JSON(), 'UTF-8'))
		
			#Receive data from the server
			received = sock.recv(BUF_SIZE)

			response = json.loads(received.decode())
			if response["statusCode"] == True:
				print ("Query Results:")
				print (response['value'])
			else:
				print ("Your query was shit, friend")
		elif val == 2:
			name = ""
			print ("Enter the torrent's name: ")
			while len(name) == 0:
				name = input(":")

			message = Message()
			message.command = "get"
			message.args = name

			sock.sendall(bytes(message.to_JSON(), 'UTF-8'))

			#Receive data from the server
			received = sock.recv(BUF_SIZE)

			response = json.loads(received.decode())
			if response["statusCode"] == True:
				print ("Torrent successfully recieved from tracker")
				print (response['value'])
				print ("Starting file download")
				if client.addTorrent(response['value']) == False:
					print ("Unable to start file download, identical torrent already in client")
			else:
				print ("Unable to find torrent on tracker")

		elif val == 3:
			name = ""
			print ("Enter the torrent's name:")
			while len(name) == 0:
				name = input(":")

			message = Message()
			message.command = "peer"

			message.args = name

			sock.sendall(bytes(message.to_JSON(), 'UTF-8'))

			#Receive data from the server
			received = sock.recv(1024)

			response = json.loads(received.decode())
			if response["statusCode"] == True:
				print ("Peers successfully recieved from tracker")
				print (response['value'])
			else:
				print ("Unable to find torrent on tracker")
			
		else:
			break
		
		print ()
	
	sock.close()

if __name__ == "__main__":
	main()
