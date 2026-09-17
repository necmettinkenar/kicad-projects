import re, io, json

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
sch = io.open(PROJ + r'\step-motor-controller.kicad_sch', encoding='utf-8').read()

wires = []
for m in re.finditer(r'\(wire \(pts \(xy (-?[\d.]+) (-?[\d.]+)\) \(xy (-?[\d.]+) (-?[\d.]+)\)\)', sch):
    wires.append(tuple(float(g) for g in m.groups()))

def pt_on_seg(px, py, x1, y1, x2, y2, tol=0.05):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return False
    t = ((px - x1) * dx + (py - y1) * dy) / L2
    if t < 0.0 or t > 1.0:
        return False
    return math_hypot(px - (x1 + t * dx), py - (y1 + t * dy)) < tol

def math_hypot(a, b):
    return ((a) ** 2 + (b) ** 2) ** 0.5

# pin konumlari (COMPS snap sonrasi): R5 (snap165, snap122)=(165.1, 121.92); pin1 = (165.1-3.81, 121.92)
pins = {
    'R5.1': (165.1 - 3.81, 121.92),
    'R6.1': (165.1 - 3.81, 139.7),
    'R2.1': (115.57 - 3.81, 236.22),
    'PS1.4': (115.57 + 10.16, 69.85 - 2.54),
    'J3.2': (245.11 + 5.08, 205.74 - 2.54 + 2.54),  # rot180: pin2 (X+5.08, Y+2.54*?) - yaklasik
    'S2.3': (55.88 + 5.08, 168.28 - 2.54),  # rot180 pin3
    'S4.2': (55.88 + 5.08, 212.09),
}

for name, (px, py) in pins.items():
    on = []
    for (x1, y1, x2, y2) in wires:
        if pt_on_seg(px, py, x1, y1, x2, y2, 0.15):
            on.append((x1, y1, x2, y2))
    print(f'{name} @ ({px:.2f},{py:.2f}): tel uzerinde={"EVET" if on else "HAYIR"} ({len(on)} tel)')
    for w in on[:3]:
        print('    ', w)

# pin konumlarini sembolden dogru almak icin: sembol instanslarini oku
inst = {}
for m in re.finditer(r'\(symbol\n\t\t\(lib_id "([^"]+)"\)\n\t\t\(at ([\d.]+) ([\d.]+) (\d+)\)', sch):
    pass
# reference'lardan bulalim
for m in re.finditer(r'\(property "Reference" "([^"]+)" \(at ([\d.]+) ([\d.]+)', sch):
    inst[m.group(1)] = (float(m.group(2)), float(m.group(3)))
print('R5 ref prop konumu:', inst.get('R5'))
