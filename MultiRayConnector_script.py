# Description: A script to create a multiple connector to connect between two group of objects
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0
# Last Update: 2018Sep27

"""
USEAGE:

Run this script from Script > User Scripts > Run Script...
This will create a sweep object called "Line" with a python tag on it.

In "Ray Attribute" of "Line", "From Objects List" and "To Objects List" defines which objects the ray will connect.
"""

import c4d
#Welcome to the world of Python

def main():

    sweepObj = c4d.BaseObject(c4d.Osweep)
    sweepObj[c4d.ID_BASELIST_NAME] = "Line"

    bc1 = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    bc1[c4d.DESC_NAME] = "Ray Attribute"
    bc1[c4d.DESC_PARENTGROUP] = c4d.DescID(0)   # Put this group as a table of the object

    [bc2,bc3] = [c4d.GetCustomDatatypeDefault(c4d.CUSTOMDATATYPE_INEXCLUDE_LIST) for i in range(0,2)]
    bc2[c4d.DESC_NAME] = "From Objects List"
    bc3[c4d.DESC_NAME] = "To Objects List"

    DesID1 = sweepObj.AddUserData(bc1) # Get root user group description ID for other insertions

    for item in [bc2, bc3]:
        item[c4d.DESC_PARENTGROUP] = DesID1
        sweepObj.AddUserData(item)

    contourSpline = c4d.BaseObject(c4d.Osplinenside)
    contourSpline[c4d.PRIM_NSIDE_RADIUS] = 5

    raySpline = c4d.BaseObject(c4d.Ospline)

    # Init a empty spline
    raySpline.ResizeObject(0,0)

    for item in [raySpline,contourSpline]:
        item.InsertUnder(sweepObj)

    # Core code in python tag
    pythonTag = c4d.BaseTag(c4d.Tpython)
    pythonTag[c4d.ID_BASELIST_NAME] = "AutoConnectionUpdater"
    pythonTag[c4d.TPYTHON_CODE] = (
"""# Description: A script to create a multiple connector to connect between two group of objects
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0
# Last Update: 2018Sep26

import c4d

lastState = False       # track last running state

def main():

    global lastState

    sweepObj = op.GetObject()
    lineObj = sweepObj.GetDown().GetNext()
    fromLs = sweepObj[c4d.ID_USERDATA,2]
    toLs = sweepObj[c4d.ID_USERDATA,3]

    fromCnt = fromLs.GetObjectCount()
    toCnt = toLs.GetObjectCount()

    if fromCnt == 0 or toCnt == 0:
        if lastState == True:           # do not pour garbage into console, or refresh scene too fast.
            lineObj.ResizeObject(0,1)   # clean spline data if nothing to generate.
            lineObj.Message(c4d.MSG_UPDATE)
            print("[RayConnector] Not enough Objects.")
            lastState = False
        return None

    if lastState == False:              # do not pour garbage into console
        lastState = True
        print("[RayConnector] OK.")

    fromMatrixLs = []
    for i in range(fromCnt):
        fromObj = (fromLs.ObjectFromIndex(doc,i))
        fromMatrixLs.append(fromObj.GetMg().off)

    toMatrixLs = []
    for i in range(toCnt):
        toObj = (toLs.ObjectFromIndex(doc,i))
        toMatrixLs.append(toObj.GetMg().off)

    rayCnt = max(fromCnt, toCnt)
    lineObj.ResizeObject(2*rayCnt, rayCnt)

    for i in range(rayCnt):
        lineObj.SetSegment(id=i, cnt=2, closed=False)

    reverse = False
    if fromCnt > toCnt:
        reverse = True

    if reverse == False:
        for i in range(toCnt):
            pairNum = i % fromCnt
            lineObj.SetPoint(i*2, fromMatrixLs[pairNum-1])
            lineObj.SetPoint(i*2+1, toMatrixLs[i])
    else:
        for i in range(fromCnt):
            pairNum = i % toCnt
            lineObj.SetPoint(i*2, fromMatrixLs[i])
            lineObj.SetPoint(i*2+1, toMatrixLs[pairNum-1])

    lineObj.Message(c4d.MSG_UPDATE)     # Update points change of object

    return True
"""
    )
    sweepObj.InsertTag(pythonTag)

    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    doc.InsertObject(sweepObj)
    doc.AddUndo(c4d.UNDOTYPE_NEW, item)
    doc.EndUndo()
    doc.SetActiveObject(sweepObj, mode=c4d.SELECTION_NEW)
    c4d.EventAdd()

if __name__=='__main__':
    main()
