f = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\gen_schematic_wired.py'
lines = open(f, encoding='utf-8').read().split('\n')
for i, ln in enumerate(lines):
    if 'for (sx, sy, bx2, by2) in path_to_segments(path):' in ln and i > 300:
        # add pin connection wires before the segment loop
        lines[i] = ('        segs = path_to_segments(path)\n'
                    '        if segs:\n'
                    '            add_wire(ax, ay, segs[0][0], segs[0][1], net)\n'
                    '            for (sx, sy, bx2, by2) in segs:\n'
                    '                add_wire(sx, sy, bx2, by2, net)\n'
                    '            add_wire(segs[-1][2], segs[-1][3], bx, by, net)')
        print('patched signal connection at line', i + 1)
        break
open(f, 'w', encoding='utf-8').write('\n'.join(lines))
