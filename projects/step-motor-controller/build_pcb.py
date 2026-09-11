#!/usr/bin/env python3
"""Step Motor Controller PCB v2 — real footprints, 45 nets, A* grid router (2-layer),
B.Cu GND pour. KiCad 10 pcbnew API."""
import pcbnew, os, json, math, heapq

PROJ = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(PROJ, 'step-motor-controller.kicad_pcb')
FP_ROOT = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
NETS = json.load(open(os.path.join(PROJ, 'nets.json'), encoding='utf-8'))

def mm(v):
    return pcbnew.FromMM(v)

WIDTHS = {'signal': 0.3, '+5V': 0.6, '+3V3': 0.4, '+24V': 0.8, 'GND': 0.5,
          'AC_L': 1.0, 'AC_N': 1.0,
          'MOT_1A': 0.8, 'MOT_1B': 0.8, 'MOT_2A': 0.8, 'MOT_2B': 0.8}
def width_for(net):
    return WIDTHS.get(net, 0.3)

CLEAR = 0.25
VIA_D, VIA_DRILL = 0.8, 0.4
CELL = 0.5
VIA_COST = 15.0

# ---------------- footprint loading ----------------
def load_fp(lib, name):
    fp = pcbnew.FootprintLoad(os.path.join(FP_ROOT, lib + '.pretty'), name)
    if fp is None:
        raise RuntimeError(f'footprint not found: {lib}:{name}')
    return fp

def pad_geo(fp):
    out = []
    org = fp.GetPosition()
    for pad in fp.Pads():
        pos = pad.GetPosition()
        sz = pad.GetSize()
        drill = pad.GetDrillSize()
        layers = pad.GetLayerSet()
        is_f = layers.Contains(pcbnew.F_Cu)
        is_b = layers.Contains(pcbnew.B_Cu)
        side = 'BOTH' if (is_f and is_b) else ('F' if is_f else 'B')
        out.append((pad.GetNumber(), pcbnew.ToMM(pos.x - org.x), pcbnew.ToMM(pos.y - org.y),
                    pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y), side, pcbnew.ToMM(drill.x)))
    return out

def make_compound(board, ref, value, pads):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    for num, x, y, w, h, side, drill in pads:
        p = pcbnew.PAD(fp)
        p.SetNumber(num)
        p.SetPinFunction(str(num))
        p.SetSize(pcbnew.VECTOR2I(mm(w), mm(h)))
        p.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        p.SetDrillSize(pcbnew.VECTOR2I(mm(drill), mm(drill)))
        lset = pcbnew.LSET()
        if side == 'BOTH':
            p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            for ly in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask):
                lset.AddLayer(ly)
        else:
            p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            for ly in (pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste) if side == 'F' else (pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_Paste):
                lset.AddLayer(ly)
        p.SetLayerSet(lset)
        fp.Add(p)
    board.Add(fp)
    return fp

COMPS = {}
def reg(ref, fp, cx, cy):
    geo = pad_geo(fp)
    # normalize corner-origin footprints: recenter pads on bbox center
    xs = [g[1] for g in geo]; ys = [g[2] for g in geo]
    bcx, bcy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    geo = [(n, x - bcx, y - bcy, w, h, s, d) for (n, x, y, w, h, s, d) in geo]
    COMPS[ref] = {'fp': fp, 'cx': cx, 'cy': cy, 'geo': geo, 'off': (bcx, bcy)}

