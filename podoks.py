import ftputil

import time
import pickle
import copy

# podoks
"""
Python-Only Document Oriented Key-value Store
"""

class NoSuchCollectionError(KeyError):
	pass

class Element:
	def __init__(self,value,podoks=None,collection=None,key=None):
		if not value:
			raise ValueError("value can't be None.")
		self.value = value
		self.podoks = podoks
		self.collection = collection
		self.key = key
		print("PODOKS : `{0}` !".format(value))
	
	def __getitem__(self, key):
		return copy.copy(self.value[key])
	
	def __setitem__(self, key, value):
		self.value[key] = value
	
	def __getattr__(self, key):
		try:
			return super().__getattr__(key)
		except AttributeError:
			pass
		try:
			return self.value[key]
		except KeyError:
			raise AttributeError(key)
	
	def __setattr__(self, key, value):
		try:
			return super().__setattr__(key,value)
		except AttributeError:
			raise AttributeError("Sadly, Podoks can't set attributes. I don't know why.")
	
	def __str__(self):
		return str(self.value)
	
	def __dict__(self):
		return self.value
	
	def save(self):
		"""
		Saves a document to the database. If the `backend` argument is not specified,
		the function resorts to the *default backend* as defined during object instantiation.
		If no such backend is defined, an `AttributeError` exception will be thrown.
		:param backend: the backend in which to store the document.
		"""
		if not self.podoks or not self.collection or not self.key:
			raise AttributeError("No instance, collection or key defined!")
		return self.podoks.put(self.collection,self.key,self.value)
	
class Instance:
	def __init__(self,name,data={}):
		self.data = data
		self.name = name
		print(name + " is opened : podoks")
	
	def __getitem__(self, key):
		self.get_collection(key)
	
	def __str__(self):
		return str(self.data)
	
	def create_collection(self, name):
		self.data[name] = {}
		print("Collection {0} created !".format(name))
	
	def collection_exists(self,name):
		return name in self.data
	
	def get_collection(self,collection):
		if collection in self.data:
			returned = {}
			for key in self.data[collection]:
				returned[key]=Element(self.get(collection,key),self,collection,key)
			return returned
		else:
			raise NoSuchCollectionError("Collection `{0}` doesn't exist in `{1}`.".format(collection,self.name)) 
	
	def get(self, collection, key, default=None):
		try:
			if not self.data[collection].get(key, None):
				return default
			else:
				return Element(self.data[collection][key],self,collection,key)
		except KeyError:
			raise NoSuchCollectionError("Collection `{0}` doesn't exist in `{1}`.".format(collection,self.name))
	
	def put(self, collection, key, value):
		try:
			self.data[collection][key] = value
			return Element(self.data[collection][key],self,collection,key)
		except KeyError:
			raise NoSuchCollectionError("Collection `{0}` doesn't exist in `{1}`.".format(collection,self.name))

	
	def save(self, ftputil_host, target):
		filename = '{0}{1}.pickle'.format(self.name,time.time())
		with open(filename, 'wb') as handle:
			pickle.dump(self.data, handle)
			# pickle.dump(self.data, handle, protocol=pickle.HIGHEST_PROTOCOL)
		ftputil_host.upload(filename,target)
	
	@staticmethod
	def load(ftputil_host, ftp_path, name):
		try:
			with ftputil_host.open(ftp_path, "rb") as fobj:
				data = pickle.loads(fobj.read())
				return Instance(name,data)
		except IOError:
			print("FTP FILE DOESN'T EXIST (YET). BLANK {0} DB USED INSTEAD.".format(name))
			return Instance(name)
	
	