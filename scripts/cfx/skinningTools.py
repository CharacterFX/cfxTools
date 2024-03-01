"""
A class to consolidate the various skinning tools
Author: John Riggs
"""

import cfx.selectionTools as selT
import cfx.getDistances as gd
import maya.OpenMaya as om
import maya.cmds as cmds

import math
import operator

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class skinningTools(object):

    def __init__(self):

        self.__selTool = selT.selectionTools()
        self.__distance = gd.getDistances()

        self.__vertWeights = dict()
        self.__infWeights = []
        self.__weightsDictionary = dict()

    def returnInfsFromVerts(self, verts):
        '''
        get which influences are affecting the verts
        @param verts: all verts to test
        '''

        if not isinstance(verts, list):
            verts = [verts]

        theObject = verts[0].rpartition('.')[0]

        skinCluster = self.findRelatedSkinCluster(theObject)

        return cmds.skinPercent(skinCluster,verts, q=True, t = None, ib = 0.000000000001 )

    def returnVertsFromInf(self, sourceInf, theObject):
        '''
        get which verts are being affected by the influences
        @param sourceInf: the influence to get info on
        @param theObject: the skinned object to test
        '''

        previouslySelected = cmds.ls(sl=True)

        cmds.select(theObject+'.vtx[*]')
        verts = cmds.ls(sl=True,fl=True)

        theSkin = self.findRelatedSkinCluster(theObject)

        returnVerts = []
        for vert in verts:
            transAvalue = cmds.skinPercent(theSkin,vert,t=sourceInf,q=True,v=True)
            if transAvalue > 0.0:
                returnVerts.append(vert)

        cmds.select(previouslySelected,r=True)

        return returnVerts

    def setVertInfluenceValue(self, verts, influences, theValue):
        '''
        brute force set an influences value
        @param verts: the verts to set a value on
        @param influences: the infs to set values for
        @param theValue: the value to set
        '''

        if not isinstance(verts, list):
            verts = [verts]

        theObject = verts[0].rpartition('.')[0]

        skinCluster = self.findRelatedSkinCluster(theObject)

        if not isinstance(influences, list):
            influences = [influences]

        for inf in influences:
            cmds.skinPercent(skinCluster,verts, tv = (inf, theValue) )


    def normalizeWeightsReplaceDict(self,valuesDict):
        '''
        this will normalize the values in a dictionary, destroying the original values
        '''
        factor=1.0/math.fsum(valuesDict.itervalues())
        for k in valuesDict:
            valuesDict[k] = valuesDict[k]*factor
        key_for_max = max(valuesDict.iteritems(), key=operator.itemgetter(1))[0]
        diff = 1.0 - math.fsum(valuesDict.itervalues())

        valuesDict[key_for_max] += diff

    def findRelatedSkinCluster(self, theObject):
        '''
        find the skin cluster deforming the mesh, there are other ways to do this
        @param theObject: skinned objet
        '''

        skinClusters = cmds.ls( typ='skinCluster')

        objType = cmds.objectType(theObject)
        if objType == 'transform':
            theObject = cmds.listRelatives(theObject,s=True)

        for skin in skinClusters:
            geoClusters = cmds.skinCluster(skin,q=True,g=True)
            doTest = True
            if geoClusters is None:
                doTest = False
            if doTest:
                for g in geoClusters:
                    if g in theObject:
                        return skin


    def isSkinned(self, theShape):
        '''
        is the shape skinned? This only returns true for shapes that are skinned, not shapes that feed into a skin cluster like a "ShapeOrig"
        @param theShape: shape to test
        '''
        if cmds.objectType(theShape) != 'mesh':
            cmds.error('need to test on a shape, not a transform')

        theSkin = self.findRelatedSkinCluster(theShape)

        if theSkin is None:
            return False

        else:
            connections = cmds.listConnections(theSkin+'.outputGeometry',shapes=True)
            if theShape in connections:
                return True
            else:
                return False

    def copyVertWeightToShell(self, vertex):
        '''
        This takes the weights from the vertex and coppies its weight to the shell of that geometry.
        That means that it can be one object, with different contrinuous sections.
        @param vertex: the vertex to copy from
        '''
        theSkin = self.findRelatedSkinCluster(vertex.split('.')[0])

        infs = self.returnInfsFromVerts(vertex)

        for inf in infs:
            weightSet = (inf,cmds.skinPercent(theSkin,vertex,query=True,t=inf))
            self.__infWeights.append(weightSet)

        self.__selTool.selectVertexShell(vertex)
        cmds.skinPercent( theSkin,transformValue=self.__infWeights )

        self.__infWeights = []


    def copyAddWeights(self,inf,weight,aDict):
        '''
        this just inserts the influences weight value into a dictionary or adds the values if its already in there.
        @param inf: the influence
        @param weight: the weight value
        @param aDict: the dictionary
        '''
        if not inf in aDict:
            aDict[inf] = weight
            
        else:
            aDict[inf] = aDict.get(inf)+weight

    def convertWeightDictToList(self,weightsDict):
        '''
        converts the dictionary to a list for use
        '''
        returnList = []
        for key, value in weightsDict.items():
            temp = (key,value)
            returnList.append(temp)

        return returnList

    
    def transferWeights(self, sourceInf, destinationInf, theObject):
        '''
        transfers the weights from one influence to another
        @param sourceInf: the source influence
        @param destinationInf: the destination influence
        @param theObject: the skinned object
        to do: add a way to transfer just a percentage of weight
        '''

        theSkin = self.findRelatedSkinCluster(theObject)
        infs = cmds.skinCluster(theSkin, q=1, weightedInfluence=1)

        if sourceInf not in infs:
            self.addInfluence(sourceInf,theObject)

        if destinationInf not in infs:
            #cmds.skinCluster(theSkin, e=True, ai = destinationInf, wt=0.0)
            self.addInfluence(destinationInf,theObject)

        selected = cmds.ls(sl=True, fl=True)

        if len(selected) > 0:
            if cmds.objectType(selected[0]) == 'mesh':
                if len(selected) > 1:
                    self.verts = selected
        else:
            self.verts = self.returnVertsFromInf(sourceInf,theObject)

        for vert in self.verts:
            transAvalue = cmds.skinPercent(theSkin,vert,t=sourceInf,q=True,v=True)
            if transAvalue > 0.0:
                cmds.skinPercent(theSkin, vert,tv=[sourceInf,0.0])
                cmds.skinPercent(theSkin, vert,r=True, tv=[destinationInf,transAvalue])
                
        cmds.skinPercent( theSkin, theObject, pruneWeights=0.0001 )

    def removeUnusedInfluences(self, theObject):
        '''
        remove influences with zero weight
        @param theObject: skinned mesh to have infs removed that are not used
        '''
        theSkin = self.findRelatedSkinCluster(theObject)
        infs = cmds.skinCluster(theSkin, q=1, weightedInfluence=1)

        nodeState = cmds.getAttr(theSkin+".nodeState")
        cmds.setAttr(theSkin+".nodeState", 1)

        previouslySelected = cmds.ls(sl=True)

        infls = cmds.skinCluster(theSkin, q=True, inf=True)
        wtinfs = cmds.skinCluster(theSkin, q=True, wi=True)

        zeroJoints = [x for x in infls if x not in wtinfs]

        if len(zeroJoints) > 0:
            for zinf in zeroJoints:
                cmds.skinCluster(theSkin, e=True, ri=zinf)
        
        cmds.select(previouslySelected,r=True)
        cmds.setAttr(theSkin+".nodeState", nodeState)

        log.info('removed influences \n%s' % zeroJoints)

    def addInfluence(self, infs, theObject):
        '''
        add influence to mesh with 0 weights, support 
        @param infs: influences to add to skin
        @param theObject: the skinned object to use the infs
        '''

        if not isinstance(infs, list):
            infs = [infs]

        for inf in infs:
            cmds.skinCluster(self.findRelatedSkinCluster(theObject),edit=True,lw=True, weight = 0.0, ai=inf)
            cmds.setAttr(inf+'.liw', 0)

    def matchSkinning(self, fromObject, toObject):

        if not isinstance(toObject, list):
            toObject = [toObject]

        newSkins = []

        for aObj in toObject:
            previousSelection = cmds.ls(sl=True)
            infs = self.getInfluences(fromObject)
            cmds.select(infs,r=True)
            cmds.select(aObj,tgl=True)
            newSkin = cmds.skinCluster(tsb=True, dr=10.0)

            fromCluster = self.findRelatedSkinCluster(fromObject)
            toCluster = self.findRelatedSkinCluster(aObj)
            
            skinngType = cmds.getAttr(fromCluster+".skinningMethod")

            cmds.setAttr(toCluster+".skinningMethod", skinngType)
            
            cmds.copySkinWeights(ss= fromCluster , ds=toCluster, noMirror = True, sa='closestPoint', influenceAssociation = ['name', 'oneToOne'])

            if len(previousSelection) != 0:
                cmds.select(previousSelection,r=True)

            newSkins.append(newSkin[0])

        return newSkins


    def getInfluences(self, theObject):

        skinClust = self.findRelatedSkinCluster(theObject)
        infs = cmds.skinCluster(skinClust,q=True,inf=True)
        
        return infs

    def transferMayaWeights(self, fromObject, toObject):

        previousSelection = cmds.ls(sl=True)
        infs = self.getInfluences(fromObject)
        cmds.select(infs,r=True)
        cmds.select(toObject,tgl=True)
        newSkin = cmds.skinCluster(tsb=True, dr=10.0)

        fromCluster = self.findRelatedSkinCluster(fromObject)
        toCluster = self.findRelatedSkinCluster(toObject)
        
        skinngType = cmds.getAttr(fromCluster+".skinningMethod")

        cmds.setAttr(toCluster+".skinningMethod", skinngType)
        
        cmds.copySkinWeights(ss= fromCluster , ds=toCluster, noMirror = True, sa='closestPoint', influenceAssociation = ['name', 'oneToOne'])

        if len(previousSelection) != 0:
            cmds.select(previousSelection,r=True)

        return newSkin

    def autoSkin(self, fileVar, geoVar):
            
        cmds.select(all=True,hi=True)
        meshs = cmds.ls(sl=True,type='mesh')

        if not cmds.optionVar(exists = fileVar):
            cmds.error('Need to set the file location in the settings gui')
            
        skinFile = cmds.optionVar(q = fileVar)
        cmds.file( skinFile, i=True,f=True)
        
        if not cmds.optionVar(exists = geoVar):
            cmds.error('Need to set the skin copy geo in the settings gui')
            
        transferMesh = cmds.optionVar(q = geoVar)
        
        if not cmds.objExists(transferMesh):
            cmds.error('Object to copy skinning from does not exist in scene')
            
        transferMesh = cmds.optionVar(q = geoVar)
            
        for mesh in meshs:
            self.transferMayaWeights(transferMesh,mesh)

    def returnVertsWithMaxInfs(self, mesh, maxNumber, tollerance = 0.001):

        vertCount=cmds.polyEvaluate( mesh , v=True)
        skinClust = self.findRelatedSkinCluster(mesh)

        overVerts = [v for v in xrange(vertCount) if len(cmds.skinPercent(skinClust, '%s.vtx[%i]' % (mesh, v), query=True, value=True, ib = tollerance)) > maxNumber]

        returnVerts = []

        for ov in overVerts:
            returnVerts.append(mesh+'.vtx['+str(ov)+']')

        return returnVerts

    def copyVertexWeights(self, verts):

        if len(verts) == 0 or cmds.objectType(verts[0]) != 'mesh':
            cmds.error('please select at least one vertex to copy weights from')

        for vert in verts:
            for inf in self.returnInfsFromVerts(vert) : 

                theSkin = self.findRelatedSkinCluster(vert.rpartition('.')[0])
                self.copyAddWeights(inf, cmds.skinPercent(theSkin, vert, t = inf, query=True, value=True), self.__weightsDictionary)

        return self.__weightsDictionary

    def pasteVertexWeights(self, verts):

        if len(self.__weightsDictionary) == 0:
            cmds.error('no weights in buffer, please copy some')

        if len(verts) == 0 or cmds.objectType(verts[0]) != 'mesh':
            cmds.error('please select at least one vertex to paste weights to')

        theSkin = self.findRelatedSkinCluster(verts[0].rpartition('.')[0])
        cmds.select(verts, r = True)
        cmds.skinPercent( theSkin,transformValue= self.convertWeightDictToList(self.__weightsDictionary), normalize = True)


    def transferFromMultiMesh(self, multiMesh, destinationMesh):

        #destinationVerts = cmds.ls(destinationMesh+'.vtx[*]', fl=1)

        allInfs = []
        for mesh in multiMesh:
            infs = self.getInfluences(mesh)
            for inf in infs:
                if inf not in allInfs:
                    allInfs.append(inf)

        cmds.select(allInfs,r=True)
        cmds.select(destinationMesh,tgl=True)
        newSkin = cmds.skinCluster(tsb=True, dr=10.0)

        """
        # prepare a zero array weight list to zero out all skin weights
        for i in xrange(0,len(infNameList),1):
            self.__indArrayUndo.append(i)
            weights.append(0)
            

        #zero out all the weights to supress error message
        self.__skinClusterNode.setWeights(self.__dagPathGeo,self.__allVert,self.__indArrayUndo,weights,False,self.__unDoWeights)
        weights.clear()
        self.__indArrayImport.clear()
        """
        
        for mesh in multiMesh:
            verts = cmds.ls(mesh+'.vtx[*]', fl=1)
            for vert in verts:
                closestVert = self.__distance.getClosestVertApi(vert,destinationMesh)

                self.copyVertexWeights([vert])
                self.pasteVertexWeights([closestVert])