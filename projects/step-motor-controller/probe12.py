import pcbnew, os

PCB = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\step-motor-controller.kicad_pcb'
board = pcbnew.LoadBoard(PCB)

MODEL_DIR = r'C:\Program Files\KiCad\10.0\share\kicad\3dmodels'
total_with = 0
total_without = 0
report = []
for fp in board.Footprints():
    ref = fp.GetReference()
    models = list(fp.Models())
    if models:
        m0 = models[0]
        path = m0.m_Filename
        # resolve ${VAR}
        resolved = path
        import re
        m = re.match(r'\$\{([^}]+)\}(.*)', path)
        if m:
            var = m.group(1)
            base = os.environ.get(var, r'C:\Program Files\KiCad\10.0\share\kicad\3dmodels' if '3DMODEL' in var else '')
            resolved = os.path.join(base, m.group(2).lstrip('/\\')) if base else path
        exists = os.path.exists(resolved)
        total_with += 1
        report.append(f'{ref:5} models={len(models)} exists={exists} :: {path[:70]}')
    else:
        total_without += 1
        report.append(f'{ref:5} NO 3D MODEL')

print(f'With models: {total_with} | Without: {total_without}')
for r in report:
    print(' ', r)
