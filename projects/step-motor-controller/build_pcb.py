#!/usr/bin/env python3
"""Generate Step Motor Controller PCB using KiCad 10.0 pcbnew API."""

import sys, os, datetime

try:
    import pcbnew
except ImportError:
    print("ERROR: pcbnew module not found.")
    print('Run with: "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" build_pcb.py')
    sys.exit(1)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PCB_FILE = os.path.join(PROJECT_DIR, "step-motor-controller.kicad_pcb")
NET_FILE = os.path.join(PROJECT_DIR, "step-motor-controller.net")

BOARD_W, BOARD_H = 100.0, 80.0

# =================== HELPERS ===================
def MM(x):
    """Convert mm to internal units (nm)."""
    return int(pcbnew.FromMM(x))

def VI(x, y):
    """Create VECTOR2I from mm coordinates."""
    return pcbnew.VECTOR2I(MM(x), MM(y))

# Constants
F_CU = pcbnew.F_Cu
B_CU = pcbnew.B_Cu
EDGE = pcbnew.Edge_Cuts
SMD_ATTR = pcbnew.PAD_ATTRIB_SMD
PTH_ATTR = pcbnew.PAD_ATTRIB_PTH
PAD_RECT = pcbnew.PAD_SHAPE_RECT
PAD_CIRC = pcbnew.PAD_SHAPE_CIRCLE
DRILL_CIRC = pcbnew.PAD_DRILL_SHAPE_CIRCLE

try:
    SHAPE_SEG = pcbnew.SHAPE_T_SEGMENT
except AttributeError:
    SHAPE_SEG = getattr(pcbnew, 'S_SEGMENT', 0)

# =================== BOARD ===================
board = pcbnew.BOARD()
try:
    board.SetFileName(PCB_FILE)
except:
    pass
try:
    board.GetDesignSettings().SetCopperLayerCount(2)
except:
    pass

# =================== NETS ===================
nets_cache = {}

def get_net(name):
    if name not in nets_cache:
        try:
            net = pcbnew.NETINFO_ITEM(board, name)
        except TypeError:
            net = pcbnew.NETINFO_ITEM(board, name, 0)
        board.Add(net)
        nets_cache[name] = net
    return nets_cache[name]

# Pre-create power nets
for n in ["GND", "+24V", "+5V", "+3V3"]:
    get_net(n)

# Net assignments from the Excel
NET_DEFS = {
    "GND": [("J1","3"),("PS1","3"),("U1","2"),("C1","2"),("C2","2"),
            ("U2","4"),("U3","14"),("U4","9"),("U4","15"),
            ("U5","8"),("U5","12"),("U6","8"),("J3","2"),
            ("SW1","3"),("SW2","3"),("S1","4"),("S2","4"),
            ("S3","3"),("S4","3")],
    "+24V": [("PS1","4"),("U1","1"),("C1","1"),("U4","16")],
    "+5V": [("U1","3"),("C2","1"),("J3","1"),("U2","1"),
            ("U4","10"),("U5","16"),("U5","4"),("U6","1"),
            ("S1","1"),("S2","1"),("S3","1"),("S4","1")],
    "+3V3": [("U3","1"),("R1","1"),("R3","1"),
             ("R5","2"),("R6","2"),("R11","1")]
}

PAD_NET = {}
for nn, conns in NET_DEFS.items():
    for r, p in conns:
        PAD_NET[(r, p)] = nn

def assign_net(pad, ref, num):
    key = (ref, str(num))
    if key in PAD_NET:
        net = get_net(PAD_NET[key])
        try:
            pad.SetNetCode(net.GetNetCode())
        except:
            try:
                pad.SetNet(net)
            except:
                pass

# =================== PAD HELPERS ===================
def add_smd_pad(fp, num, dx, dy, w, h, ref):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetShape(PAD_RECT)
    pad.SetAttribute(SMD_ATTR)
    pad.SetLayer(F_CU)
    pad.SetSize(VI(w, h))
    pad.SetPosition(VI(dx, dy))
    assign_net(pad, ref, num)
    fp.Add(pad)
    return pad

