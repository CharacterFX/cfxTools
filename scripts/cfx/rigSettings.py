import maya.cmds as cmds

class rigSettings(object):
    
    def __init__(self):


        #file extensions
        self.ctrlFileExtension = 'ctrlShape'

        #directories
        self.installLocation = __file__.rpartition('\\')[0]+'/'
        self.rigBuildScriptsLocation = self.installLocation
        self.autoSetupsDir = self.installLocation+'autoSetups'
        self.controlLocation = self.installLocation+'controlShape/'
        self.ikSystems = self.installLocation+'ikSystems/'

        #naming
        self.theSwitchControl = "theSwitchControl"
        self.pvSpaceAttrName = "poleVectorSpace"
        self.ikSpaceAttrName = "ikSpace"
        self.pvSwitchAttr = 'pvParents'
        self.ikPrefix = "Ik"
        self.fkPrefix = "Fk"
        self.worldSpacePoleVectorsGrp = 'worldSpacePoleVectors_Grp'
        self.worldSpaceIkGrp = 'worldSpaceIk_Grp'
        self.worldSpaceIkDistanceGrp = 'worldSpaceIkDistance_Grp'
        self.ctrlExtension = 'CTRL'
        self.ctrlMadeAttr = 'controlMade'
        self.needsReshapenAttr = 'needsReshapen'
        self.unrealJointNS = 'UJ'
        self.mocapJoint = 'MJ'
        
        #meta naming
        self.setupData = 'setupData'
        self.jointsInSystem = 'jointsInSystem'
        self.allJoints = 'allJoints'
        self.faceShapes = 'faceShape'
        self.driverValues = 'driverValues'
        self.faceNode = 'face'
        self.proxyMetaAttr = 'proxyGeo'
        self.isProxyAttr = 'isProxy'
        self.childSystem = 'childSystem'
        self.parentSystem = 'parentSystem'
        self.ikBake = 'ikBake'
        self.fkBake = 'fkBake'
        self.mocapBake = 'mocapBake'
        self.splineIkBake = 'splineIkBake'
        self.mainBake = 'mainBake'
        self.secondaryMocapBake = 'secondaryMocapBake'
        self.ctrlBake = 'ctrlBake'
        self.character = 'character'
        self.weapon = 'weapon'
        self.attachNodes = 'attachNodes'
        self.ikAttachConstraint = 'ikAttachConstraint'
        self.pvAttr = 'thePv'
        self.ctrlAttr = 'ctrls'
        self.ctrlOnObject = self.setupData+'_'+self.ctrlAttr
        self.allCtrls = self.ctrlAttr #'allCtrls'
        self.characterMetaNode = 'characterMetaNode'
        self.unrealJoint = 'unrealJoint'
        self.deformerRootJoint = 'deformerRootJoint'
        self.deformerGeometry = 'geometry'
        self.rootJoint = 'rootJoint'

        #attr names
        self.fkIkAttrName = "fkIk"
        self.ikTrnControlName = "ikTrnControl"
        self.shaperCtrlVis = 'showShaperControls'
        self.mocapConnect = 'mocapConnect'
        self.mocapConnectTo = 'mocapConnectTo'
        self.proxyShape = "proxyShape"
        self.spaceSwitcherCon = 'spaceSwitcherCon'
        self.control = 'theCtrl'
        self.controlled = 'controlled'
        
        #colors
        self.ikCenterColor = 17
        self.ikCenterSecondaryColor = 25
        self.fkCenterColor = 14
        self.fkCenterSecondaryColor = 26
        self.leftColor = 6
        self.rightColor = 13
        self.middleColor = 14

        #rig building
        self.debug = False
        self.doPostNaming = False
        self.downAxis = 'x'
        self.allSides = [['Left','Right'], ['left','right'], ['Lf','Rt'], ['l_','r_'], ['Lt','Rt']]
        self.defaultDownAxis = 'x'
        self.cog = 'cog'

        #attributes
        self.enums = ['autoSetups', 'ikSystems', 'ikAddOns', 'dynamicSetups', 'deformerSetups', 'muscleSetups', 'poseSetups', 'controlShape', 'proxyShape', 'mocapConstraints', 'flipJointAxis', 'rigJointType', 'buildAxis', 'rotOrder', 'mocapBake']
        self.booleans = ['animation', 'deformer', 'ikAttachPoint', 'pvSpaceAttach', 'aimAtMe']
        self.strings = ['setupOptions', 'ikAddonsOptions', 'poseOptions', 'mocapConOptions', 'deformerOptions', 'reparent', 'visGroup', 'renameCtrl', 'unrealJoint']
        self.mocapConnectOptions = "None:both:translate:rotate:parent"

        #default shapes
        self.pvShape = "snow"
        self.cameraShape = "camera"
        self.shaper = 'circle'
        self.head = 'circle'
        self.neck = 'octagon'
        self.root = 'circleXed'
        self.rootOffset = 'squareRoundedCorners'
        self.defaultRootShapes = ['fourWayFlatArrow', 'hexagon', 'circle3']
        self.spaceSwitcher = 'circle'
        self.ikFkswitch = "ikfkSwitch"
        #root building
        self.muscleSurfVis = 'showMuscleSurfaces'
        self.muscleCtrlVis = 'showMuscleControls'
        self.deformationSkelVis = 'showDeformerSystem'
        self.deformationSkelTemplate = 'displayStyleDeformerSystem'
        self.riggingSkelVis = 'showRiggingSkeleton'
        self.riggingSkelTemplate = 'templateRiggingSkeleton'
        self.mocapSkelVis = 'showMocapSkeleton'
        self.mocapSkelTemplate = 'templateMocapSkeleton'
        self.unrealSkelVis = 'showUnrealSkeleton'
        self.unrealSkelTemplate = 'templateUnrealSkeleton'
        self.proxyRig = 'proxyOrHighres'
        self.additionalAttrs = [ self.riggingSkelVis, self.riggingSkelTemplate, self.proxyRig]

        self.defaultRoots = ['topTransform', 'constrianMe_Grp', 'main_Grp']
        self.noInherits = ['joints', 'wsGroup', 'noInherit']
        self.characterGroup = 'character_Grp'
        self.controlsGroup = 'controls_Grp'
        self.topTransform = 'topTransform'