from compiler.lexer import Lexer, Token
from compiler.exceptions import *


class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.token_generator = None
        self.current_token: Token = None
        self.obj = ''

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
        self._block()
        self._assert(self.current_token.value == '.', 'expecting .')
        print('Compile Successful!')
        print(self.obj)

    def _block(self):
        def _procedure():
            self._assert(self.current_token.value == 'procedure', 'expecting procedure')
            self._forward()
            self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
            self._forward()
            self._assert(self.current_token.value == ';', 'expecting ;')
            self._forward()
            self._block()
            while self.current_token.value != ';':
                _procedure()
            self._forward()

        if self.current_token.value == 'const':
            self._forward()
            self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
            self._forward()
            self._assert(self.current_token.value == '=', 'expecting =')
            self._forward()
            self._assert(self.current_token.type == 'NUMBER', 'expecting number')
            self._forward()
            while self.current_token.value == ',':  # the following block should be identical to the above
                self._forward()
                self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
                self._forward()
                self._assert(self.current_token.value == '=', 'expecting =')
                self._forward()
                self._assert(self.current_token.type == 'NUMBER', 'expecting number')
                self._forward()
            self._assert(self.current_token.value == ';', 'expecting ;')
            self._forward()
        if self.current_token.value == 'var':
            self._forward()
            self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
            self._forward()
            while self.current_token.value == ',':  # the following block should be identical to the above
                self._forward()
                self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
                self._forward()
            self._assert(self.current_token.value == ';', 'expecting ;')
            self._forward()
        if self.current_token.value == 'procedure':
            _procedure()
        self._statement()

    def _statement(self):
        if self.current_token.type == 'IDENTIFIER':
            self._forward()
            self._assert(self.current_token.value == ':=', 'expecting :=')
            self._forward()
            self._expression()
        elif self.current_token.value == 'if':
            self._forward()
            self._condition()
            self._assert(self.current_token.value == 'then', 'expecting then')
            self._forward()
            self._statement()
            while self.current_token.value == 'else':
                self._statement()
                self._forward()
        elif self.current_token.value == 'while':
            self._forward()
            self._condition()
            self._assert(self.current_token.value == 'do', 'expecting do')
            self._forward()
            self._statement()
        elif self.current_token.value == 'call':
            self._forward()
            self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
            self._forward()
        elif self.current_token.value == 'begin':
            self._forward()
            self._statement()
            while self.current_token.value == ';':
                self._forward()
                self._statement()
            self._assert(self.current_token.value == 'end', 'expecting end')
            self._forward()
        elif self.current_token.value == 'repeat':
            self._forward()
            self._statement()
            while self.current_token.value == ';':
                self._forward()
                self._statement()
            self._assert(self.current_token.value == 'until', 'expecting until')
            self._forward()
            self._condition()
        elif self.current_token.value == 'read':
            self._forward()
            self._assert(self.current_token.value == '(', 'expecting (')
            self._forward()
            self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
            self._forward()
            while self.current_token.value == ',':
                self._forward()
                self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
                self._forward()
            self._assert(self.current_token.value == ')', 'expecting )')
            self._forward()
        elif self.current_token.value == 'write':
            self._forward()
            self._assert(self.current_token.value == '(', 'expecting (')
            self._forward()
            self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
            self._forward()
            while self.current_token.value == ',':
                self._forward()
                self._assert(self.current_token.type == 'IDENTIFIER', 'expecting identifier')
                self._forward()
            self._assert(self.current_token.value == ')', 'expecting )')
            self._forward()

    def _condition(self):
        if self.current_token.value == 'odd':
            self._forward()
        else:
            self._expression()
            self._assert(self.current_token.type == 'RELATIONAL_OPERATOR', 'expecting relational operator')
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
            self._assert(self.current_token.value == '(', 'expecting (, identifier or number')
            self._forward()
            self._expression()
            self._assert(self.current_token.value == ')', 'expecting )')
            self._forward()

    def _forward(self):
        try:
            self.current_token = next(self.token_generator)
        except StopIteration:
            raise ParserError('unexpected end of program', self.lexer.pos)

    def _assert(self, b, msg):
        if not b:
            raise ParserError(msg + 'now ' + str(self.current_token), self.lexer.pos)


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

