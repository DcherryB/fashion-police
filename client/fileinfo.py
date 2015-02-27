import io
import os
import math
import hashlib

CHUNK_SIZE = 1024 * 256

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

	return {
		'name':name,
		'extension':path.split('.')[-1],
		'size':fsize,
		'chunksize':CHUNK_SIZE,
		'hash':{
			'full':fullhash.hexdigest(), 
			'chunks':hashes
		}
	}