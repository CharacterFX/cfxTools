"""
a class to manage scenes
Author: John Riggs
"""
import cfx.fileUtils as fu
import cfx.metaSystem as rmeta
#import dar.darSettings as darSet
import cfx.systemSettings as sysSet

import maya.cmds as cmds
import maya.mel as mel

import xml.dom.minidom as xd
import logging
from maya.app.renderSetup.views.renderSetupPreferences import _exportNodesOfGivenType

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class sceneTools(object):
    
    def __init__(self):

        #self.__settings = darSet.darSettings()
        self.__settings = sysSet.sysSettings()
        self.__futil = fu.fileUtils()
        self.__meta = rmeta.metaSystem()

    def createSceneNode(self):
        '''
        creates a scene master node
        '''
        return self.__meta.addMetaNode(name = self.__settings.sceneMaster+'Node', system = self.__settings.sceneMaster)[0]

    def createExportNode(self):
        '''
        creates a scene export node
        '''
        exportNode = self.__meta.addMetaNode(name = self.__settings.exportData+'Node', system = self.__settings.exportData)[0]
        cmds.addAttr(exportNode, ln= 'exportDirectory', dt="string")
        cmds.setAttr(exportNode+'.exportDirectory', '', type="string")

        return exportNode

    def addActorToScene(self, actorFile):

        existingActors = self.__meta.findMeta(self.__settings.actors)
        print("add actor")
        sceneMasterNode = self.__meta.findMeta(self.__settings.sceneMaster)
        if len(sceneMasterNode) != 1:
            if len(sceneMasterNode) == 0:
                self.createSceneNode()
            else:
                cmds.error('More than one sceneMaster node exists, please delete all but one ', sceneMasterNode)
        else:
            sceneMasterNode = sceneMasterNode[0]

        self.__meta.connectToSystem(sceneMasterNode,actorMetaNode, self.__settings.secondaryMocapBake, objectAttr = self.__settings.mocapBake )

    #adds a static mesh export node with all necesary data
    def addStaticMeshExport(self, nodesToConnect, socketsToExport = None):

        exportNode = self.__meta.findMeta(self.__settings.exportData)
        if len(exportNode) == 0:
            exportNode = self.createExportNode()
        else:
            exportNode = exportNode[0]

        if not isinstance(nodesToConnect, list):
            nodesToConnect = [nodesToConnect]

        if socketsToExport:
            if not isinstance(socketsToExport, list):
                socketsToExport = [socketsToExport]
            
        for ntc in nodesToConnect:
            smExportNode = self.__meta.addMetaNode(name = self.__settings.smExport+'Node', system = self.__settings.smExport)[0]
            self.__meta.connectToSystem(smExportNode,ntc, 'meshToExport' )

            self.__meta.connectToSystem(exportNode,smExportNode, self.__settings.smExport+'Nodes', objectAttr = self.__settings.exportData )

            cmds.addAttr(smExportNode, ln = 'MoveToZero', at='bool')
            cmds.setAttr(smExportNode+'.MoveToZero', 1, e = True, keyable = True)

            cmds.addAttr(smExportNode, ln = 'freezeTransform', at='bool')
            cmds.setAttr(smExportNode+'.freezeTransform', 1, e = True, keyable = True)

            cmds.addAttr(smExportNode, ln = 'freezeRotation', at='bool')
            cmds.setAttr(smExportNode+'.freezeRotation', 0, e = True, keyable = True)

            cmds.addAttr(smExportNode, ln = 'freezeScale', at='bool')
            cmds.setAttr(smExportNode+'.freezeScale', 1, e = True, keyable = True)

            cmds.addAttr(smExportNode, ln= 'exportDirectory', dt="string")
            cmds.setAttr(smExportNode+'.exportDirectory', '', type="string")

            cmds.addAttr(smExportNode, ln= 'changeName', dt="string")
            cmds.setAttr(smExportNode+'.changeName', '', type="string")

        if socketsToExport:
            for ste in socketsToExport:
                self.__meta.connectToSystem(smExportNode,ste, 'socketsToExport' )
                
    #adds a skeletal mesh export node with all necesary data
    def addSkeletalMeshExport(self, nodesToConnect):

        exportNode = self.__meta.findMeta(self.__settings.exportData)
        if len(exportNode) == 0:
            exportNode = self.createExportNode()
        else:
            exportNode = exportNode[0]

        smExportNode = self.__meta.addMetaNode(name = self.__settings.skExport+'Node', system = self.__settings.skExport)[0]

        self.__meta.connectToSystem(exportNode,smExportNode, self.__settings.skExport+'Nodes', objectAttr = self.__settings.exportData )

        cmds.addAttr(smExportNode, ln= 'exportDirectory', dt="string")
        cmds.setAttr(smExportNode+'.exportDirectory', '', type="string")

        cmds.addAttr(smExportNode, ln= 'changeName', dt="string")
        cmds.setAttr(smExportNode+'.changeName', '', type="string")

        if not isinstance(nodesToConnect, list):
            nodesToConnect = [nodesToConnect]
        for ntc in nodesToConnect:
            if cmds.objectType(ntc) == 'transform':
                self.__meta.connectToSystem(smExportNode,ntc, 'meshToExport')
            if cmds.objectType(ntc) == 'joint':
                self.__meta.connectToSystem(smExportNode,ntc, 'skeletonToExport')
    
    #adds locators to export node for socket export          
    def addSocketsToStaticMeshExport(self, socketsToAdd, exportNode):

        if not isinstance(socketsToAdd, list):
            socketsToAdd = [socketsToAdd]
            
        for sta in socketsToAdd:
            self.__meta.connectToSystem(exportNode,sta, 'socketsToExport')