reg('PS1', load_fp('Converter_ACDC', 'Converter_ACDC_MeanWell_IRM-20-xx_THT'), 26, 17)
reg('J1',  load_fp('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal'), 26, 41)
reg('U1',  load_fp('Converter_DCDC', 'Converter_DCDC_Murata_OKI-78SR_Vertical'), 54, 11)
reg('C1',  load_fp('Capacitor_THT', 'CP_Radial_D6.3mm_P2.50mm'), 54, 22)
reg('C2',  load_fp('Capacitor_THT', 'CP_Radial_D5.0mm_P2.50mm'), 65, 11)
reg('U5',  load_fp('Package_DIP', 'DIP-16_W7.62mm'), 29, 55)
reg('U6',  load_fp('Package_DIP', 'DIP-16_W7.62mm'), 29, 76)
reg('Q1',  load_fp('Package_TO_SOT_THT', 'TO-92_Inline'), 52, 76)
for r in ['R2', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12']:
    reg(r, load_fp('Resistor_SMD', 'R_0805_2012Metric'), 0, 0)
for r in ['C3', 'C4', 'C5']:
    reg(r, load_fp('Capacitor_SMD', 'C_0805_2012Metric'), 0, 0)
for r in ['R1', 'R3']:
    reg(r, load_fp('Connector_PinHeader_2.54mm', 'PinHeader_1x02_P2.54mm_Vertical'), 0, 0)
for r in ['S1', 'S2', 'S3', 'S4', 'SW1', 'SW2']:
    reg(r, load_fp('Connector_PinHeader_2.54mm', 'PinHeader_1x03_P2.54mm_Vertical'), 0, 0)
reg('J2', load_fp('Connector_PinSocket_2.54mm', 'PinSocket_1x04_P2.54mm_Vertical'), 0, 0)
reg('J3', load_fp('Connector_PinSocket_2.54mm', 'PinSocket_1x08_P2.54mm_Vertical'), 0, 0)
reg('U2', load_fp('Connector_PinSocket_2.54mm', 'PinSocket_1x04_P2.54mm_Vertical'), 0, 0)

POS = {
    'U3': (77, 46), 'U4': (103, 46), 'J2': (116, 39), 'J3': (116, 57), 'U2': (99, 12),
    'R1': (12, 94), 'R3': (20, 94), 'R2': (28, 94), 'R4': (36, 94),
    'R5': (56, 84), 'R6': (56, 92), 'C3': (63, 84), 'C4': (63, 92),
    'R7': (19, 36), 'R8': (19, 44), 'R9': (27, 36), 'R10': (27, 44),
    'R11': (58, 76), 'R12': (64, 76), 'C5': (70, 76),
    'S1': (46, 60), 'S2': (46, 68), 'S3': (11, 40), 'S4': (11, 48),
    'SW1': (46, 84), 'SW2': (46, 92),
    'Q1': (50, 76),
}
for r, (cx, cy) in POS.items():
    if r not in ('U3', 'U4'):
        COMPS[r]['cx'], COMPS[r]['cy'] = cx, cy

# board init
board = pcbnew.BOARD()
net_objs = {}
for name in NETS:
    n = pcbnew.NETINFO_ITEM(board, name)
    board.Add(n)
    net_objs[name] = n

# place real footprints + assign pad nets
def net_of(ref, num):
    for net, members in NETS.items():
        for (r, p) in members:
            if r == ref and p == num:
                return net
    return None

for ref, c in COMPS.items():
    fp = c['fp']
    off = c.get('off', (0, 0))
    fp.SetPosition(pcbnew.VECTOR2I(mm(c['cx'] - off[0]), mm(c['cy'] - off[1])))
    fp.SetReference(ref)
    vals = {'J1': 'AC Input', 'J2': 'Motor', 'J3': 'Encoder', 'PS1': 'IRM-20-24', 'U1': 'OKI-78SR-5',
            'U2': 'UART Display', 'U3': 'ESP32-DevKitC', 'U4': 'LV8729', 'U5': 'AM26LS32ACN',
            'U6': '74HC4050N', 'Q1': 'BC547'}
    fp.SetValue(vals.get(ref, ref))
    board.Add(fp)
    for pad in fp.Pads():
        nm = net_of(ref, pad.GetNumber())
        if nm:
            pad.SetNet(net_objs[nm])

def build_two_row(ref, value, cx, cy, n, row_dx):
    total = (n - 1) * 2.54
    pads = []
    for i in range(n):
        pads.append((str(i + 1), -row_dx / 2, -total / 2 + i * 2.54, 1.7, 1.7, 'BOTH', 1.0))
    for i in range(n):
        pads.append((str(n + i + 1), row_dx / 2, total / 2 - i * 2.54, 1.7, 1.7, 'BOTH', 1.0))
    fp = make_compound(board, ref, value, pads)
    fp.SetPosition(pcbnew.VECTOR2I(mm(cx), mm(cy)))
    COMPS[ref] = {'fp': fp, 'cx': cx, 'cy': cy, 'geo': pads}
    for pad in fp.Pads():
        nm = net_of(ref, pad.GetNumber())
        if nm:
            pad.SetNet(net_objs[nm])

build_two_row('U3', 'ESP32-DevKitC', *POS['U3'], 19, 25.4)
build_two_row('U4', 'LV8729', *POS['U4'], 8, 15.24)

# board outline from pad extents
# overlap check first
names = list(COMPS.keys())
extents = {}
for ref in names:
    c = COMPS[ref]
    xs0 = [c['cx'] + g[1] - g[3] / 2 for g in c['geo']]
    ys0 = [c['cy'] + g[2] - g[4] / 2 for g in c['geo']]
    xs1 = [c['cx'] + g[1] + g[3] / 2 for g in c['geo']]
    ys1 = [c['cy'] + g[2] + g[4] / 2 for g in c['geo']]
    extents[ref] = (min(xs0), min(ys0), max(xs1), max(ys1))
print('=== footprint bbox overlaps (with 0.25 clearance) ===')
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = extents[names[i]], extents[names[j]]
        if a[0] < b[2] + 0.25 and b[0] < a[2] + 0.25 and a[1] < b[3] + 0.25 and b[1] < a[3] + 0.25:
            print(f'  OVERLAP: {names[i]} {a} <-> {names[j]} {b}')

x0s, y0s, x1s, y1s = [], [], [], []
for ref, c in COMPS.items():
    for (num, x, y, w, h, side, drill) in c['geo']:
        ax, ay = c['cx'] + x, c['cy'] + y
        x0s.append(ax - w / 2 - 2); y0s.append(ay - h / 2 - 2)
        x1s.append(ax + w / 2 + 2); y1s.append(ay + h / 2 + 2)
X0, Y0 = math.floor(min(x0s)), math.floor(min(y0s))
X1, Y1 = math.ceil(max(x1s)), math.ceil(max(y1s))
for (x1, y1, x2, y2) in [(X0, Y0, X1, Y0), (X1, Y0, X1, Y1), (X1, Y1, X0, Y1), (X0, Y1, X0, Y0)]:
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    seg.SetWidth(mm(0.1))
    seg.SetLayer(pcbnew.Edge_Cuts)
    board.Add(seg)
print(f'Board: {X1-X0} x {Y1-Y0} mm')

# ---------------- A* grid router ----------------
# occupancy: occ[layer][class] = dict cell->net_idx ; class = width bucket
CLASSES = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
NX = int((X1 - X0) / CELL) + 1
NY = int((Y1 - Y0) / CELL) + 1
net_idx = {n: i + 1 for i, n in enumerate(NETS)}
idx_net = {i + 1: n for n, i in net_idx.items()}

occ = {0: {c: {} for c in CLASSES}, 1: {c: {} for c in CLASSES}}

def cell_of(x, y):
    return (int(round((x - X0) / CELL)), int(round((y - Y0) / CELL)))

def cell_xy(cx_, cy_):
    return (X0 + cx_ * CELL, Y0 + cy_ * CELL)

def stamp_disc(cx_, cy_, radius, layer, val, skip_net=0):
    r_cells = int(radius / CELL) + 1
    for dx in range(-r_cells, r_cells + 1):
        for dy in range(-r_cells, r_cells + 1):
            if dx * dx + dy * dy <= (radius / CELL) ** 2:
                key = (cx_ + dx, cy_ + dy)
                cur = occ[layer][CLASSES[0]].get(key)  # check primary for skip
                cell_dict = occ[layer][CLASSES[0]]
                if cur and cur != val and skip_net and cur == skip_net:
                    continue
                for c in CLASSES:
                    if radius >= (c - CELL / 2) * 0 + 0:
                        pass
                occ[layer][0].setdefault(key, 0)
                # store in every class grid with same value (radius handled by caller)
                for c in CLASSES:
                    pass
                # actual stamp below
        # placeholder
    return

# simpler: direct stamping helpers (radius per class)
def stamp_pad(px, py, pad_r, side, net_id):
    layers = (0, 1) if side == 'BOTH' else ((0,) if side == 'F' else (1,))
    for cls in CLASSES:
        radius = pad_r + cls / 2 + CLEAR
        r_cells = int(radius / CELL) + 1
        ccx, ccy = cell_of(px, py)
        for layer in layers:
            g = occ[layer][cls]
            for dx in range(-r_cells, r_cells + 1):
                for dy in range(-r_cells, r_cells + 1):
                    if dx * dx + dy * dy <= (radius / CELL) ** 2:
                        key = (ccx + dx, ccy + dy)
                        v = g.get(key, 0)
                        if v == 0:
                            g[key] = net_id
                        elif v != net_id and v != -1:
                            g[key] = -1  # contested between two nets: blocked for all

def stamp_seg(layer, x1, y1, x2, y2, w, net_id):
    for cls in CLASSES:
        radius = w / 2 + cls / 2 + CLEAR
        r_cells = int(radius / CELL) + 1
        g = occ[layer][cls]
        steps = max(1, int(max(abs(x2 - x1), abs(y2 - y1)) / CELL) * 2)
        for s in range(steps + 1):
            t = s / steps
            sx = x1 + (x2 - x1) * t
            sy = y1 + (y2 - y1) * t
            ccx, ccy = cell_of(sx, sy)
            for dx in range(-r_cells, r_cells + 1):
                for dy in range(-r_cells, r_cells + 1):
                    if dx * dx + dy * dy <= (radius / CELL) ** 2:
                        key = (ccx + dx, ccy + dy)
                        if g.get(key, 0) == 0:
                            g[key] = net_id  # never overwrite pad claims

def stamp_via(x, y, net_id):
    for cls in CLASSES:
        radius = VIA_D / 2 + cls / 2 + CLEAR
        r_cells = int(radius / CELL) + 1
        ccx, ccy = cell_of(x, y)
        for layer in (0, 1):
            g = occ[layer][cls]
            for dx in range(-r_cells, r_cells + 1):
                for dy in range(-r_cells, r_cells + 1):
                    if dx * dx + dy * dy <= (radius / CELL) ** 2:
                        key = (ccx + dx, ccy + dy)
                        if g.get(key, 0) == 0:
                            g[key] = net_id  # never overwrite pad claims

# stamp pads
pad_list = []
for ref, c in COMPS.items():
    for (num, x, y, w, h, side, drill) in c['geo']:
        ax, ay = c['cx'] + x, c['cy'] + y
        nm = net_of(ref, num)
        nid = net_idx.get(nm, -1)  # no-net pads: -1 = blocked for everyone
        pad_r = math.hypot(w, h) / 2
        stamp_pad(ax, ay, pad_r, side, nid)
        pad_list.append({'x': ax, 'y': ay, 'r': pad_r, 'side': side, 'net': nm, 'ref': ref, 'num': num, 'nid': nid})

pad_by_rp = {(p['ref'], p['num']): p for p in pad_list if p['net']}

def blocked(cx_, cy_, layer, nid):
    g = occ[layer][CLS_IDX]
    v = g.get((cx_, cy_), 0)
    return v != 0 and v != nid  # v==-1 (contested) blocks everyone

CLS_OF = {c: i for i, c in enumerate(CLASSES)}
CLS_IDX = 0  # set per route

def astar(start, goal, nid, w, debug=False):
    global CLS_IDX
    CLS_IDX = min(CLASSES, key=lambda c: abs(c - w))
    (sx, sy, sl), (gx, gy, gl) = start, goal
    if debug:
        print(f'    A* start={start} goal={goal} nid={nid} w={w} cls={CLS_IDX}')
        print(f'    start blocked: {blocked(sx, sy, sl, nid)} | goal blocked B: {blocked(gx, gy, 1, nid)} F: {blocked(gx, gy, 0, nid)}')
        print('    neighborhood map (rows=sy-4..sy+4, cols=sx-4..sx+4, layer F/B):')
        for layer in (sl, 1 - sl):
            print(f'      layer {layer}:')
            for dy in range(-4, 5):
                row = ''
                for dx in range(-4, 5):
                    v = occ[layer][CLS_IDX].get((sx+dx, sy+dy), 0)
                    if (dx, dy) == (0, 0):
                        row += 'S' if v == 0 else ('s' if v == nid else 'X')
                    else:
                        row += '.' if v == 0 else ('o' if v == nid else 'X')
                print('      ', row)
    open_heap = [(0.0, 0.0, sx, sy, sl)]
    came = {}
    cost = {(sx, sy, sl): 0.0}
    found = False
    expansions = 0
    while open_heap:
        f, c0, x, y, l = heapq.heappop(open_heap)
        expansions += 1
        if debug and expansions <= 12:
            print(f'    pop#{expansions}: ({x},{y},{l}) cost={c0:.1f}')
        # goal: match x,y on ANY layer if goal pad is THT
        if (x, y) == (gx, gy) and (l == gl or gl is None):
            found = True
            break
        if c0 > cost.get((x, y, l), 1e18) + 1e-9:
            continue
        # neighbors: 8 moves same layer + via
        for dx, dy, dc in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.42),(1,-1,1.42),(-1,1,1.42),(-1,-1,1.42)):
            nx_, ny_ = x + dx, y + dy
            if not (0 <= nx_ < NX and 0 <= ny_ < NY):
                continue
            if blocked(nx_, ny_, l, nid):
                continue
            nc = cost[(x, y, l)] + dc
            key = (nx_, ny_, l)
            if nc < cost.get(key, 1e18):
                cost[key] = nc
                came[key] = (x, y, l, 'move')
                heapq.heappush(open_heap, (nc + abs(nx_-gx) + abs(ny_-gy), nc, nx_, ny_, l))
        # via
        ol = 1 - l
        if not blocked(x, y, ol, nid):
            nc = cost[(x, y, l)] + VIA_COST
            key = (x, y, ol)
            if nc < cost.get(key, 1e18):
                cost[key] = nc
                came[key] = (x, y, l, 'via')
                heapq.heappush(open_heap, (nc + abs(x-gx) + abs(y-gy), nc, x, y, ol))
    if not found:
        if debug:
            print(f'    A* FAILED after {expansions} expansions')
        return None
    path = []
    cur = (gx, gy, gl)
    while cur in came:
        path.append(cur)
        px, py, pl, mv = came[cur]
        path[-1] = cur + (mv,)
        cur = (px, py, pl)
    path.append((sx, sy, sl, 'start'))
    path.reverse()
    return path

