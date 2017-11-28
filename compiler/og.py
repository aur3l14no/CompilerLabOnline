import re

with open('../doc/og.txt') as f:
    raw_rules = [rule for rule in f.read().split('\n')]


rules = []  # rule[0] for left, rule[1] for right

for rule in raw_rules:
    left, right = rule.split('->')
    for right_seg in right.split('|'):
        rules.append((left, right_seg))


V = set()
V_n = set()
V_t = set()

for rule in rules:
    for v in rule[1]:
        V.add(v)
    V_n.add(rule[0])


for e in V:
    if e not in V_n:
        V_t.add(e)




def calc_F(flag):
    def insert(u, b):
        if (u, b) not in F:
            F.append((u, b))
            stack.append((u, b))
    stack = []
    F = []
    if flag == 0:
        p0, p1 = 0, 1
    else:
        p0, p1 = -1, -2
    for rule in rules:
        b = None
        if rule[1][p0] in V_t:
            b = rule[1][p0]
        if len(rule[1]) >= 2 and rule[1][p0] in V_n and rule[1][p1] in V_t:
            b = rule[1][p1]
        if b:
            insert(rule[0], b)
        while len(stack) > 0:
            v, b = stack.pop()
            for rule in rules:
                if rule[1][p0] == v:
                    insert(rule[0], b)
    return F

first_vt = calc_F(0)
last_vt = calc_F(1)

priority_tab = dict()
for rule in rules:
    for i in range(len(rule[1]) - 1):
        if rule[1][i] in V_t and rule[1][i+1] in V_t:
            priority_tab[(rule[1][i], rule[1][i+1])] = 0
        if i < len(rule[1])-2 and rule[1][i] in V_t and rule[1][i+1] in V_n and rule[1][i+2] in V_t:
            priority_tab[(rule[1])]
