'''
A script to insert a group for zeroing things
Note: This can be done with mayas normal group command now, this is kinda legacy, but I know how it works and that it works every time.

Author: John Riggs
'''

import maya.cmds as cmds   

def insertBufferGroup(theObject,postFix = "BUF", connectionName = None):
    
    theGroup = cmds.group(em=True, n = theObject+"_"+postFix)
    #moveIt(theGroup,theObject,False)
    cmds.xform(theGroup ,ws=True,m=(cmds.xform(theObject,q=True,ws=True,m=True)))

    theParent = cmds.listRelatives(theObject,p=True)
    
    if theParent is not None:
        cmds.parent(theGroup,theParent[0])
        
    cmds.parent(theObject,theGroup)
    
    cmds.addAttr(theGroup,ln='buffer',at="bool", dv = 1)

    if cmds.objExists(theObject+'.controlMade'):
        cmds.addAttr(theGroup, ln= 'theCtrl', at="message" )
        if  connectionName == None:
            connectionName = 'addedBufferGroup'
        if not cmds.objExists(theObject+'.'+connectionName):
            cmds.addAttr(theObject, ln= connectionName, at="message" )
      
        cmds.connectAttr(theGroup+'.theCtrl', theObject+'.'+connectionName, f=True)

    return theGroup