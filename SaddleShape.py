import c4d
from c4d.modules import mograph as mo
#Welcome to the world of Python

def main():
    md = mo.GeGetMoData(op)
    if md is None: return False

    cnt = md.GetCount()
    marr = md.GetArray(c4d.MODATA_MATRIX)
    fall = md.GetFalloffs()
    a = op[c4d.ID_USERDATA,2]
    b = op[c4d.ID_USERDATA,3]
    for i in reversed(xrange(0, cnt)):
        x,y,z = marr[i].off[0],marr[i].off[1],marr[i].off[2]
        y = x**2/a**2 - (z**2)/b**2
        marr[i].off = c4d.Vector(x,y,z)
    md.SetArray(c4d.MODATA_MATRIX, marr, True)
    return True
