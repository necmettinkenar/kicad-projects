import re, io

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
sch = io.open(PROJ + r'\step-motor-controller.kicad_sch', encoding='utf-8').read()

# parse wires in order with their net (net unknown from file — but we know emission order:
# rails first then taps then signals). Instead: match wires to nets geometrically is hard;
# so re-run the generator logic is better. For now: find touching wire pairs (different segments
# that share an endpoint or a T-touch) — those are potential shorts.
wires = []
for m in re.finditer(r'\(wire \(pts \(xy (-?[\d.]+) (-?[\d.]+)\) \(xy (-?[\d.]+) (-?[\d.]+)\)\)', sch):
    wires.append(tuple(float(g) for g in m.groups()))

def pt_on_seg(px, py, x1, y1, x2, y2, tol=0.05):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return False
    t = ((px - x1) * dx + (py - y1) * dy) / L2
    if t < -0.001 or t > 1.001:
        return False
    return ((px - (x1 + t * dx)) ** 2 + (py - (y1 + t * dy)) ** 2) ** 0.5 < tol

# T-touches: an endpoint of one wire lying on the interior of another wire
touch = 0
examples = []
for i, (x1, y1, x2, y2) in enumerate(wires):
    for j, (a1, b1, a2, b2) in enumerate(wires):
        if i == j:
            continue
        for (px, py) in ((x1, y1), (x2, y2)):
            if pt_on_seg(px, py, a1, b1, a2, b2):
                touch += 1
                if len(examples) < 20:
                    examples.append(((x1, y1, x2, y2), (a1, b1, a2, b2), (px, py)))
print('total wires:', len(wires))
print('T-touch incidents (endpoint on other wire interior):', touch)
for e in examples[:12]:
    print('  wire', e[0], 'endpoint', e[2], 'on wire', e[1])
