#!/usr/bin/env python3
"""
Step Motor Controller — WIRED schematic generator v3 (KiCad 10).
- A* grid router (1.27mm) for ALL wires (signals + power taps)
- Power rails with junction taps
- Obstacles: symbol bodies, foreign pins; foreign wires = high-cost (cross OK, parallel-run avoided)
- Netlist must match the Excel table exactly
"""
import re, os, json, uuid, random, math, heapq

SYM_DIR = r'C:\Program Files\KiCad\10.0\share\kicad\symbols'
PROJ = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.join(PROJ, 'step-motor-controller.kicad_sch')
ROOT = 'a1b2c3d4-0000-4000-8000-000000000001'
NETS = json.load(open(os.path.join(PROJ, 'nets.json'), encoding='utf-8'))

def uid():
    return str(uuid.UUID(int=random.getrandbits(128), version=4))

def extract_block(txt, start):
    depth = 0
    for i in range(start, len(txt)):
        if txt[i] == '(':
            depth += 1
        elif txt[i] == ')':
            depth -= 1
            if depth == 0:
                return txt[start:i + 1]
    raise ValueError('unbalanced')

def extract_lib_symbol(lib, name):
    txt = open(os.path.join(SYM_DIR, lib + '.kicad_sym'), encoding='utf-8').read()
    m = re.search(r'\(symbol "' + re.escape(name) + r'"[\s(]', txt)
    if not m:
        return None
    blk = extract_block(txt, m.start())
    depth = 0
    while depth < 4:
        em = re.search(r'\(extends "([^"]+)"\)', blk)
        if not em:
            break
        parent = em.group(1)
        pm = re.search(r'\(symbol "' + re.escape(parent) + r'"[\s(]', txt)
        pblk = extract_block(txt, pm.start())
        pblk = pblk.replace('(symbol "' + parent + '"', '(symbol "' + name + '"', 1)
        pblk = pblk.replace('"' + parent + '_', '"' + name + '_')
        blk = re.sub(r'\n?\s*\(extends "[^"]+"\)', '', pblk)
        depth += 1
    return blk.replace('(symbol "' + name + '"', '(symbol "' + lib + ':' + name + '"', 1)

def parse_pins(blk):
    pins = {}
    for m in re.finditer(r'\(pin (\w+) (\w+)\s*\n?\s*\(at (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)', blk):
        etype = m.group(1)
        x, y, a = float(m.group(3)), float(m.group(4)), float(m.group(5))
        block = extract_block(blk, m.start())
        nm = re.search(r'\(name "([^"]*)"', block)
        nb = re.search(r'\(number "([^"]*)"', block)
        if nb:
            pins[nb.group(1)] = (x, y, a, nm.group(1) if nm else '', etype)
    return pins

