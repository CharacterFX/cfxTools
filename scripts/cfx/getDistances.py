'''
A Class for getting distnance data
Author: John Riggs

'''
import cfx.returnCleanChain as rcl

import operator
import maya.cmds as cmds
from maya.OpenMaya import MVector
import maya.OpenMaya as om

import pymel.core as pm

from math import sqrt
import platform

class getDistances(object):

    def __init__(self):
        self.pythonVer = int(platform.python_version().split(".")[0])
        if self.pythonVer > 2:
            self.isPython2 = False
        else:
            self.isPython2 = True

    def fromTo(self, obj1, obj2):

        '''
        Distance from one object to the other using distance node
        @param obj1: First object
        @param obj2: Second object
        '''

        distNode = cmds.createNode("distanceDimShape");
        stp = cmds.xform(obj1,q=True,a=True,ws=True,t=True)
        cmds.setAttr(distNode+".startPointX",stp[0])
        cmds.setAttr(distNode+".startPointY",stp[1])
        cmds.setAttr(distNode+".startPointZ",stp[2])
        
        etp = cmds.xform(obj2,q=True,a=True,ws=True,t=True)
        cmds.setAttr(distNode+".endPointX",etp[0])
        cmds.setAttr(distNode+".endPointY",etp[1])
        cmds.setAttr(distNode+".endPointZ",etp[2])
        
        theDistance = cmds.getAttr(distNode+".distance")
        
        cmds.delete(cmds.listRelatives(distNode,p=True))
        
        return theDistance

    def between(self, obj1, obj2):

        '''
        Distance from one object to the other using math
        @param obj1: First object
        @param obj2: Second object
        '''

        a = cmds.xform(obj1,q=True,t=True,ws=True)
        b = cmds.xform(obj2,q=True,t=True,ws=True)

        return sqrt(sum( (a - b)**2 for a, b in zip(a, b)))

    def chainLength(self, startJoint,endJoint):

        '''
        Distance from the start of a chain to the end along the joints\
        @param startJoint: First joint
        @param endJoint: Second joint
        '''

        cleanChain = rcl.returnCleanChain(startJoint,endJoint)
        cleanChain.reverse()
        
        fullDistance = 0
        count = 0
        
        while count < len(cleanChain)-1:
            oneDist = self.between(cleanChain[count],cleanChain[count+1])
            fullDistance += oneDist
            count += 1
        
        return fullDistance

    def snapTo(self, theObject, geo, direction = (0,1,0) ):

        '''
        Snap to a point on a mesh, from an object along a vector
        @param theObject = the object to test from
        @param geo = the geometry to test for the ray hit 
        @param direction = the direction to shoot the ray
        '''
        mpDirection = om.MFloatVector(direction[0], direction[1], direction[2])

        tempLoc = cmds.spaceLocator(n='DELETEME')[0]

        cmds.xform(tempLoc ,ws=True,m=(cmds.xform(theObject,q=True,ws=True,m=True)))

        sel = om.MSelectionList()
        sel.add(tempLoc)
        sel.add(geo)

        dagPathToObject = om.MDagPath()
        sel.getDagPath( 0, dagPathToObject )

        dagPathToMesh = om.MDagPath()
        sel.getDagPath( 1, dagPathToMesh )

        # make sure the path is to the shape node (not the transform)
        dagPathToMesh.extendToShape()

        # finally create the mesh function set
        planeMesh = om.MFnMesh( dagPathToMesh )
        rayDirection = om.MFloatVector(mpDirection)
        currentLc = om.MFnTransform(dagPathToObject.transform())
        raySourceV = currentLc.translation(om.MSpace.kTransform)
        hitPoint = om.MFloatPoint()
        raySource = om.MFloatPoint(raySourceV.x, raySourceV.y, raySourceV.z)

        hit = planeMesh.closestIntersection (
        raySource, #const  MFloatPoint & raySource
        rayDirection, #const  MFloatVector & rayDirection
        None, #const  MIntArray * faceIds
        None, #const  MIntArray * triIds
        False, #bool idsSorted
        om.MSpace.kWorld, #MSpace::Space  space
        1000, #float maxParam
        False, #bool testBothDirections
        None, #MMeshIsectAccelParams *accelParams
        hitPoint, #MFloatPoint & hitPoint
        None, #float* hitRayParam
        None, #int* hitFace
        None, #int* hitTriangle
        None, #float* hitBary1
        None #float* hitBary2
        # float tolerance,
        # MStatus * ReturnStatus
        )
        hitPointV = om.MVector(hitPoint.x, hitPoint.y, hitPoint.z)

        cmds.delete(tempLoc)

        return hitPointV

    def center(self, object1, object2):

        '''
        finds the center of two objects
        @param object1 = the first object
        @param object2 = the second object
        '''
        obj1Ws = cmds.xform(object1,q=True,a=True,ws=True,t=True)
        obj2Ws = cmds.xform(object2,q=True,a=True,ws=True,t=True)
        #print obj1Ws, obj2Ws

        centerPos = [((obj1Ws[0] + obj2Ws[0])/2), ((obj1Ws[1] + obj2Ws[1])/2), ((obj1Ws[2] + obj2Ws[2])/2)]
        return centerPos

        """
        tempLoc = cmds.spaceLocator(n='DELETEME')[0]

        cmds.delete(cmds.pointConstraint(object1,object2,tempLoc))
        cmds.delete(cmds.orientConstraint(object1,object2,tempLoc))
        cmds.delete(cmds.scaleConstraint(object1,object2,tempLoc))

        returnDataT = cmds.xform(tempLoc,q=True,a=True,ws=True,t=True)
        returnDataR = cmds.xform(tempLoc,q=True,a=True,ws=True,ro=True)
        returnDataS = cmds.xform(tempLoc,q=True,a=True,ws=True,s=True)

        cmds.delete(tempLoc)
        """

        #return [returnDataT,returnDataR,returnDataS]

    #types are transform, vert, joint
    def closestItem(self, theObject, fromList):#, theType = '', fromList = []):

        '''
        find the closest item from a list of items
        #param theObject = the object to test from
        @param fromList[] = a list of objects to test

        sortedItems[0][0] is closest item
        '''

        itemsDict = {}
        #allItems = []

        #if theType != '':
            #allItems = cmds.ls(type = theType)

        #if len(fromList) != 0:
            #allItems = list(set(allItems).intersection(fromList))
            
        for item in fromList:
            itemsDict[item] = self.between(theObject, item)

        if self.isPython2:
            sortedItems = sorted(itemsDict.iteritems(), key=operator.itemgetter(1))
        else:
            sortedItems = sorted(itemsDict.items(), key=operator.itemgetter(1))

        return sortedItems

    def getClosestVert(self, testVert, allVerts):

        ''' 
        return the list of verts sorted from closest to farthest
        @param theVert = the vert to test
        @param allVerts[] = the list of verts to get distanced from
        '''
        
        itemsDict = {}

        for item in allVerts:
            itemsDict[item] = self.fromTo(testVert, item)

        sortedItems = sorted(itemsDict.iteritems(), key=operator.itemgetter(1))

        return sortedItems


    def getClosestVertApi(self, testVert, theMesh): 

        previouslySelected = cmds.ls(sl=1)

        geo = pm.PyNode(theMesh)
        #loc = pm.PyNode('locator1')
        #pos = loc.getRotatePivot(space='world')

        pos = cmds.xform(testVert, q=1,ws=1,t=1)
         
        nodeDagPath = om.MObject()
        try:
            selectionList = om.MSelectionList()
            selectionList.add(geo.name())
            nodeDagPath = om.MDagPath()
            selectionList.getDagPath(0, nodeDagPath)
        except:
            raise RuntimeError('om.MDagPath() failed on %s' % geo.name())
         
        mfnMesh = om.MFnMesh(nodeDagPath)
         
        pointA = om.MPoint(pos[0], pos[1], pos[2])
        pointB = om.MPoint()
        space = om.MSpace.kWorld
         
        util = om.MScriptUtil()
        util.createFromInt(0)
        idPointer = util.asIntPtr()
         
        mfnMesh.getClosestPoint(pointA, pointB, space, idPointer)  
        idx = om.MScriptUtil(idPointer).asInt()
         
        faceVerts = [geo.vtx[i] for i in geo.f[idx].getVertices()]
        closestVert = None
        minLength = None
        for v in faceVerts:
            thisLength = (pos - v.getPosition(space='world')).length()
            if minLength is None or thisLength < minLength:
                minLength = thisLength
                closestVert = v
        pm.select(closestVert)
        returnVert = cmds.ls(sl=1)[0]

        if len(previouslySelected) == 0:
            cmds.select(clear = True)
        else:
            cmds.select(previouslySelected,r=1)
            
        return returnVert

    def returnPointAlongVector(self, startObjectPos, finishObjectPos, offset):

        V1 = om.MVector(startObjectPos[0],startObjectPos[1],startObjectPos[2])
        V2 = om.MVector(finishObjectPos[0],finishObjectPos[1],finishObjectPos[2])
        V3 = (V2 - V1).normal()
        V4 = V1 + V3 * offset

        return(V4.x,V4.y,V4.z) 

    def returnPointAlongVectorObjects(self, startObject, finishObject, offset):

        startPos = cmds.xform(startObject,q=1,ws=1,t=1)
        finishPos = cmds.xform(finishObject,q=1,ws=1,t=1)
        V4 = self.returnPointAlongVector(startPos, finishPos, offset)

        return(V4[0],V4[1],V4[2]) 