import cfx.skinningTools as sts
    
import maya.cmds as cmds

class vertexTools(object):
    
    def __init__(self):

        self.__skinner = sts.skinningTools()

        self.__infColor1 = (0.0,1.0,0.0)
        self.__infColor2 = (0.0,0.75,0.0)
        self.__infColor3 = (0.0,0.5,0.5)
        self.__infColor4 = (0.0,0.25,0.75)
        self.__infColor5 = (0.0,0.0,1.0)
        self.__infColor6 = (0.25,0.0,0.5)
        self.__infColor7 = (0.75,0.25,0.0)
        self.__infColor8 = (1.0,0.0,0.0)
        self.__infColor9 = (0.0,0.0,0.0)

    def colorVertexByInfluences(self, theMesh):
        
        cmds.select(theMesh+'.vtx[*]')
        verts = cmds.ls(sl=True,fl=True)
        
        for vert in verts:
            infs = self.__skinner.returnInfsFromVerts(vert)

            if len(infs) ==  1:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor1)
                print(1)
                
            elif len(infs) >=  2:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor2)
                print(2)
                
            elif len(infs) >=  3:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor3)
                print(3)
                
            elif len(infs) >=  4:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor4)
                print(4)
                
            elif len(infs) >=  5:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor5)
                print(5)
                
            elif len(infs) >=  6:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor6)
                print(6)
                
            elif len(infs) >=  7:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor7)
                print(7)
                
            elif len(infs) >=  8:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor8)
                print(8)
                
            elif len(infs) >=  9:
                cmds.polyColorPerVertex(vert, rgb=self.__infColor9)
                print(9)

    def selectWithInfsEqualing(self, theMesh, number):
        
        currentSelection = cmds.ls(sl=True)

        cmds.select(theMesh+'.vtx[*]')
        verts = cmds.ls(sl=True,fl=True)
        
        vertsWithInfs = []
        
        for vert in verts:
            infs = self.__skinner.returnInfsFromVerts(vert)

            if len(infs) >  number-1:
                vertsWithInfs.append(vert)
                
            if len(vertsWithInfs) != 0:
                cmds.select(vertsWithInfs,r=True)

    def returnInfsWithMoreWeights(self, theMesh, number):
        
        currentSelection = cmds.ls(sl=True)

        cmds.select(theMesh+'.vtx[*]')
        verts = cmds.ls(sl=True,fl=True)
        cmds.select(currentSelection)

        vertsWithInfs = []
        
        for vert in verts:
            infs = self.__skinner.returnInfsFromVerts(vert)

            if len(infs) >  number-1:
                vertsWithInfs.append(vert)

        return(vertsWithInfs)