def add_tht_pad(fp, num, dx, dy, pad_size, drill, ref):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetShape(PAD_CIRC)
    pad.SetAttribute(PTH_ATTR)
    pad.SetSize(VI(pad_size, pad_size))
    pad.SetDrillSize(VI(drill, drill))
    pad.SetDrillShape(DRILL_CIRC)
    pad.SetPosition(VI(dx, dy))
    # Set layer set for THT (through all copper layers)
    try:
        lset = pcbnew.LSET()
        lset.Add(F_CU)
        lset.Add(B_CU)
        pad.SetLayerSet(lset)
    except:
        try:
            pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        except:
            pad.SetLayer(F_CU)
    assign_net(pad, ref, num)
    fp.Add(pad)
    return pad

# =================== FOOTPRINT HELPER ===================
comps = []

def create_fp(ref, val, x, y):
    try:
        fp = pcbnew.FOOTPRINT(board)
    except TypeError:
        try:
            fp = pcbnew.FOOTPRINT(None)
        except:
            fp = pcbnew.FOOTPRINT()
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(VI(x, y))
    try:
        fp.SetLayer(F_CU)
    except:
        pass
    board.Add(fp)
    comps.append(fp)
    return fp

# =================== BOARD OUTLINE ===================
print("Drawing board outline (100x80mm)...")
pts = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
for i in range(4):
    try:
        shape = pcbnew.PCB_SHAPE(board)
    except AttributeError:
        shape = pcbnew.DRAWSEGMENT(board)
    try:
        shape.SetShape(SHAPE_SEG)
    except:
        pass
    try:
        shape.SetStart(VI(*pts[i]))
        shape.SetEnd(VI(*pts[(i + 1) % 4]))
    except:
        try:
            shape.SetStartX(MM(pts[i][0]))
            shape.SetStartY(MM(pts[i][1]))
            shape.SetEndX(MM(pts[(i+1)%4][0]))
            shape.SetEndY(MM(pts[(i+1)%4][1]))
        except:
            pass
    shape.SetLayer(EDGE)
    shape.SetWidth(MM(0.15))
    board.Add(shape)

# =================== COMPONENTS ===================

# --- 0805 Resistors & Capacitors (2 SMD pads, 1.0x1.2mm, 2mm spacing) ---
def create_0805(ref, val, x, y):
    fp = create_fp(ref, val, x, y)
    add_smd_pad(fp, 1, -1.0, 0, 1.0, 1.2, ref)
    add_smd_pad(fp, 2,  1.0, 0, 1.0, 1.2, ref)
    return fp

print("Creating 0805 components...")

# R1-R10 at various positions
r_positions = [
    (20, 40), (20, 45), (20, 50), (20, 55),   # R1-R4
    (65, 35), (70, 35),                         # R5-R6
    (65, 55), (70, 55),                         # R7-R8
    (40, 60), (40, 65),                         # R9-R10
]
r_values = ["10K", "10K", "10K", "10K", "1K", "1K", "10K", "10K", "4.7K", "4.7K"]
for i, ((rx, ry), rv) in enumerate(zip(r_positions, r_values), 1):
    create_0805(f"R{i}", rv, rx, ry)

# R11, R12
create_0805("R11", "10K", 35, 45)
create_0805("R12", "1K", 35, 50)

# C3, C4, C5 (0805 caps)
create_0805("C3", "100nF", 10, 50)
create_0805("C4", "100nF", 15, 50)
create_0805("C5", "100nF", 35, 55)

# --- Electrolytic Capacitors (THT, 2 pads, 1.0mm drill, 1.7mm pad) ---
def create_elcap(ref, val, x, y):
    fp = create_fp(ref, val, x, y)
    add_tht_pad(fp, 1, -1.27, 0, 1.7, 1.0, ref)
    add_tht_pad(fp, 2,  1.27, 0, 1.7, 1.0, ref)
    return fp

print("Creating electrolytic capacitors...")
create_elcap("C1", "100uF", 25, 30)
create_elcap("C2", "10uF", 45, 30)

# --- Connectors (THT, 2.54mm pitch, 1.0mm drill, 1.7mm pad) ---
def create_connector(ref, val, x, y, num_pins):
    fp = create_fp(ref, val, x, y)
    start = -(num_pins - 1) * 2.54 / 2
    for i in range(num_pins):
        add_tht_pad(fp, i + 1, start + i * 2.54, 0, 1.7, 1.0, ref)
    return fp

