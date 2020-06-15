import numpy as np
import tables as t
import os
from contextlib import contextmanager
import warnings


################old shit#####################

class LOSE:
	'''
	old code and bad ideas!
	'''
	def __init__(self, fname=None):
		self.fname = fname
		self.atom = t.Float32Atom()

		self.batch_size = 1

		self.iterItems = None
		self.iterOutput = None
		self.loopforever = False
		self.limit = None
		self.shuffle = False
		self.mask_callback = None

		self._slices = []
		self._useCallback = False

	def __repr__(self):
		messsage = '<lose hdf5 data handler, fname={}, atom={}>'.format(self.fname, self.atom)
		messsage += '\ngenerator parameters: iterItems={}, iterOutput={}, batch_size={}, limit={}, loopforever={}, shuffle={}'.format(self.iterItems, self.iterOutput, self.batch_size, self.limit, self.loopforever, self.shuffle)
		if self.fname is not None:
			try:
				with t.open_file(self.fname, mode='r') as f:
					messsage += '\nhdf5 file structure:\n{}'.format(f.__repr__())

			except Exception as e:
				messsage += '\nfailed to open file at \'{}\':{}, make sure it\'s a not corrupted hdf5 file and is a real file'.format(self.fname, e)

		return messsage

	def __str__(self):
		messsage = '<lose hdf5 data handler, fname={}, atom={}>'.format(self.fname, self.atom)
		if self.fname is not None:
			try:
				with t.open_file(self.fname, mode='r') as f:
					messsage += '\nhdf5 file structure:\n{}'.format(f)

			except Exception as e:
				messsage += '\nfailed to open file at \'{}\':{}, make sure it\'s a not corrupted hdf5 file and is a real file'.format(self.fname, e)

		return messsage

	def newGroup(self, fmode='a', **kwards):
		if type(fmode) is not str or fmode not in ['a', 'w']:
			raise ValueError('unexpected value passed to fmode, expected \'a\' or \'w\', got \'{}\''.format(fmode))

		with t.open_file(self.fname, mode=fmode) as f:
			for groupName, val in kwards.items():
				f.create_earray(f.root, groupName, self.atom, (0, *val))

	def removeGroup(self, *args):
		with t.open_file(self.fname, mode='a') as f:
			for groupName in args:
				f.remove_node('/{}'.format(groupName), recursive=True)

	def renameGroup(self, **kwards):
		with t.open_file(self.fname, mode='a') as f:
			for oldName, newName in kwards.items():
				x = eval('f.root.{}'.format(oldName))
				f.rename_node(x, newName)

	def save(self, **kwards):
		with t.open_file(self.fname, mode='a') as f:
			for key, val in kwards.items():
				x = eval('f.root.{}'.format(key))
				x.append(val)

	def load(self, *args, batch_obj=':'):
		out = []
		with t.open_file(self.fname, mode='r') as f:
			for key in args:
				x = eval('f.root.{}[np.s_[{}]]'.format(key, batch_obj))
				out.append(x)

		return out

	def getShape(self, arrName):
		return self.getShapes(arrName)[0]

	def getShapes(self, *arrNames):
		out = []
		with t.open_file(self.fname, mode='r') as f:
			for i in arrNames:
				out.append(eval('f.root.{}.shape'.format(i)))

		return out

	def _iterator_init(self):
		if self.fname is None:
			raise ValueError('self.fname is empty')

		if self.iterItems is None or self.iterOutput is None:
			raise ValueError('self.iterItems and/or self.iterOutput are not defined')

		if len(self.iterItems) != 2 or len(self.iterOutput) != 2:
			raise ValueError('self.iterItems or self.iterOutput has wrong dimensions, self.iterItems has to be [[list of x array names], [list of y array names]] and self.iterOutput is the name map self.iterItems folowing the same dimensions')

		if not isinstance(self.mask_callback, type(None)) and hasattr(self.mask_callback, '__call__'):
			self._useCallback = True

		L = [i[0] for i in self.getShapes(*self.iterItems[0])]
		L.extend([i[0] for i in self.getShapes(*self.iterItems[1])])
		dataset_limit = min(L)

		index = 0

		while 1:
			self._slices.append(np.s_[index:index+self.batch_size])

			index += self.batch_size

			if self.limit is not None:
				if index >= self.limit or index >= dataset_limit:
					break

			elif index >= dataset_limit:
				break

	def _iterator(self):
		if self.iterItems is None or self.iterOutput is None or self.fname is None:
			raise ValueError('self.iterItems and/or self.iterOutput and/or self.fname is empty')

		if len(self.iterItems) != 2 or len(self.iterOutput) != 2:
			raise ValueError('self.iterItems or self.iterOutput has wrong dimensions, self.iterItems is [[list of x array names], [list of y array names]] and self.iterOutput is the name map for them')

		with t.open_file(self.fname, mode='r') as f:
			while 1:
				if self.shuffle:
					np.random.seed(None)
					np.random.shuffle(self._slices)

				for cheeseSlice in self._slices:
					if self.shuffle:
						np.random.seed(None)
						st = np.random.get_state()

					stepX = {}
					stepY = {}
					for name, key in zip(self.iterItems[0], self.iterOutput[0]):
						x = eval('f.root.{}[{}]'.format(name, cheeseSlice))
						if self.shuffle:
							np.random.set_state(st)
							np.random.shuffle(x)

						stepX[key] = x

					for name, key in zip(self.iterItems[1], self.iterOutput[1]):
						y = eval('f.root.{}[{}]'.format(name, cheeseSlice))
						if self.shuffle:
							np.random.set_state(st)
							np.random.shuffle(y)

						stepY[key] = y

					if self._useCallback:
						yield self.mask_callback((stepX, stepY))
					else:
						yield (stepX, stepY)

				if self.loopforever != True:
					break

		return

	@contextmanager
	def generator(self, mask_callback=None):
		try:
			self.mask_callback = mask_callback
			self._iterator_init()

			yield self._iterator

		except:
			raise

	@contextmanager
	def makeGenerator(self, layerNames, limit=None, batch_size=1, shuffle=False, mask_callback=None, **kwards):
		try:
			self.fname = './temp.h5'

			self.iterItems = layerNames
			self.iterOutput = layerNames
			self.limit = limit
			self.batch_size = batch_size
			self.shuffle = shuffle
			self.mask_callback = mask_callback

			d = {layerName: val.shape[1:] for layerName, val in kwards.items()}

			self.newGroup(fmode='w', **d)
			self.save(**kwards)

			del d
			del kwards

			self._iterator_init()

			yield self._iterator

		except:
			raise

		finally:
			if os.path.isfile('./temp.h5'):
				os.unlink('./temp.h5')

