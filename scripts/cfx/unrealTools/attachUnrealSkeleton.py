import cfx.getDistances as gd
import cfx.insertBufferGroup as ibg
import cfx.dynamicPOconstraint as dpo 
import cfx.addOrMakeGroup as aomg 
import cfx.returnObjectWithAttr as roa
import cfx.rigSettings as rigset

import maya.cmds as cmds

import cfx.metaSystem as rmeta
import cfx.fileUtils as fu

class attachUnrealSkeleton(object):

    def __init__(self):
        self.__settings = rigset.rigSettings()
        self.__meta = rmeta.metaSystem()
        self.__distance = gd.getDistances()
        self.__attrFinder = roa.returnObjectWithAttr()
        self.__fileUtils = fu.fileUtils()

    #the first in objects must be the root object
    def doIt(self, theSkeleton):

        setupDataNode = self.__meta.findMeta(self.__settings.character)

        if len(setupDataNode) == 0:
            setupDataNode = self.__meta.findMeta(self.__settings.weapon)
            if len(setupDataNode) == 0:
                cmds.error('Needs a meta system to work')
        
        setupDataNode = setupDataNode[0]

        topTransform = cmds.listConnections(setupDataNode+'.topTransform', s=0, d=1)[0]

        if not cmds.objExists(topTransform+'.'+self.__settings.deformationSkelVis):
            cmds.addAttr(topTransform,ln=self.__settings.deformationSkelVis,at="double", min=0, max=1, dv = 0)
            cmds.setAttr(topTransform+'.'+self.__settings.deformationSkelVis, 0, e = True, keyable = True, cb = True)

        if not cmds.objExists(topTransform+'.'+self.__settings.deformationSkelTemplate):
            cmds.addAttr(topTransform,ln=self.__settings.deformationSkelTemplate,at="double", min=0, max=2, dv = 2)
            cmds.setAttr(topTransform+'.'+self.__settings.deformationSkelTemplate, 2, e = True, keyable = True, cb = True)

        cmds.file(theSkeleton, i=True, ns = self.__settings.unrealJointNS, f=True)

        engineSetupData = self.__meta.findMeta('engine')
        if len(engineSetupData) == 0:
            cmds.error('Needs to be built with meta system and have joints attached to the main meta')
        engineSetupData = engineSetupData[0]

        allJoints = cmds.listConnections(engineSetupData+'.'+self.__settings.allJoints, s=0, d=1)

        defGeo = cmds.listConnections(engineSetupData+'.'+self.__settings.deformerGeometry, s=0, d=1)

        if len(defGeo) > 0:
            for dg in defGeo:
                dgShape = cmds.listRelatives(dg, shapes=1)[0]
                cmds.setAttr(dgShape+'.overrideEnabled', 1)
                cmds.connectAttr(topTransform+'.'+self.__settings.deformationSkelTemplate, dgShape+'.overrideDisplayType', f=1)
                cmds.connectAttr(topTransform+'.'+self.__settings.proxyRig, dg+'.v', f=1)

        for aj in allJoints:
            cmds.setAttr(aj+'.overrideEnabled', 1)
            cmds.connectAttr(topTransform+'.'+self.__settings.deformationSkelTemplate, aj+'.overrideDisplayType', f=1)

            if not cmds.objExists(aj+'.'+self.__settings.unrealJoint):
                newJoint= 'same'
            else:
                newJoint = cmds.getAttr( aj+'.'+self.__settings.unrealJoint)

            if newJoint == 'same' or newJoint == '':
                if cmds.objExists(aj.split(':')[-1]):
                    cmds.parentConstraint(aj.split(':')[-1], aj, mo=0)
                    cmds.scaleConstraint(aj.split(':')[-1], aj, mo=0)

            else:
                if cmds.objExists(newJoint):
                    cmds.parentConstraint(newJoint,aj, mo=0)
                    cmds.scaleConstraint(newJoint,aj, mo=0)

        if cmds.objExists(topTransform+'.'+self.__settings.deformationSkelVis):
            if cmds.objExists(engineSetupData+'.'+self.__settings.deformerRootJoint):
                rootJoint = cmds.listConnections(engineSetupData+'.'+self.__settings.deformerRootJoint, s=0, d=1)
                cmds.connectAttr(topTransform+'.'+self.__settings.deformationSkelVis, rootJoint[0]+'.v')

        if cmds.objExists(topTransform+'.'+self.__settings.deformationSkelTemplate):
            if cmds.objExists(engineSetupData+'.'+self.__settings.deformerGeometry):
                geoGroup = cmds.listConnections(engineSetupData+'.'+self.__settings.deformerGeometry, s=0, d=1)
                for geo in geoGroup:
                    cmds.setAttr(geo+".overrideEnabled", 1)

                    #commented out cause its erroring out for demo
                    #cmds.connectAttr(topTransform+'.'+self.__settings.deformationSkelTemplate, geo+'.overrideDisplayType')
                
                cmds.setAttr(topTransform+'.'+self.__settings.deformationSkelTemplate, 2)

        #need to automate this
        if cmds.objExists('hand_l'):
            cmds.parentConstraint('hand_l', 'UJ:ik_hand_l', mo=0)
        if cmds.objExists('hand_r'):
            cmds.parentConstraint('hand_r', 'UJ:ik_hand_gun', mo=0)
        if cmds.objExists('hand_l'):
            cmds.parentConstraint('hand_l', 'UJ:ik_hand_l', mo=0)
        if cmds.objExists('hand_r'):
            cmds.parentConstraint('hand_r', 'UJ:ik_hand_r', mo=0)
        
    def updateToNewestEngineVersion(self, directory):

        allAttached = []
        MetaNode = self.__meta.findMeta('engine')
        for mn in MetaNode:
            userAttrs = cmds.listAttr(mn, ud=1)
            for attr in userAttrs:
                objects = cmds.listConnections(mn+'.'+attr, s=0, d=1)
                if objects:
                    for obj in objects:
                        allAttached.append(obj)
            cmds.delete(mn)

        if len(allAttached) > 0:
            cmds.delete(allAttached)
            
        #brute force right now to make sure
        allInNS = cmds.ls('UJ:*')
        if len(allInNS) > 0:
            for ans in allInNS:
                if cmds.objExists(ans):
                    cmds.delete(ans)

        if cmds.namespace( exists='UJ' ):
            cmds.namespace(rm = 'UJ', f=1)

        currentEnginenFile = self.__fileUtils.returnNewestVersion(directory, ['mb','ma'])
        print('currentEnginenFile: ', currentEnginenFile)
        if currentEnginenFile:
            self.doIt(directory+'/'+currentEnginenFile)