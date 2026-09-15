import re

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
sch = open(PROJ + r'\step-motor-controller.kicad_sch', encoding='utf-8').read()

# find all wires touching C1's pins at (205, 66.19) and (205, 73.81)
wires = []
for m in re.finditer(r'\(wire \(pts \(xy (-?[\d.]+) (-?[\d.]+)\) \(xy (-?[\d.]+) (-?[\d.]+)\)\)', sch):
    wires.append(tuple(float(g) for g in m.groups()))

print('wires near C1 pins (x=205, y 60-80):')
for w in wires:
    x1, y1, x2, y2 = w
    if (abs(x1 - 205) < 2 or abs(x2 - 205) < 2) and (60 < y1 < 80 or 60 < y2 < 80):
        print('  ', w)

print('wires near PS1.4 (125.16, 67.46):')
for w in wires:
    x1, y1, x2, y2 = w
    if (abs(x1 - 125.16) < 2 or abs(x2 - 125.16) < 2) and (60 < y1 < 75 or 60 < y2 < 75):
        print('  ', w)

# count junctions near C1
print('junctions near C1:')
cnt = 0
for m in re.finditer(r'\(junction \(at (-?[\d.]+) (-?[\d.]+)\)', sch):
    jx, jy = float(m.group(1)), float(m.group(2))
    if abs(jx - 205) < 3 and 60 < jy < 80:
        print('  ', jx, jy)
        cnt += 1
if cnt == 0:
    print('   none')
