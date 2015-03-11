import io
import os
import math
import hashlib
import json

CHUNK_SIZE = 1024 * 256

class torrent_file:
	def __init__(self, name, ext, size, chunksize, full, chunks):
		self.name = name
		self.extension = ext
		self.size = size
		self.chunksize = chunksize
		self.full_hash = full
		self.chunk_hashes = chunks
	
	def __str__(self):
		s = str("Torrent Information:\n"
				"	Name: {0}\n"
				"	Extension: {1}\n"
				"	File Size: {2}\n"
				"	Chunk Size: {3}\n"
				"	Full Hash: {4}\n"
				"	Chunk Hashes: {5}\n").format(self.name,
												 self.extension,
												 self.size,
												 self.chunksize,
												 self.full_hash,
												 self.chunk_hashes)
		return s
		
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__)

def read_file (path, name):
	fsize = os.path.getsize(path)
	numchunks = math.ceil(fsize / CHUNK_SIZE)
	f = open(path, 'rb')
	hashes = []
	fullhash = hashlib.sha1()

	for i in range(0, numchunks):
		h = hashlib.sha1()
		if (i == numchunks-1):
			chunk = f.read(fsize - i*CHUNK_SIZE)
		else:
			chunk = f.read(CHUNK_SIZE)

		h.update(chunk)
		hashes.append(h.hexdigest())
		fullhash.update(chunk)

	f.close()

	return torrent_file(name, path.split('.')[-1], fsize, CHUNK_SIZE, fullhash.hexdigest(), hashes)