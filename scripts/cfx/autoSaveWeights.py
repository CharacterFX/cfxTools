"""
a class to auto save and load skinning weights
Autho: John Riggs
"""

import rgTools.fileUtils as fu
import rtsp.skinningTools as sts

import maya.cmds as cmds
import os

class autoSaveWeights(object):

    def __init__(self):

        self.__skins = []
        self.__defaultExtenaion = '.weights'
        self.__manualCopyfrom = '.weights'
        self.__skinner = sts.skinningTools() 

        self._notSkinned = []

        self.__futil = fu.fileUtils()

    def exportWeights(self,outputDirectory):

        #meshs = cmds.ls(type='mesh')
        skins = cmds.ls(type='skinCluster')

        #for mesh in meshs:
        for sCluster in skins:
            #sCluster = self.__skinner.findRelatedSkinCluster(mesh)
            
            #if sCluster is not None:
            
            #geosTransform = cmds.listConnections(sCluster+'.outputGeometry',s=0,d=1)[0]
            geosTransforms = cmds.skinCluster(sCluster, q=1, g=1)
            #geosTransform = cmds.listRelatives(mesh,p=True)[0]

            for geosTransform in geosTransforms:
                geoType = cmds.objectType(geosTransform)
                geoShape = geosTransform
                if geoType != 'mesh':
                    #geoShape = cmds.listRelatives(geosTransform,s = True)[0]
                    self._notSkinned.append(geosTransform)

                isMesh = cmds.objectType(geoShape)
                if isMesh == 'mesh':
                    shapeParent = cmds.listRelatives(geoShape, p=1)[0]
                    cmds.select(shapeParent,r=True)
                    __name__ = shapeParent+".weights"
                    __path__ = outputDirectory+"/"+__name__
                    #ie.weightsCluster().exportSkin(__path__)
                    cmds.rtspWeights(roundOff=int(4),action="export",quick=0,file=__path__)
 
        if len(self._notSkinned) > 0:
            print("These items were not skinned but attached to a skin cluster: ", self._notSkinned)

    def importWeights(self,inputDirectory, files = [], forcePo = False):

        if len(files) == 0:
            for aFile in os.listdir(inputDirectory):
                if aFile.endswith(".weights"):
                    self.__skins.append(aFile)
                print("Found "+str(len(self.__skins))+ ' skin files')

        else:

            self.__skins = [s + ".weights" for s in files]
            
        for skinFile in self.__skins:

            geometry = skinFile.split(".")[0]

            if cmds.objExists(geometry):
                print("associating object "+geometry+" with skin file "+skinFile)
                
                #try:
                    #ie.weightsCluster(importFunc=False).importSkin(inputDirectory+"/"+skinFile)
                cmds.select(geometry,r=True)

                theWeightsFile = inputDirectory+"/"+skinFile
                #missing = self.returnMissingInfs(inputDirectory+"/"+skinFile)
                theSkin = self.__skinner.findRelatedSkinCluster(geometry)
                if theSkin is not None:
                    infs = self.__futil.returnInfsFromWeightsFile(theWeightsFile)
                    infsInSkin = cmds.skinCluster(theSkin, q=True, inf=True)

                    addToSkin = [x for x in infs if x not in infsInSkin]
                    cmds.skinCluster(geometry, e=True,ub=True)
                #if len(addToSkin) > 0:
                    #for ats in addToSkin:
                        #cmds.skinCluster(theSkin, e=True, ai = ats, wt=0.0)
                #cmds.skinCluster(geometry, e=True,ub=True)# -e  -ub m_drn_senator_shirt_03_GeoShape
                if forcePo:
                    cmds.rtspWeights(action="import",file=theWeightsFile,fp=1)
                else:
                    cmds.rtspWeights(action="import",file=theWeightsFile)
                #except:
                    #self._notSkinned.append(geometry)
                    #pass

            else:
                print("object "+geometry+" does not exist, skipping")

        self.__skins = []
        return self._notSkinned


    def returnMissingInfs(self, theWeightsFile):

        missingInfs = []

        infs = self.__futil.returnInfsFromWeightsFile(theWeightsFile)

        for inf in infs:
            if not cmds.objExists(inf):
                missingInfs.append(inf)

        return missingInfs