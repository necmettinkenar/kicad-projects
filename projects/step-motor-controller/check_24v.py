import re, io

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
sch = io.open(PROJ + r'\step-motor-controller.kicad_sch', encoding='utf-8').read()
wires = []
for m in re.finditer(r'\(wire \(pts \(xy (-?[\d.]+) (-?[\d.]+)\) \(xy (-?[\d.]+) (-?[\d.]+)\)\)', sch):
    wires.append(tuple(float(g) for g in m.groups()))

px, py = 322.78, 124.11
print('wires touching U4.16 pin (322.78, 124.11):')
for w in wires:
    x1, y1, x2, y2 = w
    if (abs(x1 - px) < 0.05 and abs(y1 - py) < 0.05) or (abs(x2 - px) < 0.05 and abs(y2 - py) < 0.05):
        print('  ', w)

# find the vertical wire from U4.16's pin upward (the +24V tap candidate)
print('all wires with x in [320..325] and y in [20..130]:')
for w in wires:
    x1, y1, x2, y2 = w
    if 318 < x1 < 328 and 318 < x2 < 328 and min(y1, y2) < 130 and max(y1, y2) > 20:
        print('  ', w)