def emit_path(path, w, net):
    # split by via transitions; merge collinear runs
    segs = []
    run_start = path[0][:3]
    prev_dir = None
    for i in range(1, len(path)):
        px_, py_, pl_, mv = path[i]
        qx, qy, ql = path[i-1][:3]
        if mv == 'via':
            add_via_real(*cell_xy(qx, qy), net)
            segs.append((run_start, (qx, qy), ql))
            run_start = (px_, py_, pl_)
            prev_dir = None
            continue
        d = (1 if px_ > qx else -1 if px_ < qx else 0, 1 if py_ > qy else -1 if py_ < qy else 0)
        if prev_dir is not None and d != prev_dir:
            segs.append((run_start, (qx, qy), ql))
            run_start = (qx, qy, ql)
        prev_dir = d
    segs.append((run_start, path[-1][:3], path[-1][2]))
    layer_bits = {0: pcbnew.F_Cu, 1: pcbnew.B_Cu}
    n = 0
    for (a, b, l) in segs:
        ax, ay = cell_xy(a[0], a[1]) if isinstance(a[0], int) else a
        bx, by = cell_xy(b[0], b[1]) if isinstance(b[0], int) else b
        if math.hypot(bx-ax, by-ay) < 0.01:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(ax), mm(ay)))
        t.SetEnd(pcbnew.VECTOR2I(mm(bx), mm(by)))
        t.SetWidth(mm(w))
        t.SetLayer(layer_bits[l])
        t.SetNet(net_objs[net])
        board.Add(t)
        stamp_seg(l, ax, ay, bx, by, w, net_idx[net])
        n += 1
    return n

