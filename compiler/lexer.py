import re
import struct


lexicon = [
    ['blank', '\s'],
    ['key_word', 'const|var|procedure|if|then|else|while|do|call|begin|end|repeat|until|read|write|odd'],
    ['delimiter', '\.|\(|\)|,|;'],
    ['operator', '\+|-|\*|/|:=|=|<>|<|<=|>=|>'],
    ['identifier', '[A-Za-z][A-Za-z0-9]*'],
    ['constant', '\d+(\.\d+)?']
]


class LexerEngine:
    def __init__(self):
        self.lexicon = []
        for word in lexicon:
            self.lexicon.append([word[0], re.compile(word[1])])

    def process(self, program):
        cur = 0
        ret = ''
        error = ''
        while cur < len(program):
            max_length = 0
            token = ()
            for word in self.lexicon:
                r = word[1].match(program[cur:])
                if r and r.end() > max_length:
                    max_length = r.end()
                    token = (word[0], r.group())
            cur += max_length
            if max_length == 0:
                print('Error at {}'.format(cur))
                break
            if token[0] is 'blank':
                continue
            elif token[0] is 'constant' and '.' not in token[1]:
                # integer constant
                print('{}\t{}'.format(token[0], bin(int(token[1]))))
            else:
                print('{}\t{}'.format(token[0], token[1]))
                # print(token[0], token[1])

    def error(self, pos):
        pass


def main():
    lexer = LexerEngine()
    with open('../doc/program.txt') as f:
        lexer.process(f.read())

if __name__ == '__main__':
    main()