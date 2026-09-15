import re, io, json

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
    nodes = []
    for n in re.finditer(r'\(ref "([^"]+)"\)\n\t\t\t\t\(pin "([^"]+)"\)', blk):
        nodes.append(n.group(1) + '.' + n.group(2))
    nets.append((name, nodes))

print('total nets:', len(nets))
named = [n for n in nets if not n[0].startswith('unconnected-')]
unconn = [n for n in nets if n[0].startswith('unconnected-')]
print('named nets:', len(named), '| unconnected nets:', len(unconn))
for name, nodes in named[:60]:
    print(' ', name, '->', len(nodes), 'pins:', ','.join(nodes[:6]) + ('...' if len(nodes) > 6 else ''))
