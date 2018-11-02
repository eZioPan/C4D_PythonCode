# Description: A script to create an arbitrary-number-of-point circle with bezier spline
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0
# Version: 0.0.1
# Last Update: 2018Nov2

# About the algorithm of draw a circle with bezier:
# https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves/27863181#27863181

"""
USEAGE:

Run this script from Script > User Scripts > Run Script...
This will create a spline object called "Circle" with a python tag on it.
In "Circle Attribute" of "Cirle", "Radius" and "Point Number" defined circle's radius and total point count
"""

import c4d
#Welcome to the world of Python

def main():

    circle = c4d.SplineObject(pcnt=0, type=c4d.SPLINETYPE_BEZIER)
    circle[c4d.ID_BASELIST_NAME] = "Circle"
    circle[c4d.SPLINEOBJECT_CLOSED] = True

    bc0 = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    bc0[c4d.DESC_NAME] = "Circle Attribute"
    bc0[c4d.DESC_DEFAULT] = 1
    bc0[c4d.DESC_PARENTGROUP] = c4d.DescID(0)

    DesID0 = circle.AddUserData(bc0)

    bc1 = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
    bc1[c4d.DESC_NAME] = "Radius"
    bc1[c4d.DESC_DEFAULT] = 200
    bc1[c4d.DESC_MIN] = 0

    bc2 = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc2[c4d.DESC_NAME] = "Point Number"
    bc2[c4d.DESC_DEFAULT] = 4
    bc2[c4d.DESC_MIN] = 2

    DescIDLs = []
    for item in [bc1, bc2]:
        item[c4d.DESC_PARENTGROUP] = DesID0
        DescID = circle.AddUserData(item)
        DescIDLs.append(DescID)

    circle[DescIDLs[0]] = 200
    circle[DescIDLs[1]] = 4

    # Core code in python tag
    pythonTag = c4d.BaseTag(c4d.Tpython)
    pythonTag[c4d.ID_BASELIST_NAME] = "Circle Modifier"
    pythonTag[c4d.TPYTHON_CODE] = (
"""# Description: A script to create an arbitrary-number-of-point circle with bezier spline
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0
# Version: 0.0.1
# Last Update: 2018Nov2
import c4d, math
#Welcome to the world of Python

deg = math.pi/180.0

def main():

    circle = op.GetObject()

    pCnt = circle[c4d.ID_USERDATA,3]           # Here is the point count
    radius = circle[c4d.ID_USERDATA,2]         # Here is the radius of circle

    #Prepare the data
    tangentLength = (4/3)*math.tan(math.pi/(2*pCnt))*radius # single side tangent handle length
    pointPosLs = []
    tangentLs = []
    for i in range(0,pCnt):

        angle = i*(2*math.pi)/pCnt    # caculate the angle

        # caculate point position
        y = math.sin(angle)*radius
        x = math.cos(angle)*radius
        pointPosLs.append(c4d.Vector(x, y, 0))

        # tangent position
        lx = math.sin(angle)*tangentLength
        ly = -math.cos(angle)*tangentLength
        rx = -lx
        ry = -ly
        vl = c4d.Vector(lx, ly, 0)
        vr = c4d.Vector(rx, ry, 0)
        tangentLs.append([vl, vr])

    # resize bezier curve
    circle.ResizeObject(pcnt=pCnt, scnt=1)
    circle.SetSegment(id=0, cnt=pCnt, closed=True)

    circle.SetAllPoints(pointPosLs) # set point position

    # set tangent position
    for i in range(0, pCnt):
        circle.SetTangent(i, tangentLs[i][0], tangentLs[i][1])

    circle.Message(c4d.MSG_UPDATE)

    return circle
"""
    )

    circle.InsertTag(pythonTag)
    doc = c4d.documents.GetActiveDocument()

    doc.StartUndo()
    doc.InsertObject(circle)
    doc.SetActiveObject(circle, mode=c4d.SELECTION_NEW)
    doc.AddUndo(c4d.UNDOTYPE_NEW, circle)
    doc.EndUndo()

    c4d.EventAdd()

if __name__=='__main__':
    main()
