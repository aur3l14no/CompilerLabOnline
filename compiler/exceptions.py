class ScannerError(Exception):
    def __init__(self, message, pos):
        self.message = message
        self.pos = pos
