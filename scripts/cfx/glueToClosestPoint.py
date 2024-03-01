import rtsp.returnClosestPointOnMesh as rc
import rtsp.closestPointOn as cpo

import rtsp.createOffsetAtDifferentObject as co

import cfx.addOrMakeGroup as aomg
import maya.cmds as cmds
import maya.mel as mel

import cfx.moduleTools as mt
mod = mt.moduleTools()
mod.reload([co, rc])

class glueToClosestPoint(object):

    def __init__(self):

        self.__closestOn = cpo.closestPointOn()

    def curve(self, curve, theObject):

        theP = self.__closestOn.curve(cmds.xform(theObject, q=True, t=True, ws=True), curve)[0]

        pos = cmds.createNode('pointOnCurveInfo', n = 'pointOnCurve_'+curve)
    
        loc = cmds.spaceLocator(n = curve+"_loc#")[0]

        cmds.addAttr(loc, ln = 'parameter', at = 'double', dv = theP)
        cmds.setAttr(loc+".parameter", e=True, keyable = True)

        cmds.connectAttr(curve+".worldSpace", pos+".inputCurve")
        cmds.connectAttr(pos+".position", loc+".translate")
        cmds.connectAttr(loc+".parameter", pos+".parameter")
        
        return [loc,pos]

    def surface(self, mesh, theObject, glueType, doOrientCon=True, doTranslateCon=True, zeroOutCon = True, addOffset = False, maintainOffset = True):

        attachtheObject = ""
        previousSelection = cmds.ls(sl=True)
        
        posData = rc.returnClosestPointOnMesh(mesh,theObject)

        inputAttr = ''
        outputAttr = ''

        objType = cmds.objectType(mesh)
        
        if objType == 'transform':
            mesh = cmds.listRelatives(mesh,s = True)[0]
        
        objType = cmds.objectType(mesh)
        if objType == 'mesh':
            inputAttr = 'inputMesh'
            outputAttr = 'outMesh'
            
        if objType == 'nurbsSurface':
            inputAttr = 'inputSurface'
            outputAttr = 'worldSpace[0]'
                
        if glueType == "cMuscle":
            
            cmds.select(mesh+".f["+str(posData[3])+"]",r=True)
            mel.eval("cMuscleSurfAttachSetup()")
            attachtheObject = (cmds.ls(sl=True))[0]

            objParent = cmds.listRelatives(theObject, p=1)[0]
            pGroup = cmds.group(n=attachtheObject+'_at_'+objParent)
            cmds.parentConstraint(objParent, pGroup, mo=0)

            conGroup = cmds.group(em=1,n = 'cMus_at_'+theObject)
            cmds.parent(conGroup, attachtheObject)
            cmds.xform(conGroup ,ws=True,m=(cmds.xform(theObject,q=True,ws=True,m=True)))

            cmds.parentConstraint(conGroup, theObject, mo=1)

        if glueType == "follicle":
            
            follicleShapeNode = cmds.createNode('follicle', n = theObject+"_to_"+mesh)
            follicleTransformNode = cmds.listRelatives(follicleShapeNode,p=True)
            
            cmds.connectAttr(mesh+"."+outputAttr,follicleShapeNode+"."+inputAttr,f=True)
            cmds.connectAttr(mesh+".worldMatrix[0]", follicleShapeNode+".inputWorldMatrix",f=True)

            cmds.connectAttr(follicleShapeNode+".outRotate", follicleTransformNode[0]+".rotate",f=True)
            cmds.connectAttr(follicleShapeNode+".outTranslate", follicleTransformNode[0]+".translate",f=True)
            cmds.setAttr(follicleShapeNode+".parameterU", posData[1])
            cmds.setAttr(follicleShapeNode+".parameterV", posData[2])
            
            #co.createOffsetAtDifferentObject(theObject,follicleTransformNode,True, zeroOut = zeroOutCon, doOrient = doOrientCon, doTranslate = doTranslateCon, maintOffset = True)
            cmds.parentConstraint(follicleTransformNode,theObject, mo=1, dr=1)
            attachtheObject = follicleTransformNode

            theGroup = aomg.addOrMakeGroup(follicleTransformNode, "folliclesOnSurface")

            if addOffset:
                if not cmds.objExists(theObject+".offsetU"):
                    cmds.addAttr(theObject, ln = 'offsetU', at = 'double', dv = 0)
                    cmds.setAttr(theObject+".offsetU", e=True, keyable = True)

                if not cmds.objExists(theObject+".offsetV"):
                    cmds.addAttr(theObject, ln = 'offsetV', at = 'double', dv = 0)
                    cmds.setAttr(theObject+".offsetV", e=True, keyable = True)

                if not cmds.objExists(theObject+".moveMultiplier"):
                    cmds.addAttr(theObject, ln = 'moveMultiplier', at = 'double', dv = 1)
                    cmds.setAttr(theObject+".moveMultiplier", 1, e=False, keyable = False)

                pmaNode = cmds.createNode('plusMinusAverage', n=theObject+'_UV_pma')

                cmds.setAttr(pmaNode+'.input2D[0].input2Dx', posData[1])
                cmds.setAttr(pmaNode+'.input2D[0].input2Dy', posData[2])

                mulitNode = cmds.createNode('multiplyDivide', n=theObject+'_UV_mult')

                cmds.connectAttr(theObject+".moveMultiplier", mulitNode+'.input2X', f=1)
                cmds.connectAttr(theObject+".moveMultiplier", mulitNode+'.input2Y', f=1)

                cmds.connectAttr(theObject+".offsetU", mulitNode+'.input1X', f=1)
                cmds.connectAttr(theObject+".offsetV", mulitNode+'.input1Y', f=1)

                cmds.connectAttr(mulitNode+'.outputX', pmaNode+'.input2D[1].input2Dx', f=1)
                cmds.connectAttr(mulitNode+'.outputY', pmaNode+'.input2D[1].input2Dy', f=1)

                cmds.connectAttr(pmaNode+'.output2D.output2Dx', follicleShapeNode+".parameterU", f=1)
                cmds.connectAttr(pmaNode+'.output2D.output2Dy', follicleShapeNode+".parameterV", f=1)


        if len(previousSelection) != 0:
            cmds.select(previousSelection,r=True)
            
        return attachtheObject


    def addJointsToVerts(self, verts,glueSurface = ''):

        jointsMade = []
        folliclesMade = []
        
        for vert in verts:
            vertPos = cmds.pointPosition(vert,w=True)
            cmds.select(clear=True)
            jointsMade.append(cmds.joint(p=(vertPos[0],vertPos[1],vertPos[2]), n= vert+'_Jnt'))

        if glueSurface == '':
            for aJoint in jointsMade:
                folliclesMade.append(glueToClosestPointOnSurface(vert.split(".")[0], aJoint,'follicle'))

        else:
            for aJoint in jointsMade:
                folliclesMade.append(glueToClosestPointOnSurface(glueSurface, aJoint,'follicle'))
                
        return [jointsMade,folliclesMade]

    def rideOnClosestPointOnSurface(self, verts,glueSurface,orientSurface,createJoint = False):
        
        jointsMade = []
        locsMade = []
        cposMade = []
        vertPos = []

        if cmds.objectType(glueSurface) == 'transform':
            glueSurface = cmds.listRelatives(glueSurface , s=True)[0]
            
        for vert in verts:

            objType = cmds.objectType(vert)

            if objType == 'mesh':
                vertPos = cmds.pointPosition(vert,w=True)

            if objType == 'transform':
                vertPos = cmds.xform(vert,q=True,ws=True,t=True)

            cmds.select(clear=True)
            
            if createJoint:
                theJoint = cmds.joint(p=(vertPos[0],vertPos[1],vertPos[2]), n= vert+'_Jnt')
                jointsMade.append(theJoint)
            
            theLoc = cmds.spaceLocator(n= vert+'_Loc')
            cmds.setAttr(theLoc[0]+'.tx', vertPos[0])
            cmds.setAttr(theLoc[0]+'.ty', vertPos[1])
            cmds.setAttr(theLoc[0]+'.tz', vertPos[2])
            
            locsMade.append(theLoc[0])
            
            cposNode = cmds.createNode('closestPointOnSurface', n= vert+'_cpos')
            decomMatrix = cmds.createNode('decomposeMatrix', n= vert+'_dcom')
            
            cmds.connectAttr(theLoc[0]+'.worldMatrix[0]', decomMatrix+'.inputMatrix', f=True)
            cmds.connectAttr(decomMatrix+'.outputTranslate', cposNode+'.inPosition', f=True)
            
            cmds.connectAttr(glueSurface+'.worldSpace[0]', cposNode+'.inputSurface', f=True)
            #cmds.connectAttr(theLoc[0]+'.worldSpace[0]', cposNode+['.inPosition', f=True)
            
            """
            follicleShapeNode = cmds.createNode('follicle', n = theLoc[0]+"_to_"+glueSurface)
            follicleTransformNode = cmds.listRelatives(follicleShapeNode,p=True)
            
            cmds.connectAttr(glueSurface+'.worldSpace[0]',follicleShapeNode+'.inputSurface',f=True)
            cmds.connectAttr(glueSurface+".worldMatrix[0]", follicleShapeNode+".inputWorldMatrix",f=True)

            cmds.connectAttr(follicleShapeNode+".outRotate", follicleTransformNode[0]+".rotate",f=True)
            cmds.connectAttr(follicleShapeNode+".outTranslate", follicleTransformNode[0]+".translate",f=True)
            #cmds.setAttr(follicleShapeNode+".parameterU", posData[2])
            #cmds.setAttr(follicleShapeNode+".parameterV", posData[3])
            cmds.connectAttr(cposNode+'.parameterU', follicleShapeNode+'.parameterU', f=True)
            cmds.connectAttr(cposNode+'.parameterV', follicleShapeNode+'.parameterV', f=True)

            cmds.parent(theJoint,follicleTransformNode)
            """

            theOnEyeLoc = cmds.spaceLocator(n= vert+'_onSurface')
            cmds.connectAttr(cposNode+'.position', theOnEyeLoc[0]+'.translate', f=True)

            if createJoint:
                cmds.parentConstraint(theOnEyeLoc[0], theJoint,mo=False)
                
            cmds.normalConstraint(orientSurface,theOnEyeLoc[0])
            
        return locsMade