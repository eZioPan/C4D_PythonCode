import c4d,math
from c4d.modules import mograph as mo


def getBoxCoord(curNum,cntX,cntY,space):
	Z = math.floor(float(curNum)/(cntX*cntY))
	Y = math.floor((curNum-Z*(cntX*cntY))/cntX)
	X = curNum-Z*(cntX*cntY)-Y*cntX
	return (int(X*space),int(Y*space),int(Z*space))

def setC4DMat(mat=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]]):
	off = c4d.Vector(mat[0][0],mat[0][1],mat[0][2])
	v1 = c4d.Vector(mat[1][0],mat[1][1],mat[1][2])
	v2 = c4d.Vector(mat[2][0],mat[2][1],mat[2][2])
	v3 = c4d.Vector(mat[3][0],mat[3][1],mat[3][2])
	return c4d.Matrix(off,v1,v2,v3)

def main():
	md = mo.GeGetMoData(op)
	if md is None: return False
	marr=[]
	cnt = md.GetCount()
	for i in xrange(0,cnt):
		mat=setC4DMat([getBoxCoord(i,10,10,100),(1,0,0),(0,1,0),(0,0,1)])
		marr.append(mat)
	md.SetArray(c4d.MODATA_MATRIX, marr, True)
	return True