#############################################

class Loser(object):
	'''
	base data handler

	use in a context manager to enable fast mode

	use fast mode if you call load or save too frequently
	'''

	def __init__(self, fname, *, verboseRepr=False, **k):
		'''
		:fname: file path
		:verboseRepr: do i need to explain this?
		'''
		self._fname = fname
		self._fObj = None
		self._verbose = verboseRepr
		self._fmode = 'a'

	def __repr__(self):
		'''
		fucking guess
		'''
		s = f'<{self.__class__.__module__}.{self.__class__.__name__} fname="{self._fname}", fast_active={self._fObj is not None}, verboseRepr={self._verbose} at {hex(id(self))}>'

		if self._verbose:
			if os.path.isfile(self._fname):
				if self._fObj is None:
					with self:
						t = f'\n{self._fObj}'

				else:
					t = f'\n{self._fObj}'
			else:
				t = '\nfile doesn\'t exist' 

			s += t

		return s

	def __call__(self, fmode='a'):
		'''
		lame fix to pass :fmode: to the context manager
		'''
		self._fmode = fmode
		return self

	def __enter__(self):
		self._fObj = t.open_file(self._fname, mode=self._fmode)

	def __exit__(self, *exp):
		try:
			if self._fObj is not None:
				self._fObj.close()

		finally:
			self._fObj = None


	def new_group(self, fmode='a', atom=t.Float32Atom(), **groups):
		'''
		creates new group(s) using :atom: with :fmode:

		example: new_group(x=(10, 2), y=(2, 1))
		'''
		assert self._fObj is None, 'fast is active'
		if fmode not in ['a', 'w']:
			raise ValueError(f'bad fmode value: \'{fmode}\'')

		with t.open_file(self._fname, mode=fmode) as f:
			for groupName, val in groups.items():
				f.create_earray(f.root, groupName, atom, (0, *val))


	def save(self, **data):
		'''
		saves data
		'''
		if self._fObj is None:
			with t.open_file(self._fname, mode='a') as f:
				for key, val in data.items():
					x = eval('f.root.{}'.format(key))
					x.append(val)
		else:
			for key, val in data.items():
				x = eval('self._fObj.root.{}'.format(key))
				x.append(val)

	def load(self, *groups, batch_obj=':'):
		'''
		loads data

		:bathc_obj: slice like object to specify how much to load
		'''
		out = []
		if self._fObj is None:
			with t.open_file(self._fname, mode='r') as f:
				for key in groups:
					x = eval('f.root.{}[np.s_[{}]]'.format(key, batch_obj))
					out.append(x)

		else:
			for key in groups:
				x = eval('self._fObj.root.{}[np.s_[{}]]'.format(key, batch_obj))
				out.append(x)

		return out

	def get_shapes(self, *groups):
		'''
		gets group shapes
		'''
		out = []
		if self._fObj is None:
			with t.open_file(self._fname, mode='r') as f:
				for i in groups:
					out.append(eval('f.root.{}.shape'.format(i)))

		else:
			for i in groups:
				out.append(eval('self._fObj.root.{}.shape'.format(i)))

		return out

	def remove_group(self, *groups):
		'''
		removes groups
		'''
		assert self._fObj is None, 'fast is active'
		with t.open_file(self.fname, mode='a') as f:
			for groupName in groups:
				f.remove_node('/{}'.format(groupName), recursive=True)

	def rename_group(self, **kwards):
		'''
		renames groups
		'''
		assert self._fObj is None, 'fast is active'
		with t.open_file(self.fname, mode='a') as f:
			for oldName, newName in kwards.items():
				x = eval('f.root.{}'.format(oldName))
				f.rename_node(x, newName)

