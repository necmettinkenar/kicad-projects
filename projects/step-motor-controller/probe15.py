#!/usr/bin/env python3
"""Bisect: find which embedded lib symbol breaks kicad-cli."""
import subprocess, os, re

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
SCH = os.path.join(PROJ, 'step-motor-controller.kicad_sch')
KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
txt = open(SCH, encoding='utf-8').read()

# split lib_symbols into blocks
start = txt.find('\t(lib_symbols')
i = start + len('\t(lib_symbols')
blocks = []
while True:
    j = txt.find('\t\t(symbol "', i)
    if j == -1 or txt.find('\t) ', j) != -1 and False:
        pass
    if j == -1:
        break
    # block ends at balanced close
    depth = 0
    k = j
    while k < len(txt):
        if txt[k] == '(': depth += 1
        elif txt[k] == ')':
            depth -= 1
            if depth == 0:
                break
        k += 1
    blocks.append(txt[j:k+1])
    i = k + 1
print(f'lib symbol blocks: {len(blocks)}')

header = txt[:start]
# find where instances start (first "\t(symbol\n" after lib_symbols close)
lib_close = txt.find('\t)\n', i)
inst_start = txt.find('\t(symbol\n', lib_close)

def test(content, name):
    p = os.path.join(PROJ, f'bisect_{name}.kicad_sch')
    open(p, 'w', encoding='utf-8').write(content)
    r = subprocess.run([KICAD, 'sch', 'export', 'netlist', '--format', 'kicadsexpr',
                        '--output', os.path.join(PROJ, 'b.net'), p],
                       capture_output=True, text=True, timeout=60)
    return r.returncode

# test 1: header + lib_symbols(full) + close (no instances)
c1 = header + '\t(lib_symbols\n' + ''.join(blocks) + '\t)\n)\n'
print('lib_symbols only:', test(c1, 'libsonly'))

# bisect blocks
lo, hi = 1, len(blocks)
def test_k(k):
    c = header + '\t(lib_symbols\n' + ''.join(blocks[:k]) + '\t)\n)\n'
    return test(c, f'k{k}')

if test_k(len(blocks)) != 0:
    # find first failing k
    bad = None
    for k in range(1, len(blocks) + 1):
        if test_k(k) != 0:
            bad = k
            break
    if bad:
        first_line = blocks[bad-1].split('\n')[0]
        print(f'FIRST FAILING BLOCK: #{bad}: {first_line[:80]}')
        # does k-1 pass?
        print(f'k={bad-1} passes: {test_k(bad-1) == 0}')
else:
    print('all lib blocks OK — problem elsewhere (instances?)')
    # test full file without instances
    c2 = header + '\t(lib_symbols\n' + ''.join(blocks) + '\t)\n)\n'
    print('already tested')
