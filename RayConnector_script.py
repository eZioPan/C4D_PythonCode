# Description: A script to create a ray connector to connect two objects
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0

"""
USEAGE:

Run this script from Script > User Scripts > Run Script...
This will create two locator called "FromLoc"(bigger one), and "ToLoc"(smaller one), and a sweep object called "Line" with a python tag on it.

In "Ray Attribute" of "Line",

the "From Object" and "To Object" defines which objects the ray will connect;

the "Start Distance" and "End Distance" defines between how far will ray started and stopped to connect two objects,
ditance is caculate in the FromObj's Z direction;

the "Length Ratio Remap" define how the ray grow and shrink between StartDistance and EndDistance,
0 means no ray will show, 1 mean full ray will show;

the "Positive Z Only" define whether the ray will connect objects in both positive and negative Z direction of From Object or only the postive part.
"""

import c4d
#Welcome to the world of Python


def main():

    fromObj = c4d.BaseObject(c4d.Onull)
    fromObj[c4d.ID_BASELIST_NAME] = "FromLoc"
    fromObj[c4d.NULLOBJECT_RADIUS] = 20

    toObj = c4d.BaseObject(c4d.Onull)
    toObj[c4d.ID_BASELIST_NAME] = "ToLoc"
    toObjoff = c4d.Vector(0, 0, 0)
    toObjv1 = c4d.Vector(-1, 0, 0)
    toObjv2 = c4d.Vector(0, 0.8, 0)
    toObjv3 = c4d.Vector(0, 0, -1)
    toObj.SetMg(c4d.Matrix(toObjoff, toObjv1, toObjv2, toObjv3))
    toObj[c4d.NULLOBJECT_RADIUS] = 16

    # Set Pyramid shape of locator
    for item in [fromObj,toObj]:
        item[c4d.NULLOBJECT_DISPLAY] = 12
        item[c4d.NULLOBJECT_ORIENTATION] = 3

    sweepObj = c4d.BaseObject(c4d.Osweep)
    sweepObj[c4d.ID_BASELIST_NAME] = "Line"

    bc1 = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    bc1[c4d.DESC_NAME] = "Ray Attribute"
    bc1[c4d.DESC_PARENTGROUP] = c4d.DescID(0)   # Put this group as a table of the object

    [bc2,bc3] = [c4d.GetCustomDatatypeDefault(c4d.DTYPE_BASELISTLINK) for i in range(0,2)]
    bc2[c4d.DESC_NAME] = "From Object"
    bc3[c4d.DESC_NAME] = "To Object"


    [bc4,bc5] = [c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL) for i in range(0,2)]
    bc4[c4d.DESC_NAME] = "Start Distance"
    bc5[c4d.DESC_NAME] = "End Distance"

    # Set default spline data
    bc6 = c4d.GetCustomDatatypeDefault(c4d.CUSTOMDATATYPE_SPLINE)
    bc6[c4d.DESC_NAME] = "Length Ratio Remap"

    bc7 = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL)
    bc7[c4d.DESC_NAME] = "Positive Z Only"

    # Get root user group description ID for other insertions
    DesID1 = sweepObj.AddUserData(bc1)


    for item in [bc2, bc3, bc4, bc5, bc6, bc7]:
        item[c4d.DESC_PARENTGROUP] = DesID1
        sweepObj.AddUserData(item)

    sweepObj[c4d.ID_USERDATA,2] = fromObj

    sweepObj[c4d.ID_USERDATA,3] = toObj

    sweepObj[c4d.ID_USERDATA,5] = 500

    # Set customized spline user data
    initSplineData = c4d.SplineData()
    initSplineData.DeleteAllPoints()

    initSplineData.MakePointBuffer(4)

    for knot in [[0,0,0], [1,0.2,1], [2,0.8,1], [3,1,0]]:
        initSplineData.SetKnot(
                                index=knot[0],
                                vPos=c4d.Vector(knot[1], knot[2], 0),
                                lFlagsSettings=c4d.FLAG_KNOT_T_KEEPVISUALANGLE,
                                vTangentLeft=c4d.Vector(-0.05,0,0),
                                vTangentRight=c4d.Vector(0.05,0,0),
                                interpol=c4d.CustomSplineKnotInterpolationBezier
                                )

    # Replace default spline data with customized one
    sweepObj[c4d.ID_USERDATA,6] = initSplineData

    contourSpline = c4d.BaseObject(c4d.Osplinenside)

    contourSpline[c4d.PRIM_NSIDE_RADIUS] = 5

    raySpline = c4d.BaseObject(c4d.Ospline)

    # Init a 2 points spline
    raySpline.ResizeObject(2,0)

    for item in [raySpline,contourSpline]:
        item.InsertUnder(sweepObj)

    # Core code in python tag
    pythonTag = c4d.BaseTag(c4d.Tpython)
    pythonTag[c4d.DESC_NAME] = "AutoConnectionUpdater"
    pythonTag[c4d.TPYTHON_CODE] = (
"""# Description: A script to create a ray connector to connect two objects
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0

import c4d
def main():
    sweepObj = op.GetObject()
    lineObj = op.GetObject().GetDown().GetNext()
    objFrom = sweepObj[c4d.ID_USERDATA,2]
    objTo = sweepObj[c4d.ID_USERDATA,3]
    startDistance = sweepObj[c4d.ID_USERDATA,4]
    endDistance = sweepObj[c4d.ID_USERDATA,5]
    mapperSpline = sweepObj[c4d.ID_USERDATA,6]
    positiveChecker = sweepObj[c4d.ID_USERDATA,7]

    if objFrom == None or objTo == None:
        print("Not enough Object")
        return None

    if startDistance == endDistance:
        print("same value at startDistance and endDistance")
        return None

    objFromPos = objFrom.GetMg().off
    objFromZ = objFrom.GetMg().v3
    objToPos = objTo.GetMg().off

    lineObj.SetPoint(0,objFromPos)
    lineObj.SetPoint(1,objToPos)
    lineObj.Message(c4d.MSG_UPDATE)     # Update point change of object

    ratio = 0

    # Get distance of two objects in From Object's Z direction
    dotProducted = objFromZ.GetNormalized().Dot(objToPos-objFromPos)
    if positiveChecker == False or dotProducted > 0:
        dis = abs(dotProducted)
        ratio = mapperSpline.GetPoint((dis-startDistance)/(endDistance-startDistance))[1]
    sweepObj[c4d.SWEEPOBJECT_GROWTH] = ratio
    return True
"""
    )
    sweepObj.InsertTag(pythonTag)

    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    for item in [sweepObj,toObj,fromObj]:
        doc.InsertObject(item)
        doc.AddUndo(c4d.UNDOTYPE_NEW, item)
    doc.EndUndo()
    doc.SetActiveObject(sweepObj, mode=c4d.SELECTION_NEW)
    c4d.EventAdd()

if __name__=='__main__':
    main()
