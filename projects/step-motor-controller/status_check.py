import json, re, io

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
txt = io.open(PROJ + r'\exported-netlist.net', encoding='utf-8').read()
exp = json.load(io.open(PROJ + r'\nets.json', encoding='utf-8'))

nets = {}
for m in re.finditer(r'\(net \(code "\d+"\)\s*\(name "([^"]+)"\)', txt):
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
    for n in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
        nodes.add((n.group(1), n.group(2)))
    nets[name] = nodes

ok = 0
bad = []
for name, members in exp.items():
    want = set((r, str(p)) for (r, p) in members)
    got = nets.get(name, set())
    if want == got:
        ok += 1
    else:
        bad.append((name, len(want), len(got)))

print('EXACT MATCH nets:', ok, '/', len(exp))
print('mismatched:')
for b in bad[:12]:
    print('  ', b)
un = [n for n in nets if n.startswith('unconnected-')]
print('unconnected- nets:', len(un), '(expected NC: 25)')
conn = sum(len(v) for n, v in nets.items() if not n.startswith('unconnected-'))
print('connected pins in named nets:', conn, '/ 142')
