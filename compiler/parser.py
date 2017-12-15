from compiler.lexer import Lexer, Token
from compiler.exceptions import *
from collections import namedtuple
from enum import Enum
from copy import copy, deepcopy


class OpCode(Enum):
    LIT = 1
    OPR = 2
    LOD = 3
    STO = 4
    CAL = 5
    INT = 6
    JMP = 7
    JPC = 8
    RED = 9
    WRT = 10


class PCode:
    def __init__(self, op_code=None, l=None, a=None):
        self.op_code = op_code
        self.l = l
        self.a = a

    def __str__(self):
        return '({}, {}, {})'.format(self.op_code, self.l, self.a)


class Record:
    def __init__(self, type_=None, name=None, value=None, level=None, address=None, size=0):
        self.type = type_
        self.name = name
        self.value = value
        self.level = level
        self.address = address
        self.size = size

    def __str__(self):
        return '({}\t {}\t {}\t {}\t {}\t {})'.format(
            self.type, self.name, self.value, self.level, self.address, self.size)


class SymTable:
    def __init__(self):
        self.table = []

    def __getitem__(self, item):
        return self.table[item]

    def __setitem__(self, key, value):
        self.table[key] = value

    def __len__(self):
        return len(self.table)

    def get(self, name, type_=None):
        for record in self.table[::-1]:
            if record.name == name:
                if type_ and record.type != type_:
                    raise WrongSymbolType('Unexpected symbol type, expecting %s' % type_)
                else:
                    return record
        raise UndefinedSymbol('Undefined symbol: %s' % name)

    def enter(self, record):
        try:
            self.get(record.name)
        except ParserError:  # name not exists
            self.table.append(deepcopy(record))
            return
        # name exists
        raise DuplicateSymbol('Duplicate symbol name: %s' % record.name)


class PCodeManager:
    def __init__(self):
        self.code = []

    def __getitem__(self, item):
        return self.code[item]

    def __setitem__(self, key, value):
        self.code[key] = value

    def __len__(self):
        return len(self.code)

    def gen(self, op_code, l, a):
        self.code.append(PCode(op_code, l, a))


