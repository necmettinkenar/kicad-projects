import re, json, os
from collections import defaultdict

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
RAILS = {'+24V': 24, '+5V': 32, '+3V3': 40, 'GND': 276}

txt = open(os.path.join(PROJ, 'step-motor-controller.kicad_sch'), encoding='utf-8').read()
wires = []
for m in re.finditer(r'\(wire \(pts \(xy (-?[\d.]+) (-?[\d.]+)\) \(xy (-?[\d.]+) (-?[\d.]+)\)\)', txt):
    wires.append(tuple(float(g) for g in m.groups()))
print('wires in file:', len(wires))

# net of each wire: infer by matching to rails and by finding which net's pin endpoints it serves.
# simpler: a wire that has an endpoint ON rail line y (x within span) touches that rail.
per_wire = defaultdict(list)
for (x1, y1, x2, y2) in wires:
    for (x, y) in ((x1, y1), (x2, y2)):
        for net, ry in RAILS.items():
            if abs(y - ry) < 0.01 and 29.9 < x < 400.1:
                per_wire[(x1, y1, x2, y2)].append((net, x, y))

print('wire endpoints touching rail lines:')
count = 0
for w, touches in sorted(per_wire.items()):
    nets = sorted(set(t[0] for t in touches))
    print('  wire', w, '->', touches)
    count += 1
    if count > 25:
        break
print('wires touching rails:', len(per_wire))
