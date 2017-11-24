import re


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
                error += 'Error at {}'.format(cur)
                # print(error)
                return ret, error
            if token[0] is not 'blank':
                ret += token[0] + ' ' + token[1] + '\n'
                # print(token[0], token[1])
        return ret, error

    def error(self, pos):
        pass


def main():
    lexer = LexerEngine()
    with open('../program.txt') as f:
        ret, error = lexer.process(f.read())
        # print(ret)
        # print(error)

if __name__ == '__main__':
    main()