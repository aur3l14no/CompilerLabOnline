class LexerError(Exception):
    def __init__(self, message='Lexer error', pos=(0, 0)):
        self.message = message
        self.pos = pos


class ParserError(Exception):
    def __init__(self, message='Parser error', pos=(0, 0)):
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


class WrongSymbolType(ParserError):
    def __init__(self, message='Unexpected symbol type', pos=(0, 0)):
        self.message = message
        self.pos = pos


class InterpreterError(Exception):
    def __init__(self, message='Interpreter error', ln=0):
        self.message = message
        self.ln = ln
