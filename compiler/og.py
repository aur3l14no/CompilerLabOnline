import re
from collections import namedtuple
from collections import deque

Rule = namedtuple('Rule', 'left, right')

with open('../doc/og.txt') as f:
    raw_rules = [*f.read().split('\n')]


rules = []  # rule[0] for left, rule[1] for right

for rule in raw_rules:
    left, right = rule.split('->')
    for right_seg in right.split('|'):
        rules.append(Rule(left, right_seg))


V = set()
V_n = set()
V_t = set()

for rule in rules:
    for v in rule.right:
        V.add(v)
    V_n.add(rule.left)


for e in V:
    if e not in V_n:
        V_t.add(e)


def calc_F(flag):
    def insert(u, b):
        if (u, b) not in F:
            F.append((u, b))
            stack.append((u, b))
    stack = deque()
    F = []
    if flag == 0:
        p0, p1 = 0, 1
    else:
        p0, p1 = -1, -2
    for rule in rules:
        b = None
        if rule.right[p0] in V_t:
            b = rule.right[p0]
        if len(rule.right) >= 2 and rule.right[p0] in V_n and rule.right[p1] in V_t:
            b = rule.right[p1]
        if b:
            insert(rule.left, b)
        while len(stack) > 0:
            v, b = stack.pop()
            for rule in rules:
                if rule.right[p0] == v:
                    insert(rule.left, b)
    return F

first_vt = calc_F(0)
last_vt = calc_F(1)

# print(first_vt)
# print(last_vt)

priority_tab = dict()
for rule in rules:
    right = rule.right
    for i in range(len(right) - 1):
        if right[i] in V_t and right[i+1] in V_t:
            priority_tab[(right[i], right[i+1])] = 0
        if i < len(right)-2 and right[i] in V_t and right[i+1] in V_n and right[i+2] in V_t:
            priority_tab[(right[i], right[i+2])] = 0
        if right[i] in V_t and right[i+1] in V_n:
            for x, b in first_vt:
                if x == right[i+1]:
                    priority_tab[(right[i], b)] = -1
        if right[i] in V_n and right[i+1] in V_t:
            for x, a in last_vt:
                if x == right[i]:
                    priority_tab[(a, right[i+1])] = 1

print(priority_tab)

print(' \t', end='')
for v2 in V_t:
    print('{}\t'.format(v2), end='')
print()
for v1 in V_t:
    print('{}\t'.format(v1), end='')
    for v2 in V_t:
        priority = priority_tab.get((v1, v2))
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



stack = deque()
cur = 0
step = 0

def error():
    print('You fucked up my system again. I hate U!!!!')
    print(stack)
    print(program[cur:])
    exit()

program = 'i+i*i'

while cur < len(program) or len(stack) > 1:
    cur_sym = program[cur]
    if len(stack) == 0:
        priority = -1
    elif cur == len(program) - 1:
        priority = 1
    elif stack[-1] in V_n:
        priority = -1
    else:
        priority = priority_tab.get((stack[-1], cur_sym))
    if priority == 1:
        t = ''
        a = stack[-1]
        while stack[-1] in V_n or priority_tab.get(stack[-1], a) == 0:  # a_i > a_i+1
            t += stack.pop()
        tag_123 = False
        for rule in rules:
            if rule.right == t:
                stack.append(rule.left)
                tag_123 = True
        if tag_123:
            print("why>????")
    elif priority == -1:
        stack.append(cur_sym)
        cur += 1
    else:
        error()
    print(step, stack, priority, cur_sym, program[cur:])
    step += 1