class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.token_generator = None
        self.current_token = None
        self.current_level = -1
        self.obj = ''
        self.table = SymTable()
        self.pcode = PCodeManager()

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
        self.table.enter(Record())
        self._block(3)
        self._expect(Token(None, '.'))
        print('Compile Successful!')
        for ln, line in enumerate(self.pcode):
            print('[%d]' % ln, line)
        print('\n', '='*50, '\n')
        for cnt, record in enumerate(self.table):
            print('[%d]' % cnt, record)

    def _block(self, dx):
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
            record = Record('const', None, None, 0)
            self._expect(Token(None, 'const'))
            self._forward()
            while True:
                _const_decl()
                if self.current_token.value == ',':
                    self._forward()
                else:
                    break
            self._expect(Token(None, ';'))
            self._forward()

        def _var(dx):
            def _var_decl(dx):
                self._expect(Token('IDENTIFIER', None))
                record.name = self.current_token.value
                record.address = dx
                self.table.enter(record)
                self._forward()
            record = Record('var', None, None, self.current_level)

            self._expect(Token(None, 'var'))
            self._forward()

            while True:
                _var_decl(dx)
                dx += 1
                if self.current_token.value == ',':
                    self._forward()
                else:
                    break
            self._expect(Token(None, ';'))
            self._forward()
            return dx

        def _procedure():  # controversial, may require modifications
            record = Record('procedure', None, None, self.current_level)
            self._expect(Token(None, 'procedure'))
            self._forward()
            self._expect(Token('IDENTIFIER', None))
            record.name = self.current_token.value
            self.table.enter(record)
            self._forward()
            self._expect(Token(None, ';'))
            self._forward()
            self._block(3)
            while self.current_token.value != ';':
                _procedure()
            self._forward()

        self.current_level += 1
        tx0 = len(self.table)-1  # should be a procedure record
        code1 = len(self.pcode)  # record the
        self.pcode.gen(OpCode.JMP, 0, 0)

        if self.current_token.value == 'const':
            _const()
        if self.current_token.value == 'var':
            dx = _var(dx)
        if self.current_token.value == 'procedure':
            _procedure()
        self.pcode[code1].a = len(self.pcode)  # fill back the JMP inst
        self.table[tx0].address = len(self.pcode)  # this value will be used by call
        self.pcode.gen(OpCode.INT, 0, dx)
        self._statement()
        self.pcode.gen(OpCode.OPR, 0, 0)
        self.current_level -= 1

    def _statement(self):
        if self.current_token.type == 'IDENTIFIER':
            record = self.table.get(self.current_token.value, 'var')
            self._forward()
            self._expect(Token(None, ':='))
            self._forward()
            self._expression()
            self.pcode.gen(OpCode.STO, self.current_level-record.level, record.address)

        elif self.current_token.value == 'if':
            self._forward()
            self._condition()
            self._expect(Token(None, 'then'))
            self._forward()
            code1 = len(self.pcode)
            self.pcode.gen(OpCode.JPC, 0, 0)
            self._statement()  # then statement
            code2 = len(self.pcode)
            self.pcode.gen(OpCode.JMP, 0, 0)
            if self.current_token.value == 'else':
                self._forward()
                self.pcode[code1].a = len(self.pcode)
                self._statement()  # else statement
            self.pcode[code2].a = len(self.pcode)

        elif self.current_token.value == 'while':
            code1 = len(self.pcode)
            self._forward()
            self._condition()
            code2 = len(self.pcode)
            self.pcode.gen(OpCode.JPC, 0, 0)
            self._expect(Token(None, 'do'))
            self._forward()
            self._statement()
            self.pcode.gen(OpCode.JMP, 0, code1)
            self.pcode[code2].a = len(self.pcode)

        elif self.current_token.value == 'call':
            self._forward()
            self._expect(Token('IDENTIFIER', None))
            record = self.table.get(self.current_token.value, 'procedure')
            self.pcode.gen(OpCode.CAL, self.current_level-record.level, record.address)
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
            code1 = len(self.pcode)
            self._statement()
            while self.current_token.value == ';':
                self._forward()
                self._statement()
            self._expect(Token(None, 'until'))
            self._forward()
            self._condition()
            self.pcode.gen(OpCode.JPC, 0, code1)

        elif self.current_token.value == 'read':
            self._forward()
            self._expect(Token(None, '('))
            self._forward()
            while True:
                self._expect(Token('IDENTIFIER', None))
                record = self.table.get(self.current_token.value, 'var')
                self.pcode.gen(OpCode.RED, self.current_level-record.level, record.address)
                self._forward()
                if self.current_token.value != ',':
                    break
                else:
                    self._forward()
            self._expect(Token(None, ')'))
            self._forward()

        elif self.current_token.value == 'write':
            self._forward()
            self._expect(Token(None, '('))
            self._forward()
            while True:
                self._expect(Token('IDENTIFIER', None))
                record = self.table.get(self.current_token.value)
                self.pcode.gen(OpCode.WRT, record.level - self.current_level, record.address)
                self._forward()
                if self.current_token.value != ',':
                    break
                else:
                    self._forward()
            self._expect(Token(None, ')'))
            self._forward()

    def _condition(self):
        if self.current_token.value == 'odd':
            self._forward()
            self._expression()
            self.pcode.gen(OpCode.OPR, 0, 6)
        else:
            self._expression()
            self._expect(Token('RELATIONAL_OPERATOR', None))
            op = self.current_token.value
            self._forward()
            self._expression()
            if op == '=':
                self.pcode.gen(OpCode.OPR, 0, 8)
            elif op == '<>':
                self.pcode.gen(OpCode.OPR, 0, 9)
            elif op == '<':
                self.pcode.gen(OpCode.OPR, 0, 10)
            elif op == '>=':
                self.pcode.gen(OpCode.OPR, 0, 11)
            elif op == '>':
                self.pcode.gen(OpCode.OPR, 0, 12)
            elif op == '<=':
                self.pcode.gen(OpCode.OPR, 0, 13)

    def _expression(self):
        if self.current_token.type == 'PLUS_OPERATOR':  # unary operator
            op = self.current_token.value
            self._forward()
            self._term()
            if op == '-':
                self.pcode.gen(OpCode.OPR, 0, 1)
        else:
            self._term()
        while self.current_token.type == 'PLUS_OPERATOR':  # binary operator
            op = self.current_token.value
            self._forward()
            self._term()
            if op == '+':
                self.pcode.gen(OpCode.OPR, 0, 2)
            else:
                self.pcode.gen(OpCode.OPR, 0, 3)

    def _term(self):
        self._factor()
        while self.current_token.type == 'MULTIPLY_OPERATOR':
            op = self.current_token.value
            self._forward()
            self._factor()
            if op == '*':
                self.pcode.gen(OpCode.OPR, 0, 4)
            else:
                self.pcode.gen(OpCode.OPR, 0, 5)

    def _factor(self):
        if self.current_token.type == 'IDENTIFIER':
            record = self.table.get(self.current_token.value)
            if record.type == 'const':
                self.pcode.gen(OpCode.LIT, 0, record.value)
            elif record.type == 'var':
                self.pcode.gen(OpCode.LOD, self.current_level-record.level, record.address)
            elif record.type == 'procedure':
                raise ParserError('Wrong variable type')
            self._forward()
        elif self.current_token.type == 'NUMBER':
            self.pcode.gen(OpCode.LIT, 0, int(self.current_token.value))
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
            e.pos = parser.lexer.pos
            print(e)
            raise e


if __name__ == '__main__':
    main()