def box_symbol(libname, name, ref_prefix, left_pins, right_pins, value=''):
    n = max(len(left_pins), len(right_pins))
    span = (n - 1) * 2.54
    half_h = span / 2 + 1.27
    w = 12.7
    L = []
    A = L.append
    A('(symbol "' + libname + ':' + name + '" (in_bom yes) (on_board yes)')
    A('(property "Reference" "' + ref_prefix + '" (at 0 ' + str(round(half_h + 2.54, 2)) + ' 0) (effects (font (size 1.27 1.27))))')
    A('(property "Value" "' + (value or name) + '" (at 0 ' + str(round(-half_h - 2.54, 2)) + ' 0) (effects (font (size 1.27 1.27))))')
    A('(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    A('(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    A('(property "Description" "Auto-generated" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    A('(symbol "' + name + '_0_1" (rectangle (start -12.7 ' + str(round(half_h, 2)) + ') (end 12.7 ' + str(round(-half_h, 2)) + ') (stroke (width 0.254) (type default)) (fill (type background))))')
    A('(symbol "' + name + '_1_1"')
    for side, plist in (('L', left_pins), ('R', right_pins)):
        for idx, (num, pname, etype) in enumerate(plist):
            y = span / 2 - idx * 2.54
            x = -w - 5.08 if side == 'L' else w + 5.08
            ang = 0 if side == 'L' else 180
            A('(pin ' + etype + ' line (at ' + str(x) + ' ' + str(y) + ' ' + str(ang) + ') (length 5.08)')
            A('(name "' + pname + '" (effects (font (size 1.27 1.27)))) (number "' + num + '" (effects (font (size 1.27 1.27)))))')
    A(')')
    A(')')
    return '\n'.join(L)

u3_left = [('1', '3V3', 'power_out'), ('2', 'EN', 'input'), ('14', 'GND', 'power_in'), ('19', '5V', 'power_in'),
           ('3', 'GPIO36', 'bidirectional'), ('4', 'GPIO39', 'bidirectional'), ('5', 'GPIO34', 'bidirectional'),
           ('6', 'GPIO35', 'bidirectional'), ('7', 'GPIO32', 'bidirectional'), ('8', 'GPIO33', 'bidirectional'),
           ('13', 'GPIO12', 'free'), ('16', 'NC', 'free'), ('17', 'NC', 'free'), ('18', 'NC', 'free'),
           ('20', 'NC', 'free'), ('21', 'NC', 'free'), ('22', 'NC', 'free'), ('23', 'NC', 'free'), ('24', 'NC', 'free')]
u3_right = [('12', 'GPIO14', 'bidirectional'), ('26', 'GPIO4', 'bidirectional'), ('29', 'GPIO5', 'bidirectional'),
            ('9', 'GPIO25', 'bidirectional'), ('10', 'GPIO26', 'bidirectional'), ('11', 'GPIO27', 'bidirectional'),
            ('32', 'GPIO21', 'bidirectional'), ('33', 'GPIO22', 'bidirectional'), ('15', 'GPIO13', 'bidirectional'),
            ('30', 'GPIO18', 'bidirectional'), ('31', 'GPIO19', 'bidirectional'),
            ('27', 'GPIO16', 'bidirectional'), ('28', 'GPIO17', 'bidirectional'), ('37', 'GPIO23', 'bidirectional'),
            ('25', 'NC', 'free'), ('34', 'NC', 'free'), ('35', 'NC', 'free'), ('36', 'NC', 'free'), ('38', 'NC', 'free')]
u4_left = [('1', 'EN', 'passive'), ('2', 'MS1', 'passive'), ('3', 'MS2', 'passive'), ('4', 'MS3', 'passive'),
           ('7', 'STEP', 'passive'), ('8', 'DIR', 'passive'), ('5', 'RST', 'free'), ('6', 'RST2', 'free')]
u4_right = [('16', 'VM', 'power_in'), ('9', 'GND', 'power_in'), ('15', 'GND', 'power_in'), ('10', 'VDD', 'power_in'),
            ('11', '2B', 'passive'), ('12', '2A', 'passive'), ('13', '1B', 'passive'), ('14', '1A', 'passive')]
u5_left = [('10', '3A', 'passive'), ('9', '3B', 'passive'), ('6', '2A', 'passive'), ('7', '2B', 'passive'),
           ('1', '1B', 'passive'), ('2', '1A', 'passive'), ('8', 'GND', 'power_in'), ('16', 'VCC', 'power_in')]
u5_right = [('3', '1Y', 'passive'), ('5', '2Y', 'passive'), ('11', '3Y', 'passive'),
            ('4', 'G', 'power_in'), ('12', '/G', 'power_in'), ('13', '4Y', 'free'), ('14', '4A', 'free'), ('15', '4B', 'free')]
u6_left = [('3', '1A', 'passive'), ('5', '2A', 'passive'), ('7', '3A', 'passive'), ('9', '4A', 'passive'),
           ('11', '5A', 'passive'), ('1', 'VCC', 'power_in'), ('8', 'GND', 'power_in'), ('13', '6A', 'free')]
u6_right = [('2', '1Y', 'passive'), ('4', '2Y', 'passive'), ('6', '3Y', 'passive'), ('10', '4Y', 'passive'),
            ('12', '5Y', 'passive'), ('14', '6Y', 'free'), ('15', 'NC', 'free'), ('16', 'NC', 'free')]
u1_left = [('1', 'VI', 'power_in'), ('2', 'GND', 'power_in'), ('3', 'VO', 'power_out')]

CUSTOM = {
    'KicadAuto:ESP32-DevKitC': box_symbol('KicadAuto', 'ESP32-DevKitC', 'U', u3_left, u3_right, 'ESP32-DevKitC'),
    'KicadAuto:LV8729': box_symbol('KicadAuto', 'LV8729', 'U', u4_left, u4_right, 'LV8729 Module'),
    'KicadAuto:AM26LS32ACN': box_symbol('KicadAuto', 'AM26LS32ACN', 'U', u5_left, u5_right, 'AM26LS32ACN'),
    'KicadAuto:74HC4050': box_symbol('KicadAuto', '74HC4050', 'U', u6_left, u6_right, '74HC4050N'),
    'KicadAuto:OKI-78SR': box_symbol('KicadAuto', 'OKI-78SR', 'U', u1_left, [], 'OKI-78SR-5'),
}

LIB_SYMS = {}
for lib, name in [('Device', 'R'), ('Device', 'C'), ('Device', 'C_Polarized'),
                  ('Switch', 'SW_SPDT'), ('Connector_Generic', 'Conn_01x02'),
                  ('Connector_Generic', 'Conn_01x03'), ('Connector_Generic', 'Conn_01x04'),
                  ('Connector_Generic', 'Conn_01x08'), ('Converter_ACDC', 'IRM-20-24'),
                  ('Transistor_BJT', 'BC547')]:
    blk = extract_lib_symbol(lib, name)
    if blk is None:
        print('FATAL: ' + lib + ':' + name + ' missing'); raise SystemExit(1)
    LIB_SYMS[lib + ':' + name] = blk
LIB_SYMS.update(CUSTOM)
LIB_PINS = {k: parse_pins(v) for k, v in LIB_SYMS.items()}

FOOTPRINTS = {
    'J1': 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal',
    'J2': 'Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical',
    'J3': 'Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical',
    'U2': 'Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical',
    'PS1': 'Converter_ACDC:Converter_ACDC_MeanWell_IRM-20-xx_THT',
    'U1': 'Converter_DCDC:Converter_DCDC_Murata_OKI-78SR_Vertical',
    'U3': 'AUTO:ESP32_SOCKET', 'U4': 'AUTO:STEPSTICK_2x8',
    'U5': 'Package_DIP:DIP-16_W7.62mm', 'U6': 'Package_DIP:DIP-16_W7.62mm',
    'Q1': 'Package_TO_SOT_THT:TO-92_Inline',
    'R1': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
    'R3': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
    'S1': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'S2': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'S3': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'S4': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'SW1': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'SW2': 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
}

COMPS = [
    ('J1',  'Connector_Generic:Conn_01x03', 'AC Input',     55, 70, 180, False),
    ('PS1', 'Converter_ACDC:IRM-20-24',     'IRM-20-24',   115, 70,   0, False),
    ('U1',  'KicadAuto:OKI-78SR',           'OKI-78SR-5',  170, 70,   0, False),
    ('C1',  'Device:C_Polarized',           '100uF/35V',   205, 70,   0, False),
    ('C2',  'Device:C_Polarized',           '10uF/16V',    222, 70,   0, False),
    ('U3',  'KicadAuto:ESP32-DevKitC',      'ESP32-DevKitC', 250, 155, 0, False),
    ('R11', 'Device:R', '10K',   205, 124, 0, False),
    ('C5',  'Device:C', '100nF', 218, 142, 0, False),
    ('Q1',  'Transistor_BJT:BC547', 'BC547', 315, 118, 0, False),
    ('R12', 'Device:R', '1K',    295, 118, 0, False),
    ('SW1', 'Switch:SW_SPDT', 'SW1', 120, 122, 0, False),
    ('SW2', 'Switch:SW_SPDT', 'SW2', 120, 140, 0, False),
    ('R5',  'Device:R', '10K',   165, 122, 0, False),
    ('R6',  'Device:R', '10K',   165, 140, 0, False),
    ('C3',  'Device:C', '100nF', 188, 122, 0, False),
    ('C4',  'Device:C', '100nF', 188, 140, 0, False),
    ('S1',  'Connector_Generic:Conn_01x03', 'Optic LS-1', 55, 152, 180, False),
    ('S2',  'Connector_Generic:Conn_01x03', 'Optic LS-2', 55, 168, 180, False),
    ('S3',  'Connector_Generic:Conn_01x03', 'Hall-1',     55, 196, 180, False),
    ('S4',  'Connector_Generic:Conn_01x03', 'Hall-2',     55, 212, 180, False),
    ('R7',  'Device:R', '10K',   100, 200, 0, False),
    ('R8',  'Device:R', '20K',   112, 200, 0, False),
    ('R9',  'Device:R', '10K',   135, 200, 0, False),
    ('R10', 'Device:R', '20K',   147, 200, 0, False),
    ('R1',  'Connector_Generic:Conn_01x02', 'FSR (external)', 100, 232, 180, False),
    ('R3',  'Connector_Generic:Conn_01x02', 'FSR (external)', 140, 232, 180, False),
    ('R2',  'Device:R', '10K',   115, 236, 0, False),
    ('R4',  'Device:R', '10K',   155, 236, 0, False),
    ('U4',  'KicadAuto:LV8729', 'LV8729 Module', 305, 133, 0, False),
    ('J2',  'Connector_Generic:Conn_01x04', 'Step Motor', 355, 136, 0, True),
    ('U5',  'KicadAuto:AM26LS32ACN', 'AM26LS32ACN', 285, 205, 0, False),
    ('J3',  'Connector_Generic:Conn_01x08', 'Encoder', 245, 205, 180, False),
    ('U6',  'KicadAuto:74HC4050', '74HC4050N', 330, 205, 180, False),
    ('U2',  'Connector_Generic:Conn_01x04', 'UART Display', 375, 155, 0, True),
]

def pin_endpoint(cx, cy, rot, mirror, lib_id, num):
    px, py, ang, nm, et = LIB_PINS[lib_id][num]
    if mirror:
        px, py = px, -py
        ang = -ang
    a = math.radians(rot)
    rx = px * math.cos(a) - py * math.sin(a)
    ry = px * math.sin(a) + py * math.cos(a)
    return cx + rx, cy - ry, (180 - (ang + rot)) % 360, nm, et

PINS = {}
for ref, lib_id, value, cx, cy, rot, mirror in COMPS:
    for num in LIB_PINS[lib_id]:
        ex, ey, outward, nm, et = pin_endpoint(cx, cy, rot, mirror, lib_id, num)
        PINS[(ref, num)] = (round(ex, 2), round(ey, 2), outward, nm, et)

NETS_NETOF = {}
for net, members in NETS.items():
    for (r, p) in members:
        NETS_NETOF[(r, str(p))] = net

RAILS = {'+24V': 24, '+5V': 32, '+3V3': 40, 'GND': 276}
RAIL_X0, RAIL_X1 = 30, 400

# ---------------- A* grid router ----------------
CELL = 1.27
GX0, GY0 = 5.0, 10.0
NX, NY = int(410 / CELL) + 1, int(287 / CELL) + 1
WIRE_COST = 40.0   # per-cell penalty for running along/crossing foreign wires

occ_block = set()   # (cx, cy) hard-blocked (symbol bodies, foreign pins)
occ_wire = {}       # (cx, cy) -> net_id (cells stamped by routed wires)

def cell_of(x, y):
    return (int(round((x - GX0) / CELL)), int(round((y - GY0) / CELL)))

def cell_xy(cx, cy):
    return (GX0 + cx * CELL, GY0 + cy * CELL)

# block symbol bodies (inflated)
BBOX = {}
for ref in {c[0] for c in COMPS}:
    info = next(c for c in COMPS if c[0] == ref)
    lib_id = info[1]
    pts = [PINS[(ref, n)][:2] for n in LIB_PINS[lib_id]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if max(xs) - min(xs) < 1:
        xs = [min(xs) - 3, max(xs) + 3]
    if max(ys) - min(ys) < 1:
        ys = [min(ys) - 3, max(ys) + 3]
    BBOX[ref] = (min(xs) - 1.0, min(ys) - 1.0, max(xs) + 1.0, max(ys) + 1.0)
    for cx in range(int((BBOX[ref][0] - GX0) / CELL), int((BBOX[ref][2] - GX0) / CELL) + 1):
        for cy in range(int((BBOX[ref][1] - GY0) / CELL), int((BBOX[ref][3] - GY0) / CELL) + 1):
            occ_block.add((cx, cy))

# block foreign pins (1.27 radius circle)
pin_cells = {}
for (ref, num), (ex, ey, out, nm, et) in PINS.items():
    nid = NETS_NETOF.get((ref, str(num)), 0)
    ccx, ccy = cell_of(ex, ey)
    pin_cells[(ref, num)] = (ccx, ccy, nid)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            occ_block.add((ccx + dx, ccy + dy))

# pins of net N must be reachable: exclude own-net pin cells from blocking via exempt set
def astar(start_cells, goal_cells, nid):
    """start_cells/goal_cells: sets of (cx,cy). Single layer."""
    start = None
    for c in start_cells:
        if (c[0], c[1]) not in occ_block:
            start = c
            break
    if start is None:
        return None
    goals = set((c[0], c[1]) for c in goal_cells if (c[0], c[1]) not in occ_block)
    if not goals:
        return None
    open_heap = [(0.0, start)]
    cost = {start: 0.0}
    came = {}
    while open_heap:
        f, cur = heapq.heappop(open_heap)
        if cur in goals:
            # reconstruct
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            path.reverse()
            return path
        if f > cost.get(cur, 1e18) + 1e-9:
            continue
        x, y = cur
        for dx, dy, dc in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1)):
            nx_, ny_ = x + dx, y + dy
            if not (0 <= nx_ < NX and 0 <= ny_ < NY):
                continue
            key = (nx_, ny_)
            if key in occ_block:
                continue
            pen = WIRE_COST if (key in occ_wire and occ_wire[key] != nid) else 0.0
            nc = cost[cur] + dc + pen
            if nc < cost.get(key, 1e18):
                cost[key] = nc
                came[key] = cur
                heapq.heappush(open_heap, (nc + abs(nx_ - gx) + abs(ny_ - gy), key))
    return None

def path_to_segments(path):
    segs = []
    run_start = path[0]
    prev_dir = None
    for i in range(1, len(path)):
        d = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        if prev_dir is not None and d != prev_dir:
            segs.append((run_start, path[i-1]))
            run_start = path[i-1]
        prev_dir = d
    segs.append((run_start, path[-1]))
    out = []
    for (a, b) in segs:
        ax, ay = cell_xy(*a)
        bx, by = cell_xy(*b)
        if abs(ax - bx) > 0.01 or abs(ay - by) > 0.01:
            out.append((ax, ay, bx, by))
    return out

def stamp_segments(segs, net_id):
    for (ax, ay, bx, by) in segs:
        steps = max(1, int(max(abs(bx - ax), abs(by - ay)) / CELL) * 2)
        for s in range(steps + 1):
            t = s / steps
            cx, cy = cell_of(ax + (bx - ax) * t, ay + (by - ay) * t)
            occ_wire.setdefault((cx, cy), net_id)

wires = []
junctions = []

def add_wire(x1, y1, x2, y2, net):
    if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
        return
    wires.append((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2), net))
    stamp_segments([(x1, y1, x2, y2)], net_idx[net])

def route_net_connection(a_xy, b_xy, net):
    nid = net_idx[net]
    a_cells = [cell_of(*a_xy)]
    b_cells = [cell_of(*b_xy)]
    path = astar(a_cells, b_cells, nid)
    if path is None:
        return []
    return path_to_segments(path)

net_idx = {n: i + 1 for i, n in enumerate(NETS)}
idx_net = {i + 1: n for n, i in net_idx.items()}

wires = []
junctions = []

# 1) rails
for net, y in RAILS.items():
    add_wire(RAIL_X0, y, RAIL_X1, y, net)

# helper: nearest rail x for a pin
def rail_tap_cells(y_rail):
    cells = []
    for cx in range(int((RAIL_X0 - GX0) / CELL), int((RAIL_X1 - GX0) / CELL) + 1):
        cy = int(round((y_rail - GY0) / CELL))
        cells.append((cx, cy))
    return cells

# 2) power taps via A*
tap_fail = []
for net, y_rail in RAILS.items():
    for (r, p) in [(r, str(p)) for (r, p) in NETS[net]]:
        if (r, p) not in PINS:
            continue
        ex, ey, outward, nm, et = PINS[(r, p)]
        rad = math.radians(outward)
        sx = round((ex + 3.81 * math.cos(rad)) / 1.27) * 1.27
        sy = round((ey - 3.81 * math.sin(rad)) / 1.27) * 1.27
        start_cells = [cell_of(sx, sy), cell_of(ex, ey)]
        goal_cells = rail_tap_cells(y_rail)
        path = astar(start_cells, goal_cells, net_idx[net])
        if path is None:
            tap_fail.append((net, r, p))
            continue
        segs = path_to_segments(path)
        add_wire(ex, ey, *segs[0][:2] + ()), None) if False else None
        # wire: pin -> first segment start (stub) then all segments
        add_wire(ex, ey, segs[0][0], segs[0][1], net)
        for (ax, ay, bx, by) in segs:
            add_wire(ax, ay, bx, by, net)
