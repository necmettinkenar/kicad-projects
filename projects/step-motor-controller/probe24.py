import io
f = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\gen_schematic_wired.py'
with io.open(f, 'r', encoding='utf-8') as fh:
    txt = fh.read()

old = """for net, y in RAILS.items():
    A('\\t(global_label')
    A('\\t\\t"' + net + '"')
    A('\\t\\t(shape input)')
    A('\\t\\t(at ' + str(RAIL_X0) + ' ' + str(y) + ' 180)')
    A('\\t\\t(effects (font (size 1.27 1.27)))')
    A('\\t\\t(uuid "' + uid() + '")')
    A('\\t)')"""
new = """for net, y in RAILS.items():
    A('\\t(global_label')
    A('\\t\\t"' + net + '"')
    A('\\t\\t(shape input)')
    A('\\t\\t(at ' + str(RAIL_X0) + ' ' + str(y) + ' 180)')
    A('\\t\\t(effects (font (size 1.27 1.27)))')
    A('\\t\\t(uuid "' + uid() + '")')
    A('\\t)')
# name each wired net once (label on its leftmost pin) for readability + netlist names
_net_first_pin = {}
for (ref, num), (ex, ey, outward, nm, et) in PINS.items():
    nname = NETS_NETOF.get((ref, str(num)))
    if nname is None or nname in LABEL_NETS:
        continue
    cur = _net_first_pin.get(nname)
    if cur is None or (ex, ey) < cur[1]:
        _net_first_pin[nname] = ((ref, num, outward), (ex, ey))
for nname, (info, pos) in sorted(_net_first_pin.items()):
    if nname in RAILS:
        continue
    ex, ey = pos
    outward = info[2]
    A('\\t(global_label')
    A('\\t\\t"' + nname + '"')
    A('\\t\\t(shape input)')
    A('\\t\\t(at ' + str(ex) + ' ' + str(ey) + ' ' + str(outward) + ')')
    A('\\t\\t(effects (font (size 1.27 1.27)))')
    A('\\t\\t(uuid "' + uid() + '")')
    A('\\t)')"""
assert old in txt
txt = txt.replace(old, new)
with io.open(f, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(txt)
print('net naming labels added')
