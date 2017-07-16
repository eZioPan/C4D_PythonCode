# Make a grid of Jumping Bar[Python Effector Code]
# Author: eZioPan
# Date: 2017-Jul-16

"""
Need Thing
<1> Cloner Object with "Grid Array" Mode
<2> Before this Python Effector, anything to assign random color to Cloner

Notice
<1> Jumping bar is jumping alone Clone's Object Z axis,
    make sure color variation on xy plane

<2> If you want to rotate Cloner to other direction,
    keep relative Orenation of Cloner and color varation object
    Better rotate with a Null Object contain color varation object, Cloner and Effector

<3> Default code use MODATA_MATRIX to scale down a cloned object
    If you just need object disappear, nothing more(eg. no Delay Effect to jiggle object scale)
    you can set c4d.MODATE_FLAGES to c4d.MOGENFLAG_DISABLE to kill the object

"""



import c4d,math
from c4d.modules import mograph as mo


def main():

    md = mo.GeGetMoData(op)
    if md is None: return False

    # get total count on x,y,z direction from Cloner
    Rows=gen[c4d.MG_GRID_RESOLUTION]
    xRow=int(Rows[0])
    yRow=int(Rows[1])
    zRow=int(Rows[2])

    cnt = md.GetCount()

    # fetch color information and
    colorLs = md.GetArray(c4d.MODATA_COLOR)

    matrixLs=md.GetArray(c4d.MODATA_MATRIX)
    #flagLs = md.GetArray(c4d.MODATA_FLAGS)

    # get base color
    for i in range(0,xRow*yRow):

        # use color to decide how many object should show in certain bar
        ratio=c4d.utils.RGBToHSV(colorLs[i])[2]
        # use math.ceil keep floor show
        showCount=int(math.ceil(ratio*zRow))

        # make object unshow
        for j in range(0,zRow):
            if j > showCount:
                matrixLs[j*xRow*yRow+i].v1=c4d.Vector(0,0,0)
                matrixLs[j*xRow*yRow+i].v2=c4d.Vector(0,0,0)
                matrixLs[j*xRow*yRow+i].v3=c4d.Vector(0,0,0)
                #flagLs[j*xRow*yRow+i]=c4d.MOGENFLAG_DISABLE

    #md.SetArray(c4d.MODATA_FLAGS, flagLs, True)
    md.SetArray(c4d.MODATA_MATRIX, matrixLs, True)
    return True