def add_via_real(x, y, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(VIA_D))
    v.SetDrill(mm(VIA_DRILL))
    v.SetNet(net_objs[net])
    board.Add(v)
    stamp_via(x, y, net_idx[net])

def snap_layer(p):
    return 0 if p['side'] == 'F' else 1

ORDER = ['MOT_1A', 'MOT_1B', 'MOT_2A', 'MOT_2B',
         'ENC_A_P', 'ENC_A_N', 'ENC_B_P', 'ENC_B_N', 'ENC_Z_P', 'ENC_Z_N',
         'ENC_A_BUF', 'ENC_B_BUF', 'ENC_Z_BUF', 'GPIO21_ENC_A', 'GPIO22_ENC_B', 'ENC_Z_ESP',
         'GPIO18_OPTIC1', 'GPIO19_OPTIC2', 'OPTIC1_RAW', 'OPTIC2_RAW',
         'UART_M_TX', 'UART_M_RX',
         'M_EN', 'M_MS1', 'M_MS2', 'M_MS3', 'M_STEP', 'M_DIR', 'GPIO23_RST',
         'SW1_SIG', 'SW2_SIG', 'HALL1_RAW', 'HALL1_DIV', 'HALL2_RAW', 'HALL2_DIV',
         'FSR1_TOP', 'FSR2_TOP',
         '+24V', '+3V3', '+5V']

