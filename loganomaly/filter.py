import os
import re

__all__ = ["Filter", "FilteredLog"]

class Filter(object):
    def __init__(self, ignorefile):
        raw = open(ignorefile, "r").readlines()
        patterns = [pat[:-1] for pat in raw if len(pat.strip())>1]
        self.patterns = [re.compile(pat) for pat in patterns]
    
    def __contains__(self, item):
        for pattern in self.patterns:
            if pattern.search(item):
                return True
        return False

class FilteredLog(object):
    def __init__(self, logfile, filter, statedb):
        self.logfile = os.path.abspath(logfile)
        self.filter = filter
        self.statedb = statedb
    
    def __repr__(self):
        return self.logfile
    
    def _load_offset(self):
        last_inode, last_offset = self.statedb.load(self.logfile)
        
        if last_inode is None:
            # We haven't seen this log before
            return 0
        
        # Compare to the current file
        st = os.stat(self.logfile)
        
        if st.st_ino != last_inode:
            return 0  # Log was probably rotated
        
        if st.st_size < last_offset:
            return 0  # Log was probably truncated
        
        # Continue where we left off
        return last_offset
    
    def _store_offset(self, offset):
        inode = os.stat(self.logfile).st_ino
        self.statedb.store(self.logfile, inode, offset)
    
    def __iter__(self):
        offset = self._load_offset()
        log = open(self.logfile, "r")
        log.seek(offset, os.SEEK_SET)
        for line in log:
            line = line[:-1]
            if line not in self.filter:
                yield line
        offset = log.tell()
        log.close()
        self._store_offset(offset)
