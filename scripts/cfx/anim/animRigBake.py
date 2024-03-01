import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import cfx.returnObjectWithAttr as roa
import cfx.anim.ikFkSwitcher as ikfks
import cfx.metaSystem as rmeta
import cfx.returnUseableChannels as ruc
import cfx.getDistances as gd

#needs studio library installed for loading the characters default pose
#import mutils

import glob
import os
import fnmatch

class animRigBake(object):
    
    def __init__(self):
        
        self.__theNameSpace = 'anim'

        self.__locsMade = []
        self.__locsMadeParent = []
        self.__allConstraints = []
        self.__disconnects = []

        self.__rigFileVar = 'lastUsedRig'
        self.__animFileVar = 'lastUsedAnim'
        self.__animBatchFileVar = 'lastUsedBatchAnim'
        self.__rigNamespaceVar = 'lastUsedRigNamespace'
        self.__retargetFileVar = 'retargetterFile'
        self.__animLayerFileVar = 'animLayerFileVar'
        self.__boolVars = 'boolVars'

        self.__bdvar = 'bdvar'
        self.__fbxvar = 'fbxvar'
        self.__plalvar = 'plalvar'
        self.__btrvar = 'btrvar'
        self.__bikfkvar = 'bikfkvar'
        self.__ldavar = 'ldavar'
        self.__ervar = 'ervar'

        self.__nameSpaces = ['HeroDiver']

        #modules
        self.__attrFinder = roa.returnObjectWithAttr()
        self.__switcher = ikfks.ikFkSwitcher()
        self.__meta = rmeta.metaSystem()
        self.__distance = gd.getDistances()

        self.__doSubDirectories = True

        #pose testing information for default pose
        self.__jointPoseTest = 'hand_l'
        self.__jointPoseDistanceTest = 1.0

    #bakes animation from mocap file to animation rig
    def bakeToRig(self, rigFile, animationFile, bakeToExisting = False):

        isAutoKey = cmds.autoKeyframe(query = 1, state = 1)

        if isAutoKey:
            cmds.autoKeyframe(state = 0)

        if not bakeToExisting:
            cmds.file(new=1,force=1)
            cmds.currentUnit( time='ntsc' )

            print('Baking to Rig: ', animationFile)

            cmds.file(animationFile ,i=True,ra = True, mergeNamespacesOnClash = True, ignoreVersion = True, namespace = ":")

            #look for pose file incase there is no skinning data to revert to default pose.
            filePath = os.path.dirname(rigFile)
            self.poseFiles = glob.glob(filePath+"/*.mel")
            print('POSE FILES**********************')
            print(filePath)
            print(self.poseFiles)

            cmds.select(all=1)
            #self.remove_namespaces()
            self.deleteAllNS()

            cmds.viewFit( all=True )
            self.mocapSourceMeta = self.__meta.findMeta('mocapSource')
            mocapSourceJoints=[]
            if len(self.mocapSourceMeta) != 1:
                #TEMP HACK for taking in animation files that dont have meta data
                if cmds.objExists("root"):
                    self.rootToMove = "root"
                elif cmds.objExists("pelvis"):
                    self.rootToMove = "pelvis"
                elif cmds.objExists("*:root"):
                    cmds.select("*:root")
                    self.rootToMove = cmds.ls(sl=1)[0]

                cmds.select(self.rootToMove,hi=1)
                mocapSourceJoints = cmds.ls(sl=1)
                print('mocapSourceJoints: ', mocapSourceJoints)
            else:
                print('Found mocapSource: ', self.mocapSourceMeta[0])
                self.rootToMove = cmds.listConnections(self.mocapSourceMeta[0]+'.rootJoint',s=0,d=1)[0]
                mocapSourceJoints = cmds.listConnections(self.mocapSourceMeta[0]+'.allJoints', s=0,d=1)

            cmds.select(self.rootToMove,hi=1)

            theGroup = cmds.group(em=1,n='importedFbx')
            cmds.parent(self.rootToMove, theGroup)
            meshes = cmds.ls(type = 'mesh')
            if len(meshes) > 0:
                for mesh in meshes:
                    theParent = cmds.listRelatives(mesh, p=1)
                    try:
                        cmds.parent(theParent[0], theGroup)
                    except:
                        pass

            joints = []
            for jnt in mocapSourceJoints:
                joints.append(jnt.split(":")[-1])

            #rigNameSpace = self.__nameSpaces[0]
            rigNameSpace = cmds.optionMenu( self.rigNamespaceText,q=True, v=True)

            setupData = self.__meta.findMeta('mocapSource')
            if len(setupData) > 0:
                charName = cmds.getAttr(setupData[0]+'.setupData')
                if charName != '':
                    rigNameSpace = charName

            animNameSpace = mocapSourceJoints[0].rpartition(':')[0]
            print('animNameSpace: ', animNameSpace, ' rigNameSpace: ', rigNameSpace)
            print('rigFile: ', rigFile)
            cmds.file(rigFile ,r=True, mergeNamespacesOnClash = False, namespace = rigNameSpace)
            
            #set eye controller to parent to head
            #cmds.setAttr(rigNameSpace+":head_eyeSpace_Grp_CTRL.mainOrHead", 1)

            mocapDestinationMeta = self.__meta.findMeta('character')
            if len(mocapDestinationMeta) == 0:
                cmds.error('Must be built with metaSystem, missing character setupData')

            mocapRigNameSpace = mocapDestinationMeta[0].rpartition(':')[0]

            usePose = None
            print('len(self.poseFiles): ', len(self.poseFiles))
            if len(self.poseFiles) > 0:
                if len(self.poseFiles) == 1:
                    usePose = self.poseFiles[0]
                else:
                    for pf in self.poseFiles:
                        print('TESTING POSE FILE: ', pf)
                        melStatement = "source \""+pf.replace('\\', '/')+"\";"
                        mel.eval(melStatement)
                        testDist = self.__distance.between(self.__jointPoseTest, mocapRigNameSpace+':'+self.__jointPoseTest)
                        print('TESTDIST IS: ', testDist)
                        if testDist < self.__jointPoseDistanceTest:
                            print('Using POSEFILE: ', pf)
                            usePose = pf
                            break

            for jnt in joints:
                destJnt = mocapRigNameSpace+":"+jnt
                if cmds.objExists(destJnt+'.mocapConnectTo'):
                    print(animNameSpace+":"+jnt, destJnt)
                    connectTo = cmds.listConnections(destJnt+'.mocapConnectTo',s=1,d=0)
                    if usePose:
                        #for pf in self.poseFiles:
                        self.constrainAvailableChannels(animNameSpace+":"+jnt, connectTo[0], self.rootToMove, usePose)
                    else:
                        self.constrainAvailableChannels(animNameSpace+":"+jnt, connectTo[0], self.rootToMove)

                    mocapTransferOptions = cmds.getAttr(destJnt+'.mocapConOptions')
                    if mocapTransferOptions != "":
                        mocapTransferOptionsSplit = mocapTransferOptions.split(' ')
                        cmds.xform(mocapRigNameSpace+':'+mocapTransferOptionsSplit[0] ,ws=True,m=(cmds.xform(jnt,q=True,ws=True,m=True)))
                        jntParent = cmds.listRelatives(jnt,p=1)[0]
                        cmds.parentConstraint(jntParent, mocapRigNameSpace+':'+mocapTransferOptionsSplit[0], mo=1)
                        cmds.orientConstraint(jnt, mocapRigNameSpace+':'+mocapTransferOptionsSplit[1], mo=0)

                        self.__disconnects.append([mocapRigNameSpace+':'+mocapTransferOptionsSplit[1]+'.rx', mocapRigNameSpace+':'+mocapTransferOptionsSplit[2]+'.'+mocapTransferOptionsSplit[3]])
                        self.__disconnects.append([mocapRigNameSpace+':'+mocapTransferOptionsSplit[1]+'.ry', mocapRigNameSpace+':'+mocapTransferOptionsSplit[2]+'.'+mocapTransferOptionsSplit[4]])
                        self.__disconnects.append([mocapRigNameSpace+':'+mocapTransferOptionsSplit[1]+'.rx', mocapRigNameSpace+':'+mocapTransferOptionsSplit[2]+'.'+mocapTransferOptionsSplit[5]])

                        cmds.connectAttr(mocapRigNameSpace+':'+mocapTransferOptionsSplit[1]+'.rx', mocapRigNameSpace+':'+mocapTransferOptionsSplit[2]+'.'+mocapTransferOptionsSplit[3], f=1)
                        cmds.connectAttr(mocapRigNameSpace+':'+mocapTransferOptionsSplit[1]+'.ry', mocapRigNameSpace+':'+mocapTransferOptionsSplit[2]+'.'+mocapTransferOptionsSplit[4], f=1)
                        cmds.connectAttr(mocapRigNameSpace+':'+mocapTransferOptionsSplit[1]+'.rz', mocapRigNameSpace+':'+mocapTransferOptionsSplit[2]+'.'+mocapTransferOptionsSplit[5], f=1)
        
            #new style will attach to the toeTaps and others based on the rig having the toe transfer groups    
            #transferToes = cmds.ls('*_transfer', type = 'transform')
            transferToes = self.__attrFinder.all("orderOfAttach", "*")
            orientConDelete = []
            if len(transferToes) > 0:
                for tt in transferToes:
                    ttNs = tt.rpartition(':')[0]
                    ttSource = tt.rpartition(':')[-1].replace('_transfer','')
                    orientConDelete.append(cmds.orientConstraint(ttSource,tt,mo=1))
                    toeTransferOptions = cmds.getAttr(tt+'.orderOfAttach')
                    toeTransferOptionsSplit = toeTransferOptions.split(' ')
                    cmds.connectAttr(tt+'.rx', ttNs+':'+toeTransferOptionsSplit[0], f=1)
                    cmds.connectAttr(tt+'.ry', ttNs+':'+toeTransferOptionsSplit[1], f=1)
                    cmds.connectAttr(tt+'.rz', ttNs+':'+toeTransferOptionsSplit[2], f=1)

                    self.__disconnects.append([tt+'.rx', ttNs+':'+toeTransferOptionsSplit[0]])
                    self.__disconnects.append([tt+'.ry', ttNs+':'+toeTransferOptionsSplit[1]])
                    self.__disconnects.append([tt+'.rz', ttNs+':'+toeTransferOptionsSplit[2]])

        cmds.currentUnit( time='ntsc' )

        #set all ikFk to IK
        ikSystems = self.__meta.findMeta('ikFkSystem')
        ikSplines = self.__meta.findMeta('splineIk')

        print('ikSystems, ikSplines: ', ikSystems, ikSplines)
        for iks in ikSystems:
            ikSwitch = cmds.listConnections(iks+'.theSwitchControl',s=0,d=1)
            if not ikSwitch:
                cmds.error('No IK/FK switch attached to meta system', iks)

            cmds.setAttr(ikSwitch[0]+".fkIk", 1)

        controlsToBake = self.returnCtrlsToBake()

        #replace this with meta system
        topTransform = self.__attrFinder.all("topTransform", "*")
        theNamespace = topTransform[0].split(':')
        del(theNamespace[-1])
        addNamespace = ':'.join(theNamespace)

        allKeframeObjects = cmds.ls(type=('animCurve','animCurveTA','animCurveTL','animCurveTT','animCurveTU','animCurveUA','animCurveUL','animCurveUT','animCurveUU'))
        values = cmds.keyframe(allKeframeObjects,q=True,tc=True)

        if values is None:
            cmds.error('Scene has no keyframes: '+animationFile)
            
        cmds.playbackOptions(min=min(values), max=max(values))

        self.minTime = cmds.playbackOptions(q=True,min=True)
        self.maxTime = cmds.playbackOptions(q=True,max=True)

        if self.minTime < -1000:
            self.minTime = -1

        for con in self.__allConstraints:
            if cmds.objExists(con):
                cmds.delete(con)

        self.__nsCtrlsWithAttr = []
        
        for ctrl in controlsToBake:
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


        #if cmds.checkBox(self.__preLoadAnimlayer,q=1,v=1):
            #animLayerFile = cmds.textField(self.animLayerFileText, q=True, text=True)
            #cmds.file(animLayerFile ,i=True,ra = True, mergeNamespacesOnClash = True, ignoreVersion = True, namespace = ":")

        cmds.bakeResults(controlsToBake, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)

        cmds.delete(theGroup)

        animCurves = []
        for ctrl in self.__nsCtrlsWithAttr:
            tempCurves = cmds.listConnections(ctrl, s=1, d=0)
            for tc in tempCurves:
                animCurves.append(tc)

        cmds.filterCurve(animCurves)

        for disc in self.__disconnects:
            try:
                cmds.disconnectAttr(disc[0], disc[1])
            except:
                pass
            

        if not cmds.objExists('gameExporterPreset2'):
            mel.eval('gameFbxExporter;')

        if cmds.window("gameExporterWindow", exists = True):
            cmds.deleteUI("gameExporterWindow")

        animNode = 'gameExporterPreset2'

        clipName = animationFile.replace('_onMocapSkeleton.ma', '').split('/')[-1].replace('FBX_', 'A_')
        print('clipName: ', clipName)
        if not clipName.startswith('A_'):
            if '\\' in clipName:
                clipName = clipName.split('\\')[-1]
            clipName = 'A_'+clipName

        if clipName.endswith('.FBX'):
            clipName = clipName.replace('.FBX','')

        originalPath = animationFile.split('\\') 
        filePathList = animationFile.split('/')
        print('filePathList pre ', filePathList)

        filePathList[-1] = filePathList[-1].split('\\')[0]

        if filePathList[-1].endswith('FBX'):
            filePathList.insert(-1,'retargetted')

        if filePathList[-1].endswith('.ma'):
            filePathList = filePathList[:-1]

        print('filePathList ', filePathList)
        joinedPath = '/'.join(filePathList)
        justPath = os.path.dirname(joinedPath)

        cmds.setAttr(animNode+'.exp', justPath, type='string')

        cmds.setAttr(animNode+'.ac[0].acs', self.minTime)
        cmds.setAttr(animNode+'.ac[0].ace', self.maxTime)
        cmds.setAttr(animNode+'.ac[0].acn', clipName, type='string')

        animFilePath = justPath+'/'+clipName+'.ma'
        print('animFilePath: ', animFilePath)

        cmds.currentUnit( time='ntsc' )
        cmds.file(rename=animFilePath)
        cmds.file(save=1,type='mayaAscii', f=1) 

        if isAutoKey:
            cmds.autoKeyframe(state = 1)

    #this takes a skeletal animation retarget file and bakes animation and cleans up scene
    def retargetToRigMocapSkelton(self, theFile, retargetFile, addDirectory = None):

        cmds.currentUnit( time='ntsc' )
        cmds.file(retargetFile ,o=True, f=1)
        cmds.file(theFile ,i=True,ra = True, mergeNamespacesOnClash = True, ignoreVersion = True, type = "FBX", namespace = ":")
        cmds.currentUnit( time='ntsc' )

        mocapSetupData = self.__meta.findMeta('mocapSource')
        if len(mocapSetupData) == 0:
            cmds.error('Must be built with Meta system, missing mocapSource')
        bakeJoints = cmds.listConnections(mocapSetupData[0]+'.allJoints',s=0,d=1)

        allKeframeObjects = cmds.ls(type=('animCurve','animCurveTA','animCurveTL','animCurveTT','animCurveTU','animCurveUA','animCurveUL','animCurveUT','animCurveUU'))

        if len(allKeframeObjects) > 0:
            values = cmds.keyframe(allKeframeObjects,q=True,tc=True)

            cmds.playbackOptions(min=min(values), max=max(values))

            self.minTime = cmds.playbackOptions(q=True,min=True)
            self.maxTime = cmds.playbackOptions(q=True,max=True)

            if self.minTime < -1000:
                self.minTime = -1

            cmds.bakeResults(bakeJoints, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)

            objsToDelete = ['Reference', 'animBot', 'def', 'GEO', '|root']

            #new way to find source animation skeleton for cleanup
            fromMeta = cmds.listConnections(mocapSetupData[0]+'.deletes')

            if len(fromMeta) > 0:
                for otd in fromMeta:
                    objsToDelete.append(otd)

            if cmds.objExists(mocapSetupData[0]+'.objectsToDelete'):
                moreObjsToDelete = cmds.listConnections(mocapSetupData[0]+'.objectsToDelete', s=0, d=1)
                if len(moreObjsToDelete) > 0:
                    for motd in moreObjsToDelete:
                        objsToDelete.append(motd)

            for otd in objsToDelete:
                if cmds.objExists(otd):
                    cmds.delete(otd)

            #hack put in for retarget files that need a namespace
            worldNode = self.__attrFinder.all("autoSetups", "world")
            if len(worldNode) > 0:
                splitWorld = worldNode[0].split(':')
                if len(splitWorld) > 1:
                    cmds.select(worldNode[0],r=1)
                    #self.remove_namespaces()
                    self.deleteAllNS()

            newFilename = theFile.split('.')
            newFilename[0] = newFilename[0]+'_onMocapSkeleton'
            if 'fbx' in newFilename[1]:
                newFilename[1] = newFilename[1].replace('fbx','ma')
            if 'FBX' in newFilename[1]:
                newFilename[1] = newFilename[1].replace('FBX','ma')

            changedName = '.'.join(newFilename)
            changedName = changedName.replace('\\','/')

            if addDirectory:
                splitChangedName = changedName.split('/')
                splitChangedName.insert( -1, addDirectory)
                changedName = '/'.join(splitChangedName)
                justDir = os.path.dirname(changedName)

                if not os.path.exists(justDir):
                    os.mkdir(justDir)

            #some cleanup, remove namespace
            #self.remove_namespaces()
            self.deleteAllNS()


            """
            cmds.namespace(setNamespace=':')
            namespacesToClear = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
            for nstcl in namespacesToClear:
                if nstcl not in ['shared', 'UI']:
                    objs = cmds.namespaceInfo(nstcl, listNamespace=1)
                    if objs:
                        for obj in objs:
                            if cmds.objExists(obj):
                                cmds.rename(obj, obj.replace(nstcl+':',''))

                    cmds.namespace(rm=nstcl)
            """
            if not cmds.objExists('gameExporterPreset2'):
                mel.eval('gameFbxExporter;')

            if cmds.window("gameExporterWindow", exists = True):
                cmds.deleteUI("gameExporterWindow")

            animNode = 'gameExporterPreset2'

            clipName = changedName.replace('_onMocapSkeleton.ma', '').split('/')[-1].replace('FBX_', 'A_')
            if not clipName.startswith('A_'):
                if '\\' in clipName:
                    clipName = clipName.split('\\')[-1]
                clipName = 'A_'+clipName
            originalPath = changedName.split('\\') 
            filePathList = changedName.split('/')
            del(filePathList[-1])
            joinedPath = '/'.join(filePathList)
            print('joinedPath: ', joinedPath)
            cmds.setAttr(animNode+'.exp', os.path.dirname(originalPath[0]), type='string')

            cmds.setAttr(animNode+'.ac[0].acs', self.minTime)
            cmds.setAttr(animNode+'.ac[0].ace', self.maxTime)
            cmds.setAttr(animNode+'.ac[0].acn', clipName, type='string')
            print('animNode: ',animNode, clipName)

            cmds.currentUnit( time='ntsc' )
            cmds.file(rename=changedName)
            cmds.file(save=1,type='mayaAscii', f=1) 
            print('changedName: ',changedName)
            return changedName
        else:
            print("No animation in file: ", retargetFile)
            self.badFiles.append(retargetFile)

        return self.badFiles

    #sets up Game Exporter nodes from mayas game exporter
    def exportFbxFromRig(self):
        theAnimNode=None
        animNodes = []
        exportNodes = cmds.ls(type='gameFbxExporter')
        print('exportNodes: ', exportNodes)
        for eno in exportNodes:
            exportType = cmds.getAttr(eno+'.exportTypeIndex')
            if exportType == 2:
                animNodes.append(eno)
        print('animNodes: ', animNodes)
        animClips = 0        
        for an in animNodes:
            numClips = cmds.getAttr(an+'.ac', size=True)
            print(numClips)
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
            mel.eval('FBXExportUpAxis \"y\";')

            #set the maya scene up    
            cmds.playbackOptions(e=True, minTime = clipStart, maxTime = clipEnd)

            animExportSets = cmds.ls('*:animationExportSet')
            if len(animExportSets) == 1:
                self.animSet = animExportSets[0]

            animExportSets = cmds.ls('animationExportSet')
            if len(animExportSets) == 1:
                self.animSet = animExportSets[0]

            animExportSets = cmds.ls('*:*:animationExportSet')
            if len(animExportSets) == 1:
                self.animSet = animExportSets[0]
            #else:
                #cmds.error('SCENE HAS MORE THAN ONE CHARACTER')

            cmds.select(self.animSet, replace = True)
            
            print('Exporting Engine Animation: ', cle)
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
        if len(metaNodesRet) == 0:
            cmds.error('No meta nodes in scene, rig needs to be built with CFX system')
            
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

    def bakeToIk(self, bakeRange, iks = None):

        allIk = {}

        metaNodesRet = self.__meta.findMeta('ikFkSystem')
        for mnr in metaNodesRet:
            switchCtrl = cmds.listConnections(mnr+'.theSwitchControl',s=0,d=1)[0]
            ikTrn = cmds.listConnections(mnr+'.ikTrnControl', s=0,d=1)[0]
            pvTrn = cmds.listConnections(mnr+'.thePv', s=0,d=1)[0]
            allIk[switchCtrl] = [ikTrn, pvTrn]

        #currentFrame = bakeRange[0]
        
        for frame in range(bakeRange[0], bakeRange[1]):
            cmds.currentTime(frame)
            for sw in allIk.keys():
                self.__switcher.swap(sw)
                cmds.setKeyframe(allIk[sw])
                cmds.setAttr(sw+'.fkIk', 0)

    def bakeIt(self):

        self.minTime = cmds.playbackOptions(q=True,min=True)
        self.maxTime = cmds.playbackOptions(q=True,max=True)

        bakeTime = str(self.minTime)+':'+str(self.maxTime)

        cmds.bakeResults(self.__bakeJoints, simulation = True, t = (self.minTime, self.maxTime), sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True, sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, bakeOnOverrideLayer =False, minimizeRotation = True, controlPoints = False, shape = False)
        
    def animBakeGUI_V2(self):

        if cmds.window("bakeAnimationGUI", exists = True):
            cmds.deleteUI("bakeAnimationGUI")
        
        windowWidth = 600
        windowHeight = 700
        
        window = cmds.window("bakeAnimationGUI", title = "Bake Animation GUI", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = True)

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
        cmds.text(label="The Mocap retarget file")
        cmds.text(label="Locate")
        self.retargetFileText = cmds.textField("retargetFileLoc")
        cmds.button(label = "...", c=self.setRetargetFileLocation)
        cmds.text(label="Anim Layer to load")
        cmds.text(label="Locate")
        self.animLayerFileText = cmds.textField("animLayerFileLoc")
        cmds.button(label = "...", c=self.setAnimLayerFileLocation)

        #need to get vars before creating buttons to set them on creation
        if not cmds.optionVar(exists =self.__bdvar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__bdvar, 1))

        if not cmds.optionVar(exists =self.__fbxvar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__fbxvar, 0))

        if not cmds.optionVar(exists =self.__plalvar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__plalvar, 0))

        if not cmds.optionVar(exists =self.__btrvar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__btrvar, 1))

        if not cmds.optionVar(exists =self.__bikfkvar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__bikfkvar, 0))

        if not cmds.optionVar(exists =self.__ldavar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__ldavar, 0))

        if not cmds.optionVar(exists =self.__ervar):#if it doesn't exist, make it
            cmds.optionVar(iv=(self.__ervar, 1))

        self.__bakeDirectory = cmds.checkBox( label='Bake Whole Directory', v=cmds.optionVar( q = self.__bdvar ) , cc = self.updateBoolVar )
        #cmds.separator()
        self.__FbxToMocap = cmds.checkBox( label='Bake FBX to Mocap', v=cmds.optionVar( q = self.__fbxvar ) , cc = self.updateBoolVar )
        #self.__preLoadAnimlayer = cmds.checkBox( label='Pre Load Anim Layer', v=cmds.optionVar( q = self.__plalvar ) , cc = self.updateBoolVar )
        self.__bakeToRig = cmds.checkBox( label='Bake to Rig', v=cmds.optionVar( q = self.__btrvar ) , cc = self.updateBoolVar )
        self.__bakeIkFk = cmds.checkBox( label='Bake Ik To Fk', v=cmds.optionVar( q = self.__bikfkvar ) , cc = self.updateBoolVar )
        self.__loadAnimlayer = cmds.checkBox( label='Load Anim Layer', v=cmds.optionVar( q = self.__ldavar ) , cc = self.updateBoolVar )
        self.__exportFromRig = cmds.checkBox( label='Export From Rig', v=cmds.optionVar( q = self.__ervar ) , cc = self.updateBoolVar )
        cmds.button(label = "Bake Animation", c=self.getBakedV2)
        cmds.button(label = "Cancel", c=self.cancelBake)


        #update if it has been used
        if cmds.optionVar(exists =self.__rigFileVar):#if it doesn't exist, make it
            cmds.textField(self.rigFileText, e=True, text = cmds.optionVar( q = self.__rigFileVar ))

        if cmds.optionVar(exists =self.__animFileVar):#if it doesn't exist, make it
            cmds.textField(self.animFileText, e=True, text = cmds.optionVar( q = self.__animFileVar ))

        if cmds.optionVar(exists =self.__retargetFileVar):#if it doesn't exist, make it
            cmds.textField(self.retargetFileText, e=True, text = cmds.optionVar( q = self.__retargetFileVar ))


     
        cmds.showWindow(window)

        self.setRigNameSpaceText()
        
    def ikFkBakeGUI(self):

        if cmds.window("ikFkBakeGUI", exists = True):
            cmds.deleteUI("ikFkBakeGUI")
        
        windowWidth = 600
        windowHeight = 700
        
        window = cmds.window("ikFkBakeGUI", title = "Bake Ik<>Fk GUI", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = True)

        mainLayout = cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 400), (2, 200)] )
        self.bakeDirectionEnum = cmds.optionMenu( label='Bake Direction' )
        cmds.menuItem( label='Ik > Fk' )
        cmds.menuItem( label='Fk > Ik' )

        self.blankSpace = cmds.text(label="")

        self.bakeRangeBox = cmds.checkBox( label='Bake Whole range', v=1 , cc = self.updateBakeRange )
        self.blankSpace = cmds.text(label="")

        cmds.text(label="Frame Start")
        cmds.text(label="Frame End")
        self.frameStart = cmds.textField("frameStart", en = 1, cc = self.updateBakeStartIkFk)
        self.frameEnd = cmds.textField("frameEnd", en = 1, cc = self.updateBakeEndIkFk)

        cmds.button(label = "Bake!", c=self.bakeIkFkNow)
     
        self.updateBakeRange()

        cmds.showWindow(window)

    def updateBakeRange(self, *args):

        allKeframeObjects = cmds.ls(type=('animCurve','animCurveTA','animCurveTL','animCurveTT','animCurveTU','animCurveUA','animCurveUL','animCurveUT','animCurveUU'))

        if len(allKeframeObjects) > 0:
            values = cmds.keyframe(allKeframeObjects,q=True,tc=True)

            cmds.playbackOptions(min=min(values), max=max(values))

        self.minTime = cmds.playbackOptions(q=True,min=True)
        self.maxTime = cmds.playbackOptions(q=True,max=True)

        cmds.textField(self.frameStart, e=True, text = self.minTime)
        cmds.textField(self.frameEnd, e=True, text = self.maxTime)

        self.updateBakeRangeAvailable()

    def updateBakeRangeAvailable(self, *args):

        if cmds.textField(self.frameStart, q=True, en=1):
            cmds.textField(self.frameStart, e=True, en=0)
            cmds.textField(self.frameEnd, e=True,  en=0)
        else:
            cmds.textField(self.frameStart, e=True, en=1)
            cmds.textField(self.frameEnd, e=True,  en=1)

    def updateBakeStartIkFk(self, *args):
        self.minTime = float(cmds.textField(self.frameStart, q=True, text=1))
        print(self.minTime)

    def updateBakeEndIkFk(self, *args):    
        self.maxTime = float(cmds.textField(self.frameEnd, q=True, text=1))
        print(self.maxTime)

    def bakeIkFkNow(self, *args):

        bakeDirection = cmds.optionMenu(self.bakeDirectionEnum, q=1, v=1 )

        if bakeDirection == 'Ik > Fk':
            self.bakeToFk([int(self.minTime), int(self.maxTime)])
        else:
            self.bakeToIk([int(self.minTime), int(self.maxTime)])

    def updateBoolVar(self, *args):

        cmds.optionVar(iv=(self.__bdvar, cmds.checkBox(self.__bakeDirectory, q=1, v=1)))
        cmds.optionVar(iv=(self.__fbxvar, cmds.checkBox(self.__FbxToMocap, q=1, v=1)))
        #cmds.optionVar(iv=(self.__plalvar, cmds.checkBox(self.__preLoadAnimlayer, q=1, v=1)))
        cmds.optionVar(iv=(self.__btrvar, cmds.checkBox(self.__bakeToRig, q=1, v=1)))
        cmds.optionVar(iv=(self.__bikfkvar, cmds.checkBox(self.__bakeIkFk, q=1, v=1)))
        cmds.optionVar(iv=(self.__ldavar, cmds.checkBox(self.__loadAnimlayer, q=1, v=1)))
        cmds.optionVar(iv=(self.__ervar, cmds.checkBox(self.__exportFromRig, q=1, v=1)))

    def setRigLocation(self, *args):

        rigFileDialog = cmds.fileDialog2(cap = "Select Rig file", fm = 1, dialogStyle=2)

        cmds.optionVar(sv=(self.__rigFileVar, rigFileDialog[0]))
        cmds.textField(self.rigFileText, e=True, text = rigFileDialog[0])

        self.setRigNameSpaceText()

    def setRigNameSpaceText(self, *args):

        fileDialogText = cmds.textField(self.rigFileText, q=True, text = 1)

        if 'Oozume' in fileDialogText:
            cmds.optionMenu( self.rigNamespaceText,e=True, v='Oozume_brute')

        if 'Astronaut' in fileDialogText:
            cmds.optionMenu( self.rigNamespaceText,e=True, v='American_Astronaut')

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

        #animFileDialog = cmds.fileDialog2(cap = "Select Animation FBX file", fm = 2, dialogStyle=2)

        cmds.optionVar(sv=(self.__animBatchFileVar, animFileDialog[0]))
        cmds.textField(self.animBatchFileText, e=True, text = animFileDialog[0])


    def setRetargetFileLocation(self, *args):

        animFileDialog = cmds.fileDialog2(cap = "Select Animation FBX file", fm = 1, dialogStyle=2)

        cmds.optionVar(sv=(self.__retargetFileVar, animFileDialog[0]))
        cmds.textField(self.retargetFileText, e=True, text = animFileDialog[0])

    def setAnimLayerFileLocation(self, *args):

        animLayerFileDialog = cmds.fileDialog2(cap = "Select Animation Layer file", fm = 1, dialogStyle=2)

        cmds.optionVar(sv=(self.__animLayerFileVar,animLayerFileDialog[0]))
        cmds.textField(self.animLayerFileText, e=True, text = animLayerFileDialog[0])

    def getBakedV2(self, *args):

        #cmds.file(new=True,f=True)
        self.badFiles = []
        self.rigNs = cmds.optionMenu( self.rigNamespaceText,q=True, v=True)
        print('Setting rig namespace: ',self.rigNs)
        self.rigNsQuantity = cmds.textField(self.rigNamespaceQuantity, q=True, text=True)
        if self.rigNs == '':
            cmds.error('must set a namespace for the rig')
        else:
            self.rigNs = ':'+self.rigNs+'_'+self.rigNsQuantity

        self.animNs = self.rigNs+':mocap'

        self.__bakedFiles = []

        #get baked data
        FBXToMocap = cmds.checkBox(self.__FbxToMocap,q=1,v=1)
        bakeIkFk = cmds.checkBox(self.__bakeIkFk,q=1,v=1)
        bakeToRig = cmds.checkBox(self.__bakeToRig,q=1,v=1)
        importAnimLayer = cmds.checkBox(self.__loadAnimlayer,q=1,v=1)
        #preImportAnimLayer = cmds.checkBox(self.__preLoadAnimlayer,q=1,v=1)
        exportFromRig = cmds.checkBox(self.__exportFromRig,q=1,v=1)
        theAnimFileText = cmds.textField(self.animFileText, q=True, text=True)
        theRetargetFile = cmds.textField(self.retargetFileText, q=True, text=True)
        theRigFile = cmds.textField(self.rigFileText, q=True, text=True)

        filesToBake = []
        
        if FBXToMocap:
            if theAnimFileText.endswith('.fbx'):
                filesToBake.append(theAnimFileText)
                print('Baking Single File, ', filesToBake)
            else:
                #filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx")
                
                listOfFiles = list()
                for (dirpath, dirnames, filenames) in os.walk(cmds.textField(self.animFileText, q=True, text=True)):
                    listOfFiles += [os.path.join(dirpath, file) for file in filenames]

                for af in listOfFiles:
                    if af.endswith('.fbx') or af.endswith('.FBX'):
                        filesToBake.append(af)

                print('Baking Multiple, ', filesToBake)
            print('FBX files in dir, ', cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx", filesToBake)
        
        #else:
        if theAnimFileText.endswith('.ma') or theAnimFileText.endswith('.fbx') or theAnimFileText.endswith('.FBX'):
            filesToBake.append(theAnimFileText)
            print('Baking Single File, ', filesToBake)
        else:
            filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.ma")
            if len(filesToBake) == 0:
                if self.__doSubDirectories:
                    for root, dirnames, filenames in os.walk(cmds.textField(self.animFileText, q=True, text=True)):
                        for filename in fnmatch.filter(filenames, '*.fbx'):
                            filesToBake.append(os.path.join(root, filename))
                else:
                    filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx")
            if len(filesToBake) == 0:
                if self.__doSubDirectories:
                    for root, dirnames, filenames in os.walk(cmds.textField(self.animFileText, q=True, text=True)):
                        for filename in fnmatch.filter(filenames, '*.FBX'):
                            filesToBake.append(os.path.join(root, filename))
                else:
                    filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.FBX")
            print('Baking Multiple, ', filesToBake)
        print('MA files in dir, ', cmds.textField(self.animFileText, q=True, text=True)+"/*.ma", filesToBake)

        
        for ftb in filesToBake:
            cmds.file(new=1,force=1)
            if FBXToMocap:
                self.retargettedMocap = self.retargetToRigMocapSkelton(ftb , theRetargetFile, addDirectory = '_retargetted')
            if bakeToRig:
                cmds.file(new=1,force=1)
                #self.bakeToAnimRig(theRigFile, ftb)
                if FBXToMocap:
                    self.bakeToRig(theRigFile, self.retargettedMocap)
                else:
                    self.bakeToRig(theRigFile, ftb)
            if bakeIkFk:
                self.bakeToFk([int(self.minTime), int(self.maxTime)])
            if importAnimLayer:
                animLayerFile = cmds.textField(self.animLayerFileText, q=True, text=True)
                cmds.file(animLayerFile ,i=True,ra = True, mergeNamespacesOnClash = True, ignoreVersion = True, namespace = ":")
                
            if exportFromRig:
                self.exportFbxFromRig()

    def bakeIt(self, *args):

        #cmds.file(new=True,f=True)
        self.badFiles = []
        self.rigNs = cmds.optionMenu( self.rigNamespaceText,q=True, v=True)
        print('Setting rig namespace: ',self.rigNs)
        self.rigNsQuantity = cmds.textField(self.rigNamespaceQuantity, q=True, text=True)
        if self.rigNs == '':
            cmds.error('must set a namespace for the rig')
        else:
            self.rigNs = ':'+self.rigNs+'_'+self.rigNsQuantity

        self.animNs = self.rigNs+':mocap'

        self.__bakedFiles = []

        #get baked data
        FBXToMocap = cmds.checkBox(self.__FbxToMocap,q=1,v=1)
        bakeIkFk = cmds.checkBox(self.__bakeIkFk,q=1,v=1)
        bakeToRig = cmds.checkBox(self.__bakeToRig,q=1,v=1)
        importAnimLayer = cmds.checkBox(self.__loadAnimlayer,q=1,v=1)
        #preImportAnimLayer = cmds.checkBox(self.__preLoadAnimlayer,q=1,v=1)
        exportFromRig = cmds.checkBox(self.__exportFromRig,q=1,v=1)
        theAnimFileText = cmds.textField(self.animFileText, q=True, text=True)
        theRetargetFile = cmds.textField(self.retargetFileText, q=True, text=True)
        theRigFile = cmds.textField(self.rigFileText, q=True, text=True)

        filesToBake = []
        
        if FBXToMocap:
            if theAnimFileText.endswith('.fbx'):
                filesToBake.append(theAnimFileText)
                print('Baking Single File, ', filesToBake)
            else:
                #filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx")
                
                listOfFiles = list()
                for (dirpath, dirnames, filenames) in os.walk(cmds.textField(self.animFileText, q=True, text=True)):
                    listOfFiles += [os.path.join(dirpath, file) for file in filenames]

                for af in listOfFiles:
                    if af.endswith('.fbx') or af.endswith('.FBX'):
                        filesToBake.append(af)

                print('Baking Multiple, ', filesToBake)
            print('FBX files in dir, ', cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx", filesToBake)
        
        #else:
        if theAnimFileText.endswith('.ma') or theAnimFileText.endswith('.fbx') or theAnimFileText.endswith('.FBX'):
            filesToBake.append(theAnimFileText)
            print('Baking Single File, ', filesToBake)
        else:
            filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.ma")
            if len(filesToBake) == 0:
                if self.__doSubDirectories:
                    for root, dirnames, filenames in os.walk(cmds.textField(self.animFileText, q=True, text=True)):
                        for filename in fnmatch.filter(filenames, '*.fbx'):
                            filesToBake.append(os.path.join(root, filename))
                else:
                    filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.fbx")
            if len(filesToBake) == 0:
                if self.__doSubDirectories:
                    for root, dirnames, filenames in os.walk(cmds.textField(self.animFileText, q=True, text=True)):
                        for filename in fnmatch.filter(filenames, '*.FBX'):
                            filesToBake.append(os.path.join(root, filename))
                else:
                    filesToBake = glob.glob(cmds.textField(self.animFileText, q=True, text=True)+"/*.FBX")
            print('Baking Multiple, ', filesToBake)
        print('MA files in dir, ', cmds.textField(self.animFileText, q=True, text=True)+"/*.ma", filesToBake)

        
        for ftb in filesToBake:
            cmds.file(new=1,force=1)
            if FBXToMocap:
                self.retargettedMocap = self.retargetToRigMocapSkelton(ftb , theRetargetFile, addDirectory = '_retargetted')
            if bakeToRig:
                cmds.file(new=1,force=1)
                #self.bakeToAnimRig(theRigFile, ftb)
                self.bakeToRig(theRigFile, ftb)
            if bakeIkFk:
                self.bakeToFk([int(self.minTime), int(self.maxTime)])
            if importAnimLayer:
                animLayerFile = cmds.textField(self.animLayerFileText, q=True, text=True)
                cmds.file(animLayerFile ,i=True,ra = True, mergeNamespacesOnClash = True, ignoreVersion = True, namespace = ":")
                
            if exportFromRig:
                self.exportFbxFromRig()



    def cancelBake(self, *args):

        if cmds.window("bakeAnimationGUI", exists = True):
            cmds.deleteUI("bakeAnimationGUI")

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
            print(listOfFiles)
            for af in listOfFiles:
                if af.endswith('.ma'):
                    filesToBatch.append(af)

        for aFile in filesToBatch:
            print('Exporting: ',aFile)
            cmds.file(new=True,f=True)
            try:
                cmds.file(aFile, o=True,f=True)
            except:
                pass

            self.exportFbxFromRig()

    def rigToEngineGUI(self):

        if cmds.window("rigToEngineGUI", exists = True):
            cmds.deleteUI("rigToEngineGUI")
        
        windowWidth = 600
        windowHeight = 700
        
        window = cmds.window("rigToEngineGUI", title = "Export From Rig to Engine", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = True)

        mainLayout = cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 400), (2, 200)] )
        
        cmds.text(label="The Maya Ascii Animation/Mocap Directory")
        cmds.text(label="Locate")
        self.animBatchFileText = cmds.textField("animBatchImpLoc")
        cmds.button(label = "...", c=self.setAnimBatchLocation)
        cmds.separator()
        self.__exportBatchOrSingle = cmds.checkBox( label='Single File', v=1)
        cmds.button(label = "Bake From Rig To Engine!", c=self.batchExportFromRig)
        cmds.button(label = "Cancel", c=self.cancelBatchBake)


        #update if it has been used
        if cmds.optionVar(exists =self.__animBatchFileVar):#if it doesn't exist, make it
            cmds.textField(self.animBatchFileText, e=True, text = cmds.optionVar( q = self.__animBatchFileVar ))
            
        cmds.showWindow(window)

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

    def remove_namespaces(self, theNamespace = None) :
        # gather all namespaces from selection
        all_ns = []
        if theNamespace:
            for obj in pm.selected() :
                if obj.namespace() :
                    all_ns.append(obj.namespace())
        else:
            all_ns = self.getAllNS()
            all_ns.reverse()

        # remove dupes
        all_ns = list(set(all_ns)) 

        # try to remove the first namespace
        for whole_ns in all_ns :
            ns = whole_ns.split(':')[-1]
            try :
                pm.namespace(mv=[ns,':'],f=1)
                if ns in pm.namespaceInfo(lon=1) :
                    pm.namespace(rm=ns)
                print('Namespace "%s" removed.'%ns)
            except :
                print('Namespace "%s" is not removable. Possibly from a reference.'%ns)
        
        return 1


    def constrainAvailableChannels(self, theParent, theChild, rootJoint, poseFile = None):
        #print('rootJoint ', rootJoint)
        theNamespace = rootJoint.rpartition(':')[0]
        
        #swapped out bind pose setting, skinned animations from mobu loose default pose
        if poseFile:
            melStatement = "source \""+poseFile.replace('\\', '/')+"\";"
            mel.eval(melStatement)
            
        else:
            bindPose = cmds.dagPose(rootJoint , q=True, bindPose=True )
            for bp in bindPose:
                cmds.setAttr('root.ry',0)
                cmds.dagPose(bp, restore=True )

        useableChannels = ruc.returnUseableChannels(theChild)
        skipRots = []
        skipTrans = []

        if 'tx' not in useableChannels:
            skipTrans.append('x')

        if 'ty' not in useableChannels:
            skipTrans.append('y')

        if 'tz' not in useableChannels:
            skipTrans.append('z')

        if 'rx' not in useableChannels:
            skipRots.append('x')

        if 'ry' not in useableChannels:
            skipRots.append('y')

        if 'rz' not in useableChannels:
            skipRots.append('z')

        cmds.parentConstraint( theParent, theChild,mo = 1, st=skipTrans,sr=skipRots)
        print(skipRots, skipTrans)


    def getAllNS(self):

        #set the current naemspace to world
        curNS = cmds.namespaceInfo(cur=True)
        cmds.namespace(set=":")

        #because maya can only list the child namespaces of the current set namespace, we have to recursively go through setting
        #and checking child namespaces

        #start by getting the worlds children
        namespaces = []
        childspaces = cmds.namespaceInfo(lon=True)

        while childspaces:
            #move the current add spaces into the namespaces list (what we will return)
            namespaces.extend(childspaces)
            #create a list from the childspaces so that we can check for their children
            checkspaces = childspaces
            #empty the childspaces so all new children can be added to it for the next round
            childspaces = []
            #cycle through the current checkspaces and get their child namespaces
            for check in checkspaces:
                cmds.namespace(set=(":" + check))
                grandchildspaces = cmds.namespaceInfo(lon=True)
                if grandchildspaces:
                    childspaces.extend(grandchildspaces)
                    
        #remove default namespaces
        if namespaces.count('UI'): namespaces.remove('UI')
        if namespaces.count('shared'): namespaces.remove('shared')
          
        cmds.namespace(set=(":" + curNS))
        namespaces.sort()
        return namespaces


    def setLiveNS(self, namespace):
        '''
        Set the current namespace, this will cause all items created to be in this namespace.
        @note: this namespace does not need to exist, it will be created otherwise
        
        @param namespace: the namespace to create/set
        @type namespace: str
        '''
        namespace = self.cleanNS(namespace)
        # if setting to world
        if namespace == ":":
            cmds.namespace(set=":")
        else:
            createNS(namespace)
            cmds.namespace(set=":%s" % namespace)
        # confirm it
        curNS =  cmds.namespaceInfo(cur=True)
        if not curNS == namespace:
            print('The namespace "%s" was not set, current namespace is "%s"'\
                                  % (namespace, curNS))
                                  
        return True

    def createNS(self, namespace):
        '''
        Add a namespace to the scene. This namespace can be nested and already exist.
        
        @param namespace: a namespace to create
        @type namespace: str
        '''
        # clean the namespace provided
        namespace = self.cleanNS(namespace)
        
        # check that the namespace exists
        if cmds.namespace(exists=':%s' % namespace):
            return namespace
            
        # see if there is a maya node with the same name as the namespace (as this will cause your namespace to increment)
        if cmds.objExists(namespace):
            raise NamespacerError('Unable to add namespace "%s" to your scene since a node exists with the same name' % namespace)
        
        # get the current namespace
        curNS = cmds.namespaceInfo(cur=True)
        cmds.namespace(set=":")
        
        # split the namespace apart
        parts = namespace.split(":")
        # create each part
        for part in parts:
            # see if it exists (under our current namespace
            if not cmds.namespace(exists=part):
                # create it
                cmds.namespace(add=part)
            # set the current namespace to the part created
            cmds.namespace(set=part)
                
        # set it back
        cmds.namespace(set=':%s' % curNS)
        
        # check that it was made
        if not cmds.namespace(exists=":%s" % namespace):
            print('The namespace "%s" was not created, current namespaces: %s' % (namespace, getAllNS()))
        
        return namespace 

    def cleanNS(self, origNamespace):
        '''
        Clean the namespace provided (removes additional colons)
        
        Example:
            ":jack::bar:fred:"  --->   jack:bar:fred
        
        @param origNamespace: the dirty namespace to clean
        @type origNamespace: str
        
        @return: a correctly coloned namespace "foo:bar"
        @rtype: str
        
        '''
        # handle namespace of None, False, ""
        origNamespace = origNamespace if origNamespace else ""
        
        cleaned = ":".join([x for x in origNamespace.split(":") if x])
        if cleaned:
            return cleaned
        else:
            return ":"

    def nsExists(self, namespace):
        namespace = self.cleanNS(namespace)
        return cmds.namespace(exists=':%s' % namespace)

    def deleteNS(self, namespace):
        '''
        Delete a namespace from the scene, move all objects into world namespace during delete
        
        @return: all the object in the namespace after moving it - may be renamed
        @rtype: list(str)
        '''
        # clean the namespace provided
        namespace = self.cleanNS(namespace)
        
        # if world, stop
        if namespace == ":":
            return []
            
        # get the current namespace
        curNS = cmds.namespaceInfo(cur=True)
        self.setLiveNS(":")
        
        # see if the namespace provided exists
        if not cmds.namespace(exists=namespace):
            print('the namespace "%s" is not in your scene, that means its deleted!' % namespace)
            return []
            
        # get all the nodes currently in world namespace
        preSet = set(cmds.ls(":*", dag=True, dep=True))
        
        # move
        print('attempting to move namespace "%s"' % namespace)
        cmds.namespace(mv=(namespace, ":"), force=True)
        
        # get all the node after the move (includes renames
        postSet = set(cmds.ls(":*", dag=True, dep=True))
        
        # get the ones that are new
        diffSet = postSet.difference(preSet)
        
        # remove the origional namespace
        cmds.namespace(rm=namespace, force=True)
        
        # set the namespace back
        if cmds.namespace(exists=curNS):
            self.setLiveNS(curNS)
            
        if self.nsExists(namespace):
            print('The namespace %s was not successfully deleted (likely due to references in namespace' % namespace)
        
        # return them
        return list(diffSet)

    def deleteAllNS(self):
        namespaces = self.getAllNS()
        for namespace in namespaces:
            self.deleteNS(namespace)
            
        return True