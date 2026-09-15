import json, re, io, sys

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
txt = io.open(PROJ + r'\exported-netlist.net', encoding='utf-8').read()
exp = json.load(io.open(PROJ + r'\nets.json', encoding='utf-8'))

# parse exported nets (multi-line format)
exported = {}
for m in re.finditer(r'\(net\n\t\t\t\(code "\d+"\)\n\t\t\t\(name "([^"]+)"\)', txt):
    name = m.group(1)
    start = m.start()
    depth = 0
    blk = ''
    for k in range(start, len(txt)):
        if txt[k] == '(':
            depth += 1
        elif txt[k] == ')':
            depth -= 1
            if depth == 0:
                blk = txt[start:k + 1]
                break
    nodes = set()
    for n in re.finditer(r'\(ref "([^"]+)"\)\n\t\t\t\t\(pin "([^"]+)"\)', blk):
        nodes.add((n.group(1), n.group(2)))
    if not name.startswith('unconnected-') and nodes:
        exported[name] = nodes

expected = {name: set((r, str(p)) for (r, p) in members) for name, members in exp.items()}

# membership-based matching
exp_sets = {name: frozenset(members) for name, members in expected.items()}
exp_by_set = {}
for name, s in exp_sets.items():
    exp_by_set.setdefault(s, []).append(name)

matched = {}
unmatched_exp = []
for name, s in exp_sets.items():
    hit = None
    for ename, enodes in exported.items():
        if frozenset(enodes) == s:
            hit = ename
            break
    if hit:
        matched[name] = hit
    else:
        unmatched_exp.append((name, sorted(s)))

extra = []
for ename, enodes in exported.items():
    fs = frozenset(enodes)
    if fs not in exp_by_set:
        extra.append((ename, sorted(enodes)))

print('expected nets:', len(expected))
print('exported named nets:', len(exported))
print('EXACT membership matches:', len(matched), '/', len(expected))
if unmatched_exp:
    print('--- unmatched expected nets ---')
    for name, members in unmatched_exp:
        print('  ', name, '->', members)
if extra:
    print('--- exported nets with no exact expected match (merged/split?) ---')
    for ename, nodes in extra[:15]:
        print('  ', ename, '->', nodes)
