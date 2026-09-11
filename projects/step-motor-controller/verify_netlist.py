import json, re, sys

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'

txt = open(PROJ + r'\exported-netlist.net', encoding='utf-8').read()

# parse multi-line net blocks:
# (net\n (code "N")\n (name "NAME")\n (class ...)\n (node\n (ref "X")\n (pin "Y") ...\n )\n ... )
exported = {}
for nm in re.finditer(r'\(net\n\s*\(code "\d+"\)\n\s*\(name "([^"]+)"\)', txt):
    name = nm.group(1)
    blk_start = nm.start()
    # find matching close for this (net block
    depth = 0
    for k in range(blk_start, len(txt)):
        if txt[k] == '(':
            depth += 1
        elif txt[k] == ')':
            depth -= 1
            if depth == 0:
                blk = txt[blk_start:k+1]
                break
    nodes = set()
    for n in re.finditer(r'\(ref "([^"]+)"\)\s*\n\s*\(pin "([^"]+)"\)', blk):
        nodes.add((n.group(1), n.group(2)))
    exported[name] = nodes

expected_raw = json.load(open(PROJ + r'\nets.json', encoding='utf-8'))
expected = {k: set((r, str(p)) for r, p in v) for k, v in expected_raw.items()}

print(f'exported nets: {len(exported)} | expected nets: {len(expected)}')

ok = True
for name in sorted(expected):
    exp = expected[name]
    got = exported.get(name, set())
    missing = exp - got
    extra = got - exp
    if missing or extra or name not in exported:
        ok = False
        print(f'MISMATCH {name}:')
        if name not in exported:
            print('  NET MISSING ENTIRELY')
        for x in sorted(missing):
            print(f'  missing: {x[0]}.{x[1]}')
        for x in sorted(extra):
            print(f'  extra:   {x[0]}.{x[1]}')

# nets present in export but not expected (unexpected auto-nets)
auto_nets = [n for n in exported if n not in expected and not n.startswith('unconnected-')]
unconnected = [n for n in exported if n.startswith('unconnected-')]
if auto_nets:
    ok = False
    for n in auto_nets:
        print(f'UNEXPECTED NET: {n} -> {sorted(exported[n])}')
print(f'unconnected auto-nets (pins without labels): {len(unconnected)}')
for n in unconnected:
    print(f'  {n}: {sorted(exported[n])}')

# pin count totals
exp_total = sum(len(v) for v in expected.values())
sig_total = sum(len(v) for n, v in exported.items() if not n.startswith('unconnected-'))
print(f'total expected connections: {exp_total} | exported in named nets: {sig_total}')
print(f'intentional NC pins (unconnected- nets): {len(unconnected)} (SW1.3 SW2.3 U3 x16 U4.5-6 U5.13-15 U6.13-16 = 23)')
print('RESULT:', 'PASS - netlist matches Excel table exactly' if ok and not auto_nets else 'FAIL')
sys.exit(0 if ok and not auto_nets else 1)
