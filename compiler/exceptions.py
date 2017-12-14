class LexerError(Exception):
    def __init__(self, message='Error', pos=(0, 0)):
        self.message = message
        self.pos = pos


class ParserError(Exception):
    def __init__(self, message='Error', pos=(0, 0)):
        self.message = message
        self.pos = pos


class DuplicateSymbol(ParserError):
    def __init__(self, message='Duplicate symbol', pos=(0, 0)):
        self.message = message
        self.pos = pos


class UndefinedSymbol(ParserError):
    def __init__(self, message='Undefined symbol', pos=(0, 0)):
        self.message = message
        self.pos = pos



