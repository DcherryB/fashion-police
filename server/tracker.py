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
		return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

class Tracker:
	def __init__(self):
		self.torrents = []
	
	def post(self, torrent):
		exists = False
		for t in self.torrents:
			if t["name"] == torrent["name"]:
				exists = True
				break
		
		response = None
		if exists == True:
			response = Response()
			response.statusCode = False
			response.value = "Torrent name already in use"
		else:
			self.torrents.append(torrent)
			response = Response()
		return response