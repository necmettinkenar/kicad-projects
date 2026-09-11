#!/usr/bin/env python3
"""Generate Step Motor Controller .kicad_sch (KiCad 10, version 20250610).
Connectivity: one global label per pin endpoint. Netlist = Excel table."""
import re, os, json, uuid, sys

SYM_DIR = r'C:\Program Files\KiCad\10.0\share\kicad\symbols'
PROJ = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.join(PROJ, 'step-motor-controller.kicad_sch')
ROOT = 'a1b2c3d4-0000-4000-8000-000000000001'

def uid():
    return str(uuid.UUID(int=__import__('random').getrandbits(128), version=4))

# ---------- s-expression helpers ----------
def extract_block(txt, start):
    """Return balanced-paren block starting at index of '('."""
    depth = 0
    for i in range(start, len(txt)):
        if txt[i] == '(':
            depth += 1
        elif txt[i] == ')':
            depth -= 1
            if depth == 0:
                return txt[start:i+1]
    raise ValueError('unbalanced')

def extract_lib_symbol(lib, name):
    txt = open(os.path.join(SYM_DIR, lib + '.kicad_sym'), encoding='utf-8').read()
    m = re.search(r'\(symbol "' + re.escape(name) + r'"[\s(]', txt)
    if not m:
        return None
    blk = extract_block(txt, m.start())
    # resolve (extends "Parent") chains: inherit pins/graphics from parent
    depth = 0
    while depth < 4:
        em = re.search(r'\(extends "([^"]+)"\)', blk)
        if not em:
            break
        parent = em.group(1)
        pm = re.search(r'\(symbol "' + re.escape(parent) + r'"[\s(]', txt)
        if not pm:
            raise ValueError(f'extends parent {parent} not found for {lib}:{name}')
        pblk = extract_block(txt, pm.start())
        # rename parent top-level name to derived name, and child unit names
        pblk = pblk.replace('(symbol "' + parent + '"', '(symbol "' + name + '"', 1)
        pblk = pblk.replace('"' + parent + '_', '"' + name + '_')
        # drop the (extends ...) line from result, keep parent graphics/pins
        blk = re.sub(r'\n?\s*\(extends "[^"]+"\)', '', pblk)
        depth += 1
    # rename top-level:  (symbol "Name"  ->  (symbol "Lib:Name"
    blk = blk.replace('(symbol "' + name + '"', '(symbol "' + lib + ':' + name + '"', 1)
    # PS1: force -Vo/+Vo pins to power_out so GND/+24V count as driven for ERC
    if name == 'IRM-20-24':
        out = []
        i = 0
        while i < len(blk):
            m2 = re.compile(r'\(pin (\w+)').search(blk, i)
            if not m2:
                out.append(blk[i:]); break
            j = m2.start()
            out.append(blk[i:j])
            pinblk = extract_block(blk, j)
            nm2 = re.search(r'\(name "([^"]*)"', pinblk)
            pn = nm2.group(1) if nm2 else ''
            if pn in ('-Vo', '+Vo'):
                pinblk = pinblk.replace('(pin ' + m2.group(1), '(pin power_out', 1)
            out.append(pinblk)
            i = j + len(pinblk)
        blk = ''.join(out)
    return blk

def parse_pins(blk):
    """Extract pins from a symbol block: number -> (x, y, angle, name, etype)."""
    pins = {}
    for m in re.finditer(r'\(pin (\w+) (\w+)\s*\n?\s*\(at (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)', blk):
        etype, shape, x, y, a = m.group(1), m.group(2), float(m.group(3)), float(m.group(4)), float(m.group(5))
        block = extract_block(blk, m.start())
        nm = re.search(r'\(name "([^"]*)"', block)
        nb = re.search(r'\(number "([^"]*)"', block)
        if nb:
            pins[nb.group(1)] = (x, y, a, nm.group(1) if nm else '', etype)
    return pins

