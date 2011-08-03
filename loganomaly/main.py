import sys
import os
from optparse import OptionParser

from state import NullStateDB, SQLiteStateDB
from filter import Filter, FilteredLog
from config import Config

def main():
    options = OptionParser(usage="%prog [options] LOGFILE")
    options.add_option("-c", "--conf", action="store", type="string",
        dest="conf", default="/etc/loganomaly/loganomaly.conf", metavar="FILE",
        help="Configuration file")
    options.add_option("-s", "--statedb", action="store", type="string",
        dest="statedb", default="/var/loganomaly/state.db", metavar="FILE",
        help="Name of the file to store state database in [default: %default]")
    options.add_option("-i", "--ignore", action="store", type="string",
        dest="ignore", default=None, metavar="FILE",
        help="Path to file containing list of patterns to ignore")
    options.add_option("-l", "--limit", action="store", type="int",
        dest="limit", default=100, metavar="N",
        help="Limit output to N lines [default: %default]")
    options.add_option("-t", "--test", action="store_true",
        dest="test", default=False,
        help="Do not save state to state db")
    
    options.get_option("-h").help = "Show this message and exit"
    
    config = Config(options)
    
    if not config.ignore:
        options.error("Specify --ignore")
    
    if not config.statedb:
        options.error("Specify --statedb")
    
    if len(config.args) == 0:
        options.error("Specify LOGFILE")
    
    if config.test:
        statedb = NullStateDB()
    else:
        statedb = SQLiteStateDB(config.statedb)
    
    filter = Filter(config.ignore)
    
    for logfile in config.args:
        log = FilteredLog(logfile, filter, statedb)
        found = False
        i = 0
        for line in log:
            if not found:
                print "Anomalies found in log file: %s\n\n" % log
                found = True
            if i <= config.limit:
                print line
            i += 1
        if found and i > config.limit:
            print "...\n%s more lines found" % (i-config.limit)

if __name__ == '__main__':
    main()