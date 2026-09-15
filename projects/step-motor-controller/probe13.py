"""Probe: pin geometry for all symbols used in the schematic (for wire routing)."""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

SYM_DIR = r'C:\Program Files\KiCad\10.0\share\kicad\symbols'

def extract_block(txt, start):
    depth = 0
    for k in range(start, len(txt)):
        if txt[k] == '(': depth += 1
        elif txt[k] == ')':
            depth -= 1
            if depth == 0: return txt[start:k+1]
    raise ValueError('unbalanced')

def extract_lib_symbol(lib, name):
    txt = open(os.path.join(SYM_DIR, lib + '.kicad_sym'), encoding='utf-8').read()
    m = re.search(r'\(symbol "' + re.escape(name) + r'"[\s(]', txt)
    if not m: return None
    blk = extract_block(txt, m.start())
    depth = 0
    while depth < 4:
        em = re.search(r'\(extends "([^"]+)"\)', blk)
        if not em: break
        parent = em.group(1)
        pm = re.search(r'\(symbol "' + re.escape(parent) + r'"[\s(]', txt)
        pblk = extract_block(txt, pm.start())
        pblk = pblk.replace('(symbol "' + parent + '"', '(symbol "' + name + '"', 1)
        pblk = pblk.replace('"' + parent + '_', '"' + name + '_')
        blk = re.sub(r'\n?\s*\(extends "[^"]+"\)', '', pblk)
        depth += 1
    return blk

def pins(blk):
    out = []
    for m in re.finditer(r'\(pin (\w+) (\w+)\s*\n?\s*\(at (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)', blk):
        j = m.start()
        pb = extract_block(blk, j)
        nm = re.search(r'\(name "([^"]*)"', pb)
        nb = re.search(r'\(number "([^"]*)"', pb)
        x, y, a = float(m.group(3)), float(m.group(4)), float(m.group(5))
        outward = (180 - a) % 360
        out.append((nb.group(1), nm.group(1) if nm else '', x, y, a, outward))
    return out

targets = [
    ('Device', 'R'), ('Device', 'C'), ('Device', 'C_Polarized'),
    ('Switch', 'SW_SPDT'), ('Connector_Generic', 'Conn_01x02'),
    ('Connector_Generic', 'Conn_01x03'), ('Connector_Generic', 'Conn_01x04'),
    ('Connector_Generic', 'Conn_01x08'), ('Converter_ACDC', 'IRM-20-24'),
    ('Transistor_BJT', 'BC547'),
]
for lib, name in targets:
    blk = extract_lib_symbol(lib, name)
    print(f'=== {lib}:{name} ===')
    for p in pins(blk):
        print(f'  pin {p[0]:>3} {p[1]:>6} at ({p[2]:7.2f},{p[3]:7.2f}) a={p[4]:.0f} outward={p[5]:.0f}')