failed = []
seg_count = 0
via_count = 0
for net in ORDER:
    members = NETS[net]
    pts = [pad_by_rp[(r, str(p))] for (r, p) in members if (r, str(p)) in pad_by_rp]
    if len(pts) < 2:
        failed.append((net, 'pads<2'))
        continue
    # nearest neighbor chain
    remaining = pts[1:]
    chain = [pts[0]]
    cur = pts[0]
    while remaining:
        nxt = min(remaining, key=lambda q: math.hypot(q['x']-cur['x'], q['y']-cur['y']))
        chain.append(nxt)
        remaining.remove(nxt)
        cur = nxt
    ok_all = True
    for i in range(len(chain) - 1):
        a, b = chain[i], chain[i+1]
        sl = snap_layer(a)
        gl = None if b['side'] == 'BOTH' else snap_layer(b)
        w = width_for(net)
        dbg = False
        path = astar((cell_of(a['x'], a['y'])[0], cell_of(a['x'], a['y'])[1], sl),
                     (cell_of(b['x'], b['y'])[0], cell_of(b['x'], b['y'])[1], gl),
                     net_idx[net], w, debug=dbg)
        if path is None:
            ok_all = False
            failed.append((net, f'leg{i}'))
            continue
        before = seg_count + via_count
        segs = emit_path(path, w, net)
        seg_count += segs
    if ok_all:
        pass

