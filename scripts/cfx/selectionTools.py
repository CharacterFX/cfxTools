"""
A Class for selecting geometry
Author: John Riggs
"""


import maya.cmds as cmds 
import maya.mel as mel
import maya.OpenMaya as om

class selectionTools(object):
    
    def __init__(self):

        initIt = 1     
    
    def selectPolygonShell(self):
        '''
        selects all faces of a shell
        '''
        sel = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(sel)
        dag = om.MDagPath()
        obj = om.MObject()
        sel.getDagPath(0, dag, obj)

        itr = om.MItMeshPolygon(dag, obj)
        # Firstly add all faces of the selection to the array
        currfaces = om.MIntArray()
        while not itr.isDone():
            currfaces.append(itr.index())
            itr.next()

        currfaces = list(currfaces)
        cmds.polySelect(dag.fullPathName(), extendToShell = currfaces, add=True)

    def selectVertexShell(self,vertex):
        '''
        selects a geometry shell based on a vertex
        @param vertex: a vertex that belongs to the shell
        '''
        polys = cmds.polyListComponentConversion( vertex, fv=True, tf=True)
        cmds.select(polys,r=True)
        self.selectPolygonShell()

        polys = cmds.polyListComponentConversion( vertex, tv=True, ff=True)

    def printAsArray(self, arrayName):

        selected = cmds.ls(sl=1, fl=1)

        returnString = arrayName+' = ['

        for sel in selected:
            returnString = returnString+'\"'+sel+'\", '

        print(returnString)
        returnString = returnString[:-2]

        returnString = returnString+']'

        return returnString