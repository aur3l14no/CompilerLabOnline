from compiler.lexer import Lexer, Token
from compiler.exceptions import *
from collections import namedtuple
from enum import Enum
from copy import copy, deepcopy
import sys


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

    def __str__(self):
        return self.name


class PCode:
    def __init__(self, f=None, l=None, a=None):
        self.f = f
        self.l = l
        self.a = a

    def __str__(self):
        return '({}, {}, {})'.format(self.f, self.l, self.a)


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

    def get(self):
        return self.code

    def gen(self, op_code, l, a):
        self.code.append(PCode(op_code, l, a))


class Parser:
    """Parser for PL/0 grammar
    You need to create an instance of parser for each program
    """
    def __init__(self):
        self.lexer = Lexer()
        self.token_generator = None
        self.current_token = None
        self.current_level = -1
        self.table = SymTable()
        self.pcode = PCodeManager()

    def load_program(self, program):
        self.lexer.load_program(program)
        self.token_generator = self.lexer.get_symbol()

    def analyze(self):
        try:
            self._program()
            # print('Compile Successful!')
            for ln, line in enumerate(self.pcode):
                # print('[%d]' % ln, line)
                print(line)
            return self.pcode.get()
        except ParserError as e:
            e.pos = self.lexer.pos
            print('[%d] %s' % (e.pos[0], self.lexer.get_line(e.pos[0])), file=sys.stderr)
            print('*** %s at %s' % (e.message, str(e.pos)), file=sys.stderr)

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

        def _var():
            def _var_decl():
                nonlocal dx
                self._expect(Token('IDENTIFIER', None))
                record.name = self.current_token.value
                record.address = dx
                dx += 1
                self.table.enter(record)
                self._forward()

            record = Record('var', None, None, self.current_level)
            self._expect(Token(None, 'var'))
            self._forward()
            while True:
                _var_decl()
                if self.current_token.value == ',':
                    self._forward()
                else:
                    break
            self._expect(Token(None, ';'))
            self._forward()
            return dx

        def _procedure():  # controversial, may require modifications
            record = Record('procedure', None, None, self.current_level)
            while self.current_token.value == 'procedure':
                self._forward()
                self._expect(Token('IDENTIFIER', None))
                record.name = self.current_token.value
                self.table.enter(record)
                self._forward()
                self._expect(Token(None, ';'))
                self._forward()
                self._block(3)
                self._expect(Token(None, ';'))
                self._forward()

        self.current_level += 1
        tx0 = len(self.table)-1  # should be a procedure record
        code1 = len(self.pcode)  # record the
        self.pcode.gen(OpCode.JMP, 0, 0)

        if self.current_token.value == 'const':
            _const()
        if self.current_token.value == 'var':
            _var()
        if self.current_token.value == 'procedure':
            _procedure()
        self.pcode[code1].a = len(self.pcode)  # fill back the JMP inst
        self.table[tx0].address = len(self.pcode)  # this value will be used by call
        self.pcode.gen(OpCode.INT, 0, dx)
        self._statement()
        self.pcode.gen(OpCode.OPR, 0, 0)
        self.current_level -= 1
        self.table[tx0+1:] = []

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
            self.pcode[code1].a = len(self.pcode)
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
                self._expression()
                self.pcode.gen(OpCode.WRT, 0, 0)
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
                self.pcode.gen(OpCode.OPR, 0, 7)
            elif op == '<>':
                self.pcode.gen(OpCode.OPR, 0, 8)
            elif op == '<':
                self.pcode.gen(OpCode.OPR, 0, 9)
            elif op == '>=':
                self.pcode.gen(OpCode.OPR, 0, 10)
            elif op == '>':
                self.pcode.gen(OpCode.OPR, 0, 11)
            elif op == '<=':
                self.pcode.gen(OpCode.OPR, 0, 12)

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
    with open('../doc/programs/program2.txt') as f:
        parser.load_program(f.read())
        parser.analyze()


if __name__ == '__main__':
    main()
