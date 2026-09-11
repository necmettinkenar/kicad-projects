#!/usr/bin/env python3
"""Fix the last clearance violation: shift SW2_SIG via away from GPIO23_RST B.Cu track,
moving connected track endpoints along."""
import pcbnew, math

PCB = r'C:\Users\CASPER\Documents\KiCad\kicad-projects\projects\step-motor-controller\step-motor-controller.kicad_pcb'
board = pcbnew.LoadBoard(PCB)
def mmv(v): return pcbnew.ToMM(v)

target_net = 'SW2_SIG'
other_net = 'GPIO23_RST'
via = None
for t in board.GetTracks():
    if t.GetNetname() == target_net and t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        x, y = mmv(p.x), mmv(p.y)
        if abs(x - 66.5) < 1 and abs(y - 47.5) < 1:
            via = t
            vx, vy = x, y
            break
if via is None:
    print('via not found')
    raise SystemExit(1)
print('via at', vx, vy)

others = []
for t in board.GetTracks():
    if t.GetNetname() == other_net and t.Type() == pcbnew.PCB_TRACE_T and t.GetLayerName() == 'B.Cu':
        s = t.GetStart(); e = t.GetEnd()
        others.append(((mmv(s.x), mmv(s.y)), (mmv(e.x), mmv(e.y))))

def via_clear(x, y):
    for (a, b) in others:
        # point-seg distance
        dx, dy = b[0]-a[0], b[1]-a[1]
        L2 = dx*dx + dy*dy
        t = 0 if L2 == 0 else max(0, min(1, ((x-a[0])*dx + (y-a[1])*dy)/L2))
        d = math.hypot(x-(a[0]+t*dx), y-(a[1]+t*dy))
        if d < 0.4/2 + 0.3/2 + 0.3:
            return False
    return True

# connected SW2_SIG tracks (endpoint at via)
connected = []
for t in board.GetTracks():
    if t.GetNetname() == target_net and t.Type() == pcbnew.PCB_TRACE_T:
        s = t.GetStart(); e = t.GetEnd()
        sx, sy = mmv(s.x), mmv(s.y)
        ex, ey = mmv(e.x), mmv(e.y)
        if math.hypot(sx-vx, sy-vy) < 0.02:
            connected.append((t, 's', (sx, sy), (ex, ey)))
        elif math.hypot(ex-vx, ey-vy) < 0.02:
            connected.append((t, 'e', (sx, sy), (ex, ey)))
print('connected tracks:', len(connected))

placed = False
for cand in [(0,0.5),(0,-0.5),(0.5,0),(-0.5,0),(0.5,0.5),(-0.5,0.5),(0.5,-0.5),(-0.5,-0.5),
             (0,1.0),(0,-1.0),(1.0,0),(-1.0,0),(1.0,1.0),(-1.0,-1.0),(1.0,-1.0),(-1.0,1.0)]:
    nx, ny = vx + cand[0], vy + cand[1]
    if not via_clear(nx, ny):
        continue
    # check moved segments against others too (approx: just via check + endpoint clearance)
    ok = True
    for (t, end, s, e) in connected:
        pass
    # apply
    via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(nx), pcbnew.FromMM(ny)))
    for (t, end, s, e) in connected:
        if end == 's':
            t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(nx), pcbnew.FromMM(ny)))
        else:
            t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(nx), pcbnew.FromMM(ny)))
    placed = True
    print('via moved to', nx, ny)
    break

if placed:
    board.Save(PCB)
    print('saved')
else:
    print('NO SAFE OFFSET FOUND')
    raise SystemExit(1)
