import maya.cmds as cmds

def buildUnrealIK():
    print('BUILDING UNREAL IK')
    cmds.select(clear = True)
    footRootIk = cmds.joint(n='ik_foot_root')
    cmds.select(clear = True)
    footLeftIk = cmds.joint(n='ik_foot_l')
    cmds.select(clear = True)
    footRightIk = cmds.joint(n='ik_foot_r')
    cmds.select(clear = True)
    handRootIk = cmds.joint(n='ik_hand_root')
    cmds.select(clear = True)
    handGun = cmds.joint(n='ik_hand_gun')
    cmds.select(clear = True)
    handLeftIk = cmds.joint(n='ik_hand_l')
    cmds.select(clear = True)
    handRightIk = cmds.joint(n='ik_hand_r')

    cmds.parent([footRootIk,handRootIk],'root')
    cmds.parent([footLeftIk,footRightIk],footRootIk)
    cmds.parent([handRightIk,handLeftIk],handGun)
    cmds.parent(handGun,handRootIk)

    cmds.xform(footRootIk ,ws=True,m=(cmds.xform('root',q=True,ws=True,m=True)))
    cmds.xform(handRootIk ,ws=True,m=(cmds.xform('root',q=True,ws=True,m=True)))

    cmds.xform(footLeftIk ,ws=True,m=(cmds.xform('foot_l',q=True,ws=True,m=True)))
    cmds.xform(footRightIk ,ws=True,m=(cmds.xform('foot_r',q=True,ws=True,m=True)))

    cmds.xform(handGun ,ws=True,m=(cmds.xform('hand_r',q=True,ws=True,m=True)))
    cmds.xform(handRightIk ,ws=True,m=(cmds.xform('hand_r',q=True,ws=True,m=True)))
    cmds.xform(handLeftIk ,ws=True,m=(cmds.xform('hand_l',q=True,ws=True,m=True)))