print("Creating connectors...")
# J1: 3-pin terminal block at (10, 15)
create_connector("J1", "Terminal_3P", 10, 15, 3)
# J2: 4-pin motor connector at (90, 45)
create_connector("J2", "Motor_4P", 90, 45, 4)
# J3: 8-pin encoder connector at (90, 20)
create_connector("J3", "Encoder_8P", 90, 20, 8)
# U2: 4-pin UART display connector at (25, 65)
create_connector("U2", "UART_4P", 25, 65, 4)

# --- PS1: IRM-20-24 AC/DC module (4 pads THT, 2.54mm pitch, 1.2mm drill) ---
print("Creating PS1 (IRM-20-24)...")
fp = create_fp("PS1", "IRM-20-24", 25, 15)
for i in range(4):
    add_tht_pad(fp, i + 1, -3.81 + i * 2.54, 0, 2.0, 1.2, "PS1")

# --- U1: OKI-78SR-5 TO-220-3 (3 pads THT, 2.54mm pitch) ---
print("Creating U1 (TO-220-3)...")
def create_to220(ref, val, x, y):
    fp = create_fp(ref, val, x, y)
    add_tht_pad(fp, 1, -2.54, 0, 1.7, 1.0, ref)
    add_tht_pad(fp, 2,  0.0,  0, 1.7, 1.0, ref)
    add_tht_pad(fp, 3,  2.54, 0, 1.7, 1.0, ref)
    return fp

create_to220("U1", "OKI-78SR-5", 45, 15)

# --- Q1: BC547 TO-92 (3 pads THT, 0.5mm drill) ---
print("Creating Q1 (TO-92)...")
fp = create_fp("Q1", "BC547", 30, 45)
add_tht_pad(fp, 1, -1.27, 0, 1.5, 0.5, "Q1")
add_tht_pad(fp, 2,  0.0,  0, 1.5, 0.5, "Q1")
add_tht_pad(fp, 3,  1.27, 0, 1.5, 0.5, "Q1")

# --- U3: ESP32-DevKitC (38 pins THT, 2.54mm pitch, 2 rows 24mm apart) ---
print("Creating U3 (ESP32-DevKitC, 38 pins)...")
fp = create_fp("U3", "ESP32-DevKitC", 50, 45)
# Left row: pins 1-19, x = -12mm, y from -22.86 to +22.86
for i in range(19):
    y = -22.86 + i * 2.54
    add_tht_pad(fp, i + 1, -12, y, 1.7, 1.0, "U3")
# Right row: pins 20-38, x = +12mm, y from +22.86 to -22.86
for i in range(19):
    y = 22.86 - i * 2.54
    add_tht_pad(fp, i + 20, 12, y, 1.7, 1.0, "U3")

# --- U4: LV8729 SOIC-16 (16 SMD pads, 0.6x1.55mm, 1.27mm pitch) ---
print("Creating U4 (SOIC-16)...")
def create_soic16(ref, val, x, y):
    fp = create_fp(ref, val, x, y)
    # Left side: pins 1-8
    for i in range(8):
        y_pos = -4.445 + i * 1.27
        add_smd_pad(fp, i + 1, -2.7, y_pos, 0.6, 1.55, ref)
    # Right side: pins 9-16
    for i in range(8):
        y_pos = 4.445 - i * 1.27
        add_smd_pad(fp, i + 9, 2.7, y_pos, 0.6, 1.55, ref)
    return fp

create_soic16("U4", "LV8729", 75, 45)

# --- U5, U6: DIP-16 (16 THT pads, 0.8mm drill, 2.54mm pitch, 7.62mm width) ---
print("Creating DIP-16 ICs...")
def create_dip16(ref, val, x, y):
    fp = create_fp(ref, val, x, y)
    # Left side: pins 1-8
    for i in range(8):
        y_pos = -8.89 + i * 2.54
        add_tht_pad(fp, i + 1, -3.81, y_pos, 1.7, 0.8, ref)
    # Right side: pins 9-16
    for i in range(8):
        y_pos = 8.89 - i * 2.54
        add_tht_pad(fp, i + 9, 3.81, y_pos, 1.7, 0.8, ref)
    return fp

