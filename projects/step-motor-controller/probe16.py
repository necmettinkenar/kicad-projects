#!/usr/bin/env python3
"""Bisect instances and other body elements."""
import subprocess, os, re

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
SCH = os.path.join(PROJ, 'step-motor-controller.kicad_sch')
KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
txt = open(SCH, encoding='utf-8').read()

start = txt.find('\t(lib_symbols')
i = start
depth = 0
# find end of lib_symbols
k = txt.find('(lib_symbols', start)
k2 = k + len('(lib_symbols')
d = 1
p = k2
while p < len(txt):
    if txt[p] == '(': d += 1
    elif txt[p] == ')':
        d -= 1
        if d == 0:
            lib_end = p + 1
            break
    p += 1
lib_section = txt[start:lib_end]

# collect top-level items after lib_symbols
body_txt = txt[lib_end:]
items = []  # (kind, block_text)
p = 0
while p < len(body_txt):
    while p < len(body_txt) and body_txt[p] in ' \t\n\r':
        p += 1
    if p >= len(body_txt):
        break
    if body_txt[p] == ')':
        # final close of kicad_sch
        items.append(('CLOSE', body_txt[p], p))
        break
    j = p
    depth = 0
    while j < len(body_txt):
        if body_txt[j] == '(': depth += 1
        elif body_txt[j] == ')':
            depth -= 1
            if depth == 0:
                break
        j += 1
    block = body_txt[p:j+1]
    kind = block.strip().split('\n')[0].strip().split(' ')[0].strip('()')
    items.append((kind, block, p))
    p = j + 1

from collections import Counter
kinds = Counter(k for k, b, p in items)
print('body items:', dict(kinds))

header = txt[:start] + lib_section

def test(content, name):
    fn = os.path.join(PROJ, f'bisect_{name}.kicad_sch')
    open(fn, 'w', encoding='utf-8').write(content)
    r = subprocess.run([KICAD, 'sch', 'export', 'netlist', '--format', 'kicadsexpr',
                        '--output', os.path.join(PROJ, 'b.net'), fn],
                       capture_output=True, text=True, timeout=60)
    return r.returncode

# test: lib + instances only (no wires/junctions/labels/nc)
inst_blocks = [(k, b) for k, b, p in items if k == '(symbol']
close = [b for k, b, p in items if k == 'CLOSE']
c = header + ''.join(b for k, b in inst_blocks) + (close[0] if close else ')')
print('lib + all instances:', test(c, 'inst_all'))

# bisect instances
bad = None
for kk in range(1, len(inst_blocks) + 1):
    c = header + ''.join(b for k, b in inst_blocks[:kk]) + (close[0] if close else ')')
    rc = test(c, f'i{kk}')
    if rc != 0:
        bad = kk
        first_line = inst_blocks[kk-1][1].split('\n')
        ref = ''
        for ln in first_line:
            if 'Reference' in ln:
                ref = ln
        print(f'FIRST FAILING INSTANCE #{kk}: {ref[:70]}')
        print(f'  k={kk-1} passes: {test(header + "".join(b for k, b in inst_blocks[:kk-1]) + (close[0] if close else ")"), f"i{kk-1}ok") == 0}')
        break
if bad is None:
    print('all instances OK — problem in wires/junctions/labels/nc')
    # bisect those
    other = [(k, b) for k, b, p in items if k not in ('(symbol', 'CLOSE')]
    for kk in range(1, len(other) + 1):
        c = header + ''.join(b for k, b in inst_blocks) + ''.join(b for k, b in other[:kk]) + (close[0] if close else ')')
        rc = test(c, f'o{kk}')
        if rc != 0:
            kind = other[kk-1][0]
            snippet = other[kk-1][1][:150]
            print(f'FIRST FAILING OTHER #{kk}: {kind}: {snippet!r}')
            break
    else:
        print('ALL body items OK?!')
