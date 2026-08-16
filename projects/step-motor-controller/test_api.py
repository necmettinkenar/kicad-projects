import pcbnew
import os

kicad_fp_path = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'

# Try IO_MGR plugin approach
try:
    plugin = pcbnew.IO_MGR.PluginFind(pcbnew.IO_MGR.KICAD_SEXP)
    print(f"Plugin found: {plugin}")
    
    lib_path = os.path.join(kicad_fp_path, 'Resistor_SMD.pretty')
    fp = plugin.FootprintLoad(lib_path, 'R_0805_2012Metric')
    if fp:
        print(f"Load OK: {fp.GetReference()}")
    else:
        print("Load returned None")
except Exception as e:
    print(f"Plugin error: {e}")

# Alternative: use kicad-cli to create PCB from netlist
# Or create footprints manually
try:
    board = pcbnew.BOARD()
    
    # Create a simple footprint manually
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference("R1")
    
    # Add a pad
    pad = pcbnew.PAD(fp)
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.2)))
    pad.SetPosition(pcbnew.VECTOR2I(0, 0))
    pad.SetName("1")
    pad.SetLayer(pcbnew.F_Cu)
    fp.Add(pad)
    
    pad2 = pcbnew.PAD(fp)
    pad2.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.2)))
    pad2.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(2.0), 0))
    pad2.SetName("2")
    pad2.SetLayer(pcbnew.F_Cu)
    fp.Add(pad2)
    
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(50)))
    board.Add(fp)
    
    board.Save(r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\test_pcb.kicad_pcb')
    print("Manual footprint + PCB save: OK")
except Exception as e:
    print(f"Manual error: {e}")
