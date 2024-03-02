"""
a class to save, load and create control systems
Author: John Riggs
"""
import cfx.systemSettings as sysSet
import cfx.returnObjectWithAttr as roa
import cfx.attrUtilities as attru
import cfx.fileUtils as fu
import cfx.returnUseableChannels as ruc
import cfx.getDistances as gd
import cfx.mirrorSystem as ms
import cfx.metaSystem as rmeta
import cfx.insertBufferGroup as ibg
import cfx.dynamicPOconstraint as dpo
import cfx.glueToClosestPoint as gtcp

import importlib
modulesToReload = [rmeta, ms, attru, sysSet, gtcp]
for mtr in modulesToReload:
    importlib.reload(mtr)

import sys
import maya.cmds as cmds
import maya.mel as mel
import xml.dom.minidom as xd
import json

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class controlShapeSystem(object):
    
    def __init__(self):
        
        self.__settings = sysSet.sysSettings()
        self.__attrFinder = roa.returnObjectWithAttr()
        self.__attrUtil = attru.attrUtilities()
        self.__futil = fu.fileUtils()
        self.__distance = gd.getDistances()
        self.__mirrorTool = ms.mirrorSystem()
        self.__meta = rmeta.metaSystem()
        self.__gluer = gtcp.glueToClosestPoint()

        self.__ctrlScale = 1

    def saveCtrlShapeToFile(self, obj,ctrlShapeName, filename):

        '''
        Save the shape of a control to a file
        @param obj: the curve control to save 
        @param ctrlShapeName: the name of the control shape
        @param filename: the file to save
        '''

        #make sure the directory exists, if not make it
        self.__futil.checkOrMakeDirectory(filename)

        doc = xd.Document()
        root = doc.createElement("shape")
        root.setAttribute("name", str(ctrlShapeName))
        doc.appendChild(root)

        theDegree = cmds.getAttr( obj+'.degree' )
        
        degreeV = doc.createElement("degree")
        degreeV.setAttribute("value", str(theDegree))
        root.appendChild(degreeV)

        colorValue = cmds.getAttr( obj+'.overrideColor' )
        theColor = doc.createElement("color")
        theColor.setAttribute("value", str(colorValue))
        root.appendChild(theColor)
        
        formValue = cmds.getAttr( obj+'.form' )
        theForm = doc.createElement("form")
        theForm.setAttribute("value", str(formValue))
        root.appendChild(theForm)

        vertPos = doc.createElement('vertPos')
        root.appendChild(vertPos)
        
        cmds.select((obj+'.cv[*]'),r=True)
        verts = cmds.ls(sl=True,fl=True)
        for vert in verts:
            
            pos = cmds.pointPosition(vert)
            
            vertnum = doc.createElement("vert")
            vertPos.appendChild(vertnum)
            
            vertnum.setAttribute("x",str(pos[0]))
            vertnum.setAttribute("y",str(pos[1]))
            vertnum.setAttribute("z",str(pos[2]))

        f = open(filename, 'w')

        f.write(doc.toprettyxml())

        f.close()

    def buildCtrlShapeFromFile(self, filename,name,ctrlScale=1.0):
        
        '''
        Build the control from a shape file
        @param filename: the control shape file to load
        @param name: what to name the control
        @param ctrlScale: scale of the control        
        '''

        shapeFile = xd.parse(filename)

        verts = shapeFile.getElementsByTagName('vert')
        theColor = shapeFile.getElementsByTagName('color')

        allPoints = []
        knots = []

        for i, v in enumerate(verts):
            
            allPoints.append([v.attributes['x'].value,v.attributes['y'].value,v.attributes['z'].value])
            knots.append(i)


        theCtrl = cmds.curve(d=1,p=allPoints, k=knots)

        theDegree = shapeFile.getElementsByTagName('degree')

        for td in theDegree:
            if(td.attributes['value'].value == '3'):
                cmds.rebuildCurve(theCtrl,ch=0,rpo=1,rt=0,end=0,kr=1,kcp=1,kep=0,kt=0,s=0,d=3,tol=1e-008)

        theForm = shapeFile.getElementsByTagName('form')
        for fr in theForm:
            if(fr.attributes['value'].value != '0'):
                cmds.closeCurve(theCtrl,ch=0, ps=0, rpo=1, bb=0.5, bki=0, p=0.1)

        theCtrl = cmds.rename(theCtrl,name)

        self.__ctrlScale = ctrlScale
        cmds.scale(self.__ctrlScale, self.__ctrlScale, self.__ctrlScale,theCtrl+".cv[*]",r=True)

        #add attr to make ctrls easy to find
        cmds.addAttr(theCtrl, ln= self.__settings.ctrlMadeAttr, dt="string" )
        cmds.setAttr(theCtrl+"."+self.__settings.ctrlMadeAttr, filename.rpartition('/')[-1], type="string")

        if len(theColor) == 1:
            for tc in theColor:
                cmds.setAttr(theCtrl+".overrideEnabled", 1)
                cmds.setAttr(theCtrl+".overrideColor", int(tc.attributes['value'].value))

        cmds.addAttr(theCtrl, ln= 'reshapeable', at="bool")
        cmds.setAttr(theCtrl+'.reshapeable', 1)
        
        cmds.addAttr(theCtrl, ln= self.__settings.needsReshapenAttr, at="bool")
        cmds.setAttr(theCtrl+'.'+self.__settings.needsReshapenAttr, 1)

        cmds.addAttr(theCtrl, ln= 'allowReColor', at="bool")
        cmds.setAttr(theCtrl+'.allowReColor', 1)

        #if self.__settings.defaultDownAxis == 'x':
            #cmds.rotate( 0, 0, 90, theCtrl+'.cv[*]')

        characterDataNode = self.__meta.findMeta(self.__settings.character)
        if len(characterDataNode) != 1:
            characterDataNode = self.__meta.findMeta(self.__settings.weapon)

        if characterDataNode:
            self.__meta.connectToSystem(characterDataNode[0],theCtrl, self.__settings.allCtrls, self.__settings.characterMetaNode )
        
        return theCtrl
        
    def swapShape(self, ctrl, newShape,ctrlScale=1.0):

        '''
        swap a control shape to a new control shape without breaking control structure
        @param ctrl: the control to change
        @param newShape: what shape to switch to 
        @param ctrlScale: scale of the control        
        '''
        connections = []

        isReshapable = False
        if cmds.objExists(ctrl+'.reshapeable'):
            isReshapable = True
            self.__reshapeable = cmds.getAttr(ctrl+'.reshapeable')
        else:
            cmds.addAttr(ctrl, ln= 'reshapeable', at="bool")
            cmds.setAttr(ctrl+'.reshapeable', 1)

        tempShape = self.buildCtrlShapeFromFile(self.__settings.controlLocation +'\\'+newShape+'.'+self.__settings.ctrlFileExtension,newShape+"temp#")

        cmds.xform(tempShape ,ws=True,m=(cmds.xform(ctrl,q=True,ws=True,m=True)))

        oldShape = cmds.listRelatives(ctrl,s=True)
        newShape = cmds.listRelatives(tempShape,s=True)

        #check if vis is connected, when I have time add all connections
        if oldShape is not None:
            connections = cmds.listConnections(oldShape[0]+'.v',s=True,d=False,p=True)

        cmds.parent(newShape,ctrl,r=True,s=True)

        if oldShape is not None:
            cmds.delete(oldShape)

        cmds.delete(tempShape)
        
        #reconnect vis 
        if oldShape is not None:
            if connections is not None:
                cmds.connectAttr(connections[0],newShape+'.v',f=True )

        cmds.scale(ctrlScale, ctrlScale, ctrlScale,ctrl+".cv[*]",r=True)

        cmds.rename(newShape,ctrl+"Shape")

        if not cmds.objExists(ctrl+'.'+self.__settings.ctrlMadeAttr ):
            cmds.addAttr(ctrl, ln= self.__settings.ctrlMadeAttr, dt="string" )
        cmds.setAttr(ctrl+"."+self.__settings.ctrlMadeAttr, 'swappedShape', type="string") #filename.rpartition('/')[-1]

        if isReshapable:
            if not cmds.objExists(ctrl+'.reshapeable'):
                cmds.addAttr(ctrl, ln= 'reshapeable', at="bool")
                cmds.setAttr(ctrl+'.reshapeable', reshapeable)

        return ctrl
    
    def rebuildControl(self, oldCtrl, newCtrlFile):

        '''
        Rebuild a control shape
        @param oldCtrl: the control to rebuild
        @param newCtrlFile: what shape to switch to    
        '''

        oldShapeName = cmds.listRelatives(oldCtrl,shapes=True)

        connections = cmds.listConnections(oldShapeName[0]+'.v',s=True,d=False,p=True)

        muscleConnection = cmds.listConnections(oldShapeName[0]+'.worldSpace[0]', s=False,d=True,p=True)
        
        doMuscleControl = False

        if muscleConnection is not None:
            doMuscleControl = True


        cmds.delete(oldShapeName)

        newCtrl = self.buildCtrlShapeFromFile(newCtrlFile, oldCtrl+'newShape')

        dupeCtrl = cmds.duplicate(newCtrl)

        cmds.parent(cmds.listRelatives(newCtrl,shapes=True), oldCtrl, add=True,s=True) #a=True,

        cmds.delete(newCtrl)

        newShapeName = cmds.rename(cmds.listRelatives(oldCtrl, s=True),oldCtrl+'Shape')

        if connections is not None:
            cmds.connectAttr(connections[0],newShapeName+'.v',f=True )
            
        cmds.select(dupeCtrl[0]+'.cv[*]',r=True)
        verts = cmds.ls(sl=True,fl=True)

        for idx, vert in enumerate(verts):
            pos = cmds.pointPosition( dupeCtrl[0]+'.cv['+str(idx)+']' )
            cmds.xform(oldCtrl+'.cv['+str(idx)+']',t=(pos[0], pos[1], pos[2]), a=True, ws=True)
  
        cmds.delete(dupeCtrl)

        if doMuscleControl:
            cmds.connectAttr(newShapeName+'.worldSpace[0]', muscleConnection[0], f=True)

        #do color post since it seems to be overwritten
        shapeFile = xd.parse(newCtrlFile)
        theColor = shapeFile.getElementsByTagName('color')
        if len(theColor) == 1:
            for tc in theColor:
                cmds.setAttr(oldCtrl+".overrideEnabled", 1)
                cmds.setAttr(oldCtrl+".overrideColor", int(tc.attributes['value'].value))

        return oldCtrl



    

    def makeAndGroupCtrl(self, items, shape, ctrlScale, autoChannelLock = False, doConstraint = True, ctrlExtension = 'CTRL', doScale = False, doVisGroup = True, jiggle = False):

        '''
        This is the main rigging part, make a control and add the heirarchy for a full rigging control
        @param items[]: The items to make a control for, generally this is just one item
        @param shape: what shape the control will be
        @param ctrlScale: scale of the control
        @param autoChannelLock: = Lock channels of the control based on which channels are locked on the item that is controlled
        @param doConstraint: Constrain the control system correctly, very few scenarios where this is not needed.
        @param ctrlExtension: extension to add to control "LeftArm" becomes "LeftArm_CTRL"
        @param doScale: allow the control to scale
        '''
        #quick test to make sure we pass an array
        if isinstance(items, str):# or isinstance(items, unicode):
            items = [items]

        originalSelect = cmds.ls(sl=True)
        
        #need top transform for parenting
        topTransform = self.__attrFinder.all("topTransform", "*")

        characterDataNode = self.__meta.findMeta(self.__settings.character)
        if len(characterDataNode) != 1:
            characterDataNode = self.__meta.findMeta(self.__settings.weapon)
            
        if characterDataNode:
            characterDataNode = characterDataNode[0]

        else:
            print('NO META DATA NODE, Creating a generic one')
            characterDataNode = self.__meta.addMetaNode(name = 'generic', system = 'generic')[0]

        print(characterDataNode,self.__settings.topTransform)
        if cmds.objExists(characterDataNode+'.'+self.__settings.topTransform):
            topTransform = cmds.listConnections(characterDataNode+'.'+self.__settings.topTransform, s=0, d=1)

        doTop = True

        if topTransform == []:
            doTop = False

        for item in items:

            theParent = cmds.listRelatives(item, p=True)

            ctrl = self.buildCtrlShapeFromFile(self.__settings.controlLocation +'\\'+shape+'.'+self.__settings.ctrlFileExtension,item+"_"+ctrlExtension)

            mocapData = None
            if cmds.objExists(item+'.'+self.__settings.mocapBake):
                mocapData = cmds.getAttr(item+'.'+self.__settings.mocapBake, asString = True)
                if mocapData == 'mainBake':
                    self.__meta.connectToSystem(characterDataNode,ctrl, self.__settings.mainBake, objectAttr = self.__settings.mocapBake )

            self.__ctrlScale = ctrlScale
            if ctrlScale == 0.0:
                ctrlDist = 1.0
                if theParent is not None:
                    ctrlDist = self.__distance.between(item, theParent[0]) * 0.1
                    if ctrlDist > 0.1:
                        self.__ctrlScale = ctrlDist
                    else:
                        self.__ctrlScale = 1.0

            cmds.scale(self.__ctrlScale, self.__ctrlScale, self.__ctrlScale,ctrl+".cv[*]",r=True)

            cmpa = cmds.group(em=True, n= item+"_CMPA#")
            cmpb = cmds.group(em=True, n= item+"_CMPB#")
            cmpc = cmds.group(em=True, n= item+"_CMPC#")

            cmds.addAttr(ctrl, ln='CMPA',at="message")
            cmds.addAttr(ctrl, ln='CMPB',at="message")
            cmds.addAttr(ctrl, ln='CMPC',at="message")
            
            cmds.addAttr(cmpa, ln='ctrlComp',at="message")
            cmds.addAttr(cmpb, ln='ctrlComp',at="message")
            cmds.addAttr(cmpc, ln='ctrlComp',at="message")
            
            cmds.connectAttr(ctrl+'.CMPA', cmpa + '.ctrlComp', f=1)
            cmds.connectAttr(ctrl+'.CMPB', cmpb + '.ctrlComp', f=1)
            cmds.connectAttr(ctrl+'.CMPC', cmpc + '.ctrlComp', f=1)            
            
            cmds.addAttr(cmpc, ln= 'lastCMP', at="bool")
            cmds.setAttr(cmpc+'.lastCMP', 1)

            cmds.parent(ctrl,cmpc)
            cmds.parent(cmpc,cmpb)
            cmds.parent(cmpb,cmpa)

            if doTop:
                cmds.parent(cmpa,topTransform)

            if theParent != None:
                cmds.xform(cmpa ,ws=True,m=(cmds.xform(theParent[0],q=True,ws=True,m=True)))
                pcon = cmds.pointConstraint(theParent[0],cmpa,o=[0,0,0],w=1)[0]
                ocon = cmds.orientConstraint(theParent[0],cmpa,o=[0,0,0],w=1)[0]
                
                cmds.addAttr(ctrl, ln='topConstraints',at="message")
                cmds.addAttr(pcon, ln='topConstraints',at="message")
                cmds.addAttr(ocon, ln='topConstraints',at="message")
                
                cmds.connectAttr(ctrl+'.topConstraints', pcon + '.topConstraints', f=1)
                cmds.connectAttr(ctrl+'.topConstraints', ocon + '.topConstraints', f=1)
                
            cmds.xform(cmpb ,ws=True,m=(cmds.xform(item,q=True,ws=True,m=True)))

            cmds.xform(cmpc ,ws=True,m=(cmds.xform(item,q=True,ws=True,m=True)))

            cmds.xform(ctrl ,ws=True,m=(cmds.xform(item,q=True,ws=True,m=True)))

            #connect ctrl visibility
            if doTop:
                if doVisGroup:
                    if cmds.objExists(item+'.visGroup'):
                        if cmds.getAttr(item+'.visGroup') != '':
                            hideGroup = cmds.getAttr(item+'.visGroup')
                            if hideGroup is not None:
                                if cmds.objExists(topTransform[0]):
                                    if not cmds.objExists(topTransform[0]+'.'+ hideGroup):
                                        cmds.addAttr(topTransform[0],ln=hideGroup,at="bool", min=0, max=1, dv = 0)
                                        cmds.setAttr(topTransform[0]+'.'+hideGroup, 0, e=True,keyable=True)

                                    ctrlShape = cmds.listRelatives(ctrl,shapes=True)
                                    cmds.connectAttr(topTransform[0]+'.'+hideGroup, ctrlShape[0]+'.v',f=True)

            if doConstraint:
                cmds.parentConstraint(ctrl,item, mo=False,w=1)# ,st=["x", "y", "z"])

            if doScale:
                cmds.scaleConstraint(ctrl,item, mo=True,w=1)

            if autoChannelLock:
                lockTheseAttrs = ruc.returnUseableChannels(item,True)
                if len(lockTheseAttrs) > 0:
                    for lta in lockTheseAttrs:
                        cmds.setAttr(ctrl+'.'+lta, l=True,cb=False,k=False)

            #transfer attrs for mirroring to ctrls
            for attr in ['side', 'type', 'otherType']:
                self.__attrUtil.transfer(item , ctrl, attr)

            #connect with message attr to link control and controlled
            if not cmds.objExists(item+'.'+self.__settings.control):
                cmds.addAttr(item, ln=self.__settings.control,at="message")
            if not cmds.objExists(ctrl+'.'+self.__settings.controlled):
                cmds.addAttr(ctrl, ln=self.__settings.controlled,at="message")

            cmds.connectAttr(ctrl+'.'+self.__settings.controlled, item+'.'+self.__settings.control, f =True)

            order = 0

            if cmds.objExists( item+'.rotOrder'):
                order = cmds.getAttr(item+'.rotOrder')

            if cmds.objExists( item+'.originalJnt'):
                originalJnt = cmds.listConnections(item+'.originalJnt',s=1,d=0)
                if originalJnt:
                    order = cmds.getAttr(originalJnt[0]+'.rotOrder')

            if order:
                if order == 1:
                    cmds.setAttr(ctrl+'.rotateOrder', 0)
                if order == 2:
                    cmds.setAttr(ctrl+'.rotateOrder', 3)
                if order == 3:
                    cmds.setAttr(ctrl+'.rotateOrder', 4)
                if order == 4:
                    cmds.setAttr(ctrl+'.rotateOrder', 1)
                if order == 5:
                    cmds.setAttr(ctrl+'.rotateOrder', 2)
                if order == 6:
                    cmds.setAttr(ctrl+'.rotateOrder', 5)

            if jiggle:
                self.createParticleForControl(ctrl)

        if len(originalSelect) != 0:
            cmds.select(originalSelect,r=True)

        return ctrl, cmpa



    def saveVertexPosition(self, objects, objectSpace, muscle, removeNamespace, filename):

        '''
        Saves control shapes to auto rebuild in rig
        @param objects: the objects to save their vertex coordinates
        @param objectSpace: Wether its saved in objectspace or worldspace (other spaces not implemented at this time)
        @param muscle: Is it a muscle?
        @param removeNamespace: should the namespace be removed
        @param filename: the file name to save the file
        '''

        prevSelection = cmds.ls(sl=True)

        jsonDict={}
        posList = []
        colorList = []

        jsonDict['objectSpace'] = objectSpace

        for obj in objects:
            if cmds.objectType(obj) == "nurbsCurve":
                obj = cmds.listRelatives(obj,p=True)[0]

            colorAttr = str(cmds.getAttr(obj+'.overrideColor'))
            if removeNamespace: obj = obj.rpartition(":")[2]
            colorList.append(obj + " " + colorAttr)

        for obj in objects:
            cmds.select( clear=True )
            cmds.select((obj+'.cv[*]'),r=True)
            verts = cmds.ls(sl=True,fl=True)
            for vert in verts:
                pos = cmds.pointPosition(vert)
                if(objectSpace): pos = cmds.pointPosition(vert, l=True)
                if removeNamespace: vert = vert.rpartition(":")[2]
                vertPosforFile = (vert+" "+str(pos[0])+" "+str(pos[1])+" "+str(pos[2]))

                posList.append(vertPosforFile)

        f = open(filename, 'w')
        jsonDict['colors'] = colorList
        jsonDict['pointPositions']= posList
        jsonDump=json.dumps(jsonDict,indent=4)
        f.write(jsonDump)
        f.close()

        if len(prevSelection) > 0:
            cmds.select(prevSelection, r=True)


    def selectAndSaveCtrls(self, directory, removeNamespace = True):

        '''
        Auto save all controls to file for rig rebuild
        @param directory: The directory to dump all the control shapes into
        @param removeNamespace: should the namespace be removed
        '''

        ctrls = self.__attrFinder.all('controlMade')

        log.info('Controls to save :\n%s' % ctrls)

        for ctrl in ctrls:
            ctrlFileName = ctrl.split(':')[-1]
            self.saveCtrlShapeToFile(ctrl, cmds.getAttr(ctrl+'.controlMade'), directory+'/'+ctrlFileName+'.ctrl')

    def selectAndSaveMuscles(self, filename, removeNamespace = True):

        '''
        Auto save all muscles to file for rig rebuild
        @param directory: The directory to dump all the control shapes into
        @param removeNamespace: should the namespace be removed
        '''

        muscles = self.__attrFinder.all('muscleCtrl')

        log.info('Muscles to save :\n%s' % muscles)

        for muscle in muscles:
            ctrlFileName = muscle.split(':')[-1]
            self.saveCtrlShapeToFile(muscle, cmds.getAttr(muscle+'.muscleCtrl'), filename+'/'+ctrlFileName+'.muscle')

    def setVertexPosition(self, filename, addNameSpace = '', doShapes = True, doColors = True):

        '''
        Save vertex positions to a file
        @param directory: The directory to dump all the control shapes into
        @param addNameSpace: should the namespace be added
        @param doShapes: save the shape?
        @param doColors: save the color?
        '''

        doColor = True

        srcDict = {}
        colors = {}

        fileIn = open(filename)
        fileData = fileIn.read()
        fileIn.close()
        srcDict = json.loads(fileData)
        
        objectSpace = srcDict['objectSpace']
        
        vertPositions = srcDict['pointPositions']

        try:
            colors = srcDict['colors']

        except:
            doColor = False
        
        if doShapes:
            for each in vertPositions:
                data = each.split(" ")
                if addNameSpace != "": data[0] = addNameSpace+":"+data[0]
                if(cmds.objExists(data[0])):
                    cmds.xform(data[0],ws=True,a=True,t=(data[1],data[2],data[3]))
                else: 
                    log.info('control not found, skipping :\n%s' % data[0]) 

        if doColors:
            if doColor:
                for each in colors:
                    data = each.split(" ")
                    if addNameSpace != "": data[0] = addNameSpace+":"+data[0]
                    if(cmds.objExists(data[0])):
                        cmds.setAttr(data[0] + '.overrideEnabled',1)
                        cmds.setAttr(data[0] + '.overrideColor',k=True,l=False)
                        cmds.setAttr(data[0] + '.overrideColor',int(data[1]))

                        if cmds.objExists(data[0]+"Shape.overrideEnabled"):
                            cmds.setAttr(data[0]+"Shape.overrideEnabled", 0)
                        else:
                            log.info('Object '+data[0]+'Shape.overrideEnabled doesnt exist, skipping') 


    def mirrorCtrlShape(self, ctrls, fromPrefix = 'Left', axis = 'X'):

        '''
        Mirror a control shape
        @param ctrls: Controls to mirror
        @param fromPrefix: From prefix for mirroring
        @param axis: The axis to mirror
        '''

        toPrefix = ''
        searchFor = ''
        replaceWith = ''

        if fromPrefix == 'Left':
            toPrefix = 'Right'

        if fromPrefix == 'left':
            toPrefix = 'right'

        if fromPrefix == 'Lf':
            toPrefix = 'Rt'


        for ctrl in ctrls:

            toCtrl = ctrl.replace(fromPrefix,toPrefix)
            if fromPrefix == 'Left':
                if 'Lf' in toCtrl:
                    toCtrl = toCtrl.replace('Lf','Rt')

            if fromPrefix == 'Lf':
                if 'Left' in toCtrl:
                    toCtrl = toCtrl.replace('Left','Right')

            cmds.select(ctrl+'.cv[*]')
            verts = cmds.ls(sl=True,fl=True)

            for vert in verts:

                newVert = toCtrl+'.'+ vert.rpartition('.')[2]

                vertPos = cmds.pointPosition(vert)

                if axis == 'X':
                    vertPos = [vertPos[0]* -1, vertPos[1], vertPos[2]]

                if axis == 'Y':
                    vertPos = [vertPos[0], vertPos[1]* -1, vertPos[2]]

                if axis == 'Z':
                    vertPos = [vertPos[0], vertPos[1], vertPos[2]* -1]

                if cmds.objExists(toCtrl):
                    cmds.xform(newVert, ws=True, a=True, t=(vertPos[0], vertPos[1], vertPos[2]))

                else:
                    log.info('Object does not exist : %s' % toCtrl)


    def manualMirrorShape(self, fromCtrl, toCtrl, axis = 'X'):

        '''
        Mirrors single controls over
        @param fromCtrl: Really?
        @param toCtrl: Derp
        @param axis: The axis to mirror
        '''

        isTransform = cmds.objectType(fromCtrl)
        if isTransform == 'transform':
            fromCtrl = cmds.listRelatives(fromCtrl, s=True)[0]

        objType = cmds.objectType(fromCtrl)

        if objType == 'mesh':
            cmds.select(fromCtrl+'.vtx[*]')

        if objType == 'nurbsCurve':
            cmds.select(fromCtrl+'.cv[*]')
        
        verts = cmds.ls(sl=True,fl=True)

        for vert in verts:

            newVert = toCtrl+'.'+ vert.rpartition('.')[2]

            vertPos = cmds.pointPosition(vert)

            if axis == 'X':
                vertPos = [vertPos[0]* -1, vertPos[1], vertPos[2]]

            if axis == 'Y':
                vertPos = [vertPos[0], vertPos[1]* -1, vertPos[2]]

            if axis == 'Z':
                vertPos = [vertPos[0], vertPos[1], vertPos[2]* -1]

            if cmds.objExists(newVert):
                cmds.xform(newVert, ws=True, a=True, t=(vertPos[0], vertPos[1], vertPos[2]))
            else:
                print('No object, ', newVert, ' skipping.')
    

    def autoMirrorAll(self):

        '''
        Auto mirrors all controls built with this system
        '''

        allCtrls = self.__attrFinder.all(self.__settings.ctrlMadeAttr, '*')

        self.__settings.allSides = [['Left','Right'], ['left','right'], ['Lf','Rt'], ['l_','r_'], ['Lt','Rt']]

        fullSides = [['Left','Right'], ['left','right']]

        for ctrl in allCtrls:
            namespace = ''
            theCtrl = ctrl
            nsList = ctrl.split(':')

            if len(nsList) > 1:
                theCtrl = nsList[-1]
                del nsList[-1]
                namespace = ":".join(nsList)

            for sides in self.__settings.allSides:
                #log.info('Mirroring sides : %s' % sides)

                fromSide = sides[0]
                toSide = sides[1]

                #if theCtrl.startswith(fromSide):
                if fromSide in theCtrl :
                    for fs in fullSides:
                        toCtrl = ctrl.replace(fromSide, toSide)

                        if fs[0] in toCtrl:
                            toCtrl = toCtrl.replace(fs[0], fs[1])
                        #ADD CHECKSUM TO MAKE SURE ITS THE SAME SHAPE
                        
                    self.manualMirrorShape(ctrl, toCtrl)

    def autoMirrorAllTEMP(self):

        '''
        Auto mirrors all controls built with this system
        '''

        allCtrls = self.__attrFinder.all(self.__settings.ctrlMadeAttr, '*')

        self.__settings.allSides = [['Lt','Rt']]

        for ctrl in allCtrls:

            for sides in self.__settings.allSides:
                log.info('Mirroring sides : %s' % sides)

                fromSide = sides[0]
                toSide = sides[1]

                if fromSide in ctrl:
                    toCtrl = ctrl.replace(fromSide, toSide)
                    if cmds.objExists(toCtrl):
                        self.manualMirrorShape(ctrl, toCtrl)


    def mirrorAllCtrlsNew(self):

        allCtrls = self.__attrFinder.all(self.__settings.ctrlMadeAttr, '*')

        for ctrl in allCtrls:

            for sides in self.__settings.allSides:
                #log.info('Mirroring sides : %s' % sides)

                fromSide = sides[0]

                if fromSide in ctrl:
                    toSide = self.__mirrorTool.returnMirrorPartner(ctrl)

                    if toSide is not None:
                        if cmds.objExists(toSide):
                            self.manualMirrorShape(ctrl, toSide)


    def autoColorBySide(self, threshold = 0.01, reversed = False, axis = 'X', typeWork = 'ctrl'):

        '''
        Colors controls at initial build based on the side of the rig they are on by worldspace
        @param threshold: Anything within this +/- will be considered center
        @param reversed: Needed for special scenarios where the rig is backwards in the scene
        @param axis: The axis to color by
        '''
        if typeWork == 'ctrl':
            allCtrls = self.__attrFinder.all(self.__settings.ctrlMadeAttr, '*')
        else:
            allCtrls = cmds.ls(type=typeWork)

        for ctrl in allCtrls:
            allowRecolor = 1
            ctrlNameSplit = ctrl.split('_')
            for it in ['l','r','left','right','CTRL']:
                if it in ctrlNameSplit:
                    ctrlNameSplit.remove(it)
            ctrlName = '_'.join(ctrlNameSplit)

            if cmds.objExists(ctrl+'.allowReColor'):
                allowRecolor = cmds.getAttr(ctrl+'.allowReColor')
            cmds.setAttr(ctrl+".overrideEnabled", 1)    
            if axis == 'X':
                distFromCenter = cmds.xform(ctrl,q=True,ws=True,t=True)[0]
                if distFromCenter > threshold:
                    if reversed:
                        if allowRecolor:
                            cmds.setAttr(ctrl+".overrideColor", self.__settings.rightColor)
                            if cmds.objExists(ctrl+".side"):
                                cmds.setAttr(ctrl+".side", 2)
                                cmds.setAttr(ctrl+".type", 18)
                                cmds.setAttr(ctrl+".otherType", ctrlName, type="string")
                    else:
                        if allowRecolor:
                            cmds.setAttr(ctrl+".overrideColor", self.__settings.leftColor)
                            if cmds.objExists(ctrl+".side"):
                                cmds.setAttr(ctrl+".side", 1)
                                cmds.setAttr(ctrl+".type", 18)
                                cmds.setAttr(ctrl+".otherType", ctrlName, type="string")

                elif distFromCenter < threshold * -1:
                    if reversed:
                        if allowRecolor:
                            cmds.setAttr(ctrl+".overrideColor", self.__settings.leftColor)
                            if cmds.objExists(ctrl+".side"):
                                cmds.setAttr(ctrl+".side", 1)
                                cmds.setAttr(ctrl+".type", 18)
                                cmds.setAttr(ctrl+".otherType", ctrlName, type="string")
                    else:
                        if allowRecolor:
                            cmds.setAttr(ctrl+".overrideColor", self.__settings.rightColor)
                            if cmds.objExists(ctrl+".side"):
                                cmds.setAttr(ctrl+".side", 2)
                                cmds.setAttr(ctrl+".type", 18)
                                cmds.setAttr(ctrl+".otherType", ctrlName, type="string")

                elif distFromCenter >= threshold * -1 and distFromCenter <= threshold:
                    if allowRecolor:
                        cmds.setAttr(ctrl+".overrideColor", self.__settings.middleColor)
                        if cmds.objExists(ctrl+".side"):
                            cmds.setAttr(ctrl+".side", 0)
                            cmds.setAttr(ctrl+".type", 18)
                            cmds.setAttr(ctrl+".otherType", ctrlName, type="string")

    def createParticleForControl(self, theObject):
    
        position = cmds.xform(theObject, q=1, t=1, ws=1)
        theParticle = cmds.particle(p=[position], c = 1, n=theObject+'_particle')
        
        buf1 = ibg.insertBufferGroup(theObject)
        bufCon = ibg.insertBufferGroup(theObject,'con')
        
        wsGroup = cmds.group(em=True, n=theObject+'_particleSpace')
        parentGroup = cmds.group(em=True, n=theObject+'_parentSpace')
        bufDyn = cmds.group(em=True, n=theObject+'_dyn')
        
        cmds.xform(wsGroup, m=(cmds.xform(theObject,q=1,ws=1, m=1)))
        cmds.xform(parentGroup, m=(cmds.xform(theObject,q=1,ws=1, m=1)))
        cmds.xform(bufDyn, m=(cmds.xform(theObject,q=1,ws=1, m=1)))
        
        cmds.parent(parentGroup, buf1)
        cmds.parent(bufDyn, buf1)
        
        cmds.connectAttr(theParticle[1]+'.worldCentroid', wsGroup+'.translate')
        
        cmds.goal(theParticle,g=buf1,w=1)
        
        cmds.parentConstraint(wsGroup,bufDyn,mo=1)
        
        cmds.addAttr(theObject,ln='settleSpeed',at="double", min=0, max=4, dv = 2)
        cmds.setAttr(theObject+'.settleSpeed', 2, e=True,keyable=True)
        cmds.connectAttr( theObject+'.settleSpeed', theParticle[1]+'.goalSmoothness', f=1)
        
        cmds.addAttr(theObject,ln='speedToTarget',at="double", min=0, max=1, dv = 0.2)
        cmds.setAttr(theObject+'.speedToTarget', 0.2, e=True,keyable=True)
        cmds.connectAttr( theObject+'.speedToTarget', theParticle[1]+'.goalWeight[0]', f=1)
        
        theDpo = dpo.dynamicPOconstraint([bufDyn, parentGroup],bufCon)
        cmds.addAttr(theObject,ln='parentOrDynamic',at="double", min=0, max=1, dv = 0)
        cmds.setAttr(theObject+'.parentOrDynamic', 0, e=True,keyable=True)
        cmds.connectAttr( theObject+'.parentOrDynamic', theDpo[2], f=1)
        
    def reshapeGUI(self):
        
        if cmds.window("reshapeGUI", exists = True):
            cmds.deleteUI("reshapeGUI")
        
        windowWidth = 400
        windowHeight = 700
        textColumWidth = windowWidth * 0.70
        buttonColumWidth = windowWidth * 0.1
        bufferWidth = 5
        
        reshapeWindow = cmds.window("reshapeGUI", title = "Control Reshape GUI", w = windowWidth, h = windowHeight, mnb = False, mxb = False, sizeable = True)
        
        listColumWidth = windowWidth * 0.49
        ctrlRowColumnLayout = cmds.rowColumnLayout(nc = 2, cw = [(1, listColumWidth), (2, listColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth)])

        cmds.text(label="Controls that need reshaped : ", align = "left")
        cmds.text(label="Already been reshaped : ", align = "right")
        
        cmds.textScrollList( "needsReshapen", numberOfRows=30, allowMultiSelection=True, showIndexedItem=4, dcc = self.reshapeCtrlFromList )
        cmds.popupMenu()
        cmds.menuItem(label="Update List", c = self.updateReshapebale)
        
        cmds.textScrollList( "alreadyReshapen", numberOfRows=8, allowMultiSelection=True, showIndexedItem=4, dcc = self.reshapeDueCtrlFromList )
        cmds.popupMenu()
        cmds.menuItem(label="Update List", c = self.updateReshapebale)

        cmds.button(label = "Rotate 90 on the X axis", w = windowWidth, h = 50, c = self.rotateX90)
        cmds.text(label="",vis=False)
        cmds.button(label = "Rotate 90 on the Y axis", w = windowWidth, h = 50, c = self.rotateY90)
        cmds.text(label="",vis=False)
        cmds.button(label = "Rotate 90 on the Z axis", w = windowWidth, h = 50, c = self.rotateZ90)
        cmds.text(label="",vis=False)
        
        cmds.button(label = "Mark selected reshaped", w = windowWidth, h = 50, c = self.markReshaped)
        cmds.text(label="",vis=False)
        
        cmds.button(label = "Finalize Selected", w = windowWidth, h = 50, c = self.finalizeReshape)
        cmds.text(label="",vis=False)
        
        cmds.showWindow(reshapeWindow)
        
        self.updateReshapebale()
        
    def markReshaped(self, *args):
        
        selectedReshapable = cmds.textScrollList("needsReshapen", q=True, si=True)

        for rsh in selectedReshapable:
            cmds.setAttr(rsh+'.'+self.__settings.needsReshapenAttr, 0)
            
        self.updateReshapebale()
        
    def rotateX90(self, *args):
    
        cmds.rotate(90,0,0)
        
    def rotateY90(self, *args):
    
        cmds.rotate(0,90,0)
        
    def rotateZ90(self, *args):
    
        cmds.rotate(0,0,90)
        
        
    def reshapeCtrlFromList(self, *args):

        selectedCtrls = cmds.textScrollList( "needsReshapen", q=True, si=True)
        self.__shapeBeingEdited = selectedCtrls[0]
        self.__visConnected = cmds.listConnections(self.__shapeBeingEdited+'.v', s=1, d=0, p=1)

        if self.__visConnected:
            cmds.disconnectAttr(self.__visConnected[0], self.__shapeBeingEdited+'.v')
            cmds.setAttr(self.__shapeBeingEdited+'.v', 1)
            
        cmds.select(selectedCtrls[0]+'.cv[*]',r=True)
        
        cmds.viewFit( f=0.25 )
        #self.finalizeReshape(selectedCtrls[0])
        
    def reshapeDueCtrlFromList(self, *args):

        selectedCtrls = cmds.textScrollList( "alreadyReshapen", q=True, si=True)
        self.__shapeBeingEdited = selectedCtrls[0]
        self.__visConnected = cmds.listConnections(self.__shapeBeingEdited+'.v', s=1, d=0, p=1)

        if self.__visConnected:
            cmds.disconnectAttr(self.__visConnected[0], self.__shapeBeingEdited+'.v')
            cmds.setAttr(self.__shapeBeingEdited+'.v', 1)
            
        cmds.select(selectedCtrls[0]+'.cv[*]',r=True)
        
        cmds.viewFit( f=0.25 )
        #self.finalizeReshape(selectedCtrls[0])
        
    def finalizeReshape(self, *args):
        
        cmds.setAttr(self.__shapeBeingEdited+'.'+self.__settings.needsReshapenAttr, 0)
        
        if self.__visConnected:
            cmds.connectAttr(self.__visConnected[0], self.__shapeBeingEdited+'.v')
            
        self.updateReshapebale()
        
    def updateReshapebale(self, *args):
        
        needsReshapedCtrls = self.__attrFinder.all(self.__settings.needsReshapenAttr, True)
        alreadyReshapedCtrls = self.__attrFinder.all(self.__settings.needsReshapenAttr, False)
        
        cmds.textScrollList("needsReshapen", edit = True, ra = True)
        cmds.textScrollList("alreadyReshapen", edit = True, ra = True)
            
        for each in needsReshapedCtrls:   
            cmds.textScrollList("needsReshapen",edit = True, append = each)

        for each in alreadyReshapedCtrls:   
            cmds.textScrollList("alreadyReshapen",edit = True, append = each)
    
    """
    add a space switcher to a control
    theCtrl is the control you want to be able to space switch
    newParent is what it should attach to, use "worldSpace" to attach to the world space system of the character.
    """
    def addSpaceSwitcher(self, theCtrl, newParent):
    
        ctrlParent = cmds.listRelatives(theCtrl, p=1)
        if len(ctrlParent) < 1:
            cmds.error('Control must have a parent in order for this to work.')
        
        ctrlParentParent = cmds.listRelatives(ctrlParent[0], p=1)
        if len(ctrlParentParent) < 1:
            cmds.error('Control must be built with 2 levels of parents in order for this to work.')
        
        if not cmds.objExists(theCtrl+'.'+self.__settings.spaceSwitcherCon):
            cmds.addAttr(theCtrl, ln= self.__settings.spaceSwitcherCon, at="message" )
            parentSpaceNode = cmds.group(em=1, name = theCtrl+'_parentSpace')
            cmds.parent(parentSpaceNode, ctrlParentParent[0])
            cmds.xform(parentSpaceNode ,ws=True,m=(cmds.xform(ctrlParent[0],q=True,ws=True,m=True)))
            
            self.theCon =  cmds.parentConstraint(parentSpaceNode, ctrlParent[0])[0]
            cmds.addAttr(self.theCon, ln= self.__settings.spaceSwitcherCon, at="message" )
            cmds.connectAttr(theCtrl+'.'+self.__settings.spaceSwitcherCon, self.theCon+'.'+self.__settings.spaceSwitcherCon)
            wal = cmds.parentConstraint(self.theCon, q=1, wal=1)[0]
            cmds.addAttr(theCtrl,ln= 'parentSpace',at="double", min=0, max=1, dv = 1)
            cmds.connectAttr(theCtrl+'.parentSpace', self.theCon+'.'+wal)
            cmds.setAttr(self.theCon+".interpType", 2)
        else:
            self.theCon =  cmds.listConnections(theCtrl+'.'+self.__settings.spaceSwitcherCon, s=0,d=1)[0]
            
        if newParent == 'worldSpace':
        #find the worldspace node thru the meta system
            newParent = 'worldSpace'
            
        newSpaceNode = cmds.group(em=1, name = theCtrl+'_'+newParent)
        cmds.parent(newSpaceNode, ctrlParentParent[0])
        cmds.xform(newSpaceNode ,ws=True,m=(cmds.xform(ctrlParent[0],q=True,ws=True,m=True)))
        
        spaceAtParentNode = cmds.group(em=1, name = newParent+'_'+theCtrl)
        cmds.parent(spaceAtParentNode, newParent)
        cmds.xform(spaceAtParentNode ,ws=True,m=(cmds.xform(ctrlParent[0],q=True,ws=True,m=True)))
        
        cmds.parentConstraint(spaceAtParentNode, newSpaceNode)[0]
        self.theCon =  cmds.parentConstraint(newSpaceNode, ctrlParent[0])[0]
        wal = cmds.parentConstraint(self.theCon, q=1, wal=1)[-1]
        
        cmds.addAttr(theCtrl,ln= newParent+'_Spc',at="double", min=0, max=1, dv = 0)
        cmds.connectAttr(theCtrl+'.'+newParent+'_Spc', self.theCon+'.'+wal)
        
        self.swapShape(spaceAtParentNode, self.__settings.spaceSwitcher)
        cmds.connectAttr(theCtrl+'.'+newParent+'_Spc', spaceAtParentNode+'.v')
        
        
    def glueExistingCtrlToMesh(self, theCtrl, theMesh):

        controlled = cmds.listConnections(theCtrl+"."+self.__settings.controlled,s=0,d=1)
        controlledCon = cmds.listConnections(controlled[0]+'.translateX', s=1, d=0)

        cmds.delete(cmds.listConnections(theCtrl+".topConstraints",s=0,d=1), controlledCon)
        
        #ctrlBuf = ibg.insertBufferGroup(theCtrl,'zero')
        ctrlBuf = cmds.listConnections(theCtrl+".CMPC",s=0,d=1)
        bufCon = ibg.insertBufferGroup(controlled[0],'follicleBuffer')
        
        cmds.connectAttr(theCtrl+".rotate", controlled[0]+".rotate", f=1)
        cmds.connectAttr(theCtrl+".translate", controlled[0]+".translate", f=1)
        
        self.__gluer.surface(theMesh, ctrlBuf[0], 'follicle')

    def convertConstraintToConnection(self, theCtrl):

        controlledJoint = cmds.listConnections(theCtrl+'.controlled', s=0, d=1, type='joint')
        connections = cmds.listConnections(theCtrl+'.t', s=0, d=1, type='parentConstraint')

        #this need to querry channels and do it based on that

        cmds.delete(connections)

        buf1 = ibg.insertBufferGroup(controlledJoint[0])

        cmds.connectAttr(theCtrl+'.t', controlledJoint[0]+'.t')
        cmds.connectAttr(theCtrl+'.r', controlledJoint[0]+'.r')