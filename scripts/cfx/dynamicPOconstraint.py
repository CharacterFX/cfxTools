'''
A script that sets up a fadeable point and orient constraint

Author: John Riggs
'''

import rtsp.returnUseableChannels as ruc

import maya.cmds as cmds

def dynamicPOconstraint(parents,child, translation = True, rotation =True, useConstraints = True, createOffsets = False):

    cmds.dgdirty(a=True)

    if not isinstance(parents, list):
        parents = [parents]

    if len(parents) == 1:

        childsParent = cmds.listRelatives(child,p=True)
        parentSpace = cmds.group(em=True,n=child+'_parentSpace')
        if childsParent is not None:
            cmds.parent(parentSpace,childsParent[0])
        cmds.xform(parentSpace ,ws=True,m=(cmds.xform(child,q=True,ws=True,m=True)))
        parents.append(parentSpace)

    useableChanels = ruc.returnUseableChannels(child)
    nonUseableChanels = ruc.returnUseableChannels(child,False)

    thePoint = []
    weightListP = []
    theOrient = []
    weightListO = []

    attrName = parents[0].split(':')[-1]+"_Or_"+parents[1].split(':')[-1]

    if cmds.objExists(child+"."+attrName):
        attrName = parents[0].split(':')[-1]+"_Or_"+parents[1].split(':')[-1]+'1'

    cmds.addAttr(child,ln=attrName,at="double", min=0, max=1)
    cmds.setAttr(child+"."+attrName, e=True,keyable=True)

    if useConstraints:
        if createOffsets:
            newParent1 = cmds.spaceLocator(n= child+'_at_'+parents[0])
            cmds.parent(newParent1, parents[0])
            cmds.xform(newParent1[0] ,ws=True,m=(cmds.xform(child,q=True,ws=True,m=True)))
            parents[0] = newParent1[0] 

            newParent2 = cmds.spaceLocator(n= child+'_at_'+parents[1])
            cmds.parent(newParent2, parents[1])
            cmds.xform(newParent2[0] ,ws=True,m=(cmds.xform(child,q=True,ws=True,m=True)))
            parents[1] = newParent2[0] 

        if 'tx' and 'ty' and 'tz' in useableChanels:
            if translation:
                thePoint = cmds.pointConstraint(parents,child, o=[0,0,0],w=1)
                weightListP = cmds.pointConstraint(thePoint[0],q=True,wal=True)
        
        if 'rx' and 'ry' and 'rz' in useableChanels:
            if rotation:
                theOrient = cmds.orientConstraint(parents,child, o=[0,0,0],w=1)
                weightListO = cmds.orientConstraint(theOrient[0],q=True,wal=True)
        
        reverseNode = cmds.createNode("reverse")
        
        cmds.connectAttr(child+"."+attrName, reverseNode+".inputX")

        if 'tx' and 'ty' and 'tz' in useableChanels:
            if translation:
                cmds.connectAttr(child+"."+attrName, thePoint[0]+"."+weightListP[0])

        if 'rx' and 'ry' and 'rz' in useableChanels:
            if rotation:
                cmds.connectAttr(child+"."+attrName, theOrient[0]+"."+weightListO[0])

        if 'tx' and 'ty' and 'tz' in useableChanels:
            if translation:
                cmds.connectAttr(reverseNode+".outputX", thePoint[0]+"."+weightListP[1])

        if 'rx' and 'ry' and 'rz' in useableChanels:
            if rotation:
                cmds.connectAttr(reverseNode+".outputX", theOrient[0]+"."+weightListO[1])
            
        if rotation is False or 'rx' and 'ry' and 'rz' in nonUseableChanels:
            theOrient.append(None)

        if translation is False or 'tx' and 'ty' and 'tz' in nonUseableChanels:
            thePoint.append(None)

    #use blendColors Nodes to speed up rig
    else:
        if translation:
            transBlendNode = cmds.createNode('blendColors', n = parents[0]+"_to_"+parents[1]+'_TBC')
            cmds.connectAttr(parents[0]+'.translate',transBlendNode+'.color1',f=True)
            cmds.connectAttr(parents[1]+'.translate',transBlendNode+'.color2',f=True)
            cmds.connectAttr(transBlendNode+'.output',child+'.translate',f=True)

            cmds.connectAttr(child+"."+attrName, transBlendNode+".blender", f=True)

            thePoint.append(transBlendNode)

        if rotation:
            rotBlendNode = cmds.createNode('blendColors', n = parents[0]+"_to_"+parents[1]+'_RBC')
            cmds.connectAttr(parents[0]+'.rotate',rotBlendNode+'.color1',f=True)
            cmds.connectAttr(parents[1]+'.rotate',rotBlendNode+'.color2',f=True)
            cmds.connectAttr(rotBlendNode+'.output',child+'.rotate',f=True)

            cmds.connectAttr(child+"."+attrName, rotBlendNode+".blender", f=True)

            theOrient.append(rotBlendNode)

    return [thePoint[0], theOrient[0],child+"."+attrName]