print('power taps done | failures:', len(tap_fail))
for f in tap_fail[:8]:
    print('  TAP FAIL:', f)

# 3) signal nets via A*
fail_log = []
for net, members in NETS.items():
    if net in RAILS:
        continue
    pts = [k for k in ((r, str(p)) for (r, p) in members) if k in PINS]
    if len(pts) < 2:
        continue
    pts_sorted = sorted(pts, key=lambda k: (PINS[k][0], PINS[k][1]))
    chain = [pts_sorted.pop(0)]
    while pts_sorted:
        cur = chain[-1]
        nxt = min(pts_sorted, key=lambda k: abs(PINS[k][0] - PINS[cur][0]) + abs(PINS[k][1] - PINS[cur][1]))
        chain.append(nxt)
        pts_sorted.remove(nxt)
    for i in range(len(chain) - 1):
        ax, ay, _, _, _ = PINS[chain[i]]
        bx, by, _, _, _ = PINS[chain[i + 1]]
        path = astar([cell_of(ax, ay)], [cell_of(bx, by)], net_idx[net])
        if path is None:
            fail_log.append((net, chain[i], chain[i + 1], 'astar-fail'))
            continue
        for (sx, sy, bx2, by2) in path_to_segments(path):
            add_wire(sx, sy, bx2, by2, net)

print('signal routing done | failures:', len(fail_log))
for f in fail_log[:8]:
    print('  FALLBACK:', f)

# junctions
def point_on_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return False
    t = ((px - x1) * dx + (py - y1) * dy) / L2
    if t <= 0.01 or t >= 0.99:
        return False
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)) < 0.05

endpoints = set()
for (x1, y1, x2, y2, net) in wires:
    endpoints.add((x1, y1, net))
    endpoints.add((x2, y2, net))
for (px, py, net) in endpoints:
    for (x1, y1, x2, y2, wnet) in wires:
        if wnet != net:
            continue
        if point_on_seg(px, py, x1, y1, x2, y2):
            junctions.append((px, py))
            break

print('wires:', len(wires), '| junctions:', len(junctions))
