#!/usr/bin/env python3
"""Diff the passing (o444) vs failing (o445) bisect files and capture kicad-cli stderr."""
import subprocess, os, difflib

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'

p444 = os.path.join(PROJ, 'bisect_o444.kicad_sch')
p445 = os.path.join(PROJ, 'bisect_o445.kicad_sch')
t444 = open(p444, encoding='utf-8').read()
t445 = open(p445, encoding='utf-8').read()

diff = list(difflib.unified_diff(t444.split('\n'), t445.split('\n'), lineterm=''))
print('=== DIFF (o444 -> o445) ===')
for ln in diff[:30]:
    print(ln)

outp = os.path.join(PROJ, 'probe_o445.net')
errp = os.path.join(PROJ, 'probe_o445.err')
r = subprocess.run([KICAD, 'sch', 'export', 'netlist', '--format', 'kicadsexpr',
                    '--output', outp, p445],
                   capture_output=True, text=True, timeout=120)
print(f'\no445: exit={r.returncode}')
print(f'stdout: {r.stdout[:300]!r}')
print(f'stderr: {r.stderr[:600]!r}')
print(f'netlist exists: {os.path.exists(outp)}')
