import re


lexicon = [
    ['blank', ['\s']],
    ['key_word', [re.escape(x) for x in ['const', 'var', 'procedure', 'if', 'then', 'else', 'while', 'do',
                                         'call', 'begin', 'end', 'repeat', 'until', 'read', 'write', 'odd']]],
    ['delimiter', [re.escape(x) for x in ['.', '(', ')', ',', ';']]],
    ['operator', [re.escape(x) for x in ['+', '-', '*', '/', ':=', '=', '<>', '<', '<=', '>', '>=']]],
    ['identifier', ['[A-Za-z][A-Za-z0-9]*']],
    ['constant', ['\d+(\.\d+)?']]
]


class LexerEngine:
    def __init__(self):
        self.cur = 0
        self.regexes = []
        self.program = ''

    def build_regexes(self):
        for _type in lexicon:
            for word in _type[1]:
                self.regexes.append(re.compile(word))

    def process(self):
        while self.cur < len(self.program):
            token = ()
            max_length = 0
            for i, regex in enumerate(self.regexes):
                r = regex.match(self.program[self.cur:])
                if r and r.end() > max_length:
                    max_length = r.end()
                    token = (i, r.group())
            self.cur += max_length
            if max_length == 0:
                self.error(self.cur)
            self.print_token(token)

    def print_token(self, token):
        regex_sum = 0
        for _type in lexicon:
            regex_sum += len(_type[1])
            if regex_sum > token[0]:
                if _type[0] is not 'blank': print(_type[0], token[1])
                break

    def error(self, pos):
        print('Error at {}'.format(pos))
        exit()


def main():
    lexer = LexerEngine()
    with open('program.txt') as f:
        lexer.program = f.read()
        lexer.build_regexes()
        lexer.process()

if __name__ == '__main__':
    main()