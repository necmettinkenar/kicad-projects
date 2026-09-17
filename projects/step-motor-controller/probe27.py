import re, io, json

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
txt = io.open(PROJ + r'\exported-netlist.net', encoding='utf-8').read()
exp = json.load(io.open(PROJ + r'\nets.json', encoding='utf-8'))

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
    nodes = set(re.findall(r'\(ref "([^"]+)"\)\n\t\t\t\t\(pin "([^"]+)"\)', blk))
    exported[name] = nodes

for net in ['GND', '+24V', 'SW1_SIG', 'SW2_SIG', 'FSR1_TOP']:
    want = set((r, str(p)) for (r, p) in exp[net])
    got = exported.get(net, set())
    missing = want - got
    extra = got - want
    print(f'{net}: eksik={sorted(missing)} | fazla={sorted(extra)}')

# bu pinlerin netlist'te nerede olduguna bak
missing_pins = {('PS1', '4'), ('R5', '1'), ('R6', '1'), ('R2', '1')}
for name, nodes in exported.items():
    hit = missing_pins & nodes
    if hit:
        print(f'  bulundu: {hit} -> net "{name}"')
