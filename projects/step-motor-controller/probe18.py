import re
f = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\gen_schematic_wired.py'
lines = open(f, encoding='utf-8').read().split('\n')
BS = chr(92)  # backslash
fixed = 0
for i, ln in enumerate(lines):
    if 'FOOTPRINTS.get(ref' in ln and (BS + 't') in ln:
        # build the correct line: A('\t\t(property "Footprint" "...' + ... + '...hide))')
        correct = "    A('" + BS + "t" + BS + "t(property \"Footprint\" \"' + FOOTPRINTS.get(ref, '') + '\" (at ' + str(cx) + ' ' + str(cy) + ' 0) (effects (font (size 1.27 1.27)) hide))')"
        lines[i] = correct
        fixed += 1
        print('fixed line', i)
open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('fixed count:', fixed)
