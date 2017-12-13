class LexerError(Exception):
    def __init__(self, message='Error', pos=(0, 0)):
        self.message = message
        self.pos = pos


class ParserError(Exception):
    def __init__(self, message='Error', pos=(0, 0)):
        self.message = message
        self.pos = pos