class HumanIterator(Loser):
	'''
	iterator
	'''

	def __init__(self, fname, *groups, batch_size=5, limit=-1, seed=None, shuffle=False, loopforever=False, **kwards):
		'''
		:fname: file path
		:groups: group names
		:batch_size: load batch size
		:limit: number of rows to load, negative goes from the end
		:seed: shuffle seed
		:shuffle: shuffle?
		:loopforever: loop for ever?
		'''
		super().__init__(fname, **kwards)
		self.groups = groups

		self.batch_size = batch_size
		self.limit = limit
		self.loopforever = loopforever
		self.seed = seed
		self.shuffle = shuffle

		self._context = False

		self.currentIndex = 0

	def __enter__(self):
		self._context = True
		self._fObj = t.open_file(self._fname, mode='r')


	def __exit__(self, *exp):
		self._context = False
		try:
			if self._fObj is not None:
				self._fObj.close()

		finally:
			self._fObj = None

	def __iter__(self):
		np.random.seed(self.seed)
		L = [i[0] for i in self.get_shapes(*self.groups)]
		dataset_limit = min(L)

		self._slices = []

		index = 0

		while 1:
			self._slices.append(np.s_[index:index+self.batch_size])

			index += self.batch_size


			if self.limit < 0:
				if index >= dataset_limit + self.limit:
					break

			elif index >= self.limit:
				break

		if not self._context:
			warnings.warn('slow mode is active, use a context manager!')

		return self

	def __next__(self):
		if self.currentIndex < len(self._slices):
			self.currentIndex += 1
			if not self.shuffle:
				return self.load(*self.groups, batch_obj=self._slices[self.currentIndex-1])
			else:
				d = self.load(*self.groups, batch_obj=self._slices[self.currentIndex-1])
				st = np.random.get_state()
				h = 0
				while h<len(d):
					np.random.set_state(st)
					np.random.shuffle(d[h])
					h+= 1

				return d


		if self.loopforever:
			if self.shuffle:
				np.random.shuffle(self._slices)
			self.currentIndex = 0
			return self.load(*self.groups, batch_obj=self._slices[0])

		raise StopIteration