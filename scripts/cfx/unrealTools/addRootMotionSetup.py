import maya.cmds as cmds
import math

import cfx.cfxSettings as rigset
import cfx.controlShapeSystem as css

import cfx.metaSystem as rmeta

class addRootMotionSetup(object):
    
    def __init__(self):

        #modules
        self.__meta = rmeta.metaSystem()
        self.__settings = rigset.rgSettings()

    def doIt(self, namespaced = ''):

        setupDataNode = self.__meta.findMeta(self.__settings.character)

        worldRefNode = namespaced+'worldRef'

        cmds.select(worldRefNode,hi=True)

        #MANUALLY COPPIED IN HERE FOR NOW NEEDS TO BE PYTHONIZED
        controlMaker = css.controlShapeSystem()

        setupGroup = cmds.group(em=True,n='rootMotionSetup')
        rootWSP = cmds.group(em=True,n='rootMotionWorldSpaceParent')
        rootWS = cmds.group(em=True,n='rootMotionWorldSpace')
        rootWSD = cmds.group(em=True,n='rootMotionWorldSpaceDriven')
        rootBSP = cmds.group(em=True,n='rootMotionBodySpaceParent')
        rootBS = cmds.group(em=True,n='rootMotionBodySpace')
        rootBSD = cmds.group(em=True,n='rootMotionBodySpaceDriven')

        cmds.parent(rootWSP,rootBSP, setupGroup)
        cmds.parent(rootBSD, rootBSP)
        cmds.parent(rootWSD, rootWSP)
        cmds.parent(rootBS, rootBSD)
        cmds.parent(rootWS, rootWSD)

        cmds.xform(setupGroup ,ws=True,m=(cmds.xform(worldRefNode,q=True,ws=True,m=True)))

        cmds.setAttr(rootWSP+".inheritsTransform", 0)
        cmds.xform(rootWSP ,ws=True,m=(cmds.xform(worldRefNode,q=True,ws=True,m=True)))

        wsCtrl = controlMaker.makeAndGroupCtrl([rootWS],'pentagon',20.0, ctrlExtension = self.__settings.ctrlExtension)
        cmds.rotate(-90,0,0, wsCtrl[0]+'.cv[*]',os=True)
        bsCtrl = controlMaker.makeAndGroupCtrl([rootBS],'triangleArrow',15.0, ctrlExtension = self.__settings.ctrlExtension)
        cmds.rotate(90,0,0, bsCtrl[0]+'.cv[*]',os=True)
        rootCon = cmds.listConnections(worldRefNode+'.tx',s=1,d=0)
        defaultWeight = cmds.parentConstraint(rootCon,q=1,wal=1)

        #if cmds.lockNode(topTransform, q=1):
            #cmds.lockNode(topTransform, lock = 0)

        #used to be to placement_Grp
        topTransform = cmds.listConnections(setupDataNode[0]+'.topTransform')[0]

        if not cmds.objExists(topTransform+'.defaultRootMotion'):
            cmds.addAttr(topTransform,ln='defaultRootMotion',at="float", min = 0, max = 1, dv = 0)
            cmds.setAttr(topTransform+'.defaultRootMotion', 0, e=True, keyable=True)
        cmds.connectAttr(topTransform+'.defaultRootMotion', rootCon[0]+'.'+defaultWeight[0], f=1)

        cmds.parentConstraint(rootWS,worldRefNode)
        defaultWeight = cmds.parentConstraint(rootCon,q=1,wal=1)
        if not cmds.objExists(topTransform+'.worldSpaceRootMotion'):
            cmds.addAttr(topTransform,ln='worldSpaceRootMotion',at="float", min = 0, max = 1, dv = 1)
            cmds.setAttr(topTransform+'.worldSpaceRootMotion', 0, e=True, keyable=True)
        cmds.connectAttr(topTransform+'.worldSpaceRootMotion', rootCon[0]+'.'+defaultWeight[-1], f=1)

        cmds.parentConstraint(rootBS,worldRefNode)
        defaultWeight = cmds.parentConstraint(rootCon,q=1,wal=1)
        if not cmds.objExists(topTransform+'.BodySpaceRootMotion'):
            cmds.addAttr(topTransform,ln='BodySpaceRootMotion',at="float", min = 0, max = 1, dv = 0)
            cmds.setAttr(topTransform+'.BodySpaceRootMotion', 0, e=True, keyable=True)
        cmds.connectAttr(topTransform+'.BodySpaceRootMotion', rootCon[0]+'.'+defaultWeight[-1], f=1)

        cmds.connectAttr(topTransform+'.worldSpaceRootMotion', wsCtrl[0]+'.v', f=1)
        cmds.connectAttr(topTransform+'.BodySpaceRootMotion', bsCtrl[0]+'.v', f=1)

        cmds.setAttr(""+topTransform+".worldSpaceRootMotion", 1)

        if cmds.objExists('main_Grp'):
            cmds.parent('rootMotionSetup', 'main_Grp')

        if cmds.objExists('rig_Grp'):
            cmds.parent('rootMotionSetup', 'rig_Grp')

        #syncCtrl = controlMaker.makeAndGroupCtrl(['syncNode'],'star',15.0, ctrlExtension = self.__settings.ctrlExtension)
        #cmds.rotate(90,0,0, syncCtrl[0]+'.cv[*]',os=True)

        cmds.rename('rootMotionWorldSpace_CTRL', 'rootMotionWorldSpace_CTRL')
        cmds.rename('rootMotionBodySpace_CTRL', 'rootMotionBodySpace_CTRL')