create_dip16("U5", "AM26LS32ACN", 75, 20)
create_dip16("U6", "74HC4050", 50, 65)

# --- SW1, SW2: Limit switches (3 pads THT, 2.54mm pitch) ---
print("Creating switches and sensors...")
create_connector("SW1", "Limit_SW", 5, 55, 3)
create_connector("SW2", "Limit_SW", 5, 65, 3)

# --- S1, S2: Optical sensors (4 pads THT, 2.54mm pitch) ---
create_connector("S1", "Optical", 5, 45, 4)
create_connector("S2", "Optical", 5, 50, 4)

# --- S3, S4: Hall sensors (3 pads THT, 2.54mm pitch) ---
create_connector("S3", "Hall", 5, 70, 3)
create_connector("S4", "Hall", 5, 75, 3)

# =================== SUMMARY ===================
print(f"\n=== PCB Generation Summary ===")
print(f"Components placed: {len(comps)}")
print(f"Nets created: {len(nets_cache)}")
print(f"Board size: {BOARD_W} x {BOARD_H} mm")

# Count total pads
total_pads = 0
for fp in comps:
    try:
        total_pads += fp.Pads().GetCount()
    except:
        try:
            total_pads += len(list(fp.Pads()))
        except:
            pass
print(f"Total pads: {total_pads}")

# =================== SAVE PCB ===================
print(f"\nSaving PCB to: {PCB_FILE}")
try:
    board.Save(PCB_FILE)
    print("PCB saved successfully (board.Save).")
except Exception as e:
    print(f"board.Save() failed: {e}")
    try:
        pcbnew.SaveBoard(PCB_FILE, board)
        print("PCB saved successfully (SaveBoard).")
    except Exception as e2:
        print(f"SaveBoard also failed: {e2}")
        sys.exit(1)

# =================== NETLIST FILE ===================
print(f"\nGenerating netlist file...")

# Build component list
all_comps = [
    ("J1", "Terminal_3P"), ("PS1", "IRM-20-24"), ("U1", "OKI-78SR-5"),
    ("C1", "100uF"), ("C2", "10uF"), ("U3", "ESP32-DevKitC"),
    ("U4", "LV8729"), ("J2", "Motor_4P"), ("U5", "AM26LS32ACN"),
    ("J3", "Encoder_8P"), ("U6", "74HC4050"), ("Q1", "BC547"),
    ("R11", "10K"), ("R12", "1K"), ("C5", "100nF"),
    ("SW1", "Limit_SW"), ("SW2", "Limit_SW"),
    ("S1", "Optical"), ("S2", "Optical"),
    ("S3", "Hall"), ("S4", "Hall"),
    ("C3", "100nF"), ("C4", "100nF"), ("U2", "UART_4P"),
]
for i in range(1, 11):
    all_comps.append((f"R{i}", r_values[i - 1]))

# Generate KiCad netlist (s-expression format)
nl = '(export (version "E")\n'
nl += '  (design\n'
nl += f'    (source "step-motor-controller")\n'
nl += f'    (date "{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")\n'
nl += '    (tool "KiCad PCB Generator (Python pcbnew API)")\n'
nl += '  )\n'
nl += '  (components\n'
for ref, val in sorted(all_comps, key=lambda c: (c[0][0], int(''.join(filter(str.isdigit, c[0])) or 0))):
    nl += f'    (comp (ref "{ref}") (value "{val}"))\n'
nl += '  )\n'
nl += '  (nets\n'
for idx, (net_name, conns) in enumerate(NET_DEFS.items(), 1):
    nl += f'    (net (code "{idx}") (name "{net_name}")\n'
    for ref, pad in conns:
        nl += f'      (node (ref "{ref}") (pin "{pad}"))\n'
    nl += '    )\n'
nl += '  )\n'
nl += ')\n'

with open(NET_FILE, 'w', encoding='utf-8') as f:
    f.write(nl)
print(f"Netlist saved: {NET_FILE}")

print(f"\n=== Done! PCB file: {PCB_FILE} ===")
print(f"=== Total components: {len(comps)} | Total nets: {len(nets_cache)} ===")
