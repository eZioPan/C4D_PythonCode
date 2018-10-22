# Description: A script to create a multiple connector to connect between two group of objects
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0
# Version: 0.2.0
# Last Update: 2018Oct22

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
    bc1[c4d.DESC_DEFAULT] = 1                   # Make userdata group tab stay open in default-open-tab mode(Right mouse button click on an object tab).
    bc1[c4d.DESC_PARENTGROUP] = c4d.DescID(0)   # Put this group as a table of the object

    [bc2, bc4] = [c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL) for i in range(0,2)]
    [bc3, bc5] = [c4d.GetCustomDatatypeDefault(c4d.CUSTOMDATATYPE_INEXCLUDE_LIST) for i in range(0,2)]
    bc2[c4d.DESC_NAME] = "From Point"
    bc3[c4d.DESC_NAME] = "From Objects List"
    bc4[c4d.DESC_NAME] = "To Point"
    bc5[c4d.DESC_NAME] = "To Objects List"

    DesID1 = sweepObj.AddUserData(bc1) # Get root user group description ID for other insertions, and active tab


    for item in [bc2, bc3, bc4, bc5]:
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
    pythonTag[c4d.ID_BASELIST_NAME] = "Auto Connection Updater"
    pythonTag[c4d.TPYTHON_CODE] = (
"""# Description: A script to create a multiple connector to connect between two group of objects
# Author: eZioPan
# Page: github.com/eZioPan
# License: Creative Commons Attribution Share Alike 4.0
# Version: 0.2.0
# Last Update: 2018Oct22

import c4d
from c4d.modules import mograph as mo

lastState = False       # track last running state

# filter non-exist objects out of result object list
def extractInExData(inExData):
    output = []
    inExLen = inExData.GetObjectCount()
    for i in range(0,inExLen):
        obj = inExData.ObjectFromIndex(doc,i)
        # check both InExcludeData.GetObjectCount() and InExcludeData.ObjectFromIndex() to get actual objects in list.
        if obj == None:
            continue
        output.append(obj)
    return output

# extract point postion information on demand
def GetGroupPointsPos(objLs=[], usePoint=False):
    posLs = []
    for obj in objLs:
        objMg = obj.GetMg()
        if usePoint == False or obj.GetType() == c4d.Onull:
             posLs.append(objMg.off)
        elif obj.IsInstanceOf(c4d.Obasemogen):
            md = mo.GeGetMoData(obj)
            moMatrixLs = md.GetArray(c4d.MODATA_MATRIX)
            for moMatrix in moMatrixLs:
                point = moMatrix.off
                posLs.append(objMg*point)
        else:
            pointPosLs = obj.GetCache().GetDeformCache().GetAllPoints()
            for point in pointPosLs:
                posLs.append(objMg*point)
    return posLs

# modify line data from point position
def SetLinePointPos(lineObj, fromPosLs, toPosLs):
    fromPosCnt = len(fromPosLs)
    toPosCnt = len(toPosLs)
    rayCnt = max(fromPosCnt, toPosCnt)

    iLineMg = ~(lineObj.GetMg()) # Invert carrier global matrix

    # apply invert carrier matrix to all point position
    for i in range(fromPosCnt):
        fromPosLs[i] = iLineMg * fromPosLs[i]
    for i in range(toPosCnt):
        toPosLs[i] = iLineMg * toPosLs[i]

    lineObj.ResizeObject(2*rayCnt, rayCnt)

    for i in range(rayCnt):
        lineObj.SetSegment(id=i, cnt=2, closed=False)

    if fromPosCnt <= toPosCnt:
        for i in range(toPosCnt):
            pairNum = i % fromPosCnt
            lineObj.SetPoint(i*2, fromPosLs[pairNum-1])
            lineObj.SetPoint(i*2+1, toPosLs[i])
    else:
        for i in range(fromPosCnt):
            pairNum = i % toPosCnt
            lineObj.SetPoint(i*2, fromPosLs[i])
            lineObj.SetPoint(i*2+1, toPosLs[pairNum-1])

def main():

    global lastState

    sweepObj = op.GetObject()
    lineObj = sweepObj.GetDown().GetNext()
    fromPoint = sweepObj[c4d.ID_USERDATA,2]
    fromInExData = sweepObj[c4d.ID_USERDATA,3]
    toPoint = sweepObj[c4d.ID_USERDATA,4]
    toInExData = sweepObj[c4d.ID_USERDATA,5]

    fromLs = extractInExData(fromInExData)
    toLs = extractInExData(toInExData)

    if len(fromLs) == 0 or len(toLs) == 0:
        if lastState == True: # do not pour garbage into console, or refresh scene too fast.
            lineObj.ResizeObject(0,1)   # clean spline data if nothing to generate.
            lineObj.Message(c4d.MSG_UPDATE)
            print("[RayConnector] Not enough Objects.")
            lastState = False
        return None           # Terminate execution

    if lastState == False:              # do not pour garbage into console
        lastState = True
        print("[RayConnector] OK.")

    fromPosLs = GetGroupPointsPos(fromLs,fromPoint)
    toPosLs = GetGroupPointsPos(toLs,toPoint)

    SetLinePointPos(lineObj, fromPosLs, toPosLs)

    lineObj.Message(c4d.MSG_UPDATE)     # Update points change of object

    return True
"""
    )

    intActTag = c4d.BaseTag(c4d.Tinteraction)
    intActTag[c4d.ID_BASELIST_NAME] = "Disable Viewport Selection"
    intActTag[c4d.INTERACTIONTAG_SELECT] = True

    for tag in [pythonTag, intActTag]:
        sweepObj.InsertTag(tag)

    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    doc.InsertObject(sweepObj)
    doc.SetActiveObject(sweepObj, mode=c4d.SELECTION_NEW)
    c4d.gui.ActiveObjectManager_SetObject(      # Change active tab after insert into scene
        id=c4d.ACTIVEOBJECTMODE_OBJECT,
        op=sweepObj,
        flags=c4d.ACTIVEOBJECTMANAGER_SETOBJECTS_NOMODESWITCH,
        activepage=DesID1
    )
    doc.AddUndo(c4d.UNDOTYPE_NEW, item)
    doc.EndUndo()
    c4d.EventAdd()

if __name__=='__main__':
    main()
