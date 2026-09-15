#!/usr/bin/env python3
"""Isolate which construct breaks kicad-cli by generating file variants."""
import re, subprocess, os, sys

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
SCH = os.path.join(PROJ, 'step-motor-controller.kicad_sch')
KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'

txt = open(SCH, encoding='utf-8').read()

variants = {
    'full': txt,
    'no_junctions': re.sub(r'\t\(junction \(at [^)]+\) \(diameter 0\) \(color 0 0 0 0\) \(uuid "[^"]+"\)\)\n', '', txt),
    'no_wires': re.sub(r'\t\(wire \(pts[^)]*\)\) \)\n?\t\(stroke[^)]*\)\)\n\t\(uuid "[^"]+"\)\)\n', '', txt),
    'no_mirror': txt.replace('\t\t(mirror x)\n', ''),
    'no_nc': re.sub(r'\t\(no_connect \(at [^)]+\) \(uuid "[^"]+"\)\)\n', '', txt),
}
# simpler no_wires: remove all (wire ...) blocks via balanced scan
def remove_blocks(txt, header):
    out = []
    i = 0
    while True:
        j = txt.find(header, i)
        if j == -1:
            out.append(txt[i:])
            break
        out.append(txt[i:j])
        # skip to end of line containing header start... find balanced
        depth = 0
        k = j
        while k < len(txt):
            if txt[k] == '(': depth += 1
            elif txt[k] == ')':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        i = k + 1
    return ''.join(out)

variants['no_wires'] = remove_blocks(txt, '\t(wire ')
variants['no_junctions'] = remove_blocks(txt, '\t(junction ')
variants['no_nc'] = remove_blocks(txt, '\t(no_connect ')
variants['no_labels'] = remove_blocks(txt, '\t(global_label')

for name, content in variants.items():
    p = os.path.join(PROJ, f'test_{name}.kicad_sch')
    open(p, 'w', encoding='utf-8').write(content)
    r = subprocess.run([KICAD, 'sch', 'export', 'netlist', '--format', 'kicadsexpr',
                        '--output', os.path.join(PROJ, 't.net'), p],
                       capture_output=True, text=True, timeout=60)
    print(f'{name:14} exit={r.returncode} stderr={r.stderr.strip()[:80]!r}')
