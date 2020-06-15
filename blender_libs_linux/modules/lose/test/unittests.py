import unittest as u
import os
from lose import LOSE
import lose
import numpy as np
import tables as t

v = [int(i) for i in lose.__version__.split('.')]

class Tests(u.TestCase):
	def setUp(self):
		if os.path.isfile('./temp.h5'):
			os.unlink('./temp.h5')

		self.l = LOSE('./temp.h5')

	def test_mk_group_valid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		self.l.newGroup(fmode='w', x=(15, 5), y=(2,))

	def test_mk_group_valid2(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		self.l.newGroup(fmode='a', y=(2,))
		self.l.newGroup(fmode='a', x=(15, 5))

	def test_mk_group_invalid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		with self.assertRaises(ValueError):
			self.l.newGroup(fmode='t', y=(2,))

	def test_save_valid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		check = True
		E = None

		self.l.newGroup(fmode='w', x=(25, 4), y=(2,))

		self.l.save(x=np.zeros((10, 25, 4)), y=np.zeros((2, 2)))
		self.l.save(x=np.zeros((15, 25, 4)), y=np.zeros((5, 2)))
		self.l.save(x=np.zeros((50, 25, 4)), y=np.zeros((8, 2)))

	def test_save_invalid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		self.l.newGroup(fmode='w', x=(25, 4), y=(2,))

		with self.assertRaises(ValueError):
			self.l.save(x=np.zeros((25, 4)), y=np.zeros((2, 2)))

	def test_save_invalid2(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		self.l.newGroup(fmode='w', x=(25, 4), y=(2,))

		with self.assertRaises(ValueError):
			self.l.save(x=np.zeros((10, 25, 4)), y=np.zeros((2, 5)))

	def test_save_invalid3(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		self.l.newGroup(fmode='w', x=(25, 4), y=(2,))

		with self.assertRaises(TypeError):
			self.l.save(x='lul')

	def test_load_valid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		a, b = self.l.load('x', 'y')

		self.assertEqual(np.all(a==X), np.all(b==Y), 'should be equal')

	@u.skipIf(v < [0, 6, 0], 'unsupported version')
	def test_load_valid2(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		a, b = self.l.load('x', 'y', batch_obj=':5')

		self.assertEqual(np.all(a==X[:5]), np.all(b==Y[:5]), 'should be equal')

	@u.skipIf(v > [0, 5, 0], 'version 0.5.0 and below only')
	def test_load_valid2_old(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		a, b = self.l.load('x', 'y', batch_obj='[:5]')

		self.assertEqual(np.all(a==X[:5]), np.all(b==Y[:5]), 'should be equal')

	def test_load_invalid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		with self.assertRaises(TypeError):
			a, b = self.l.load('x', 'y', batch_obj=None)

	def test_load_invalid2(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		with self.assertRaises(t.exceptions.NoSuchNodeError):
			a, b = self.l.load('z', 'g', batch_obj=None)

	@u.skipIf(v < [0, 5, 0], 'version 0.5 and up only')
	def test_rename_group_valid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		self.l.renameGroup(x='z', y='g')

		a, b = self.l.load('z', 'g')

		self.assertEqual(np.all(X == a), np.all(Y == b), 'should be equal')

	@u.skipIf(v < [0, 5, 0], 'version 0.5 and up only')
	def test_rename_group_invalid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		with self.assertRaises(t.exceptions.NoSuchNodeError):
			self.l.renameGroup(g='x')

	@u.skipIf(v < [0, 4, 5], 'version 0.4.5 and up only')
	def test_rm_group_valid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		self.l.removeGroup('x', 'y')

		with self.assertRaises(t.exceptions.NoSuchNodeError):
			a, b = self.l.load('x', 'y')

	@u.skipIf(v < [0, 4, 5], 'version 0.4.5 and up only')
	def test_rm_group_invalid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		with self.assertRaises(t.exceptions.NoSuchNodeError):
			self.l.removeGroup('x', 'y')

	@u.skipIf(v < [0, 6, 0], 'version 0.6 and up only')
	def test_getShapes_valid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		a, b = self.l.getShapes('x', 'y')

		self.assertEqual(a, X.shape, 'should be equal')
		self.assertEqual(b, Y.shape, 'should be equal')

	@u.skipIf(v > [0, 4, 5], 'version 0.4.5 and below only')
	def test_getShapes_valid_old(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=(0, X.shape[1:]), y=(0, Y.shape[1:]))
		self.l.save(x=X, y=Y)

		a = self.l.get_hape('x')
		b = self.l.get_hape('y')

		self.assertEqual(a, X.shape, 'should be equal')
		self.assertEqual(b, Y.shape, 'should be equal')

	@u.skipIf(v < [0, 4, 5], 'version 0.4.5 and up only')
	def test_getShapes_invalid(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)

		X = np.zeros((10, 5, 10))
		Y = np.zeros((10, 5))

		self.l.newGroup(fmode='w', x=X.shape[1:], y=Y.shape[1:])
		self.l.save(x=X, y=Y)

		with self.assertRaises(t.exceptions.NoSuchNodeError):
			a = self.l.getShape('g')

	# def test_generator_valid(self):
	# 	if os.path.isfile(self.l.fname):
	# 		os.unlink(self.l.fname)

		

	def tearDown(self):
		if os.path.isfile(self.l.fname):
			os.unlink(self.l.fname)