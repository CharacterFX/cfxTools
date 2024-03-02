import cfx.systemSettings as sysSet

import maya.cmds as cmds

import importlib
importlib.reload(sysSet)

class metaSystem(object):
    
    def __init__(self):
        
        self.__settings = sysSet.sysSettings()

    def metaGUI(self):

        if cmds.window("metaGUI", exists = True):
            cmds.deleteUI("metaGUI")
        
        windowWidth = 400
        windowHeight = 700
        
        window = cmds.window("metaGUI", title = "Meta nodes", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = True)

        cmds.columnLayout()
        self.metaNodeSystemsMenu = cmds.optionMenu( label='Meta System', cc = self.updateListedNodes )
        cmds.menuItem( label='All' )
        cmds.menuItem( label='character' )
        cmds.menuItem( label='engine' )
        cmds.menuItem( label='deformer' )
        cmds.menuItem( label='facial' )
        cmds.menuItem( label='face' )
        cmds.menuItem( label='faceShape' )
        cmds.menuItem( label='body' )
        cmds.menuItem( label='bodySdks' )
        cmds.menuItem( label='bodyShapes' )
        cmds.menuItem( label='mocap' )
        cmds.menuItem( label='mocapDestination' )
        cmds.menuItem( label='mocapSource' )

        self.metaTextList = cmds.iconTextScrollList(allowMultiSelection=True, dcc = self.selectMetaNode)
        #cmds.popupMenu(self.metaTextList, pmc = self.runMenuCommand)
        #cmds.menuItem('delete')
        #cmds.menuItem('select')

        cmds.button(label = "Delete Selected Nodes", c=self.deleteSelectedMenuNodes)
     
        self.updateListedNodes()

        cmds.showWindow(window)

    def updateListedNodes(self, *args):

        metaType = cmds.optionMenu( self.metaNodeSystemsMenu, q=1, v=1 )
        if metaType == 'All':
            metaNodes = self.findMeta()
        else:
            print(metaType)
            metaNodes = self.findMeta(metaType)
            print(metaNodes)

        cmds.iconTextScrollList(self.metaTextList, e = 1, ra = 1)
        cmds.iconTextScrollList(self.metaTextList, e = 1, append = metaNodes)

    def selectMetaNode(self, *args):

        metaType = cmds.iconTextScrollList( self.metaTextList, q=1, si=1 )
        cmds.select(metaType,r=1)

    def deleteSelectedMenuNodes(self, *args):

        metaType = cmds.iconTextScrollList( self.metaTextList, q=1, si=1 )
        cmds.delete(metaType)
        self.updateListedNodes()

    def connectToSystem(self, setupDataNode, objectToConnect, attrToConnectTo, objectAttr = 'setupData', multiAttr = False):

        if cmds.objExists(setupDataNode):

            if cmds.objExists(setupDataNode+"."+attrToConnectTo) is False:
                cmds.addAttr(setupDataNode, ln= attrToConnectTo, at="message" )
            if cmds.objExists(objectToConnect+"."+objectAttr) is False:
                cmds.addAttr(objectToConnect, ln= objectAttr, at="message" , multi = multiAttr )
            alreadyConnected = cmds.listConnections(objectToConnect+'.'+objectAttr,s=1,d=0)
            if alreadyConnected is None:
                cmds.connectAttr(setupDataNode+'.'+attrToConnectTo, objectToConnect+'.'+objectAttr, f=True)
            else:
                if setupDataNode not in alreadyConnected:
                    cmds.connectAttr(setupDataNode+'.'+attrToConnectTo, objectToConnect+'.'+objectAttr, f=True)

        else:
            cmds.error('setupData node does not exist', setupDataNode)

    def addSystemTag(self, setupDataNode, tagName = None):

        cmds.addAttr(setupDataNode, ln= 'system', dt="string" )
        if tagName is not None:
            cmds.setAttr(setupDataNode+".system", tagName, type="string")

    def addMetaNode(self, name = None, system = 'root'):

        setupDataName = 'setupData'

        if name is not None:
            setupDataName = name + '_setupData'
            if system == 'faceShape':
                setupDataName = name

        setupDataNode = cmds.createNode('network',  n = setupDataName)
        cmds.addAttr(setupDataNode, ln= self.__settings.setupData, dt="string" )
        #cmds.setAttr(setupDataNode+"."+self.__settings.setupData, system, type="string")
        cmds.setAttr(setupDataNode+".nodeState", 1)

        self.addSystemTag(setupDataNode, system)

        return [setupDataNode]

    def returnMeta(self, node, root = False):

        sdExists = cmds.objExists(node+'.'+self.__settings.setupData)
        if sdExists:
            setupDataNode = cmds.listConnections(node+'.'+self.__settings.setupData , s=1, d=0)

            if len(setupDataNode) > 0:
                return setupDataNode[0]
            else:
                return None
        else:
            return None

    def findMeta(self, system = ''):

        returnNodes = []
        networkNodes = cmds.ls(type='network')

        allMetaNodes = []

        for node in networkNodes:
            if cmds.objExists(node+'.system'):
                allMetaNodes.append(node)
                if cmds.getAttr(node+'.system') == system:
                    returnNodes.append(node)

        if system is not '':
            return returnNodes

        else:
            return allMetaNodes