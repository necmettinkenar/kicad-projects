#!/usr/bin/env python3
"""Fill GND zone in a separate process (isolates pcbnew ZONE_FILLER crash)."""
import pcbnew, sys

PCB = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\step-motor-controller.kicad_pcb'
board = pcbnew.LoadBoard(PCB)
print('Board loaded')
zones = board.Zones()
print('Zones:', len(list(zones)))
try:
    filler = pcbnew.ZONE_FILLER(board)
    ok = filler.Fill(zones)
    print('Fill result:', ok)
except Exception as e:
    print('Fill exception:', e)
    sys.exit(2)
board.Save(PCB)
print('Saved with filled zone')
