import sys
import os
import optparse

__all__ = ["Config"]

class Config(object):
    def __init__(self, options):
        self.config = {}
        self._parseargs(options)
    
    def __repr__(self):
        return str(self.config)
    
    def __getattr__(self, name):
        return self.config[name]
    
    def _parseargs(self, parser):
        args = sys.argv[1:]
        
        # values is set so that defaults don't get set in options
        options, args = parser.parse_args(args=args, values=optparse.Values())
        
        # Load default options first
        defaults = parser.get_default_values()
        self._loadopts(defaults)
        
        # Then the config file options if set
        if hasattr(options, "conf"):
            # The user-specified config
            self._loadconf(options.conf)
        elif hasattr(defaults, "conf"):
            # Only load the default conf if the file exists
            self._loadconf(defaults.conf, ignore_missing=True)
        
        # Load the command-line options last as they have highest priority
        self._loadopts(options)
        
        # Save any remaining args
        self.args = args
    
    def _loadopts(self, options):
        ignore = set(dir(optparse.Values()))
        items = set(dir(options)) - ignore
        for name in items:
            self.config[name] = getattr(options, name)
    
    def _loadconf(self, path, ignore_missing=False):
        path = os.path.expanduser(path)
        
        if not os.path.isfile(path):
            if ignore_missing:
                return
        
        # The config file is python
        local = {}
        execfile(path, {}, local)
        
        for name, value in local.items():
            self.config[name] = value
