import re
f = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\step-motor-controller.kicad_sch'
txt = open(f, encoding='utf-8').read()
i = txt.find('(symbol "Converter_ACDC:IRM-20-24"')
seg = txt[i:i+8000]
for m in re.finditer(r'\(pin (\w+) (\w+)\s*\n?\s*\(at ([^)]+)\)', seg):
    j = m.start()
    blk = seg[j:j+400]
    nm = re.search(r'\(name "([^"]*)"', blk)
    num = re.search(r'\(number "([^"]*)"', blk)
    print('pin', num.group(1) if num else '?', repr(nm.group(1) if nm else '?'), 'type:', m.group(1))
