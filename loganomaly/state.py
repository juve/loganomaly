import os
import sqlite3

__all__ = ["NullStateDB","SQLiteStateDB"]

class NullStateDB(object):
    def load(self, logfile):
        return None, None
    
    def store(self, logfile, inode, offset):
        pass

class SQLiteStateDB(object):
    def __init__(self, dbfile):
        dirname = os.path.abspath(os.path.dirname(dbfile))
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except Exception, e:
                raise Exception("Error creating statedb directory %s: %s" % (dirname, e.args))
        if not os.path.isdir(dirname):
            raise Exception("Invalid statedb directory: %s" % dirname)
        
        create = not os.path.isfile(dbfile)
        
        self.db = sqlite3.connect(dbfile)
        
        if create:
            self.db.execute("""
            create table STATE (
                logfile string primary key,
                inode integer,
                offset integer
            )""")
    
    def load(self, logfile):
        cur = self.db.cursor()
        cur.execute("select inode, offset from state where logfile=?", (logfile,))
        rec = cur.fetchone()
        cur.close()
        if rec is None:
            # There was no previous state
            return (None, None)
        return (rec[0], rec[1])
    
    def store(self, logfile, inode, offset):
        cur = self.db.cursor()
        cur.execute("insert or replace into state (logfile, inode, offset) values (?,?,?)", (logfile, inode, offset))
        cur.close()
        self.db.commit()
    
    def __del__(self):
        if hasattr(self, "db"):
            self.db.close()
