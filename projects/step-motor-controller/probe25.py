import io
f = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\gen_schematic_wired.py'
with io.open(f, 'r', encoding='utf-8') as fh:
    txt = fh.read()

# merge_collinear cagrisini kapat (KURAL-2 dedupe ile saglaniyor)
old = "merge_collinear()\n\n# ---- pin-stitch"
new = "# merge_collinear()  # KURAL-2 dedupe ile saglandi; collinear merge kopukluk yaratti\n\n# ---- pin-stitch"
assert old in txt
txt = txt.replace(old, new)

# pin-stitch tol'unu 0.01'e dusur (daha katı temas kontrolu)
old2 = "    if any(pt_on_wire(ex, ey, w) for w in net_wires):\n        continue"
new2 = "    if any(pt_on_wire(ex, ey, w, 0.01) for w in net_wires):\n        continue"
if old2 in txt:
    txt = txt.replace(old2, new2)
    print('stitch tol 0.01')

with io.open(f, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(txt)
print('merge kapatildi')
