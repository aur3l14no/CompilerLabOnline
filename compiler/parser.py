from compiler.lexer import Lexer, Token
from compiler.exceptions import *
from collections import namedtuple

Record = namedtuple('Record', 'type, name, value, level, address, size')
Record.__new__.__defaults__ = (None, None, None, None, None, 0)


class SymTable:
    def __init__(self):
        self.table = []
        self.dx = 3

    def get(self, name):
        for record in self.table[::-1]:
            if record.name == name:
                return record
        raise UndefinedSymbol('Undefined symbol: %s' % name)

    def enter(self, record):
        if self.get(record.name) is not None:
            raise DuplicateSymbol('Duplicate symbol name: %s' % record.name)
        else:
            self.table.append(record)
            self.dx += 1


class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.token_generator = None
        self.current_token: Token = None
        self.obj = ''
        self.table = SymTable()

    def load_program(self, program):
        self.lexer.load_program(program)
        self.token_generator = self.lexer.get_symbol()

    def analyze(self):
        self._program()

    '''
    The following is rec-descent parser. 
    Each handler will move forward 1 token before return, therefore self.current_token is assigned at 
    the beginning of each function. 
    '''

    def _program(self):
        self._forward()
        self._block(0)
        self._expect(Token(None, '.'))
        print('Compile Successful!')
        print(self.obj)

    def _block(self, level):
        def _const():
            def _const_decl():
                self._expect(Token('IDENTIFIER', None))
                record.name = self.current_token.value
                self._forward()
                self._expect(Token(None, '='))
                self._forward()
                self._expect(Token('NUMBER', None))
                record.value = int(self.current_token.value)
                self.table.enter(record)
                self._forward()
            record = Record('const', None, None, level)
            self._expect(Token(None, 'const'))
            self._forward()
            _const_decl()
            while self.current_token.value == ',':  # the following block should be identical to the above
                self._forward()
                _const_decl()
            self._expect(Token(None, ';'))
            self._forward()

        def _var():
            def _var_decl():
                self._expect(Token('IDENTIFIER', None))
                record.name = self.current_token.value
                self.table.enter(record)
                self._forward()
            record = Record('var', None, None, level)
            self._expect(Token(None, 'var'))
            self._forward()
            _var_decl()
            while self.current_token.value == ',':  # the following block should be identical to the above
                self._forward()
                _var_decl()
            self._expect(Token(None, ';'))
            self._forward()

        def _procedure():  # controversial, may require modifications
            record = Record('procedure', None, None, level)
            self._expect(Token(None, 'procedure'))
            self._forward()
            self._expect(Token('IDENTIFIER', None))
            record.name = self.current_token.value
            self.table.enter(record)
            self._forward()
            self._expect(Token(None, ';'))
            self._forward()
            self._block(level+1)
            while self.current_token.value != ';':
                _procedure()
            self._forward()

        self.table.dx = 3
        if self.current_token.value == 'const':
            _const()
        if self.current_token.value == 'var':
            _var()
        if self.current_token.value == 'procedure':
            _procedure()
        self._statement()

    def _statement(self):
        if self.current_token.type == 'IDENTIFIER':
            self._forward()
            self._expect(Token(None, ':='))
            self._forward()
            self._expression()
        elif self.current_token.value == 'if':
            self._forward()
            self._condition()
            self._expect(Token(None, 'then'))
            self._forward()
            self._statement()
            while self.current_token.value == 'else':
                self._statement()
                self._forward()
        elif self.current_token.value == 'while':
            self._forward()
            self._condition()
            self._expect(Token(None, 'do'))
            self._forward()
            self._statement()
        elif self.current_token.value == 'call':
            self._forward()
            self._expect(Token('IDENTIFIER', None))
            self._forward()
        elif self.current_token.value == 'begin':
            self._forward()
            self._statement()
            while self.current_token.value == ';':
                self._forward()
                self._statement()
            self._expect(Token(None, 'end'))
            self._forward()
        elif self.current_token.value == 'repeat':
            self._forward()
            self._statement()
            while self.current_token.value == ';':
                self._forward()
                self._statement()
            self._expect(Token(None, 'until'))
            self._forward()
            self._condition()
        elif self.current_token.value == 'read':
            self._forward()
            self._expect(Token(None, '('))
            self._forward()
            self._expect(Token('IDENTIFIER', None))
            self._forward()
            while self.current_token.value == ',':
                self._forward()
                self._expect(Token('IDENTIFIER', None))
                self._forward()
            self._expect(Token(None, ')'))
            self._forward()
        elif self.current_token.value == 'write':
            self._forward()
            self._expect(Token(None, '('))
            self._forward()
            self._expect(Token('IDENTIFIER', None))
            self._forward()
            while self.current_token.value == ',':
                self._forward()
                self._expect(Token('IDENTIFIER', None))
                self._forward()
            self._expect(Token(None, ')'))
            self._forward()

    def _condition(self):
        if self.current_token.value == 'odd':
            self._forward()
        else:
            self._expression()
            self._expect(Token('RELATIONAL_OPERATOR', None))
            self._forward()
        self._expression()

    def _expression(self):
        if self.current_token.type == 'PLUS_OPERATOR':  # unary operator
            self._forward()
        self._term()
        while self.current_token.type == 'PLUS_OPERATOR':  # binary operator
            self._forward()
            self._term()

    def _term(self):
        self._factor()
        while self.current_token.type == 'MULTIPLY_OPERATOR':
            self._forward()
            self._factor()

    def _factor(self):
        if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self._forward()
        else:
            self._expect(Token(None, '('))
            self._forward()
            self._expression()
            self._expect(Token(None, ')'))
            self._forward()

    def _forward(self):
        try:
            self.current_token = next(self.token_generator)
        except StopIteration:
            raise ParserError('unexpected end of program', self.lexer.pos)

    def _expect(self, token: Token):
        if token.type is None:
            b = token.value == self.current_token.value
        elif token.value is None:
            b = token.type == self.current_token.type
        else:
            b = token == self.current_token
        if not b:
            raise ParserError('Expecting %s but current token is %s' % (str(token), str(self.current_token)),
                              self.lexer.pos)


def main():
    parser = Parser()
    with open('../doc/program.txt') as f:
        parser.load_program(f.read())
        try:
            parser.analyze()
        except ParserError as e:
            print(e)
            raise e


if __name__ == '__main__':
    main()