# ---------- custom symbol builder ----------
def box_symbol(libname, name, ref_prefix, pins, w=10.16, value=''):
    """pins: list of (number, name, side 'L'/'R', index_in_col, col_count, etype)."""
    half_h = (max(p[4] for p in pins)) * 2.54 / 2 + 1.27
    pitch_span = (max(p[4] for p in pins) - 1) * 2.54
    y0 = pitch_span / 2
    lines = []
    A = lines.append
    A(f'(symbol "{libname}:{name}" (in_bom yes) (on_board yes)')
    A(f'(property "Reference" "{ref_prefix}" (at 0 {half_h+2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    A(f'(property "Value" "{value or name}" (at 0 {-half_h-2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    A('(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    A('(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    A('(property "Description" "Auto-generated from Excel connection table" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    A(f'(symbol "{name}_0_1" (rectangle (start {-w:.2f} {half_h:.2f}) (end {w:.2f} {-half_h:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))')
    A(f'(symbol "{name}_1_1"')
    for num, pname, side, idx, cnt, etype in pins:
        y = y0 - (idx - 1) * 2.54
        x = -w - 5.08 if side == 'L' else w + 5.08
        ang = 0 if side == 'L' else 180
        A(f'(pin {etype} line (at {x:.2f} {y:.2f} {ang}) (length 5.08)')
        A(f'(name "{pname}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')
    A(')')
    A(')')
    return '\n'.join(lines)

def col_pins(defs, n_per_col):
    """defs: ordered list of (number, name, etype) laid out DIP-style:
    left col 1..n top->bottom, right col n+1..2n bottom->top."""
    out = []
    for i, (num, nm, et) in enumerate(defs[:n_per_col]):
        out.append((num, nm, 'L', i + 1, n_per_col, et))
    right = defs[n_per_col:]
    for i, (num, nm, et) in enumerate(reversed(right)):
        out.append((num, nm, 'R', i + 1, n_per_col, et))
    return out

# custom symbols
U3_NAMES = {1:'3V3',2:'EN',3:'GPIO36',4:'GPIO39',5:'GPIO34',6:'GPIO35',7:'GPIO32',8:'GPIO33',
    9:'GPIO25',10:'GPIO26',11:'GPIO27',12:'GPIO14',13:'GPIO12',14:'GND',15:'GPIO13',16:'NC',
    17:'NC',18:'NC',19:'5V',20:'NC',21:'NC',22:'NC',23:'NC',24:'NC',25:'NC',26:'GPIO4',
    27:'GPIO16',28:'GPIO17',29:'GPIO5',30:'GPIO18',31:'GPIO19',32:'GPIO21',33:'GPIO22',
    34:'NC',35:'NC',36:'NC',37:'GPIO23',38:'NC'}
U3_MAP = {1:'+3V3',2:'CHIP_PU',3:'SW1_SIG',4:'SW2_SIG',5:'HALL1_DIV',6:'HALL2_DIV',7:'FSR1_TOP',
    8:'FSR2_TOP',9:'M_MS3',10:'M_STEP',11:'M_DIR',12:'M_EN',14:'GND',15:'ENC_Z_ESP',19:'+5V',
    26:'M_MS1',27:'UART_M_TX',28:'UART_M_RX',29:'M_MS2',30:'GPIO18_OPTIC1',31:'GPIO19_OPTIC2',
    32:'GPIO21_ENC_A',33:'GPIO22_ENC_B',37:'GPIO23_RST'}
u3_pins = []
for n in range(1, 39):
    et = 'free' if U3_NAMES[n] == 'NC' else ('power_out' if n == 1 else ('power_in' if n in (14, 19) else ('input' if n == 2 else 'bidirectional')))
    u3_pins.append((str(n), U3_NAMES[n], et))

U4_MAP = {1:'M_EN',2:'M_MS1',3:'M_MS2',4:'M_MS3',7:'M_STEP',8:'M_DIR',9:'GND',10:'+5V',
    11:'MOT_2B',12:'MOT_2A',13:'MOT_1B',14:'MOT_1A',15:'GND',16:'+24V'}
U4_NAMES = {1:'EN',2:'MS1',3:'MS2',4:'MS3',5:'RST',6:'RST2',7:'STEP',8:'DIR',9:'GND',10:'VDD',
    11:'2B',12:'2A',13:'1B',14:'1A',15:'GND',16:'VM'}
u4_pins = [(str(n), U4_NAMES[n], 'free' if n in (5, 6) else ('power_in' if n in (9, 15, 16, 10) else 'passive')) for n in range(1, 17)]

U5_NAMES = {1:'1B',2:'1A',3:'1Y',4:'G',5:'2Y',6:'2A',7:'2B',8:'GND',9:'3B',10:'3A',11:'3Y',
    12:'/G',13:'4Y',14:'4A',15:'4B',16:'VCC'}
U5_MAP = {1:'ENC_A_N',2:'ENC_A_P',3:'ENC_A_BUF',4:'+5V',5:'ENC_B_BUF',6:'ENC_B_N',7:'ENC_B_P',
    8:'GND',9:'ENC_Z_P',10:'ENC_Z_N',11:'ENC_Z_BUF',12:'GND',16:'+5V'}
u5_pins = [(str(n), U5_NAMES[n], 'free' if n in (13, 14, 15) else ('power_in' if n in (8, 16) else 'passive')) for n in range(1, 17)]

U6_NAMES = {1:'VCC',2:'1Y',3:'1A',4:'2Y',5:'2A',6:'3Y',7:'3A',8:'GND',9:'4A',10:'4Y',11:'5A',
    12:'5Y',13:'6A',14:'6Y',15:'NC',16:'NC'}
U6_MAP = {1:'+5V',2:'GPIO21_ENC_A',3:'ENC_A_BUF',4:'GPIO22_ENC_B',5:'ENC_B_BUF',6:'ENC_Z_ESP',
    7:'ENC_Z_BUF',8:'GND',9:'OPTIC1_RAW',10:'GPIO18_OPTIC1',11:'OPTIC2_RAW',12:'GPIO19_OPTIC2'}
u6_pins = [(str(n), U6_NAMES[n], 'free' if n in (15, 16) else ('power_in' if n in (1, 8) else 'passive')) for n in range(1, 17)]

U1_MAP = {1:'+24V', 2:'GND', 3:'+5V'}
u1_pins = [('1', 'VI', 'power_in'), ('2', 'GND', 'power_in'), ('3', 'VO', 'power_out')]

# ---------- component / net tables ----------
# (ref, libname, symbol_name, value, footprint, pin->net map or None for special)
COMPS = [
    ('J1',  'Connector_Generic', 'Conn_01x03', 'AC Input 3Pin', 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal',
        {1:'AC_L', 2:'AC_N', 3:'GND'}),
    ('J2',  'Connector_Generic', 'Conn_01x04', 'Step Motor', 'Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical',
        {1:'MOT_1A', 2:'MOT_1B', 3:'MOT_2A', 4:'MOT_2B'}),
    ('J3',  'Connector_Generic', 'Conn_01x08', 'Encoder', 'Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical',
        {1:'+5V', 2:'GND', 3:'ENC_A_P', 4:'ENC_A_N', 5:'ENC_B_P', 6:'ENC_B_N', 7:'ENC_Z_P', 8:'ENC_Z_N'}),
    ('PS1', 'Converter_ACDC', 'IRM-20-24', 'IRM-20-24', 'Converter_ACDC:Converter_ACDC_MeanWell_IRM-20-xx_THT', 'BY_NAME'),
    ('U1',  'KicadAuto', 'OKI-78SR', 'OKI-78SR-5/1.5-W36-C', 'Converter_DCDC:Converter_DCDC_Murata_OKI-78SR_Vertical', U1_MAP),
    ('U2',  'Connector_Generic', 'Conn_01x04', 'UART Display', 'Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical',
        {1:'+5V', 2:'UART_M_TX', 3:'UART_M_RX', 4:'GND'}),
    ('U3',  'KicadAuto', 'ESP32-DevKitC', 'ESP32-DevKitC', 'AUTO:ESP32_SOCKET', U3_MAP),
    ('U4',  'KicadAuto', 'LV8729', 'LV8729 Module', 'AUTO:STEPSTICK_2x8', U4_MAP),
    ('U5',  'KicadAuto', 'AM26LS32ACN', 'AM26LS32ACN', 'Package_DIP:DIP-16_W7.62mm', U5_MAP),
    ('U6',  'KicadAuto', '74HC4050', '74HC4050N_652', 'Package_DIP:DIP-16_W7.62mm', U6_MAP),
    ('Q1',  'Transistor_BJT', 'BC547', 'BC547', 'Package_TO_SOT_THT:TO-92_Inline', 'BY_BJT'),
    ('R1',  'Connector_Generic', 'Conn_01x02', 'FSR (external)', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', {1:'+3V3', 2:'FSR1_TOP'}),
    ('R2',  'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'FSR1_TOP', 2:'GND'}),
    ('R3',  'Connector_Generic', 'Conn_01x02', 'FSR (external)', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', {1:'+3V3', 2:'FSR2_TOP'}),
    ('R4',  'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'FSR2_TOP', 2:'GND'}),
    ('R5',  'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'SW1_SIG', 2:'+3V3'}),
    ('R6',  'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'SW2_SIG', 2:'+3V3'}),
    ('R7',  'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'HALL1_RAW', 2:'HALL1_DIV'}),
    ('R8',  'Device', 'R', '20K', 'Resistor_SMD:R_0805_2012Metric', {1:'GND', 2:'HALL1_DIV'}),
    ('R9',  'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'HALL2_RAW', 2:'HALL2_DIV'}),
    ('R10', 'Device', 'R', '20K', 'Resistor_SMD:R_0805_2012Metric', {1:'GND', 2:'HALL2_DIV'}),
    ('R11', 'Device', 'R', '10K', 'Resistor_SMD:R_0805_2012Metric', {1:'+3V3', 2:'CHIP_PU'}),
    ('R12', 'Device', 'R', '1K', 'Resistor_SMD:R_0805_2012Metric', {1:'GPIO23_RST', 2:'Q1_BASE'}),
    ('C1',  'Device', 'C_Polarized', '100uF/35V', 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm', {1:'+24V', 2:'GND'}),
    ('C2',  'Device', 'C_Polarized', '10uF/16V', 'Capacitor_THT:CP_Radial_D5.0mm_P2.50mm', {1:'+5V', 2:'GND'}),
    ('C3',  'Device', 'C', '100nF', 'Capacitor_SMD:C_0805_2012Metric', {1:'SW1_SIG', 2:'GND'}),
    ('C4',  'Device', 'C', '100nF', 'Capacitor_SMD:C_0805_2012Metric', {1:'SW2_SIG', 2:'GND'}),
    ('C5',  'Device', 'C', '100nF', 'Capacitor_SMD:C_0805_2012Metric', {1:'CHIP_PU', 2:'GND'}),
    ('S1',  'Connector_Generic', 'Conn_01x03', 'Optic LS-1', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', {1:'+5V', 2:'OPTIC1_RAW', 3:'GND'}),
    ('S2',  'Connector_Generic', 'Conn_01x03', 'Optic LS-2', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', {1:'+5V', 2:'OPTIC2_RAW', 3:'GND'}),
    ('S3',  'Connector_Generic', 'Conn_01x03', 'Hall-1', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', {1:'+5V', 2:'GND', 3:'HALL1_RAW'}),
    ('S4',  'Connector_Generic', 'Conn_01x03', 'Hall-2', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', {1:'+5V', 2:'GND', 3:'HALL2_RAW'}),
    ('SW1', 'Switch', 'SW_SPDT', 'Limit SW-1', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', {1:'SW1_SIG', 2:'GND'}),
    ('SW2', 'Switch', 'SW_SPDT', 'Limit SW-2', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical', {1:'SW2_SIG', 2:'GND'}),
]

# schematic positions (centers)
POS = {
    'J1': (35, 45), 'PS1': (75, 45), 'U1': (115, 45), 'C1': (75, 72), 'C2': (115, 72),
    'U3': (235, 85), 'U4': (315, 85), 'J2': (355, 70), 'J3': (355, 130),
    'U5': (75, 115), 'U6': (135, 115),
    'Q1': (170, 52), 'R11': (170, 70), 'R12': (196, 70), 'C5': (170, 88),
    'SW1': (35, 165), 'SW2': (35, 187), 'R5': (66, 160), 'R6': (66, 182), 'C3': (92, 165), 'C4': (92, 187),
    'S1': (35, 210), 'S2': (35, 232), 'S3': (90, 215), 'S4': (90, 240),
    'R7': (122, 210), 'R8': (122, 228), 'R9': (148, 210), 'R10': (148, 228),
    'R1': (195, 160), 'R2': (222, 160), 'R3': (195, 182), 'R4': (222, 182),
    'U2': (250, 195),
}
PWR_FLAGS = {'+24V': (35, 25), '+5V': (75, 25), '+3V3': (115, 25), 'GND': (155, 25)}

# ---------- build symbol table ----------
lib_syms = {}
pin_maps = {}   # ref -> {pinnum: (x,y,ang)}
for lib, name in [('Device', 'R'), ('Device', 'C'), ('Device', 'C_Polarized'),
                  ('Switch', 'SW_SPDT'), ('Connector_Generic', 'Conn_01x02'),
                  ('Connector_Generic', 'Conn_01x03'), ('Connector_Generic', 'Conn_01x04'),
                  ('Connector_Generic', 'Conn_01x08'), ('Converter_ACDC', 'IRM-20-24'),
                  ('Transistor_BJT', 'BC547')]:
    blk = extract_lib_symbol(lib, name)
    if blk is None:
        print(f'FATAL: symbol {lib}:{name} not found'); sys.exit(1)
    lib_syms[f'{lib}:{name}'] = blk

# custom symbols
custom = {
    'KicadAuto:ESP32-DevKitC': box_symbol('KicadAuto', 'ESP32-DevKitC', 'U', col_pins(u3_pins, 19), w=12.7),
    'KicadAuto:LV8729': box_symbol('KicadAuto', 'LV8729', 'U', col_pins(u4_pins, 8), w=7.62),
    'KicadAuto:AM26LS32ACN': box_symbol('KicadAuto', 'AM26LS32ACN', 'U', col_pins(u5_pins, 8), w=7.62),
    'KicadAuto:74HC4050': box_symbol('KicadAuto', '74HC4050', 'U', col_pins(u6_pins, 8), w=7.62),
    'KicadAuto:OKI-78SR': box_symbol('KicadAuto', 'OKI-78SR', 'U',
        [('1', 'VI', 'L', 2, 3, 'power_in'), ('2', 'GND', 'L', 1, 3, 'power_in'), ('3', 'VO', 'L', 3, 3, 'power_out')], w=7.62),
}
lib_syms.update(custom)

# pin position maps
lib_pins = {}
for key, blk in lib_syms.items():
    lib_pins[key] = parse_pins(blk)

# report library symbol pin maps used for special components
print('PS1 (IRM-20-24) pins:', {k: v[3] for k, v in sorted(lib_pins['Converter_ACDC:IRM-20-24'].items())})
print('Q1 (BC547) pins:', {k: v[3] for k, v in sorted(lib_pins['Transistor_BJT:BC547'].items())})
print('SW_SPDT pins:', {k: v[3] for k, v in sorted(lib_pins['Switch:SW_SPDT'].items())})
print('Device:C_Polarized pins:', {k: v[3] for k, v in sorted(lib_pins['Device:C_Polarized'].items())})

# PS1 name-based mapping
ps1_pins = lib_pins['Converter_ACDC:IRM-20-24']
ps1_map = {}
for num, (x, y, a, nm, et) in ps1_pins.items():
    nlu = nm.upper().replace(' ', '')
    if 'L' in nlu and 'AC' in nlu: ps1_map[num] = 'AC_L'
    elif 'N' in nlu and 'AC' in nlu: ps1_map[num] = 'AC_N'
    elif '+' in nm or 'V+' in nlu: ps1_map[num] = '+24V'
    elif 'GND' in nlu or 'V-' in nlu or '−' in nm or '-' in nm: ps1_map[num] = 'GND'
print('PS1 mapping:', ps1_map)
assert len(ps1_map) == 4, f'PS1 mapping incomplete: {ps1_map}'

# Q1 name-based mapping (C/B/E)
q1_pins = lib_pins['Transistor_BJT:BC547']
q1_map = {}
for num, (x, y, a, nm, et) in q1_pins.items():
    if nm == 'C': q1_map[num] = 'CHIP_PU'
    elif nm == 'B': q1_map[num] = 'Q1_BASE'
    elif nm == 'E': q1_map[num] = 'GND'
print('Q1 mapping:', q1_map)
assert len(q1_map) == 3

def get_pin_map(ref, lib_id):
    for c in COMPS:
        if c[0] == ref:
            return c[5]
    return None

# ---------- emit schematic ----------
L = []
A = L.append
A('(kicad_sch')
A('\t(version 20250610)')
A('\t(generator "kicad-autogen")')
A('\t(generator_version "9.99")')
A(f'\t(uuid "{ROOT}")')
A('\t(paper "A3")')
A('\t(title_block')
A('\t\t(title "Step Motor Controller")')
A('\t\t(date "2026-09-11")')
A('\t\t(rev "2.0")')
A('\t\t(comment 1 "Auto-generated from Sema_Baglanti_Tablosu.xlsx - all 6 sheets")')
A('\t)')
A('\t(lib_symbols')
for key, blk in lib_syms.items():
    for line in blk.split('\n'):
        A('\t\t' + line if line.strip() else line)
A('\t)')

symbol_ems = []
label_ems = []
nc_ems = []
nets_json = {}

for ref, lib, name, value, fp, pinmap in COMPS:
    X, Y = POS[ref]
    lib_id = f'{lib}:{name}'
    pins = lib_pins[lib_id]
    u = uid()
    A('\t(symbol')
    A(f'\t\t(lib_id "{lib_id}")')
    A(f'\t\t(at {X} {Y} 0)')
    A('\t\t(unit 1)')
    A('\t\t(exclude_from_sim no)')
    A('\t\t(in_bom yes)')
    A('\t\t(on_board yes)')
    A('\t\t(dnp no)')
    A(f'\t\t(uuid "{u}")')
    A(f'\t\t(property "Reference" "{ref}" (at {X} {Y-3} 0) (effects (font (size 1.27 1.27))))')
    A(f'\t\t(property "Value" "{value}" (at {X} {Y+3} 0) (effects (font (size 1.27 1.27))))')
    A(f'\t\t(property "Footprint" "{fp}" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) hide))')
    A(f'\t\t(property "Datasheet" "" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) hide))')
    A(f'\t\t(property "Description" "{value}" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) hide))')
    pmap = ps1_map if pinmap == 'BY_NAME' else (q1_map if pinmap == 'BY_BJT' else pinmap)
    net_members = {}
    for num in sorted(pins, key=lambda s: int(s) if s.isdigit() else 999):
        A(f'\t\t(pin "{num}"')
        A(f'\t\t\t(uuid "{uid()}")')
        A('\t\t)')
        px, py, a, pname, et = pins[num]
        ex, ey = X + px, Y - py
        outward = (180 - a) % 360
        net = pmap.get(int(num)) if isinstance(pmap, dict) and all(isinstance(k, int) for k in pmap) else pmap.get(num)
        if net is None and isinstance(pmap, dict):
            net = pmap.get(str(num))
        if net:
            label_ems.append((net, ex, ey, outward))
            net_members.setdefault(net, []).append([ref, num])
        else:
            # unconnected pin: emit no_connect marker (ERC pin_not_connected fix)
            nc_ems.append((ex, ey))
    A('\t\t(instances')
    A('\t\t\t(project "step-motor-controller"')
    A(f'\t\t\t\t(path "/{ROOT}"')
    A(f'\t\t\t\t\t(reference "{ref}")')
    A('\t\t\t\t\t(unit 1)')
    A('\t\t\t\t)')
    A('\t\t\t)')
    A('\t\t)')
    A('\t)')
    for net, members in net_members.items():
        nets_json.setdefault(net, []).extend(members)

# NOTE: PWR_FLAG symbols omitted - power nets are driven by PS1's +Vo/-Vo outputs
# (power_out), U1's VO (power_out) and U3.1 3V3 (power_out), satisfying ERC.

# (FLG refs are assigned directly per-flag at emit time; no rename pass needed)

# no_connect markers on unlabeled pins
for (ex, ey) in nc_ems:
    A('\t(no_connect')
    A(f'\t\t(at {ex:.4f} {ey:.4f})')
    A(f'\t\t(uuid "{uid()}")')
    A('\t)')

# global labels
for net, ex, ey, ang in label_ems:
    A('\t(global_label')
    A(f'\t\t"{net}"')
    A('\t\t(shape input)')
    A(f'\t\t(at {ex:.4f} {ey:.4f} {ang})')
    A('\t\t(effects (font (size 1.27 1.27)))')
    A(f'\t\t(uuid "{uid()}")')
    A('\t)')

A('\t(sheet_instances')
A('\t\t(path "/" (page "1"))')
A('\t)')
A(')')

content = '\n'.join(L)
with open(SCH, 'w', encoding='utf-8') as f:
    f.write(content)

with open(os.path.join(PROJ, 'nets.json'), 'w', encoding='utf-8') as f:
    json.dump(nets_json, f, indent=1)

print(f'Schematic written: {SCH} ({len(content)} bytes)')
print(f'Components: {len(COMPS)} | labels: {len(label_ems)} | nets: {len(nets_json)}')
for net in sorted(nets_json):
    print(f'  {net}: {len(nets_json[net])} pins')
