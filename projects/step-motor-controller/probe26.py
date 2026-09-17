import re, io

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
txt = io.open(PROJ + r'\exported-netlist.net', encoding='utf-8').read()

nets = []
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
    nodes = re.findall(r'\(ref "([^"]+)"\)\n\t\t\t\t\(pin "([^"]+)"\)', blk)
    nets.append((name, len(nodes), sorted(nodes)[:8]))

print('tum netler:')
for (name, n, sample) in sorted(nets):
    if not name.startswith('unconnected-'):
        print(f'  {name:20} {n:2} pins: {sample}')
