import unittest
import os
import warnings
import threading
import time
import sqlite3

from loganomaly import state

class LockThread(threading.Thread):
	def __init__(self, dbfile, sem):
		threading.Thread.__init__(self)
		self.dbfile = dbfile
		self.sem = sem
	
	def run(self):
		db = sqlite3.connect(self.dbfile)
		cur = db.cursor()
		cur.execute("BEGIN EXCLUSIVE");
		self.sem.release()
		time.sleep(2)
		cur.close()
		db.commit()

class TestState(unittest.TestCase):
	def setUp(self):
		warnings.simplefilter('ignore', RuntimeWarning)
		self.tmpfile = os.tmpnam() # This method has a warning
		self.db = state.SQLiteStateDB(self.tmpfile)
	
	def tearDown(self):
		os.remove(self.tmpfile)
   	
	def test_store(self):
		logfile = "file"
		inode = 1000
		offset = 1010
		self.db.store(logfile, inode, offset)
		
		result = self.db.load(logfile)
		self.assertEquals(inode, result[0])
		self.assertEquals(offset, result[1])
    
	def test_load(self):
		logfile = "file"
		inode, offset = self.db.load(logfile)
		self.assertTrue(inode is None)
		self.assertTrue(offset is None)
	
	def test_locked_load(self):
		def op():
			logfile = "file"
			inode, offset = self.db.load(logfile)
			self.assertTrue(inode is None)
			self.assertTrue(offset is None)
		
		self.withLockedDB(op)
	
	def test_locked_store(self):
		def op():
			logfile = "file"
			inode = 1000
			offset = 1010
			self.db.store(logfile, inode, offset)
		
		self.withLockedDB(op)
	
	def withLockedDB(self, operation):
		s = threading.Semaphore(0)
		t = LockThread(self.tmpfile, s)
		t.start()
		
		s.acquire() # yield to LockThread
		
		start = time.time()
		
		# This should take more than 1 second because the db is locked
		operation()
		
		end = time.time()
		
		self.assertTrue((end-start) > 1)
		
		t.join()

if __name__ == '__main__':
	unittest.main()
