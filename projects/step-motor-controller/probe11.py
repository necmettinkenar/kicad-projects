import sys
sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin\Lib\site-packages')
f = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\step-motor-controller.kicad_sch'
from kibot.kicad.sexpdata import load
with open(f, encoding='utf-8') as fh:
    obj = load(fh)
print('SEXPDATA PARSE OK')
