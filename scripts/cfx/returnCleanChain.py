#returns just the chain of a joint chain, not other children
import maya.cmds as cmds

def returnCleanChain(startJoint, endJoint):

    children = cmds.listRelatives(startJoint,c=True,ad=True)
    if endJoint not in children:
        cmds.error(endJoint+" is not a child of "+startJoint)
        
    testJoint = endJoint
    cleanChain = []
	
    while testJoint != startJoint:
    
        cleanChain.append(testJoint)
        testJoint = cmds.listRelatives(testJoint, p=True)[0]
        
    cleanChain.append(startJoint)
    
    return cleanChain