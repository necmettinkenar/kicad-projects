import re

PROJ = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
txt = open(PROJ + r'\exported-netlist.net', encoding='utf-8').read()
print('contains +24V:', '+24V' in txt)
print('contains +5V:', '+5V' in txt)
print('contains GND:', 'GND' in txt)

for comp, pin in [('C1', '1'), ('C1', '2'), ('PS1', '4'), ('R5', '2')]:
    m = re.search(r'\(net \(code "\d+"\)\s*\(name "([^"]+)"\)((?:(?!\(net ).)*)\(ref "' + comp + r'"\)\s*\(pin "' + pin + r'"', txt, re.S)
    if m:
        print(comp + '.' + pin, 'net:', m.group(1))
    else:
        print(comp + '.' + pin, 'NOT FOUND in any named net')

sch = open(PROJ + r'\step-motor-controller.kicad_sch', encoding='utf-8').read()
print('rail wire (30,24):', '(xy 30 24) (xy 400 24)' in sch)
print('label +24V present:', '"+24V"' in sch)
i = sch.find('"24V"')
if i == -1:
    i = sch.find('+24V')
print('label context:', sch[max(0, i-80):i+60] if i > 0 else 'none')
