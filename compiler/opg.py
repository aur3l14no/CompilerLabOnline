import re
from io import StringIO
from collections import namedtuple
from collections import deque

Rule = namedtuple('Rule', 'left, right')
PRIORITY_SYM = ('=', '>', '<')


class OPGEngine:
    def __init__(self):
        self.rules = []  # rule[0] for left, rule[1] for right
        self.V = set()
        self.V_n = set()
        self.V_t = set()
        self.terminal = ''
        self.priority_tab = dict()

    def import_rules(self, raw_rules):
        for rule in raw_rules:
            left, right = rule.split('->')
            for right_seg in right.split('|'):
                self.rules.append(Rule(left, right_seg))
        self.terminal = self.rules[0].left
        for rule in self.rules:
            for v in rule.right:
                self.V.add(v)
            self.V_n.add(rule.left)
        for v in self.V:
            if v not in self.V_n:
                self.V_t.add(v)

    def calc_priority_tab(self):
        # tab[v1][v2]
        # 1   :   >
        # -1  :   <
        # 0   :   =
        # ?   :   ?

        def calc_F(flag):  # calculate FIRSTVT(flag==0) and LASTVT(flag!=0)
            stack = deque()
            F = []

            def insert(u, b):
                if (u, b) not in F:
                    F.append((u, b))
                    stack.append((u, b))

            if flag == 0:  # FIRST
                p0, p1 = 0, 1
            else:  # LAST
                p0, p1 = -1, -2
            for rule in self.rules:
                b = None
                if rule.right[p0] in self.V_t:
                    b = rule.right[p0]
                if len(rule.right) >= 2 and rule.right[p0] in self.V_n and rule.right[p1] in self.V_t:
                    b = rule.right[p1]
                if b:
                    insert(rule.left, b)
                while len(stack) > 0:
                    v, b = stack.pop()
                    for rule in self.rules:
                        if rule.right[p0] == v:
                            insert(rule.left, b)
            return F

        first_vt = calc_F(0)
        last_vt = calc_F(1)
        # print(first_vt)
        # print(last_vt)
        for rule in self.rules:
            right = rule.right
            for i in range(len(right) - 1):
                if right[i] in self.V_t and right[i + 1] in self.V_t:
                    self.priority_tab[(right[i], right[i + 1])] = 0
                if i < len(right) - 2 and right[i] in self.V_t and right[i + 1] in self.V_n and right[i + 2] in self.V_t:
                    self.priority_tab[(right[i], right[i + 2])] = 0
                if right[i] in self.V_t and right[i + 1] in self.V_n:
                    for x, b in first_vt:
                        if x == right[i + 1]:
                            self.priority_tab[(right[i], b)] = -1
                if right[i] in self.V_n and right[i + 1] in self.V_t:
                    for x, a in last_vt:
                        if x == right[i]:
                            self.priority_tab[(a, right[i + 1])] = 1
        return self.priority_tab

    def print_priority_tab(self):
        print(' \t', end='')
        for v2 in self.V_t:
            print('{}\t'.format(v2), end='')
        print()
        for v1 in self.V_t:
            print('{}\t'.format(v1), end='')
            for v2 in self.V_t:
                priority = self.priority_tab.get((v1, v2))
                if priority == 0:
                    sym = '='
                elif priority == 1:
                    sym = '>'
                elif priority == -1:
                    sym = '<'
                else:
                    sym = '?'
                print('{}\t'.format(sym), end='')
            print()

    def analyse(self, program):
        template = '{step:>3}    {stack:60}    {priority:3}   {cur_sym:3}    {program_remaining:40}'
        stack = []
        cur = 0
        step = 0

        def error():
            print('Error at {}'.format(cur))

        def reduce(seg):
            seg = ''.join([*map(lambda x: '$' if x in self.V_n else x, seg)])
            for rule in self.rules:
                right = ''.join([*map(lambda x: '$' if x in self.V_n else x, rule.right)])
                if seg == right:
                    return rule.left

        while cur <= len(program):
            step += 1
            if len(stack) == 1 and stack[-1] == self.terminal and cur == len(program):
                print(template.format(step=step, stack=str(stack), priority='END', cur_sym='', program_remaining=''))
                break
            if cur == len(program):
                cur_sym = ''
                priority = 1
            else:
                priority = -1
                cur_sym = program[cur]
                for i in range(len(stack)-1, -1, -1):
                    if stack[i] in self.V_t:
                        priority = self.priority_tab.get((stack[i], cur_sym))
                        break

            print(template.format(
                step=step,
                stack=str(stack),
                priority='?' if priority is None else PRIORITY_SYM[priority],
                cur_sym=cur_sym,
                program_remaining=program[min(len(program), cur + 1):]))

            if priority == 1:
                t = ''
                a = None
                # find the string that is to reduce
                while True:
                    if stack[-1] in self.V_t:
                        if a and self.priority_tab.get((stack[-1], a)) == -1:
                            break
                        else:
                            a = stack[-1]
                    t += stack.pop()
                    if len(stack) == 0:
                        break
                t = t[::-1]
                reduced = reduce(t)
                if reduced:
                    stack.append(reduce(t))
                else:
                    error()
                    break
            elif priority == 0 or priority == -1:
                stack.append(cur_sym)
                cur += 1
            else:
                error()
                break


def main():
    with open('../doc/og.txt') as f:
        raw_rules = [*f.read().split('\n')]
    opg_engine = OPGEngine()
    opg_engine.import_rules(raw_rules)
    opg_engine.calc_priority_tab()
    # opg_engine.print_priority_tab()
    program = 'i+i*(i+i)'
    opg_engine.analyse(program)


if __name__ == '__main__':
    main()
