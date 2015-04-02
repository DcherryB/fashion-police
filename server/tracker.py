import json

class Response:
	def __init__(self):
		self.statusCode = True
		self.value = None
		
	def __str__(self):
		s = str("Response Information:\n"
			"	Status: {0}\n"
			"	Value: {1}\n").format(self.statusCode,
						      self.value)
		return s
		
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__)

class Tracker:
	def __init__(self):
		self.torrents = {}
	
	def post(self, info):
		key = info["full_hash"]
		if key in self.torrents:
			response = Response()
			response.statusCode = False
			response.value = "File is already in tracker"
			return response
	
		exists = False
		t = None
		for key in self.torrents:
			t = self.torrents[key]
			if t.info["name"] == info["name"]:
				exists = True
				break
		
		response = None
		if exists == True:
			response = Response()
			response.statusCode = False
			response.value = "Torrent name already in use"
		else:
			torrent = Torrent(info)
			self.torrents[info["full_hash"]] = torrent
			response = Response()
			
		return response

	def query(self, args):
		name = ''
		if 'name' in args:
			name = args['name']

		results = []
		for key in self.torrents:
			t = self.torrents[key]
			if name == '' or name in t.info['name']:
				results.append(t.preview())

		response = Response()
		response.statusCode = True
		response.value = results

		return response

	def get(self, args):
		name = args
		for key in self.torrents:
			t = self.torrents[key]
			if t.info["name"] == name:
				response = Response()
				response.statusCode = True
				response.value = (t.info, t.peers)
				return response

		response = Response()
		response.statusCode = False
		return response
		
	def peer(self, args):
		name = args
		for key in self.torrents:
			t = self.torrents[key]
			if t.info["name"] == name:
				response = Response()
				response.statusCode = True
				response.value = t.peers
				return response
		
		response = Response()
		response.statusCode = False
		return response
		
	def upload(self, args, addr):
		info = args
		for key in self.torrents:
			t = self.torrents[key]
			if t.info["name"] == info['name'] and t.info['full_hash'] == info['full_hash']:
				newPeer = {}
				newPeer["ip"] = addr[0]
				newPeer["port"] = addr[1]
				t.peers.append(newPeer)

				response = Response()
				response.statusCode = True
				return response
		
		response = Response()
		response.statusCode = False
		return response

class Torrent:
	def __init__(self, info):
		self.info = info
		self.peers = []

	def __str__(self):
		s = str("Torrent:\n"+json.dumps(self.info))
		return s

	def preview(self):
		ret = {}
		for prop in ['name', 'extension', 'size', 'full_hash']:
			ret[prop] = self.info[prop]
		return ret