print(f'Routing done. segments: {seg_count} | failed legs: {len(failed)}')
for f in failed[:15]:
    print('  FAIL:', f)

# GND SMD stubs
gnd_smd = [p for p in pad_list if p['net'] == 'GND' and p['side'] != 'BOTH']
stub_ok = 0
for p in gnd_smd:
    done = False
    for dx, dy in [(0, 0), (1.27, 0), (-1.27, 0), (0, 1.27), (0, -1.27)]:
        vx, vy = p['x'] + dx, p['y'] + dy
        ccx, ccy = cell_of(vx, vy)
        if 0 <= ccx < NX and 0 <= ccy < NY and not blocked(ccx, ccy, 0, net_idx['GND']) and not blocked(ccx, ccy, 1, net_idx['GND']):
            if dx or dy:
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(mm(p['x']), mm(p['y'])))
                t.SetEnd(pcbnew.VECTOR2I(mm(vx), mm(vy)))
                t.SetWidth(mm(0.5))
                t.SetLayer(pcbnew.F_Cu)
                t.SetNet(net_objs['GND'])
                board.Add(t)
            add_via_real(vx, vy, 'GND')
            done = True
            break
    if done:
        stub_ok += 1
print(f'GND SMD stubs: {stub_ok}/{len(gnd_smd)}')

# GND zone B.Cu (left UNFILLED here; filled by fill_zones.py in a separate process)
zone = pcbnew.ZONE(board)
zone.SetLayer(pcbnew.B_Cu)
zone.SetNet(net_objs['GND'])
poly = pcbnew.SHAPE_POLY_SET()
poly.NewOutline()
poly.Append(mm(X0 + 1), mm(Y0 + 1))
poly.Append(mm(X1 - 1), mm(Y0 + 1))
poly.Append(mm(X1 - 1), mm(Y1 - 1))
poly.Append(mm(X0 + 1), mm(Y1 - 1))
zone.SetOutline(poly)
zone.SetMinThickness(mm(0.2))
zone.SetLocalClearance(mm(0.3))
zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
board.Add(zone)
print('Zone added (unfilled)')

board.Save(PCB)
print(f'PCB saved: {PCB}')
