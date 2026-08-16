"""
Auto-route the Step Motor Controller PCB using pcbnew Python API.
Connects pads that share the same net with copper tracks.
"""
import pcbnew
import os
import subprocess

PROJECT_DIR = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller'
PCB_FILE = os.path.join(PROJECT_DIR, 'step-motor-controller.kicad_pcb')

board = pcbnew.LoadBoard(PCB_FILE)
print(f"Board loaded")
print(f"Footprints: {len(list(board.Footprints()))}")

# Build net -> pads mapping
net_pads = {}
for fp in board.Footprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        net_name = pad.GetNetname()
        if net_name and net_name != "":
            if net_name not in net_pads:
                net_pads[net_name] = []
            net_pads[net_name].append((ref, pad))

print(f"Nets found: {len(net_pads)}")
for net_name, pads in sorted(net_pads.items()):
    print(f"  {net_name}: {len(pads)} pads")

# Route tracks between pads on the same net
tracks_created = 0
for net_name, pads in net_pads.items():
    if len(pads) < 2:
        continue
    if net_name in ['GND', '+24V', '+5V', '+3V3']:
        tw = pcbnew.FromMM(0.8)
    else:
        tw = pcbnew.FromMM(0.25)
    
    ref0, pad0 = pads[0]
    pos0 = pad0.GetPosition()
    
    for i in range(1, len(pads)):
        ref_i, pad_i = pads[i]
        pos_i = pad_i.GetPosition()
        
        # L-shaped track: horizontal then vertical
        track1 = pcbnew.PCB_TRACK(board)
        track1.SetStart(pos0)
        mid = pcbnew.VECTOR2I(pos_i.x, pos0.y)
        track1.SetEnd(mid)
        track1.SetWidth(tw)
        track1.SetLayer(pcbnew.F_Cu)
        track1.SetNet(pad0.GetNet())
        board.Add(track1)
        tracks_created += 1
        
        track2 = pcbnew.PCB_TRACK(board)
        track2.SetStart(mid)
        track2.SetEnd(pos_i)
        track2.SetWidth(tw)
        track2.SetLayer(pcbnew.F_Cu)
        track2.SetNet(pad_i.GetNet())
        board.Add(track2)
        tracks_created += 1

# Add GND pour on B.Cu
gnd_net = None
for net_name, pads in net_pads.items():
    if net_name == 'GND':
        gnd_net = pads[0][1].GetNet()
        break

if gnd_net:
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(gnd_net)
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    poly.Append(pcbnew.FromMM(2), pcbnew.FromMM(2))
    poly.Append(pcbnew.FromMM(98), pcbnew.FromMM(2))
    poly.Append(pcbnew.FromMM(98), pcbnew.FromMM(78))
    poly.Append(pcbnew.FromMM(2), pcbnew.FromMM(78))
    zone.SetOutline(poly)
    zone.SetMinThickness(pcbnew.FromMM(0.2))
    board.Add(zone)
    print("GND copper pour added on B.Cu")

board.Save(PCB_FILE)
print(f"Tracks created: {tracks_created}")
print(f"PCB saved")

# Run DRC
kicad_cli = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
drc_out = os.path.join(PROJECT_DIR, 'drc_report_routed.txt')
result = subprocess.run([kicad_cli, 'pcb', 'drc', '--output', drc_out, PCB_FILE],
    capture_output=True, text=True, timeout=120)
print(f"DRC exit code: {result.returncode}")
print(f"DRC stdout: {result.stdout[:300]}")

# Generate Gerbers
gerber_dir = os.path.join(PROJECT_DIR, 'fabrication', 'gerbers')
os.makedirs(gerber_dir, exist_ok=True)
result2 = subprocess.run([kicad_cli, 'pcb', 'export', 'gerbers', '--output', gerber_dir, PCB_FILE],
    capture_output=True, text=True, timeout=120)
print(f"Gerber exit code: {result2.returncode}")
print(f"Gerber stdout: {result2.stdout[:300]}")

# Generate drill
drill_dir = os.path.join(PROJECT_DIR, 'fabrication', 'drills')
os.makedirs(drill_dir, exist_ok=True)
result3 = subprocess.run([kicad_cli, 'pcb', 'export', 'drill', '--output', drill_dir, PCB_FILE],
    capture_output=True, text=True, timeout=120)
print(f"Drill exit code: {result3.returncode}")

# Generate position file
pos_dir = os.path.join(PROJECT_DIR, 'fabrication', 'pnp')
os.makedirs(pos_dir, exist_ok=True)
result4 = subprocess.run([kicad_cli, 'pcb', 'export', 'pos', '--output', pos_dir, PCB_FILE],
    capture_output=True, text=True, timeout=120)
print(f"Position exit code: {result4.returncode}")

# List all output files
print("\n=== Output files ===")
for root, dirs, files in os.walk(PROJECT_DIR):
    for f in files:
        if f.endswith(('.gbr', '.drl', '.pos', '.gko', '.gtl', '.gbl', '.gbo', '.gto', '.gm1', '.csv', '.txt')):
            fpath = os.path.join(root, f)
            print(f"  {os.path.relpath(fpath, PROJECT_DIR)} ({os.path.getsize(fpath)} bytes)")
