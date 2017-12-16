import re
from collections import namedtuple
from compiler.exceptions import *

Token = namedtuple('Token', 'type, value')
Token.__new__.__defaults__ = (None,) * len(Token._fields)


lexicon = [
    ('BLANK', '\s'),
    ('KEYWORD', 'const|var|procedure|if|then|else|while|do|call|begin|end|repeat|until|read|write|odd'),
    ('DELIMITER', '\.|\(|\)|,|;'),
    ('PLUS_OPERATOR', '\+|-'),
    ('MULTIPLY_OPERATOR', '\*|/'),
    ('ASSIGN_OPERATOR', ':='),
    ('RELATIONAL_OPERATOR', '=|<>|<=|<|>=|>'),
    ('IDENTIFIER', '[A-Za-z][A-Za-z0-9]*'),
    ('NUMBER', '\d+(\.\d+)?')
]

lexicon = [(x[0], re.compile(x[1])) for x in lexicon]


class Lexer:
    def __init__(self):
        self.program = ''
        self.cur = 0
        self.pos = [1, 0]  # line number, position in line

    def load_program(self, program):
        self.program = program

    def get_symbol(self):
        last_line_count = 0  # char count when finishing the last line
        while self.cur < len(self.program):
            token = None
            for record in lexicon:
                r = record[1].match(self.program[self.cur:])
                if r and (token is None or r.end() > len(token.value)):
                    token = Token(record[0], r.group())
            if token is None:
                raise LexerError('Unidentified character', self.pos)
            self.cur += len(token.value)
            self.pos[1] = self.cur - last_line_count
            if token.type is 'BLANK':
                if token.value is '\n':
                    last_line_count = self.cur
                    self.pos[0] += 1
                continue
            else:
                yield token
                # print(token[0], token[1])

    def get_line(self, ln):
        return self.program.split('\n')[ln-1].strip()



def main():
    lexer = Lexer()
    with open('../doc/program.txt') as f:
        lexer.load_program(f.read())
        try:
            for symbol in lexer.get_symbol():
                print(symbol)
        except LexerError as e:
            print(e)

if __name__ == '__main__':
    main()