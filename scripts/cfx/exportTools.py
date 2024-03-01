"""
A Class to make exporting files easier, aimed at our tools
Autho: John Riggs
"""
import maya.cmds as cmds

import cfx.systemSettings as sysSet
import cfx.metaSystem as rmeta


class exportTools(object):
    
    def __init__(self):
        self.__settings = sysSet.sysSettings()
        self.__meta = rmeta.metaSystem()

    def exportAllMeshs(self):
        
        staticMeshes = self.__meta.findMeta(self.__settings.smExport)
        skeletalMeshes = self.__meta.findMeta(self.__settings.skExport)

        if len(staticMeshes) > 0:
            for sme in staticMeshes:
                self.exportStaticMesh(cmds.listConnections(sme+'.meshToExport', s=0, d=1)[0])
                
        if len(skeletalMeshes) > 0:
            for sme in skeletalMeshes:
                self.exportSkeletalMesh(cmds.listConnections(sme+'.meshToExport', s=0, d=1)[0])
                
                        
    def exportStaticMesh(self, meshToExport):
        
        exportDataNode = self.__meta.findMeta(self.__settings.exportData)
        
        objectsToExport = [meshToExport]
        #if no exportData add it and pop open a file dialog to set the directory
        
        self.setDefaultExportSetting()
        cmds.FBXExportSkins("-v", False)
        
        exportSMNode = cmds.listConnections(meshToExport+'.setupData', s=1, d=0)
        print(exportSMNode)
        if cmds.attributeQuery( 'socketsToExport', node=exportSMNode[0], ex=True ):
            objsToAdd = cmds.listConnections(exportSMNode[0]+'.socketsToExport', s=0, d=1)
            for ota in objsToAdd:
                objectsToExport.append(ota)
        
        exportDir = cmds.getAttr(exportDataNode[0]+'.exportDirectory')
        exportName = exportDir+'/'+meshToExport+'.fbx'
        
        if cmds.getAttr(exportSMNode[0]+'.MoveToZero'):
            orig_pos = cmds.xform(meshToExport, query=True, worldSpace=True, translation=True)
            cmds.move(0,0,0,meshToExport, rotatePivotRelative = True)
            
        cmds.select(objectsToExport, r=1)
        
        cmds.FBXExport("-file", exportName, "-s")
        
        cmds.xform(meshToExport, worldSpace=True, translation=orig_pos)
        
    def exportSkeletalMesh(self, meshToExport):
        
        exportDataNode = self.__meta.findMeta(self.__settings.exportData)
        exportSKNode = cmds.listConnections(meshToExport+'.setupData', s=1, d=0)
        
        exportDir = cmds.getAttr(exportDataNode[0]+'.exportDirectory')
        exportName = exportDir+'/'+meshToExport+'.fbx'
        
        skelParent = cmds.listConnections(exportSKNode[0]+'.skeletonToExport', s=0, d=1)
        objectsToExport = cmds.listRelatives(skelParent[0], ad=1 )
        objectsToExport.append(meshToExport)
        #if no exportData add it and pop open a file dialog to set the directory
        
        self.setDefaultExportSetting()
        cmds.FBXExportSkins("-v", True)
        
        cmds.select(objectsToExport, r=1)
        
        cmds.FBXExport("-file", exportName, "-s")
        
    def moveToZeroExport(self, item):
        
        orig_pos = cmds.xform(item, query=True, worldSpace=True, translation=True)
    
        cmds.move(0,0,0,item, rotatePivotRelative = True)
    
        print('Do Export')
    
        cmds.xform(item, worldSpace=True, translation=orig_pos)
        
    def setDefaultExportSetting(self):
        
        #TODO add these to the export node as options
        cmds.FBXExportInAscii("-v", False)
        cmds.FBXExportSmoothingGroups("-v", True)
        cmds.FBXExportSmoothMesh("-v", False)
        cmds.FBXExportTriangulate("-v", False)
        
        