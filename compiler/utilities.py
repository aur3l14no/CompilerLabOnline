class Logger(object):
    def __init__(self, f):
        self.f = f

    def critical(self, msg, *args, **kwargs):
        self.f.write((msg % args) + '\n')

    def warning(self, msg, *args, **kwargs):
        self.f.write('WARNING: ' + (msg % args) + '\n')

    def error(self, msg, *args, **kwargs):
        self.f.write('ERROR: ' + (msg % args) + '\n')

    info = critical
    debug = critical
