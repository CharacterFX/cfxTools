import maya.cmds as cmds

import cfx.returnObjectWithAttr as roa
import cfx.controlShapeSystem as css
import cfx.rigSettings as rigset
import cfx.insertBufferGroup as ibg
import cfx.metaSystem as rmeta

meta = rmeta.metaSystem()
attrFinder = roa.returnObjectWithAttr()

def addSkeleton(theFile, allUs = [], wrongTwistNames =False, addNamespace = None):
    
    characterMeta = meta.findMeta('character')
    if len(characterMeta) > 0:
        characterMeta = characterMeta[0]

    characterGroup = None
    if characterMeta:
        if cmds.objExists(characterMeta+'.character_Grp'):
            characterGroup = cmds.listConnections(characterMeta+'.character_Grp', s=0, d=1)

    #worldNode = 'worldRef'
    worldNode = attrFinder.all("autoSetups", 'world')
    cogNode = attrFinder.all("autoSetups", 'cog')
    pelvisNode = attrFinder.all("autoSetups", 'hip')
    print("worldNode: ", worldNode)
    
    if addNamespace:
        namespaced = addNamespace
        if not cmds.namespace( ex=namespaced ):
            cmds.namespace( add=namespaced )
        
        cmds.select(characterGroup,hi=1,r=1)
        allNodes = cmds.ls(sl=1, type = 'transform')

        for an in allNodes:
            #print("testing: ", an)
            if cmds.objExists(an):
                cmds.rename(an, namespaced+':'+an)

    print('Importing default skeleton: ', theFile)
    cmds.file(theFile, i=True, f=True)
    
    if len(worldNode) != 1:
        cmds.error('too little or too many worls nodes: ', len(worldNode))
    worldNode = worldNode[0]
    worldSplit = worldNode.split(':')
    if len(worldSplit) > 1:
        worldSplit.pop()
        namespaced = ':'.join(worldSplit)

    cmds.parentConstraint(namespaced+':'+worldNode, 'root',mo=False)

    cmds.delete(cmds.parentConstraint(namespaced+':'+cogNode[0], pelvisNode[0],mo=False))
    cmds.parentConstraint(namespaced+':'+pelvisNode[0], pelvisNode[0],mo=True)

    for au in allUs:
        if cmds.objExists(namespaced+':'+au):
            cmds.parentConstraint(namespaced+':'+au, au, mo=True) 

    #cmds.parentConstraint(namespaced+':thumb_MC_l', 'thumb_01_l', mo=False)
    #cmds.parentConstraint(namespaced+':thumb_MC_r', 'thumb_01_r', mo=False)

    #cmds.parentConstraint(namespaced+':thumb_01_l', 'thumb_02_l', mo=False)
    #cmds.parentConstraint(namespaced+':thumb_01_r', 'thumb_02_r', mo=False)

    #cmds.parentConstraint(namespaced+':thumb_02_l', 'thumb_03_l', mo=False)
    #cmds.parentConstraint(namespaced+':thumb_02_r', 'thumb_03_r', mo=False)

    #cmds.setAttr("thumb_03_l_parentConstraint1.thumb_03_lW0", 0)
    #cmds.setAttr("thumb_02_l_parentConstraint1.thumb_02_lW0", 0)
    #cmds.setAttr("thumb_01_l_parentConstraint1.thumb_01_lW0", 0)
    #cmds.setAttr("thumb_03_r_parentConstraint1.thumb_03_rW0", 0)
    #cmds.setAttr("thumb_02_r_parentConstraint1.thumb_02_rW0", 0)
    #cmds.setAttr("thumb_01_r_parentConstraint1.thumb_01_rW0", 0)

    if  wrongTwistNames:
        cmds.parentConstraint(namespaced+':hand_l_twist_1', 'lowerarm_twist_01_l', mo=False)
        cmds.parentConstraint(namespaced+':hand_r_twist_1', 'lowerarm_twist_01_r', mo=False)
        cmds.parentConstraint(namespaced+':hand_l_twist_2', 'lowerarm_twist_02_l', mo=False)
        cmds.parentConstraint(namespaced+':hand_r_twist_2', 'lowerarm_twist_02_r', mo=False)

        cmds.parentConstraint(namespaced+':upperarm_l_twist_1', 'upperarm_twist_01_l', mo=False)
        cmds.parentConstraint(namespaced+':upperarm_r_twist_1', 'upperarm_twist_01_r', mo=False)
        cmds.parentConstraint(namespaced+':upperarm_l_twist_2', 'upperarm_twist_02_l', mo=False)
        cmds.parentConstraint(namespaced+':upperarm_r_twist_2', 'upperarm_twist_02_r', mo=False)

        cmds.parentConstraint(namespaced+':foot_l_twist_1', 'calf_twist_01_l', mo=False)
        cmds.parentConstraint(namespaced+':foot_r_twist_1', 'calf_twist_01_r', mo=False)
        cmds.parentConstraint(namespaced+':foot_l_twist_2', 'calf_twist_02_l', mo=False)
        cmds.parentConstraint(namespaced+':foot_r_twist_2', 'calf_twist_02_r', mo=False)

        cmds.parentConstraint(namespaced+':thigh_l_twist_1', 'thigh_twist_01_l', mo=False)
        cmds.parentConstraint(namespaced+':thigh_r_twist_1', 'thigh_twist_01_r', mo=False)
        cmds.parentConstraint(namespaced+':thigh_l_twist_2', 'thigh_twist_02_l', mo=False)
        cmds.parentConstraint(namespaced+':thigh_r_twist_2', 'thigh_twist_02_r', mo=False)

    if cmds.objExists('headRoot'):
        cmds.parentConstraint(namespaced+':head', 'headRoot', mo=False) 

    if not cmds.objExists(namespaced+':topTransform.showDeformationSkeleton'):
        cmds.addAttr(namespaced+':topTransform',ln='showDeformationSkeleton',at="double", min=0, max=1, dv = 0)
        cmds.setAttr(namespaced+':topTransform.showDeformationSkeleton', 0, e=True,keyable=True)

    if not cmds.objExists(namespaced+':topTransform.templateDeformationSkeleton'):
        cmds.addAttr(namespaced+':topTransform',ln='templateDeformationSkeleton',at="double", min=0, max=1, dv = 0)
        cmds.setAttr(namespaced+':topTransform.templateDeformationSkeleton', 0, e=True,keyable=True)

    cmds.connectAttr(namespaced+':topTransform.showDeformationSkeleton', 'root.visibility', f=True)
    cmds.connectAttr(namespaced+':topTransform.templateDeformationSkeleton', 'root.template', f=True)

    cmds.setAttr("pup:topTransform.templateDeformationSkeleton", 1)

    if cmds.objExists('pv_leg_r'):
        cmds.parentConstraint(namespaced+':_r_thigh_r_pole_CTRL', 'pv_leg_r', mo=False)
    if cmds.objExists('pv_leg_l'):
        cmds.parentConstraint(namespaced+':_l_thigh_l_pole_CTRL', 'pv_leg_l', mo=False)

    if cmds.objExists('pv_arm_r'):
        cmds.parentConstraint(namespaced+':_r_upperarm_r_pole_CTRL', 'pv_arm_r', mo=False)
    if cmds.objExists('pv_arm_l'):
        cmds.parentConstraint(namespaced+':_l_upperarm_l_pole_CTRL', 'pv_arm_l', mo=False)

    if cmds.objExists('ik_hand_l'):
        cmds.parentConstraint(namespaced+':hand_l', 'ik_hand_l', mo=False)
    if cmds.objExists('ik_hand_gun'):
        cmds.parentConstraint(namespaced+':hand_r', 'ik_hand_gun', mo=False)
    if cmds.objExists('ik_hand_root'):
        cmds.parentConstraint(namespaced+':hand_r', 'ik_hand_root', mo=False)
    if cmds.objExists('ik_foot_l'):
        cmds.parentConstraint(namespaced+':foot_l', 'ik_foot_l', mo=False)
    if cmds.objExists('ik_foot_r'):
        cmds.parentConstraint(namespaced+':foot_r', 'ik_foot_r', mo=False)

    #cmds.setAttr("ball_r_parentConstraint1.target[0].targetOffsetRotateZ", 180)

    #cmds.setAttr("root_parentConstraint1.target[0].targetOffsetRotateX", 180)

    #cmds.orientConstraint(namespaced+':lowerarm_twist_01_l', 'lowerarm_twist_01_l', mo=False)

    cmds.select('root',hi=True)

    for jnt in cmds.ls(sl=True, type = 'joint'):
        cmds.setAttr(jnt+".jointOrientX", 0)
        cmds.setAttr(jnt+".jointOrientY", 0)
        cmds.setAttr(jnt+".jointOrientZ", 0)

    #MANUALLY COPPIED IN HERE FOR NOW NEEDS TO BE PYTHONIZED
    settings = rigset.rigSettings()
    controlMaker = css.controlShapeSystem()

    

    #syncCtrl = controlMaker.makeAndGroupCtrl(['syncNode'],'star',15.0, ctrlExtension = settings.ctrlExtension)
    #cmds.rotate(90,0,0, syncCtrl[0]+'.cv[*]',os=True)

    cmds.rename('rootMotionWorldSpace_CTRL', namespaced+':rootMotionWorldSpace_CTRL')
    cmds.rename('rootMotionBodySpace_CTRL', namespaced+':rootMotionBodySpace_CTRL')

    
                    
    #for jnt in [namespaced+':rootMotionWorldSpace_CTRL', namespaced+':rootMotionBodySpace_CTRL']
    """
    mocapBuffer = ibg.insertBufferGroup(namespaced+':rootMotionWorldSpace_CTRL','mocapTransfer')
    pc = cmds.parentConstraint('root', mocapBuffer, mo=True)
    weights = cmds.parentConstraint(pc[0],q=True, wal=True)
    for wt in weights:
        cmds.connectAttr(namespaced+':topTransform.transferMocap', pc[0]+'.'+wt, f=True)

    mocapBuffer = ibg.insertBufferGroup(namespaced+':rootMotionBodySpace_CTRL','mocapTransfer')
    pc = cmds.parentConstraint('root', mocapBuffer, mo=True)
    weights = cmds.parentConstraint(pc[0],q=True, wal=True)
    for wt in weights:
        cmds.connectAttr(namespaced+':topTransform.transferMocap', pc[0]+'.'+wt, f=True)
    """

    #add atr for mocap consdtraints
    if not cmds.objExists(namespaced+':rootMotionWorldSpace_CTRL.'+settings.mocapConnect):
        cmds.addAttr(namespaced+':rootMotionWorldSpace_CTRL', ln=settings.mocapConnect, at="enum", en = settings.mocapConnectOptions, dv=0 )
        cmds.setAttr(namespaced+':rootMotionWorldSpace_CTRL.'+settings.mocapConnect, 1, cb=True,keyable=True)

    mocapAttr = settings.mocapConnectTo
    if cmds.objExists('mocap:worldRef.'+settings.mocapConnectTo):
        mocapAttr = mocapAttr+'Secondary'

    if cmds.objExists('mocap:worldRef'):
        cmds.addAttr('mocap:worldRef', ln = mocapAttr, at="message" )
        cmds.connectAttr(namespaced+':rootMotionWorldSpace_CTRL.'+settings.mocapConnect , 'mocap:worldRef.'+mocapAttr, f=True)

    if not cmds.objExists(namespaced+':rootMotionBodySpace_CTRL.'+settings.mocapConnect):
        cmds.addAttr(namespaced+':rootMotionBodySpace_CTRL', ln=settings.mocapConnect, at="enum", en = settings.mocapConnectOptions, dv=0 )
        cmds.setAttr(namespaced+':rootMotionBodySpace_CTRL.'+settings.mocapConnect, 1, cb=True,keyable=True)

    mocapAttr = settings.mocapConnectTo
    if cmds.objExists('mocap:worldRef.'+settings.mocapConnectTo):
        mocapAttr = mocapAttr+'Secondary'

    if cmds.objExists('mocap:worldRef'):
        cmds.addAttr('mocap:worldRef', ln = mocapAttr, at="message" )
        cmds.connectAttr(namespaced+':rootMotionBodySpace_CTRL.'+settings.mocapConnect , 'mocap:worldRef.'+mocapAttr, f=True)

    ctrl = namespaced+':rootMotionWorldSpace_CTRL'
    conType = cmds.getAttr(ctrl+'.'+settings.mocapConnect, asString = True)
    mocapBuffer = ibg.insertBufferGroup(ctrl,'mocapTransfer')
    
    #doing them all as parentConstraints for now
    #if conType == 'both':
    if cmds.objExists('mocap:worldRef'):
        pc = cmds.parentConstraint('mocap:worldRef', mocapBuffer, mo=True)
        weights = cmds.parentConstraint(pc[0],q=True, wal=True)
        for wt in weights:
            cmds.connectAttr(namespaced+':topTransform.transferMocap', pc[0]+'.'+wt, f=True)

    ctrl = namespaced+':rootMotionBodySpace_CTRL'
    conType = cmds.getAttr(ctrl+'.'+settings.mocapConnect, asString = True)
    mocapBuffer = ibg.insertBufferGroup(ctrl,'mocapTransfer')
    
    #doing them all as parentConstraints for now
    #if conType == 'both':
    if cmds.objExists('mocap:worldRef'):
        pc = cmds.parentConstraint('mocap:worldRef', mocapBuffer, mo=True)
        weights = cmds.parentConstraint(pc[0],q=True, wal=True)
        for wt in weights:
            cmds.connectAttr(namespaced+':topTransform.transferMocap', pc[0]+'.'+wt, f=True)
