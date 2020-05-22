import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import cfx.returnObjectWithAttr as roa
import cfx.anim.ikFkSwitcher as ikfks
import cfx.metaSystem as rmeta

import glob
import os

reload(ikfks)

class simpleAnimRigBake(object):
    
    def __init__(self):
        
        self.__theNameSpace = 'anim'

        self.__allCtrls = ['rootMotionWorldSpace_CTRL', 'rootMotionBodySpace_CTRL', 'thumb_MC_r_CTRL', 'thumb_01_r_CTRL', 'thumb_02_r_CTRL', 'ring_01_r_CTRL', 'pinky_03_r_CTRL', 'pinky_02_r_CTRL', 'ring_03_r_CTRL', 'ring_02_r_CTRL', 'index_03_r_CTRL', 'index_02_r_CTRL', 'index_01_r_CTRL', 'middle_03_r_CTRL', 'middle_02_r_CTRL', 'middle_01_r_CTRL', 'pinky_01_r_CTRL', 'thumb_MC_l_CTRL', 'thumb_01_l_CTRL', 'thumb_02_l_CTRL', 'ring_01_l_CTRL', 'pinky_03_l_CTRL', 'pinky_02_l_CTRL', 'ring_03_l_CTRL', 'ring_02_l_CTRL', 'index_03_l_CTRL', 'index_02_l_CTRL', 'index_01_l_CTRL', 'middle_03_l_CTRL', 'middle_02_l_CTRL', 'middle_01_l_CTRL', 'pinky_01_l_CTRL', 'ik_r_foot_r_foot_CTRL', 'ik_l_foot_l_foot_CTRL', 'neck_end_Jnt1_CTRL', 'neck_start_Jnt1_CTRL', 'spine_end_Jnt1_CTRL','spine_start_Jnt1_CTRL', 'root_CTRL', 'pelvis_CTRL', 'clavicle_l_CTRL', 'clavicle_r_CTRL', 'IK_upperarm_l_CTRL', 'IK_upperarm_r_CTRL', 'Fk_neck_end_CTRL', 'Fk_neck_02_CTRL', 'Fk_neck_01_CTRL', 'Fk_spine_03_buffer_CTRL', 'Fk_spine_02_CTRL', 'Fk_spine_01_CTRL']

        self.__locsMade = []
        self.__locsMadeParent = []
        self.__allConstraints = []

        self.__rigFileVar = 'lastUsedRig'
        self.__animFileVar = 'lastUsedAnim'
        self.__animBatchFileVar = 'lastUsedBatchAnim'
        self.__rigNamespaceVar = 'lastUsedRigNamespace'
        self.__nameSpaces = ['armorFemale']

        self.__attrFinder = roa.returnObjectWithAttr()
        self.__switcher = ikfks.ikFkSwitcher()
        self.__meta = rmeta.metaSystem()

        self.__extraBakeChannels = ['toeTap']


    def doIt(self):

        self.createLocsAndBake(self.__allCtrls)

    def createLocsAndBake(self, controlsToBake):

        cmds.setAttr(self.rigNs+":pup:thigh_l_ikFkSwitch.fkIk", 1)
        cmds.setAttr(self.rigNs+":pup:thigh_r_ikFkSwitch.fkIk", 1)
        cmds.setAttr(self.rigNs+":pup:hand_l_ikFkSwitch.fkIk", 1)
        cmds.setAttr(self.rigNs+":pup:hand_r_ikFkSwitch.fkIk", 1)

        topTransform = self.__attrFinder.all("topTransform", "*")
        cmds.setAttr(topTransform[0]+".transferMocap", 1)

        theNamespace = topTransform[0].split(':')
        del(theNamespace[-1])
        addNamespace = ':'.join(theNamespace)

        for ctrl in controlsToBake:
            ctrl=addNamespace+':'+ctrl
            locMade = cmds.spaceLocator(n=ctrl+'_updatedLocation')[0]
            self.__locsMade.append(locMade)
            self.__allConstraints.append(cmds.parentConstraint(ctrl, locMade, mo=False)[0])

        
        #do pole controls
        #manually constrain poles for now
        ikPoles = ['_r_thigh_r_pole_CTRL', '_l_thigh_l_pole_CTRL', '_r_upperarm_r_pole_CTRL', '_l_upperarm_l_pole_CTRL']
        transOnly = ['head_eyeSpace_Grp_CTRL']

        #for ctrl in ikPoles:
        
        locMade = cmds.spaceLocator(n='_r_thigh_r_pole_CTRL_updatedLocation')[0]
        parentLocMade = cmds.spaceLocator(n='_r_thigh_r_pole_CTRL_parentLocation')[0]
        cmds.parent(parentLocMade , self.animNs+':thigh_r')
        cmds.xform(parentLocMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_r_thigh_r_pole_CTRL',q=True,ws=True,m=True)))
        cmds.xform(locMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_r_thigh_r_pole_CTRL',q=True,ws=True,m=True)))
        
        self.__locsMade.append(locMade)
        self.__locsMade.append( parentLocMade)
        self.__allConstraints.append(cmds.pointConstraint(self.rigNs+':pup:_r_thigh_r_pole_CTRL', '_r_thigh_r_pole_CTRL_updatedLocation', mo=False)[0])

        locMade = cmds.spaceLocator(n='_l_thigh_l_pole_CTRL_updatedLocation')[0]
        parentLocMade = cmds.spaceLocator(n='_l_thigh_l_pole_CTRL_parentLocation')[0]
        cmds.parent(parentLocMade , self.animNs+':thigh_l')
        cmds.xform(parentLocMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_l_thigh_l_pole_CTRL',q=True,ws=True,m=True)))
        cmds.xform(locMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_l_thigh_l_pole_CTRL',q=True,ws=True,m=True)))

        self.__locsMade.append(locMade)
        self.__locsMade.append( parentLocMade)
        self.__allConstraints.append(cmds.pointConstraint(self.rigNs+':pup:_l_thigh_l_pole_CTRL', '_l_thigh_l_pole_CTRL_updatedLocation', mo=False)[0])

        #for ctrl in ikPoles:
        locMade = cmds.spaceLocator(n='_r_upperarm_r_pole_CTRL_updatedLocation')[0]
        parentLocMade = cmds.spaceLocator(n='_r_upperarm_r_pole_CTRL_parentLocation')[0]
        cmds.parent(parentLocMade , self.animNs+':upperarm_r')
        cmds.xform(parentLocMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_r_upperarm_r_pole_CTRL',q=True,ws=True,m=True)))
        cmds.xform(locMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_r_upperarm_r_pole_CTRL',q=True,ws=True,m=True)))

        self.__locsMade.append(locMade)
        self.__locsMade.append( parentLocMade)
        self.__allConstraints.append(cmds.pointConstraint(self.rigNs+':pup:_r_upperarm_r_pole_CTRL', '_r_upperarm_r_pole_CTRL_updatedLocation', mo=False)[0])

        #for ctrl in ikPoles:
        locMade = cmds.spaceLocator(n='_l_upperarm_l_pole_CTRL_updatedLocation')[0]
        parentLocMade = cmds.spaceLocator(n='_l_upperarm_l_pole_CTRL_parentLocation')[0]
        cmds.parent(parentLocMade , self.animNs+':upperarm_l')
        cmds.xform(parentLocMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_l_upperarm_l_pole_CTRL',q=True,ws=True,m=True)))
        cmds.xform(locMade ,ws=True,m=(cmds.xform(self.rigNs+':pup:_l_upperarm_l_pole_CTRL',q=True,ws=True,m=True)))

        self.__locsMade.append(locMade)
        self.__locsMade.append( parentLocMade)
        self.__allConstraints.append(cmds.pointConstraint(self.rigNs+':pup:_l_upperarm_l_pole_CTRL', '_l_upperarm_l_pole_CTRL_updatedLocation', mo=False)[0])
        
        #for ctrl in ikPoles:
        locMade = cmds.spaceLocator(n='head_eyeSpace_Grp_CTRL_updatedLocation')[0]
        parentLocMade = cmds.spaceLocator(n='head_eyeSpace_Grp_CTRL_parentLocation')[0]
        cmds.parent(parentLocMade , self.animNs+':head')
        cmds.setAttr(parentLocMade+".translateX", 0)
        cmds.setAttr(parentLocMade+".translateY", -40.0)
        cmds.setAttr(parentLocMade+".translateZ", 0)

        self.__locsMade.append(locMade)
        self.__locsMadeParent.append( parentLocMade)
        self.__allConstraints.append(cmds.parentConstraint(parentLocMade, 'head_eyeSpace_Grp_CTRL_updatedLocation', mo=False)[0])

        allKeframeObjects = cmds.ls(type=('animCurve','animCurveTA','animCurveTL','animCurveTT','animCurveTU','animCurveUA','animCurveUL','animCurveUT','animCurveUU'))
        values = cmds.keyframe(allKeframeObjects,q=True,tc=True)

        cmds.playbackOptions(min=min(values), max=max(values))

        self.minTime = cmds.playbackOptions(q=True,min=True)
        self.maxTime = cmds.playbackOptions(q=True,max=True)

        #manual constrain worldRef for now
        self.__allConstraints.append(cmds.parentConstraint('worldRef', self.rigNs+':mocap:worldRef')[0])

        cmds.bakeResults(self.__locsMade, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)

        for con in self.__allConstraints:
            if cmds.objExists(con):
                cmds.delete(con)

        self.__allConstraints = []

        self.__nsCtrls = []

        self.__nsCtrlsWithAttr = []

        for ctrl in controlsToBake:
            ctrl=addNamespace+':'+ctrl
            self.__nsCtrls.append(ctrl)
            testTransChannels = ['tx','ty','tz']
            testRotChannels = ['rx','ry','rz']
            unLockedTransChannel = []
            unLockedRotChannel = []

            for chan in testTransChannels:
                isLocked = cmds.getAttr(ctrl+'.'+chan,l=True)
                if not isLocked:
                    unLockedTransChannel.append(chan)
                    self.__nsCtrlsWithAttr.append(ctrl+'.'+chan)

            for chan in testRotChannels:
                isLocked = cmds.getAttr(ctrl+'.'+chan,l=True)
                if not isLocked:
                    unLockedRotChannel.append(chan)
                    self.__nsCtrlsWithAttr.append(ctrl+'.'+chan)

            for chan in self.__extraBakeChannels:
                if cmds.objExists(ctrl+'.'+chan):
                    self.__nsCtrlsWithAttr.append(ctrl+'.'+chan)

            if len(unLockedTransChannel) == 3:

                self.__allConstraints.append(cmds.pointConstraint(ctrl+'_updatedLocation', ctrl, mo=False)[0])
            else:
                locked = [x for x in testTransChannels if x not in unLockedTransChannel]
                justAxis = []
                for lc in locked:
                    justAxis.append(lc.replace('t',''))
                self.__allConstraints.append(cmds.pointConstraint(ctrl+'_updatedLocation', ctrl, skip=justAxis, mo=False)[0])

            if len(unLockedRotChannel) == 3:
                self.__allConstraints.append(cmds.orientConstraint(ctrl+'_updatedLocation', ctrl, mo=True)[0])
            else:
                locked = [x for x in testRotChannels if x not in unLockedRotChannel]
                justAxis = []
                for lc in locked:
                    justAxis.append(lc.replace('r',''))

                self.__allConstraints.append(cmds.orientConstraint(ctrl+'_updatedLocation', ctrl, skip=justAxis, mo=True)[0])

        cmds.setAttr(topTransform[0]+".transferMocap", 0)


        self.__allConstraints.append(cmds.parentConstraint('head_eyeSpace_Grp_CTRL_updatedLocation', addNamespace+':head_eyeSpace_Grp_CTRL', mo=False)[0])
        
        self.__allConstraints.append(cmds.pointConstraint('_r_thigh_r_pole_CTRL_updatedLocation', addNamespace+':_r_thigh_r_pole_CTRL', mo=False)[0])
        self.__allConstraints.append(cmds.pointConstraint('_l_thigh_l_pole_CTRL_updatedLocation', addNamespace+':_l_thigh_l_pole_CTRL', mo=False)[0])
        self.__allConstraints.append(cmds.pointConstraint('_r_upperarm_r_pole_CTRL_updatedLocation', addNamespace+':_r_upperarm_r_pole_CTRL', mo=False)[0])
        self.__allConstraints.append(cmds.pointConstraint('_l_upperarm_l_pole_CTRL_updatedLocation', addNamespace+':_l_upperarm_l_pole_CTRL', mo=False)[0])

        self.__nsCtrls.append(addNamespace+':_r_thigh_r_pole_CTRL')
        self.__nsCtrls.append(addNamespace+':_l_thigh_l_pole_CTRL')
        self.__nsCtrls.append(addNamespace+':_r_upperarm_r_pole_CTRL')
        self.__nsCtrls.append(addNamespace+':_l_upperarm_l_pole_CTRL')
        
        self.__nsCtrls.append(addNamespace+':head_eyeSpace_Grp_CTRL')
        
        #HACK to connect ball for bake
        cmds.connectAttr(addNamespace.replace(':pup','')+':mocap:ball_l.rotateZ', addNamespace+":ik_l_foot_l_foot_CTRL.toeTap", force=1 )
        cmds.connectAttr(addNamespace.replace(':pup','')+':mocap:ball_r.rotateZ', addNamespace+":ik_r_foot_r_foot_CTRL.toeTap", force=1 )

        cmds.bakeResults(self.__nsCtrls, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)
        
        cmds.delete(self.__allConstraints)
        cmds.delete(self.__locsMade)
        cmds.delete(self.__locsMadeParent)

        animCurves = []
        for ctrl in self.__nsCtrlsWithAttr:
            tempCurves = cmds.listConnections(ctrl, s=1, d=0)
            for tc in tempCurves:
                animCurves.append(tc)

        cmds.filterCurve(animCurves)

        try:
            cmds.disconnectAttr(addNamespace.replace(':pup','')+':mocap:ball_l.rotateZ', addNamespace+':ik_l_foot_l_foot_CTRL.toeTap')
        except:
            pass

        try:
            cmds.disconnectAttr(addNamespace.replace(':pup','')+':mocap:ball_r.rotateZ', addNamespace+':ik_r_foot_r_foot_CTRL.toeTap')
        except:
            pass

        bakeIkFk = cmds.checkBox(self.__bakeIkFk,q=1,v=1)
        if bakeIkFk:
            self.bakeToFk([int(self.minTime), int(self.maxTime)])

    def bakeToAnimRig(self, rigFile, animationFile, bakeToExisting = False):

        if not bakeToExisting:
            cmds.file(new=1,force=1)
            cmds.currentUnit( time='ntsc' )
            cmds.file(animationFile ,i=True,ra = True, mergeNamespacesOnClash = True, ignoreVersion = True, namespace = ":")
            cmds.viewFit( all=True )
            self.mocapMeta = self.__meta.findMeta('mocapBake')
            if len(self.mocapMeta) != 1:
                #TEMP HACK
                self.rootToMove = "root"
                #cmds.error('No mocap meta data in animation file', animationFile)
            else:
                self.rootToMove = cmds.listConnections(self.mocapMeta[0]+'.jointRootBake',s=0,d=1)[0]

            cmds.select(self.rootToMove,hi=1)
            joints = cmds.ls(sl=True)
            theGroup = cmds.group(em=1,n='importedFbx')
            cmds.parent(self.rootToMove, theGroup)
            #cmds.setAttr(theGroup+".rotateX", -90)

            #replace this with a process that figures out the correct namespace
            rigNameSpace = 'armorFemale_01'
            animNameSpace = rigNameSpace+':pup:mocap'

            cmds.file(rigFile ,r=True, mergeNamespacesOnClash = False, namespace = rigNameSpace)

            for jnt in joints:
                rigJnt = animNameSpace+":"+jnt
                print rigJnt, cmds.objExists(rigJnt)
                if cmds.objExists(rigJnt):
                    cmds.parentConstraint(jnt, rigJnt, mo=False)
        
        cmds.currentUnit( time='ntsc' )

        #set all ikFk to IK
        ikSystems = self.__meta.findMeta('ikFkSystem')
        ikSplines = self.__meta.findMeta('splineIk')

        for iks in ikSystems:
            ikSwitch = cmds.listConnections(iks+'.theSwitchControl',s=0,d=1)
            if not ikSwitch:
                cmds.error('No IK/FK switch attached to meta system', iks)

            cmds.setAttr(ikSwitch[0]+".fkIk", 1)

        controlsToBake = self.returnCtrlsToBake()
        #replace this with meta system
        topTransform = self.__attrFinder.all("topTransform", "*")
        cmds.setAttr(topTransform[0]+".transferMocap", 1)

        theNamespace = topTransform[0].split(':')
        del(theNamespace[-1])
        addNamespace = ':'.join(theNamespace)

        #first we must bake the controls in worldspace
        for ctrl in controlsToBake:
            locMade = cmds.spaceLocator(n=ctrl+'_updatedLocation')[0]
            self.__locsMade.append(locMade)
            self.__allConstraints.append(cmds.parentConstraint(ctrl, locMade, mo=False)[0])

        allKeframeObjects = cmds.ls(type=('animCurve','animCurveTA','animCurveTL','animCurveTT','animCurveTU','animCurveUA','animCurveUL','animCurveUT','animCurveUU'))
        values = cmds.keyframe(allKeframeObjects,q=True,tc=True)

        cmds.playbackOptions(min=min(values), max=max(values))

        self.minTime = cmds.playbackOptions(q=True,min=True)
        self.maxTime = cmds.playbackOptions(q=True,max=True)

        #manual constrain worldRef for now
        mocapRoot = self.__meta.findMeta('mocapBake')
        #TEMP HACK
        mocapRoot = 'root'
        #need to add automation for the :mocap:worldRef
        
        cmds.bakeResults(self.__locsMade, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)
        
        for con in self.__allConstraints:
            if cmds.objExists(con):
                cmds.delete(con)

        self.__allConstraints = []

        self.__nsCtrls = []

        self.__nsCtrlsWithAttr = []

        for ctrl in controlsToBake:
            self.__nsCtrls.append(ctrl)
            testTransChannels = ['tx','ty','tz']
            testRotChannels = ['rx','ry','rz']
            unLockedTransChannel = []
            unLockedRotChannel = []

            for chan in testTransChannels:
                isLocked = cmds.getAttr(ctrl+'.'+chan,l=True)
                if not isLocked:
                    unLockedTransChannel.append(chan)
                    self.__nsCtrlsWithAttr.append(ctrl+'.'+chan)

            for chan in testRotChannels:
                isLocked = cmds.getAttr(ctrl+'.'+chan,l=True)
                if not isLocked:
                    unLockedRotChannel.append(chan)
                    self.__nsCtrlsWithAttr.append(ctrl+'.'+chan)

            for chan in self.__extraBakeChannels:
                if cmds.objExists(ctrl+'.'+chan):
                    self.__nsCtrlsWithAttr.append(ctrl+'.'+chan)

            if len(unLockedTransChannel) == 3:
                self.__allConstraints.append(cmds.pointConstraint(ctrl+'_updatedLocation', ctrl, mo=False)[0])
            else:
                locked = [x for x in testTransChannels if x not in unLockedTransChannel]
                justAxis = []
                for lc in locked:
                    justAxis.append(lc.replace('t',''))
                self.__allConstraints.append(cmds.pointConstraint(ctrl+'_updatedLocation', ctrl, skip=justAxis, mo=False)[0])

            if len(unLockedRotChannel) == 3:
                self.__allConstraints.append(cmds.orientConstraint(ctrl+'_updatedLocation', ctrl, mo=True)[0])
            else:
                locked = [x for x in testRotChannels if x not in unLockedRotChannel]
                justAxis = []
                for lc in locked:
                    justAxis.append(lc.replace('r',''))
                self.__allConstraints.append(cmds.orientConstraint(ctrl+'_updatedLocation', ctrl, skip=justAxis, mo=True)[0])

        cmds.setAttr(topTransform[0]+".transferMocap", 0)
        
        #HACK to connect ball for bake
        #this needs to be setup to work with meta data
        toeAdjusterL = cmds.createNode('addDoubleLinear', n = 'toeAdjusterL')
        toeAdjusterR = cmds.createNode('addDoubleLinear', n = 'toeAdjusterR')

        additiveInverseL = cmds.getAttr(addNamespace+':mocap:ball_l.rotateZ') * -1
        additiveInverseR = cmds.getAttr(addNamespace+':mocap:ball_r.rotateZ') * -1

        cmds.connectAttr(addNamespace+':mocap:ball_l.rotateZ',toeAdjusterL+'.input1', force=1 )
        cmds.setAttr(toeAdjusterL+'.input2', additiveInverseL)

        cmds.connectAttr(addNamespace+':mocap:ball_r.rotateZ',toeAdjusterR+'.input1', force=1 )
        cmds.setAttr(toeAdjusterR+'.input2', additiveInverseR)

        cmds.connectAttr(toeAdjusterL+'.output', addNamespace+":ik_l_foot_l_foot_CTRL.toeTap", force=1 )
        cmds.connectAttr(toeAdjusterR+'.output', addNamespace+":ik_r_foot_r_foot_CTRL.toeTap", force=1 )

        #hack to fix flipping constraint, will update with a real fix
        #cmds.setAttr("IK_upperarm_l_CTRL_orientConstraint1.offsetZ", 180)
        #cmds.setAttr("IK_upperarm_l_CTRL_orientConstraint1.offsetX", 180)
        #cmds.setAttr("IK_upperarm_l_CTRL_orientConstraint1.offsetY", 180)
        cmds.setAttr("IK_upperarm_l_CTRL_orientConstraint1.interpType", 0)
        cmds.bakeResults(self.__nsCtrlsWithAttr, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)
        
        cmds.delete(self.__allConstraints)
        cmds.delete(self.__locsMade)
        cmds.delete(self.__locsMadeParent)

        animCurves = []
        for ctrl in self.__nsCtrlsWithAttr:
            tempCurves = cmds.listConnections(ctrl, s=1, d=0)
            for tc in tempCurves:
                animCurves.append(tc)

        cmds.filterCurve(animCurves)

        try:
            cmds.disconnectAttr(addNamespace.replace(':pup','')+':mocap:ball_l.rotateZ', addNamespace+':ik_l_foot_l_foot_CTRL.toeTap')
        except:
            pass

        try:
            cmds.disconnectAttr(addNamespace.replace(':pup','')+':mocap:ball_r.rotateZ', addNamespace+':ik_r_foot_r_foot_CTRL.toeTap')
        except:
            pass

        if not cmds.objExists('gameExporterPreset2'):
            mel.eval('gameFbxExporter;')

        if cmds.window("gameExporterWindow", exists = True):
            cmds.deleteUI("gameExporterWindow")

        animNode = 'gameExporterPreset2'

        clipName = animationFile.replace('_onMocapSkeleton.ma', '').split('/')[-1].replace('FBX_', 'A_')
        if not clipName.startswith('A_'):
            if '\\' in clipName:
                clipName = clipName.split('\\')[-1]
            clipName = 'A_'+clipName
        originalPath = animationFile.split('\\') 
        filePathList = animationFile.split('/')
        del(filePathList[-1])
        joinedPath = '/'.join(filePathList)
        cmds.setAttr(animNode+'.exp', joinedPath, type='string')
        cmds.setAttr(animNode+'.ac[0].acs', self.minTime)
        cmds.setAttr(animNode+'.ac[0].ace', self.maxTime)
        cmds.setAttr(animNode+'.ac[0].acn', clipName, type='string')

        animFilePath = joinedPath+'/'+clipName+'.ma'
        cmds.currentUnit( time='ntsc' )
        cmds.file(rename=animFilePath)
        cmds.file(save=1,type='mayaAscii', f=1) 

    def exportFbxFromRig(self):
        theAnimNode=None
        animNodes = []
        exportNodes = cmds.ls(type='gameFbxExporter')
        print 'exportNodes: ', exportNodes
        for eno in exportNodes:
            exportType = cmds.getAttr(eno+'.exportTypeIndex')
            if exportType == 2:
                animNodes.append(eno)
        print 'animNodes: ', animNodes
        animClips = 0        
        for an in animNodes:
            numClips = cmds.getAttr(an+'.ac', size=True)
            print numClips
            if numClips > 0:
                theAnimNode = an
                animClips = numClips

        clipPath = cmds.getAttr(theAnimNode+'.exportPath')

        for i in range(0, animClips):
            #get the anim data
            clipName = cmds.getAttr(theAnimNode+'.ac['+str(i)+'].acn')
            cle = clipPath+'/'+clipName+'.fbx'

            clipStart = cmds.getAttr(theAnimNode+'.ac['+str(i)+'].acs')
            clipEnd = cmds.getAttr(theAnimNode+'.ac['+str(i)+'].ace')
            
            #set fbx options, seems to need to be done EVERY TIME
            mel.eval('FBXExportBakeComplexAnimation -v true;')
            mel.eval('FBXExportAnimationOnly -v false;')
            mel.eval('FBXExportInputConnections -v false;')
            mel.eval('FBXExportBakeComplexStart -v '+str(clipStart)+';')
            mel.eval('FBXExportBakeComplexEnd -v '+str(clipEnd)+';')

            #set the maya scene up    
            cmds.playbackOptions(e=True, minTime = clipStart, maxTime = clipEnd)

            animExportSets = cmds.ls('*:animationExportSet')
            if len(animExportSets) == 1:
                self.animSet = animExportSets[0]
            #else:
                #cmds.error('SCENE HAS MORE THAN ONE CHARACTER')

            #cmds.select(self.animSet, replace = True)
            
            print 'Exporting Engine Animation: ', cle
            melExport = "FBXExport -s -f \""+cle+"\""
 
            mel.eval(melExport)

    #TODO add baking of specific controls
    def bakeToFkInScene(self):

        minTime = cmds.playbackOptions(q=True,min=True)
        maxTime = cmds.playbackOptions(q=True,max=True)

        self.bakeToFk([int(minTime), int(maxTime)])

    def bakeToFk(self, bakeRange, iks = None):

        allIk = {}

        metaNodesRet = self.__meta.findMeta('ikFkSystem')
        for mnr in metaNodesRet:
            switchCtrl = cmds.listConnections(mnr+'.theSwitchControl',s=0,d=1)[0]
            allIk[switchCtrl] = cmds.listConnections(mnr+'.fkPartners', s=0,d=1)

        #currentFrame = bakeRange[0]
        
        for frame in range(bakeRange[0], bakeRange[1]):
            cmds.currentTime(frame)
            for sw in allIk.keys():
                self.__switcher.swap(sw)
                cmds.setKeyframe(allIk[sw])
                cmds.setAttr(sw+'.fkIk', 1)

    def simpleAnimRigBakeGUI_V2(self):

        if cmds.window("simpleAnimRigBakeGUI", exists = True):
            cmds.deleteUI("simpleAnimRigBakeGUI")
        
        windowWidth = 600
        windowHeight = 700
        
        window = cmds.window("simpleAnimRigBakeGUI", title = "Simple Anim Rig bake", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = True)

        mainLayout = cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 400), (2, 200)] )
        cmds.text(label="The Rig")
        cmds.text(label="Locate")
        self.rigFileText = cmds.textField("rigRefLoc")
        cmds.button(label = "...", c=self.setRigLocation)
        self.rigNamespaceText = cmds.optionMenu( 'namespaceOptions', changeCommand=self.setRigQuantity)
        for ns in self.__nameSpaces:
            cmds.menuItem( label=ns )
        self.rigNamespaceQuantity = cmds.textField('rigQuantity', text = '01')
        cmds.text(label="The FBX Animation/Mocap Directory")
        cmds.text(label="Locate")
        self.animFileText = cmds.textField("animImpLoc")
        cmds.button(label = "...", c=self.setAnimLocation)
        self.__bakeDirectory = cmds.checkBox( label='Bake Whole Directory', v=1 )
        self.__bakeIkFk = cmds.checkBox( label='Bake Ik To Fk', v=1)
        cmds.button(label = "Bake Animation", c=self.simpleAnimRigBakeV2)
        cmds.button(label = "Cancel", c=self.cancelBake)

        #update if it has been used
        if cmds.optionVar(exists =self.__rigFileVar):#if it doesn't exist, make it
            cmds.textField(self.rigFileText, e=True, text = cmds.optionVar( q = self.__rigFileVar ))

        if cmds.optionVar(exists =self.__animFileVar):#if it doesn't exist, make it
            cmds.textField(self.animFileText, e=True, text = cmds.optionVar( q = self.__animFileVar ))
            
        cmds.showWindow(window)

    def setRigLocation(self, *args):

        rigFileDialog = cmds.fileDialog2(cap = "Select Rig file", fm = 1, dialogStyle=2)
        #if not cmds.optionVar(exists = self.__rigFileVar):#if it doesn't exist, make it
        cmds.optionVar(sv=(self.__rigFileVar, rigFileDialog[0]))
        cmds.textField(self.rigFileText, e=True, text = rigFileDialog[0])

        if 'Male' in rigFileDialog[0]:
            cmds.optionMenu( self.rigNamespaceText,e=True, v='maleRig')

        if 'Walker' in rigFileDialog[0]:
            cmds.optionMenu( self.rigNamespaceText,e=True, v='walkerRig')

        if 'SkyLabGuy' in rigFileDialog[0]:
            cmds.optionMenu( self.rigNamespaceText,e=True, v='slgRig')


    def setAnimLocation(self, *args):

        if cmds.checkBox(self.__bakeDirectory, q=1, v=1):
            animFileDialog = cmds.fileDialog2(cap = "Select Animation FBX file", fm = 3, dialogStyle=3)
        else:
            animFileDialog = cmds.fileDialog2(cap = "Select Animation FBX file", fm = 1, dialogStyle=2)

        #animFileDialog = cmds.fileDialog2(cap = "Select Animation FBX file", fm = 2, dialogStyle=2)

        cmds.optionVar(sv=(self.__animFileVar, animFileDialog[0]))
        cmds.textField(self.animFileText, e=True, text = animFileDialog[0])

    def setAnimBatchLocation(self, *args):

        basicFilter = "*.ma"
        if cmds.checkBox(self.__exportBatchOrSingle, q=1, v=1):
            animFileDialog = cmds.fileDialog2(cap = "Select Animation Single MA file",fileFilter=basicFilter, fm = 1, dialogStyle=2)
        else:
            animFileDialog = cmds.fileDialog2(cap = "Select Directory of MA files", fm = 3, dialogStyle=3)

        cmds.optionVar(sv=(self.__animBatchFileVar, animFileDialog[0]))
        cmds.textField(self.animBatchFileText, e=True, text = animFileDialog[0])

    def simpleAnimRigBakeV2(self, *args):

        #cmds.file(new=True,f=True)
        self.badFiles = []
        self.rigNs = cmds.optionMenu( self.rigNamespaceText,q=True, v=True)
        print 'Setting rig namespace: ',self.rigNs
        self.rigNsQuantity = cmds.textField(self.rigNamespaceQuantity, q=True, text=True)
        if self.rigNs == '':
            cmds.error('must set a namespace for the rig')
        else:
            self.rigNs = ':'+self.rigNs+'_'+self.rigNsQuantity

        self.animNs = self.rigNs+':mocap'

        self.__bakedFiles = []

        #get baked data
        #FBXToMocap = cmds.checkBox(self.__FbxToMocap,q=1,v=1)
        bakeIkFk = cmds.checkBox(self.__bakeIkFk,q=1,v=1)
        #bakeToRig = cmds.checkBox(self.__bakeToRig,q=1,v=1)
        #importAnimLayer = cmds.checkBox(self.__loadAnimlayer,q=1,v=1)
        #exportFromRig = cmds.checkBox(self.__exportFromRig,q=1,v=1)
        theAnimFileText = cmds.textField(self.animFileText, q=True, text=True)
        #theRetargetFile = cmds.textField(self.retargetFileText, q=True, text=True)
        theRigFile = cmds.textField(self.rigFileText, q=True, text=True)

        filesToBake = []

        if theAnimFileText.endswith('.ma') or theAnimFileText.endswith('.fbx') or theAnimFileText.endswith('.FBX'):
            filesToBake.append(theAnimFileText)
            print 'Baking Single File, ', filesToBake
        else:
            #filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.ma")
            #if len(filesToBake) == 0:
            filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx")
            if len(filesToBake) == 0:
                filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.FBX")
            print 'Baking Multiple, ', filesToBake
        #print 'MA files in dir, ', cmds.textField(self.animFileText, q=True, text=True)+"/*.ma", filesToBake

        print 'filesToBake: ', filesToBake
        for ftb in filesToBake:
            print 'FTB: ', ftb, theRigFile
            cmds.file(new=1,force=1)

            self.bakeToAnimRig(theRigFile, ftb)
            if bakeIkFk:
                self.bakeToFk([int(self.minTime), int(self.maxTime)])


    def cancelBake(self, *args):

        if cmds.window("simpleAnimRigBakeGUI", exists = True):
            cmds.deleteUI("simpleAnimRigBakeGUI")

    def cancelBatchBake(self, *args):

        if cmds.window("rigToEngineGUI", exists = True):
            cmds.deleteUI("rigToEngineGUI")

    def setRigQuantity(self, *args):

        #manual set for now, add ability to see how many rigs in the scene and adjust
        cmds.textField(self.rigNamespaceQuantity, e=True, text = '01')

    def batchExportFromRig(self, *args):

        filesToBatch = []
        if cmds.checkBox(self.__exportBatchOrSingle, q=1, v=1):
            filesToBatch.append(cmds.textField(self.animBatchFileText, q=True, text=True))
        else:
            listOfFiles = list()
            for (dirpath, dirnames, filenames) in os.walk(cmds.textField(self.animBatchFileText, q=True, text=True)):
                listOfFiles += [os.path.join(dirpath, file) for file in filenames]
            for af in listOfFiles:
                if af.endswith('.ma'):
                    filesToBatch.append(af)

        for aFile in filesToBatch:
            cmds.file(new=True,f=True)
            try:
                cmds.file(aFile, o=True,f=True)
            except:
                pass

            self.exportFbxFromRig()

    def returnCtrlsToBake(self):

        characterNode = self.__meta.findMeta('character')

        if characterNode:
            characterNode = characterNode[0]

        else:
            cmds.error('No Character meta system exists in scene')

        allCtrls = []

        ikBake = cmds.listConnections(characterNode+'.ikBake', s=0, d=1)
        splineIkBake = cmds.listConnections(characterNode+'.splineIkBake', s=0, d=1)
        secondaryMocapBake = cmds.listConnections(characterNode+'.secondaryMocapBake', s=0, d=1)

        if ikBake:
            for ikb in ikBake:
                allCtrls.append(ikb)

        if splineIkBake:
            for ikb in splineIkBake:
                allCtrls.append(ikb)

        if secondaryMocapBake:
            for ikb in secondaryMocapBake:
                allCtrls.append(ikb)

        if len(allCtrls) == 0:
            cmds.error('No mocap bake meta systems in scene')
        else:
            return allCtrls

    def remove_namespaces(self) :
        # gather all namespaces from selection
        all_ns = []
        for obj in pm.selected() :
            if obj.namespace() :
                all_ns.append(obj.namespace())
        
        # remove dupes
        all_ns = list(set(all_ns)) 
        
        # try to remove the first namespace
        for whole_ns in all_ns :
            ns = whole_ns.split(':')[0]
            try :
                pm.namespace(mv=[ns,':'],f=1)
                if ns in pm.namespaceInfo(lon=1) :
                    pm.namespace(rm=ns)
                print 'Namespace "%s" removed.'%ns
            except :
                warning('Namespace "%s" is not removable. Possibly from a reference.'%ns)
        
        return 1

    def setDefaultPose(self, character):

        if character == 'armorFemale_01':
            cmds.setAttr('root.tx', -3.552713679e-15)
            cmds.setAttr('root.ty', -2.220446049e-16)
            cmds.setAttr('root.tz', -3.552713679e-15)
            cmds.setAttr('root.rx', 0)
            cmds.setAttr('root.ry', 0)
            cmds.setAttr('root.rz', 0)
            cmds.setAttr('pelvis.tx', 1.375283438e-06)
            cmds.setAttr('pelvis.ty', 99.94680053)
            cmds.setAttr('pelvis.tz', 3.351735807)
            cmds.setAttr('pelvis.rx', 0)
            cmds.setAttr('pelvis.ry', 0)
            cmds.setAttr('pelvis.rz', 0)
            cmds.setAttr('spine_01.tx', 0)
            cmds.setAttr('spine_01.ty', 1.421085472e-14)
            cmds.setAttr('spine_01.tz', 3.552713679e-15)
            cmds.setAttr('spine_01.rx', -90)
            cmds.setAttr('spine_01.ry', 0)
            cmds.setAttr('spine_01.rz', 90)
            cmds.setAttr('spine_02.tx', 8.871510817)
            cmds.setAttr('spine_02.ty', 5.329070518e-15)
            cmds.setAttr('spine_02.tz', 1.969868716e-15)
            cmds.setAttr('spine_02.rx', 0)
            cmds.setAttr('spine_02.ry', 0)
            cmds.setAttr('spine_02.rz', 0)
            cmds.setAttr('spine_03.tx', 8.871510817)
            cmds.setAttr('spine_03.ty', -2.664535259e-15)
            cmds.setAttr('spine_03.tz', 1.969871892e-15)
            cmds.setAttr('spine_03.rx', 0)
            cmds.setAttr('spine_03.ry', 0)
            cmds.setAttr('spine_03.rz', 7.79407943)
            cmds.setAttr('neck_01.tx', 21.63625757)
            cmds.setAttr('neck_01.ty', 1.421085472e-14)
            cmds.setAttr('neck_01.tz', -5.148389073e-16)
            cmds.setAttr('neck_01.rx', 0)
            cmds.setAttr('neck_01.ry', 0)
            cmds.setAttr('neck_01.rz', -15.69071137)
            cmds.setAttr('neck_02.tx', 7.525546953)
            cmds.setAttr('neck_02.ty', 8.526512829e-14)
            cmds.setAttr('neck_02.tz', 2.0401121e-15)
            cmds.setAttr('neck_02.rx', 0)
            cmds.setAttr('neck_02.ry', 0)
            cmds.setAttr('neck_02.rz', 4.367729231)
            cmds.setAttr('head.tx', 6.87411548)
            cmds.setAttr('head.ty', 0.0040563999)
            cmds.setAttr('head.tz', 8.473419025e-16)
            cmds.setAttr('head.rx', 0)
            cmds.setAttr('head.ry', 0)
            cmds.setAttr('head.rz', 3.528902713)
            cmds.setAttr('faceAttach.tx', -0.6605604554)
            cmds.setAttr('faceAttach.ty', -1.59965794)
            cmds.setAttr('faceAttach.tz', -0.01373608522)
            cmds.setAttr('faceAttach.rx', 0)
            cmds.setAttr('faceAttach.ry', 0)
            cmds.setAttr('faceAttach.rz', 0)
            cmds.setAttr('C_jaw.tx', -0.002095171142)
            cmds.setAttr('C_jaw.ty', -1.341659587)
            cmds.setAttr('C_jaw.tz', 0.01373608522)
            cmds.setAttr('C_jaw.rx', -170.4213547)
            cmds.setAttr('C_jaw.ry', 90)
            cmds.setAttr('C_jaw.rz', 0)
            cmds.setAttr('tongue.tx', 5.448962234e-13)
            cmds.setAttr('tongue.ty', 6.023221277)
            cmds.setAttr('tongue.tz', 1.963118302)
            cmds.setAttr('tongue.rx', -89.99999714)
            cmds.setAttr('tongue.ry', 15.90437673)
            cmds.setAttr('tongue.rz', 89.99999882)
            cmds.setAttr('teeth_lower.tx', 7.22468228e-13)
            cmds.setAttr('teeth_lower.ty', 5.904165701)
            cmds.setAttr('teeth_lower.tz', 2.505943891)
            cmds.setAttr('teeth_lower.rx', 0)
            cmds.setAttr('teeth_lower.ry', 0)
            cmds.setAttr('teeth_lower.rz', 0)
            cmds.setAttr('R_lip_lower_outer.tx', -1.160133426)
            cmds.setAttr('R_lip_lower_outer.ty', 8.09664584)
            cmds.setAttr('R_lip_lower_outer.tz', 1.685205924)
            cmds.setAttr('R_lip_lower_outer.rx', 97.04898358)
            cmds.setAttr('R_lip_lower_outer.ry', -2.442556456)
            cmds.setAttr('R_lip_lower_outer.rz', -149.8248868)
            cmds.setAttr('C_lip_lower_mid.tx', -0.000649273635)
            cmds.setAttr('C_lip_lower_mid.ty', 8.198735676)
            cmds.setAttr('C_lip_lower_mid.tz', 1.898981053)
            cmds.setAttr('C_lip_lower_mid.rx', -77.07063382)
            cmds.setAttr('C_lip_lower_mid.ry', -180)
            cmds.setAttr('C_lip_lower_mid.rz', 0)
            cmds.setAttr('L_lip_lower_outer.tx', 1.16013072)
            cmds.setAttr('L_lip_lower_outer.ty', 8.09664584)
            cmds.setAttr('L_lip_lower_outer.tz', 1.685205924)
            cmds.setAttr('L_lip_lower_outer.rx', 97.04898389)
            cmds.setAttr('L_lip_lower_outer.ry', 2.442556379)
            cmds.setAttr('L_lip_lower_outer.rz', 149.8248879)
            cmds.setAttr('L_eye.tx', 4.11907826)
            cmds.setAttr('L_eye.ty', -6.12198967)
            cmds.setAttr('L_eye.tz', -2.983753124)
            cmds.setAttr('L_eye.rx', -180.0000033)
            cmds.setAttr('L_eye.ry', 90)
            cmds.setAttr('L_eye.rz', 0)
            cmds.setAttr('L_brow_outer.tx', 6.191228312)
            cmds.setAttr('L_brow_outer.ty', -6.869757984)
            cmds.setAttr('L_brow_outer.tz', -4.918482932)
            cmds.setAttr('L_brow_outer.rx', -96.26780686)
            cmds.setAttr('L_brow_outer.ry', 50.22372012)
            cmds.setAttr('L_brow_outer.rz', -108.0865896)
            cmds.setAttr('R_lip_upper_outer.tx', -1.534952289)
            cmds.setAttr('R_lip_upper_outer.ty', -9.422606033)
            cmds.setAttr('R_lip_upper_outer.tz', 1.132653734)
            cmds.setAttr('R_lip_upper_outer.rx', 9.818847185)
            cmds.setAttr('R_lip_upper_outer.ry', 64.06463374)
            cmds.setAttr('R_lip_upper_outer.rz', -82.75544765)
            cmds.setAttr('teeth_upper.tx', -4.121360315)
            cmds.setAttr('teeth_upper.ty', -7.805539516)
            cmds.setAttr('teeth_upper.tz', 0.01373608522)
            cmds.setAttr('teeth_upper.rx', 99.57864527)
            cmds.setAttr('teeth_upper.ry', 90)
            cmds.setAttr('teeth_upper.rz', 0)
            cmds.setAttr('R_eye.tx', 4.11907826)
            cmds.setAttr('R_eye.ty', -6.12198967)
            cmds.setAttr('R_eye.tz', 3.011228105)
            cmds.setAttr('R_eye.rx', -180.0000033)
            cmds.setAttr('R_eye.ry', 90)
            cmds.setAttr('R_eye.rz', 0)
            cmds.setAttr('R_lip_corner.tx', -2.466594656)
            cmds.setAttr('R_lip_corner.ty', -7.568795647)
            cmds.setAttr('R_lip_corner.tz', 2.615189334)
            cmds.setAttr('R_lip_corner.rx', -33.05682673)
            cmds.setAttr('R_lip_corner.ry', -179.231184)
            cmds.setAttr('R_lip_corner.rz', 1.064909173)
            cmds.setAttr('R_lip_corner_top.tx', -0.2670911488)
            cmds.setAttr('R_lip_corner_top.ty', -0.6078832902)
            cmds.setAttr('R_lip_corner_top.tz', 0.06598814597)
            cmds.setAttr('R_lip_corner_top.rx', -176.6437354)
            cmds.setAttr('R_lip_corner_top.ry', 2.961851488)
            cmds.setAttr('R_lip_corner_top.rz', -84.74796987)
            cmds.setAttr('R_lip_corner_Bottom.tx', 0.1039989698)
            cmds.setAttr('R_lip_corner_Bottom.ty', -0.4643946887)
            cmds.setAttr('R_lip_corner_Bottom.tz', 0.1528613765)
            cmds.setAttr('R_lip_corner_Bottom.rx', -3.513383917)
            cmds.setAttr('R_lip_corner_Bottom.ry', 169.3875254)
            cmds.setAttr('R_lip_corner_Bottom.rz', -85.58298595)
            cmds.setAttr('R_cheek_inner.tx', -1.55827234)
            cmds.setAttr('R_cheek_inner.ty', -5.740214573)
            cmds.setAttr('R_cheek_inner.tz', 4.77402856)
            cmds.setAttr('R_cheek_inner.rx', -8.300086238)
            cmds.setAttr('R_cheek_inner.ry', -154.7849342)
            cmds.setAttr('R_cheek_inner.rz', -93.87615118)
            cmds.setAttr('R_brow_outer.tx', 6.191228312)
            cmds.setAttr('R_brow_outer.ty', -6.869757984)
            cmds.setAttr('R_brow_outer.tz', 4.945957919)
            cmds.setAttr('R_brow_outer.rx', 83.73219301)
            cmds.setAttr('R_brow_outer.ry', 50.22372047)
            cmds.setAttr('R_brow_outer.rz', 71.91341044)
            cmds.setAttr('R_brow_mid.tx', 6.395224562)
            cmds.setAttr('R_brow_mid.ty', -8.757641131)
            cmds.setAttr('R_brow_mid.tz', 1.700168511)
            cmds.setAttr('R_brow_mid.rx', 92.256441)
            cmds.setAttr('R_brow_mid.ry', 1.330955155)
            cmds.setAttr('R_brow_mid.rz', 79.11632674)
            cmds.setAttr('C_nose_bridge.tx', 3.190024712)
            cmds.setAttr('C_nose_bridge.ty', -9.151952446)
            cmds.setAttr('C_nose_bridge.tz', 0.01438535886)
            cmds.setAttr('C_nose_bridge.rx', 103.1069047)
            cmds.setAttr('C_nose_bridge.ry', -90)
            cmds.setAttr('C_nose_bridge.rz', 0)
            cmds.setAttr('L_lip_corner.tx', -2.466594656)
            cmds.setAttr('L_lip_corner.ty', -7.568795647)
            cmds.setAttr('L_lip_corner.tz', -2.587714383)
            cmds.setAttr('L_lip_corner.rx', 33.05682757)
            cmds.setAttr('L_lip_corner.ry', 179.2311833)
            cmds.setAttr('L_lip_corner.rz', 1.064909173)
            cmds.setAttr('L_lip_corner_top.tx', -0.2670911517)
            cmds.setAttr('L_lip_corner_top.ty', -0.6078832234)
            cmds.setAttr('L_lip_corner_top.tz', -0.06598803284)
            cmds.setAttr('L_lip_corner_top.rx', 3.356252729)
            cmds.setAttr('L_lip_corner_top.ry', 2.961855967)
            cmds.setAttr('L_lip_corner_top.rz', 95.25203007)
            cmds.setAttr('L_lip_corner_Bottom.tx', 0.1039989657)
            cmds.setAttr('L_lip_corner_Bottom.ty', -0.464394678)
            cmds.setAttr('L_lip_corner_Bottom.tz', -0.1528613498)
            cmds.setAttr('L_lip_corner_Bottom.rx', -3.513381028)
            cmds.setAttr('L_lip_corner_Bottom.ry', 10.61247559)
            cmds.setAttr('L_lip_corner_Bottom.rz', -85.58298657)
            cmds.setAttr('L_lip_upper_outer.tx', -1.534952289)
            cmds.setAttr('L_lip_upper_outer.ty', -9.422606033)
            cmds.setAttr('L_lip_upper_outer.tz', -1.10517878)
            cmds.setAttr('L_lip_upper_outer.rx', 9.818847791)
            cmds.setAttr('L_lip_upper_outer.ry', 115.9353648)
            cmds.setAttr('L_lip_upper_outer.rz', -82.75544765)
            cmds.setAttr('C_lip_upper_mid.tx', -1.550557109)
            cmds.setAttr('C_lip_upper_mid.ty', -9.565102391)
            cmds.setAttr('C_lip_upper_mid.tz', 0.01438535886)
            cmds.setAttr('C_lip_upper_mid.rx', 91.68283232)
            cmds.setAttr('C_lip_upper_mid.ry', 90)
            cmds.setAttr('C_lip_upper_mid.rz', 0)
            cmds.setAttr('L_cheek_inner.tx', -1.55827234)
            cmds.setAttr('L_cheek_inner.ty', -5.740214573)
            cmds.setAttr('L_cheek_inner.tz', -4.746553691)
            cmds.setAttr('L_cheek_inner.rx', 8.300085183)
            cmds.setAttr('L_cheek_inner.ry', 154.7849333)
            cmds.setAttr('L_cheek_inner.rz', -93.87615118)
            cmds.setAttr('L_brow_mid.tx', 6.395224562)
            cmds.setAttr('L_brow_mid.ty', -8.757641131)
            cmds.setAttr('L_brow_mid.tz', -1.672693638)
            cmds.setAttr('L_brow_mid.rx', -87.74355898)
            cmds.setAttr('L_brow_mid.ry', 1.330954765)
            cmds.setAttr('L_brow_mid.rz', -100.8836733)
            cmds.setAttr('C_brow_mid.tx', 6.236784142)
            cmds.setAttr('C_brow_mid.ty', -8.913233168)
            cmds.setAttr('C_brow_mid.tz', 0.01373746051)
            cmds.setAttr('C_brow_mid.rx', 170.4213547)
            cmds.setAttr('C_brow_mid.ry', -90)
            cmds.setAttr('C_brow_mid.rz', 0)
            cmds.setAttr('R_midCheek.tx', 1.88598114)
            cmds.setAttr('R_midCheek.ty', -8.081202738)
            cmds.setAttr('R_midCheek.tz', 1.759110233)
            cmds.setAttr('R_midCheek.rx', 83.22255824)
            cmds.setAttr('R_midCheek.ry', 9.776065059)
            cmds.setAttr('R_midCheek.rz', 72.2855181)
            cmds.setAttr('L_midCheek.tx', 1.88598114)
            cmds.setAttr('L_midCheek.ty', -8.081202738)
            cmds.setAttr('L_midCheek.tz', -1.731635358)
            cmds.setAttr('L_midCheek.rx', -96.77744187)
            cmds.setAttr('L_midCheek.ry', 9.776063807)
            cmds.setAttr('L_midCheek.rz', -107.7144819)
            cmds.setAttr('L_eye_lid_upper_mid.tx', 3.708725444)
            cmds.setAttr('L_eye_lid_upper_mid.ty', -5.809368461)
            cmds.setAttr('L_eye_lid_upper_mid.tz', -2.970257495)
            cmds.setAttr('L_eye_lid_upper_mid.rx', -39.13059402)
            cmds.setAttr('L_eye_lid_upper_mid.ry', -83.44350317)
            cmds.setAttr('L_eye_lid_upper_mid.rz', -111.810762)
            cmds.setAttr('L_eye_lid_lower_mid.tx', 5.117188596)
            cmds.setAttr('L_eye_lid_lower_mid.ty', -5.931654992)
            cmds.setAttr('L_eye_lid_lower_mid.tz', -2.911590383)
            cmds.setAttr('L_eye_lid_lower_mid.rx', -127.4214656)
            cmds.setAttr('L_eye_lid_lower_mid.ry', 84.34575393)
            cmds.setAttr('L_eye_lid_lower_mid.rz', 39.69207186)
            cmds.setAttr('R_eye_lid_lower_mid.tx', 5.117188596)
            cmds.setAttr('R_eye_lid_lower_mid.ty', -5.931654992)
            cmds.setAttr('R_eye_lid_lower_mid.tz', 2.939065238)
            cmds.setAttr('R_eye_lid_lower_mid.rx', 52.57853446)
            cmds.setAttr('R_eye_lid_lower_mid.ry', 95.65424557)
            cmds.setAttr('R_eye_lid_lower_mid.rz', 39.69207186)
            cmds.setAttr('R_eye_lid_upper_mid.tx', 3.708725444)
            cmds.setAttr('R_eye_lid_upper_mid.ty', -5.809368461)
            cmds.setAttr('R_eye_lid_upper_mid.tz', 2.997732421)
            cmds.setAttr('R_eye_lid_upper_mid.rx', -39.13059399)
            cmds.setAttr('R_eye_lid_upper_mid.ry', -83.44350317)
            cmds.setAttr('R_eye_lid_upper_mid.rz', 68.18923798)
            cmds.setAttr('L_outterCheek.tx', 1.953104833)
            cmds.setAttr('L_outterCheek.ty', -6.611179587)
            cmds.setAttr('L_outterCheek.tz', -5.148651569)
            cmds.setAttr('L_outterCheek.rx', -90.99912288)
            cmds.setAttr('L_outterCheek.ry', 37.94872068)
            cmds.setAttr('L_outterCheek.rz', -114.7174425)
            cmds.setAttr('R_outterCheek.tx', 1.953104833)
            cmds.setAttr('R_outterCheek.ty', -6.611179587)
            cmds.setAttr('R_outterCheek.tz', 5.176126262)
            cmds.setAttr('R_outterCheek.rx', 89.00087718)
            cmds.setAttr('R_outterCheek.ry', 37.94872215)
            cmds.setAttr('R_outterCheek.rz', 65.28255747)
            cmds.setAttr('clavicle_l.tx', 19.44421097)
            cmds.setAttr('clavicle_l.ty', 0.6610197075)
            cmds.setAttr('clavicle_l.tz', -2.461505939)
            cmds.setAttr('clavicle_l.rx', -24.47164675)
            cmds.setAttr('clavicle_l.ry', 92.89267237)
            cmds.setAttr('clavicle_l.rz', -31.83848815)
            cmds.setAttr('upperarm_l.tx', 11.6467247)
            cmds.setAttr('upperarm_l.ty', -2.220446049e-16)
            cmds.setAttr('upperarm_l.tz', -1.136868377e-13)
            cmds.setAttr('upperarm_l.rx', 0.6503470699)
            cmds.setAttr('upperarm_l.ry', 41.01652551)
            cmds.setAttr('upperarm_l.rz', 7.339346506)
            cmds.setAttr('lowerarm_l.tx', 27.39923096)
            cmds.setAttr('lowerarm_l.ty', -2.220446049e-16)
            cmds.setAttr('lowerarm_l.tz', 1.136868377e-13)
            cmds.setAttr('lowerarm_l.rx', 0)
            cmds.setAttr('lowerarm_l.ry', 0)
            cmds.setAttr('lowerarm_l.rz', -15.49763596)
            cmds.setAttr('hand_l.tx', 24.00681686)
            cmds.setAttr('hand_l.ty', 1.243449788e-14)
            cmds.setAttr('hand_l.tz', 0)
            cmds.setAttr('hand_l.rx', -77.93671534)
            cmds.setAttr('hand_l.ry', 1.123726641)
            cmds.setAttr('hand_l.rz', -7.045138104)
            cmds.setAttr('index_metacarpal_l.tx', 3.018457224)
            cmds.setAttr('index_metacarpal_l.ty', -0.2036138947)
            cmds.setAttr('index_metacarpal_l.tz', -1.100608077)
            cmds.setAttr('index_metacarpal_l.rx', 4.905331545)
            cmds.setAttr('index_metacarpal_l.ry', 4.236431794)
            cmds.setAttr('index_metacarpal_l.rz', -2.637747015)
            cmds.setAttr('index_01_l.tx', 6.0009723)
            cmds.setAttr('index_01_l.ty', -5.684341886e-14)
            cmds.setAttr('index_01_l.tz', -2.131628207e-14)
            cmds.setAttr('index_01_l.rx', -4.445199305)
            cmds.setAttr('index_01_l.ry', -6.040914786)
            cmds.setAttr('index_01_l.rz', 24.47687516)
            cmds.setAttr('index_02_l.tx', 4.242363071)
            cmds.setAttr('index_02_l.ty', 0)
            cmds.setAttr('index_02_l.tz', 7.105427358e-15)
            cmds.setAttr('index_02_l.rx', -6.51997135)
            cmds.setAttr('index_02_l.ry', -8.022532838)
            cmds.setAttr('index_02_l.rz', 28.88086834)
            cmds.setAttr('index_03_l.tx', 2.464811105)
            cmds.setAttr('index_03_l.ty', 0)
            cmds.setAttr('index_03_l.tz', -1.776356839e-14)
            cmds.setAttr('index_03_l.rx', -0.4163968435)
            cmds.setAttr('index_03_l.ry', -0.4600920682)
            cmds.setAttr('index_03_l.rz', 20.17939425)
            cmds.setAttr('thumb_01_l.tx', 3.646285612)
            cmds.setAttr('thumb_01_l.ty', 1.629395896)
            cmds.setAttr('thumb_01_l.tz', -2.424686838)
            cmds.setAttr('thumb_01_l.rx', 58.85439116)
            cmds.setAttr('thumb_01_l.ry', 19.39761044)
            cmds.setAttr('thumb_01_l.rz', 18.0540374)
            cmds.setAttr('thumb_02_l.tx', 3.234890566)
            cmds.setAttr('thumb_02_l.ty', 7.105427358e-14)
            cmds.setAttr('thumb_02_l.tz', -5.684341886e-14)
            cmds.setAttr('thumb_02_l.rx', -1.350703226)
            cmds.setAttr('thumb_02_l.ry', -3.375461537)
            cmds.setAttr('thumb_02_l.rz', 0.927888096)
            cmds.setAttr('thumb_03_l.tx', 2.872667651)
            cmds.setAttr('thumb_03_l.ty', -5.684341886e-14)
            cmds.setAttr('thumb_03_l.tz', 8.526512829e-14)
            cmds.setAttr('thumb_03_l.rx', 0.02848485218)
            cmds.setAttr('thumb_03_l.ry', -0.305905793)
            cmds.setAttr('thumb_03_l.rz', -4.041738503)
            cmds.setAttr('pinky_metacarpal_l.tx', 1.400265183)
            cmds.setAttr('pinky_metacarpal_l.ty', 0.007601392004)
            cmds.setAttr('pinky_metacarpal_l.tz', 3.036237294)
            cmds.setAttr('pinky_metacarpal_l.rx', -3.573552147)
            cmds.setAttr('pinky_metacarpal_l.ry', -23.74537061)
            cmds.setAttr('pinky_metacarpal_l.rz', 1.114930234)
            cmds.setAttr('pinky_01_l.tx', 5.313183688)
            cmds.setAttr('pinky_01_l.ty', 7.105427358e-14)
            cmds.setAttr('pinky_01_l.tz', 8.881784197e-15)
            cmds.setAttr('pinky_01_l.rx', 0.3692465164)
            cmds.setAttr('pinky_01_l.ry', 8.264591124)
            cmds.setAttr('pinky_01_l.rz', 31.00563478)
            cmds.setAttr('pinky_02_l.tx', 3.473259422)
            cmds.setAttr('pinky_02_l.ty', 1.421085472e-14)
            cmds.setAttr('pinky_02_l.tz', -1.953992523e-14)
            cmds.setAttr('pinky_02_l.rx', -0.08153715714)
            cmds.setAttr('pinky_02_l.ry', 2.325205886)
            cmds.setAttr('pinky_02_l.rz', 19.58169752)
            cmds.setAttr('pinky_03_l.tx', 2.064882273)
            cmds.setAttr('pinky_03_l.ty', -7.105427358e-15)
            cmds.setAttr('pinky_03_l.tz', -6.217248938e-15)
            cmds.setAttr('pinky_03_l.rx', -0.2876513717)
            cmds.setAttr('pinky_03_l.ry', 3.075759726)
            cmds.setAttr('pinky_03_l.rz', 10.21626862)
            cmds.setAttr('middle_metacarpal_l.tx', 2.687285131)
            cmds.setAttr('middle_metacarpal_l.ty', -0.1830501862)
            cmds.setAttr('middle_metacarpal_l.tz', 0.07356184096)
            cmds.setAttr('middle_metacarpal_l.rx', -11.86547908)
            cmds.setAttr('middle_metacarpal_l.ry', -8.851350369)
            cmds.setAttr('middle_metacarpal_l.rz', -4.666912943)
            cmds.setAttr('middle_01_l.tx', 5.795293274)
            cmds.setAttr('middle_01_l.ty', 7.105427358e-14)
            cmds.setAttr('middle_01_l.tz', 1.065814104e-14)
            cmds.setAttr('middle_01_l.rx', 0.05612149058)
            cmds.setAttr('middle_01_l.ry', -7.024277449)
            cmds.setAttr('middle_01_l.rz', 33.01488902)
            cmds.setAttr('middle_02_l.tx', 4.845106833)
            cmds.setAttr('middle_02_l.ty', -1.421085472e-14)
            cmds.setAttr('middle_02_l.tz', 2.664535259e-15)
            cmds.setAttr('middle_02_l.rx', -0.3459176713)
            cmds.setAttr('middle_02_l.ry', -5.152909857)
            cmds.setAttr('middle_02_l.rz', 27.82391804)
            cmds.setAttr('middle_03_l.tx', 2.717296679)
            cmds.setAttr('middle_03_l.ty', 1.421085472e-14)
            cmds.setAttr('middle_03_l.tz', 4.329869796e-15)
            cmds.setAttr('middle_03_l.rx', -0.1772796638)
            cmds.setAttr('middle_03_l.ry', -1.052347969)
            cmds.setAttr('middle_03_l.rz', 18.50754878)
            cmds.setAttr('ring_metacarpal_l.tx', 2.101582292)
            cmds.setAttr('ring_metacarpal_l.ty', -0.3230889326)
            cmds.setAttr('ring_metacarpal_l.tz', 1.997445103)
            cmds.setAttr('ring_metacarpal_l.rx', -7.861499372)
            cmds.setAttr('ring_metacarpal_l.ry', -13.45615672)
            cmds.setAttr('ring_metacarpal_l.rz', -0.999947615)
            cmds.setAttr('ring_01_l.tx', 5.164995127)
            cmds.setAttr('ring_01_l.ty', 5.684341886e-14)
            cmds.setAttr('ring_01_l.tz', 1.110223025e-14)
            cmds.setAttr('ring_01_l.rx', -2.344533041)
            cmds.setAttr('ring_01_l.ry', -3.404821962)
            cmds.setAttr('ring_01_l.rz', 28.72887883)
            cmds.setAttr('ring_02_l.tx', 4.677883058)
            cmds.setAttr('ring_02_l.ty', 2.842170943e-14)
            cmds.setAttr('ring_02_l.tz', -3.996802889e-15)
            cmds.setAttr('ring_02_l.rx', 0.5809469072)
            cmds.setAttr('ring_02_l.ry', 0.8964100654)
            cmds.setAttr('ring_02_l.rz', 26.29684336)
            cmds.setAttr('ring_03_l.tx', 2.375662587)
            cmds.setAttr('ring_03_l.ty', 2.842170943e-14)
            cmds.setAttr('ring_03_l.tz', -5.329070518e-15)
            cmds.setAttr('ring_03_l.rx', -2.064904971)
            cmds.setAttr('ring_03_l.ry', -3.05136873)
            cmds.setAttr('ring_03_l.rz', 17.15882405)
            cmds.setAttr('lowerarm_twist_01_l.tx', 24.00681686)
            cmds.setAttr('lowerarm_twist_01_l.ty', -1.776356839e-15)
            cmds.setAttr('lowerarm_twist_01_l.tz', 2.842170943e-14)
            cmds.setAttr('lowerarm_twist_01_l.rx', -77.84381884)
            cmds.setAttr('lowerarm_twist_01_l.ry', 0)
            cmds.setAttr('lowerarm_twist_01_l.rz', 0)
            cmds.setAttr('upperarm_twist_01_l.tx', -2.842170943e-14)
            cmds.setAttr('upperarm_twist_01_l.ty', -1.665334537e-15)
            cmds.setAttr('upperarm_twist_01_l.tz', 5.684341886e-14)
            cmds.setAttr('upperarm_twist_01_l.rx', 0)
            cmds.setAttr('upperarm_twist_01_l.ry', 0)
            cmds.setAttr('upperarm_twist_01_l.rz', 0)
            cmds.setAttr('clavicle_r.tx', 19.44421097)
            cmds.setAttr('clavicle_r.ty', 0.6610197075)
            cmds.setAttr('clavicle_r.tz', 2.461508696)
            cmds.setAttr('clavicle_r.rx', -24.47164675)
            cmds.setAttr('clavicle_r.ry', 92.89267239)
            cmds.setAttr('clavicle_r.rz', 148.1615118)
            cmds.setAttr('upperarm_r.tx', -11.6467247)
            cmds.setAttr('upperarm_r.ty', 7.105427358e-15)
            cmds.setAttr('upperarm_r.tz', 1.705302566e-13)
            cmds.setAttr('upperarm_r.rx', 0.6503502071)
            cmds.setAttr('upperarm_r.ry', 41.01652605)
            cmds.setAttr('upperarm_r.rz', 7.339351338)
            cmds.setAttr('lowerarm_r.tx', -27.39923096)
            cmds.setAttr('lowerarm_r.ty', 1.110223025e-13)
            cmds.setAttr('lowerarm_r.tz', -2.131628207e-13)
            cmds.setAttr('lowerarm_r.rx', 0)
            cmds.setAttr('lowerarm_r.ry', 0)
            cmds.setAttr('lowerarm_r.rz', -15.49764359)
            cmds.setAttr('hand_r.tx', -24.00681686)
            cmds.setAttr('hand_r.ty', 8.704148513e-14)
            cmds.setAttr('hand_r.tz', 4.475083983e-07)
            cmds.setAttr('hand_r.rx', -77.93671314)
            cmds.setAttr('hand_r.ry', 1.123724951)
            cmds.setAttr('hand_r.rz', -7.045134412)
            cmds.setAttr('index_metacarpal_r.tx', -3.018459208)
            cmds.setAttr('index_metacarpal_r.ty', 0.2036157564)
            cmds.setAttr('index_metacarpal_r.tz', 1.100607255)
            cmds.setAttr('index_metacarpal_r.rx', 4.905335836)
            cmds.setAttr('index_metacarpal_r.ry', 4.236435799)
            cmds.setAttr('index_metacarpal_r.rz', -2.637739809)
            cmds.setAttr('index_01_r.tx', -6.000971352)
            cmds.setAttr('index_01_r.ty', -1.018619855e-07)
            cmds.setAttr('index_01_r.tz', 3.083673761e-08)
            cmds.setAttr('index_01_r.rx', -4.445203286)
            cmds.setAttr('index_01_r.ry', -6.040919328)
            cmds.setAttr('index_01_r.rz', 24.47686318)
            cmds.setAttr('index_02_r.tx', -4.242363273)
            cmds.setAttr('index_02_r.ty', -7.538325519e-08)
            cmds.setAttr('index_02_r.tz', 2.510476271e-08)
            cmds.setAttr('index_02_r.rx', -6.51997055)
            cmds.setAttr('index_02_r.ry', -8.022532729)
            cmds.setAttr('index_02_r.rz', 28.88086499)
            cmds.setAttr('index_03_r.tx', -2.46481111)
            cmds.setAttr('index_03_r.ty', -4.43335253e-08)
            cmds.setAttr('index_03_r.tz', 9.916707455e-09)
            cmds.setAttr('index_03_r.rx', -0.4163889808)
            cmds.setAttr('index_03_r.ry', -0.4600826817)
            cmds.setAttr('index_03_r.rz', 20.1794435)
            cmds.setAttr('thumb_01_r.tx', -3.646286837)
            cmds.setAttr('thumb_01_r.ty', -1.629394694)
            cmds.setAttr('thumb_01_r.tz', 2.424686383)
            cmds.setAttr('thumb_01_r.rx', 58.85438235)
            cmds.setAttr('thumb_01_r.ry', 19.39760301)
            cmds.setAttr('thumb_01_r.rz', 18.05402021)
            cmds.setAttr('thumb_02_r.tx', -3.234890914)
            cmds.setAttr('thumb_02_r.ty', -1.180367803e-08)
            cmds.setAttr('thumb_02_r.tz', 5.199406417e-08)
            cmds.setAttr('thumb_02_r.rx', -1.350676063)
            cmds.setAttr('thumb_02_r.ry', -3.375392569)
            cmds.setAttr('thumb_02_r.rz', 0.927893519)
            cmds.setAttr('thumb_03_r.tx', -2.872666521)
            cmds.setAttr('thumb_03_r.ty', -1.304842101e-08)
            cmds.setAttr('thumb_03_r.tz', 4.629310979e-08)
            cmds.setAttr('thumb_03_r.rx', 0.02849434279)
            cmds.setAttr('thumb_03_r.ry', -0.3060081705)
            cmds.setAttr('thumb_03_r.rz', -4.041747568)
            cmds.setAttr('pinky_metacarpal_r.tx', -1.400265793)
            cmds.setAttr('pinky_metacarpal_r.ty', -0.007600928278)
            cmds.setAttr('pinky_metacarpal_r.tz', -3.036237547)
            cmds.setAttr('pinky_metacarpal_r.rx', -3.57355303)
            cmds.setAttr('pinky_metacarpal_r.ry', -23.74537082)
            cmds.setAttr('pinky_metacarpal_r.rz', 1.114928381)
            cmds.setAttr('pinky_01_r.tx', -5.31318387)
            cmds.setAttr('pinky_01_r.ty', -9.765498987e-08)
            cmds.setAttr('pinky_01_r.tz', 1.512203163e-08)
            cmds.setAttr('pinky_01_r.rx', 0.3692431844)
            cmds.setAttr('pinky_01_r.ry', 8.26459133)
            cmds.setAttr('pinky_01_r.rz', 31.0056142)
            cmds.setAttr('pinky_02_r.tx', -3.473259846)
            cmds.setAttr('pinky_02_r.ty', -6.509380057e-08)
            cmds.setAttr('pinky_02_r.tz', 3.831791995e-09)
            cmds.setAttr('pinky_02_r.rx', -0.0815343423)
            cmds.setAttr('pinky_02_r.ry', 2.325205229)
            cmds.setAttr('pinky_02_r.rz', 19.58178749)
            cmds.setAttr('pinky_03_r.tx', -2.064882359)
            cmds.setAttr('pinky_03_r.ty', -3.879509336e-08)
            cmds.setAttr('pinky_03_r.tz', 1.255000548e-09)
            cmds.setAttr('pinky_03_r.rx', -0.2876547114)
            cmds.setAttr('pinky_03_r.ry', 3.075761561)
            cmds.setAttr('pinky_03_r.rz', 10.2161436)
            cmds.setAttr('ring_metacarpal_r.tx', -2.101583472)
            cmds.setAttr('ring_metacarpal_r.ty', 0.3230899534)
            cmds.setAttr('ring_metacarpal_r.tz', -1.9974456)
            cmds.setAttr('ring_metacarpal_r.rx', -7.861503006)
            cmds.setAttr('ring_metacarpal_r.ry', -13.45615558)
            cmds.setAttr('ring_metacarpal_r.rz', -0.9999394562)
            cmds.setAttr('ring_01_r.tx', -5.164994252)
            cmds.setAttr('ring_01_r.ty', -9.690121772e-08)
            cmds.setAttr('ring_01_r.tz', 6.480775028e-09)
            cmds.setAttr('ring_01_r.rx', -2.344532034)
            cmds.setAttr('ring_01_r.ry', -3.404822312)
            cmds.setAttr('ring_01_r.rz', 28.72885897)
            cmds.setAttr('ring_02_r.tx', -4.677883415)
            cmds.setAttr('ring_02_r.ty', -8.777911376e-08)
            cmds.setAttr('ring_02_r.tz', 2.911603847e-09)
            cmds.setAttr('ring_02_r.rx', 0.5809467113)
            cmds.setAttr('ring_02_r.ry', 0.8964110923)
            cmds.setAttr('ring_02_r.rz', 26.29682116)
            cmds.setAttr('ring_03_r.tx', -2.375662452)
            cmds.setAttr('ring_03_r.ty', -4.462007297e-08)
            cmds.setAttr('ring_03_r.tz', 5.261187042e-10)
            cmds.setAttr('ring_03_r.rx', -2.064908024)
            cmds.setAttr('ring_03_r.ry', -3.051369512)
            cmds.setAttr('ring_03_r.rz', 17.15889502)
            cmds.setAttr('middle_metacarpal_r.tx', -2.687285368)
            cmds.setAttr('middle_metacarpal_r.ty', 0.1830503853)
            cmds.setAttr('middle_metacarpal_r.tz', -0.07356194606)
            cmds.setAttr('middle_metacarpal_r.rx', -11.86547912)
            cmds.setAttr('middle_metacarpal_r.ry', -8.851353255)
            cmds.setAttr('middle_metacarpal_r.rz', -4.666922195)
            cmds.setAttr('middle_01_r.tx', -5.795294447)
            cmds.setAttr('middle_01_r.ty', -1.081811547e-07)
            cmds.setAttr('middle_01_r.tz', -2.063188731e-09)
            cmds.setAttr('middle_01_r.rx', 0.05612160336)
            cmds.setAttr('middle_01_r.ry', -7.024276828)
            cmds.setAttr('middle_01_r.rz', 33.01489862)
            cmds.setAttr('middle_02_r.tx', -4.845106817)
            cmds.setAttr('middle_02_r.ty', -9.102241449e-08)
            cmds.setAttr('middle_02_r.tz', 4.73808548e-09)
            cmds.setAttr('middle_02_r.rx', -0.3459153549)
            cmds.setAttr('middle_02_r.ry', -5.152910316)
            cmds.setAttr('middle_02_r.rz', 27.82389113)
            cmds.setAttr('middle_03_r.tx', -2.717296489)
            cmds.setAttr('middle_03_r.ty', -5.070629072e-08)
            cmds.setAttr('middle_03_r.tz', 1.829989493e-09)
            cmds.setAttr('middle_03_r.rx', -0.177279641)
            cmds.setAttr('middle_03_r.ry', -1.052347764)
            cmds.setAttr('middle_03_r.rz', 18.50757266)
            cmds.setAttr('lowerarm_twist_01_r.tx', -24.00681686)
            cmds.setAttr('lowerarm_twist_01_r.ty', 8.526512829e-14)
            cmds.setAttr('lowerarm_twist_01_r.tz', 4.475084125e-07)
            cmds.setAttr('lowerarm_twist_01_r.rx', -77.84381298)
            cmds.setAttr('lowerarm_twist_01_r.ry', 0)
            cmds.setAttr('lowerarm_twist_01_r.rz', 0)
            cmds.setAttr('upperarm_twist_01_r.tx', -4.263256415e-14)
            cmds.setAttr('upperarm_twist_01_r.ty', 6.661338148e-16)
            cmds.setAttr('upperarm_twist_01_r.tz', -2.842170943e-14)
            cmds.setAttr('upperarm_twist_01_r.rx', 0)
            cmds.setAttr('upperarm_twist_01_r.ry', 0)
            cmds.setAttr('upperarm_twist_01_r.rz', 0)
            cmds.setAttr('breast_l.tx', 5.511614774)
            cmds.setAttr('breast_l.ty', -6.953179133)
            cmds.setAttr('breast_l.tz', -7.710329245)
            cmds.setAttr('breast_l.rx', -1.724428375)
            cmds.setAttr('breast_l.ry', 155.0585926)
            cmds.setAttr('breast_l.rz', 88.18022323)
            cmds.setAttr('breast_r.tx', 5.511614774)
            cmds.setAttr('breast_r.ty', -6.953179133)
            cmds.setAttr('breast_r.tz', 7.710331862)
            cmds.setAttr('breast_r.rx', 1.72442931)
            cmds.setAttr('breast_r.ry', -155.0585895)
            cmds.setAttr('breast_r.rz', 88.18022323)
            cmds.setAttr('thigh_l.tx', 9.555135727)
            cmds.setAttr('thigh_l.ty', -10.40276241)
            cmds.setAttr('thigh_l.tz', 0.4112044871)
            cmds.setAttr('thigh_l.rx', -89.00055191)
            cmds.setAttr('thigh_l.ry', -0.06219345487)
            cmds.setAttr('thigh_l.rz', 89.81255673)
            cmds.setAttr('calf_l.tx', -39.69218063)
            cmds.setAttr('calf_l.ty', 1.16351373e-13)
            cmds.setAttr('calf_l.tz', 3.801403636e-13)
            cmds.setAttr('calf_l.rx', 0)
            cmds.setAttr('calf_l.ry', 0)
            cmds.setAttr('calf_l.rz', -7.822613865)
            cmds.setAttr('calf_twist_01_l.tx', -42.09862142)
            cmds.setAttr('calf_twist_01_l.ty', 6.418461318e-10)
            cmds.setAttr('calf_twist_01_l.tz', 1.440331125e-07)
            cmds.setAttr('calf_twist_01_l.rx', -0.9174649231)
            cmds.setAttr('calf_twist_01_l.ry', 0)
            cmds.setAttr('calf_twist_01_l.rz', 0)
            cmds.setAttr('foot_l.tx', -42.09862142)
            cmds.setAttr('foot_l.ty', 6.447065104e-10)
            cmds.setAttr('foot_l.tz', 1.440331303e-07)
            cmds.setAttr('foot_l.rx', -0.8391769687)
            cmds.setAttr('foot_l.ry', 0.5924180095)
            cmds.setAttr('foot_l.rz', 8.489112099)
            cmds.setAttr('ball_l.tx', -6.059318391)
            cmds.setAttr('ball_l.ty', -12.32535726)
            cmds.setAttr('ball_l.tz', -0.1148606275)
            cmds.setAttr('ball_l.rx', 0.7834203988)
            cmds.setAttr('ball_l.ry', 1.934618939)
            cmds.setAttr('ball_l.rz', -89.69025935)
            cmds.setAttr('thigh_twist_01_l.tx', 0)
            cmds.setAttr('thigh_twist_01_l.ty', 8.881784197e-16)
            cmds.setAttr('thigh_twist_01_l.tz', -1.776356839e-15)
            cmds.setAttr('thigh_twist_01_l.rx', 0)
            cmds.setAttr('thigh_twist_01_l.ry', 0)
            cmds.setAttr('thigh_twist_01_l.rz', 180)
            cmds.setAttr('thigh_r.tx', -9.555137634)
            cmds.setAttr('thigh_r.ty', -10.40276241)
            cmds.setAttr('thigh_r.tz', 0.4112044871)
            cmds.setAttr('thigh_r.rx', 90.99944728)
            cmds.setAttr('thigh_r.ry', 0.06220043646)
            cmds.setAttr('thigh_r.rz', -89.81255638)
            cmds.setAttr('calf_r.tx', 39.69218063)
            cmds.setAttr('calf_r.ty', 6.217248938e-15)
            cmds.setAttr('calf_r.tz', 7.105427358e-15)
            cmds.setAttr('calf_r.rx', 0)
            cmds.setAttr('calf_r.ry', 0)
            cmds.setAttr('calf_r.rz', -7.822600293)
            cmds.setAttr('calf_twist_01_r.tx', 42.09899907)
            cmds.setAttr('calf_twist_01_r.ty', 8.872092394e-09)
            cmds.setAttr('calf_twist_01_r.tz', 8.859979825e-07)
            cmds.setAttr('calf_twist_01_r.rx', -0.9174725096)
            cmds.setAttr('calf_twist_01_r.ry', 0)
            cmds.setAttr('calf_twist_01_r.rz', 0)
            cmds.setAttr('foot_r.tx', 42.09899907)
            cmds.setAttr('foot_r.ty', 8.879165847e-09)
            cmds.setAttr('foot_r.tz', 8.859979843e-07)
            cmds.setAttr('foot_r.rx', 0.839183925)
            cmds.setAttr('foot_r.ry', -0.5924231599)
            cmds.setAttr('foot_r.rz', -171.5108947)
            cmds.setAttr('ball_r.tx', -6.059318377)
            cmds.setAttr('ball_r.ty', -12.32535725)
            cmds.setAttr('ball_r.tz', 0.1148626952)
            cmds.setAttr('ball_r.rx', -0.7834252392)
            cmds.setAttr('ball_r.ry', -1.934624341)
            cmds.setAttr('ball_r.rz', -89.69025918)
            cmds.setAttr('thigh_twist_01_r.tx', 1.421085472e-14)
            cmds.setAttr('thigh_twist_01_r.ty', 0)
            cmds.setAttr('thigh_twist_01_r.tz', 3.552713679e-15)
            cmds.setAttr('thigh_twist_01_r.rx', 0)
            cmds.setAttr('thigh_twist_01_r.ry', 0)
            cmds.setAttr('thigh_twist_01_r.rz', -180)
            cmds.setAttr('ik_foot_root.tx', 0)
            cmds.setAttr('ik_foot_root.ty', 0)
            cmds.setAttr('ik_foot_root.tz', 0)
            cmds.setAttr('ik_foot_root.rx', 0)
            cmds.setAttr('ik_foot_root.ry', 0)
            cmds.setAttr('ik_foot_root.rz', 0)
            cmds.setAttr('ik_foot_l.tx', 9.188915965)
            cmds.setAttr('ik_foot_l.ty', 8.152026726)
            cmds.setAttr('ik_foot_l.tz', -2.05444174)
            cmds.setAttr('ik_foot_l.rx', -89.84597373)
            cmds.setAttr('ik_foot_l.ry', 0.614504887)
            cmds.setAttr('ik_foot_l.rz', 89.23182075)
            cmds.setAttr('ik_foot_r.tx', -9.188913786)
            cmds.setAttr('ik_foot_r.ty', 8.151651987)
            cmds.setAttr('ik_foot_r.tz', -2.05449359)
            cmds.setAttr('ik_foot_r.rx', -90.15401844)
            cmds.setAttr('ik_foot_r.ry', 0.6145047738)
            cmds.setAttr('ik_foot_r.rz', 90.76818464)
            cmds.setAttr('ik_hand_root.tx', -51.13765379)
            cmds.setAttr('ik_hand_root.ty', 101.3774832)
            cmds.setAttr('ik_hand_root.tz', 0.7870470358)
            cmds.setAttr('ik_hand_root.rx', 6.893915732)
            cmds.setAttr('ik_hand_root.ry', 16.43339643)
            cmds.setAttr('ik_hand_root.rz', 43.05058753)
            cmds.setAttr('ik_hand_gun.tx', -7.105427358e-15)
            cmds.setAttr('ik_hand_gun.ty', -1.421085472e-14)
            cmds.setAttr('ik_hand_gun.tz', 1.776356839e-15)
            cmds.setAttr('ik_hand_gun.rx', 5.888995777e-15)
            cmds.setAttr('ik_hand_gun.ry', -8.348956039e-15)
            cmds.setAttr('ik_hand_gun.rz', 8.746525374e-15)
            cmds.setAttr('ik_hand_r.tx', 0)
            cmds.setAttr('ik_hand_r.ty', -2.842170943e-14)
            cmds.setAttr('ik_hand_r.tz', 3.552713679e-15)
            cmds.setAttr('ik_hand_r.rx', 0)
            cmds.setAttr('ik_hand_r.ry', 0)
            cmds.setAttr('ik_hand_r.rz', 0)
            cmds.setAttr('ik_hand_l.tx', 71.68471493)
            cmds.setAttr('ik_hand_l.ty', -66.77496377)
            cmds.setAttr('ik_hand_l.tz', 29.37081096)
            cmds.setAttr('ik_hand_l.rx', 24.18268428)
            cmds.setAttr('ik_hand_l.ry', -156.2616694)
            cmds.setAttr('ik_hand_l.rz', 88.90585289)
