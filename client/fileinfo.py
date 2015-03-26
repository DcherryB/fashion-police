import io
import os
import math
import hashlib
import json

CHUNK_SIZE = 1024 * 256
FILE_DIR = 'file'
INFO_DIR = 'file/info'
STATUS_DIR = 'file/status'


class Torrent:
	def __init__(self, info):
		self.info = info
		self.status = get_torrent_status(info)

	#this should only be called once over a torrent's lifetime
	def save_info(self):
		if not os.path.exists(FILE_DIR):
			os.makedirs(FILE_DIR)
		if not os.path.exists(INFO_DIR):
			os.makedirs(INFO_DIR)

		filename = generate_filename(self.info) + '.fashion'
		filename = unique_filename(INFO_DIR + '/' + filename)

		f = open(filename, 'w')
		f.write(self.info.to_JSON())
		f.close()

	def save_status(self):
		if not os.path.exists(STATUS_DIR):
			os.makedirs(STATUS_DIR)

		filename = STATUS_DIR + '/' + self.info.full_hash + '.status'
		f = open(filename, 'w')
		#f.write(self.status.to_JSON())
		f.write(json.dumps(self.status))
		f.close()

class Torrent_Info:
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


'''
If similarly named files already exist, appends a number to avoid collision.
	path: path to the file you're attempting to save
'''
def unique_filename (path):
	n = 2
	p = path
	ext = ''
	if '.' in path:
		ext = '.'+path.split('.')[-1]
		p = path[:-len(ext)]

	p2 = p
	while (os.path.isfile(p2+ext)):
		p2 = p + '(' + str(n) + ')'
		n += 1
	return p2+ext

'''
Generates a friendly file name based on the torrent's name.
	info: torrent info
'''
def generate_filename (info):
	validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
	filename = ''.join(c for c in info.name if c in validchars)
	if (filename == ''):
		filename = 'file'
	filename += '.' + info.extension
	return filename

'''
Generates the .fashion (torrent) info for a file
	path: path to the file to be read
	name: desired name for this torrent
'''
def generate_torrent_info (path, name):
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

	return Torrent_Info(name, path.split('.')[-1], fsize, CHUNK_SIZE, fullhash.hexdigest(), hashes)
	

'''
Find the local status of the torrent, based on the file's full hash
	info: torrent info
'''
def get_torrent_status(info):
	f = None
	try:
		f = open(STATUS_DIR + '/' + info.full_hash + '.status', 'r')
		return json.loads(f.read())
	except:
		#TODO: add chunk status etc
		return {
			'filename':unique_filename(FILE_DIR + '/' + generate_filename(info))
		}