import maya.cmds as cmds
import cfx.returnObjectWithAttr as roa
import cfx.fileUtils as fu
import cfx.metaSystem as rmeta

class attachWeapon(object):
    
    def __init__(self):

        #modules
        self.__attrFinder = roa.returnObjectWithAttr()
        self.__futil = fu.fileUtils()
        self.__meta = rmeta.metaSystem()

        self.__weaponDirectory = ''
        self.__weaponDirName = 'baseWeaponDirectory'

        if not cmds.optionVar(exists =self.__weaponDirName):#if it doesn't exist, make it
            cmds.optionVar(sv=(self.__weaponDirName, self.__weaponDirectory))
            self.availableWeapons = []#creates a string one
        else:
            self.__weaponDirectory = cmds.optionVar(q=self.__weaponDirName)
            self.availableWeapons = self.__futil.returnWeapons(self.__weaponDirectory)

    def attachWeaponGUI(self):

        if cmds.window("attachWeaponGUI", exists = True):
            cmds.deleteUI("attachWeaponGUI")
        if cmds.windowPref( 'attachWeaponGUI', exists=True ):
            cmds.windowPref( 'attachWeaponGUI', r=True )

        windowWidth = 260
        windowHeight = 800
        
        self.window = cmds.window("attachWeaponGUI", title = "Attach Weapon GUI", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = False, rtf=True)

        menuBarLayout = cmds.menuBarLayout()
        cmds.menu( label='File' )
        cmds.menuItem( label='Settings', c=self.settingsUI)

        cmds.menu( label='Help', helpMenu=True )
        cmds.menuItem( label='About...', c=self.helpUI )

        cmds.setParent( '..' )

        mainLayout = cmds.columnLayout( columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )

        #self.attachDirectionMenu = cmds.optionMenu( label='Attach Direction', cc = self.updateAll )
        #cmds.menuItem( label='Weapon To AttachPoints' )
        #cmds.menuItem( label='Hand To Weapon' )

        cmds.text(label="Attach Points")
        self.attachList = cmds.textScrollList('attachList', numberOfRows=8, allowMultiSelection=False, dcc= self.selectAttachPoint)
        cmds.button(label = "Update", c=self.updateAll)
        self.availableWeaponsList = cmds.textScrollList('availableWeaponsList', numberOfRows=8, allowMultiSelection=False, sc = self.updateWeaponImage)
        cmds.button(label = "Attach!", c=self.attachTheWeapon)
        cmds.button(label = "Cancel", c=self.closeGUI)

        if len(self.availableWeapons) > 0:
            self.weaponImage = cmds.image( image=self.availableWeapons[0] )
        else:
            self.weaponImage = cmds.image( image='' )

        cmds.setParent( '..' )

        self.updateAttachPoints()
        self.updateWeapons()

        cmds.showWindow(self.window)

        cmds.textScrollList( self.availableWeaponsList, edit=True,sii=1)
        cmds.textScrollList( self.attachList, edit=True,sii=2)


    def helpUI(self, *args):
        if cmds.window("helpGUI", exists = True):
            cmds.deleteUI("helpGUI")

        windowWidth = 400
        windowHeight = 500

        helpWindow = cmds.window("helpGUI", title = "Help", w = windowWidth, h = windowHeight, mnb = False, mxb = False, sizeable = True)

        helpLayout = cmds.columnLayout( columnAttach=('both', 5), rowSpacing=10, columnWidth=700 )
        cmds.text(label="Attach Points GUI \nOn first run you will need to set you root weapon directory under File>Setting, once set its persistent.\nThe system then parses that whole file structure for a png image of the weapon that is in the same directory as the weapon rig.\nThe image needs to have \"attach_\" at the beginging and NO \"_rig\" at the end.\nSo for the ARifle_Red you will have a file called \"attach_ARifle_Red_A_01.png\" in the directory where \"SK_ARifle_Red_A_01_rig.ma\" lives.\nIt adds attributes to the root weapon control and sets the one you had selected to 1.\nImage size should be 256x256 for the GUI", ww=1)

        cmds.button(label = "Close", c=self.closeHelpGUI)

        cmds.showWindow(helpWindow)

    def settingsUI(self, *args):

        if cmds.window("settingGUI", exists = True):
            cmds.deleteUI("settingGUI")
        
        windowWidth = 400
        windowHeight = 700
        textColumWidth = windowWidth * 0.70
        buttonColumWidth = windowWidth * 0.1
        bufferWidth = 5

        settingsWindow = cmds.window("settingGUI", title = "Settings", w = windowWidth, h = windowHeight, mnb = False, mxb = False, sizeable = True)

        ctrlFileColumnLayout = cmds.rowColumnLayout(nc = 3, cw = [(1, textColumWidth), (2, buttonColumWidth), (3, buttonColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth),(3, "both", bufferWidth)])
        
        
        cmds.text(label="Weapons Root Directory : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)
        
        self.riggingDirectoryTextField = cmds.textField("Weapons Root Directory", w = textColumWidth+buttonColumWidth, text = self.__weaponDirectory)
        cmds.text(label="",vis=False)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = buttonColumWidth, c = self.updateWeaponDirField)

        cmds.showWindow(settingsWindow)

    def selectAttachPoint(self, *args):

        selectedAttachPoint = cmds.textScrollList( self.attachList, q=True, si = True)
        cmds.select(selectedAttachPoint, r=1)

    def updateWeaponImage(self, *args):

        selectedWeapon = cmds.textScrollList( self.availableWeaponsList, q=True, si = True)

        for aw in self.availableWeapons:
            if selectedWeapon[0] in aw:
                cmds.image(self.weaponImage, e=1, i=aw)

    def updateWeaponDirField(self, *args):

        ctrlFileDir = cmds.fileDialog2(cap = "Select Weapons Root Directory", fm = 2, dialogStyle=2)

        cmds.optionVar(sv=(self.__weaponDirName, ctrlFileDir[0]))

        cmds.textField(self.riggingDirectoryTextField , e=True, text = ctrlFileDir[0])

    def updateAll(self, *args):
        self.updateAttachPoints()
        self.updateWeapons()

    def updateAttachPoints(self, *args):

        cmds.textScrollList( self.attachList, edit=True,removeAll = True)
        self.availableAttachPoints = self.__attrFinder.all('autoSetups', 'attachPoint')

        cmds.textScrollList( self.attachList, edit=True, append = self.availableAttachPoints)

    def updateWeapons(self, *args):

        cmds.textScrollList( self.availableWeaponsList, edit=True,removeAll = True)
        self.availableWeapons = self.__futil.returnWeapons(self.__weaponDirectory)

        for aw in self.availableWeapons:
            cmds.textScrollList( self.availableWeaponsList, edit=True, append = aw.split('\\')[-1].replace('attach_','').replace('.png',''))

    def attachTheWeapon(self, *args):

        selectedWeapon = cmds.textScrollList( self.availableWeaponsList, q=True, si = True)
        if not selectedWeapon:
            selectedWeapon = cmds.ls(sl=1)
            if not selectedWeapon:
                cmds.error("please set the weapon directory correctly or select the root joint of a weapon")

        for aw in self.availableWeapons:
            if selectedWeapon[0] in aw:
                fileToRef = aw.replace('attach_','SKM_').replace('.png','_rig.ma')
        
        cmds.file(fileToRef, r=True, ns='gun')

        setupDataNode = self.__meta.findMeta('weapon')
        if len(setupDataNode) < 1:
            cmds.error('No weapons built with meta system in scene')

        weaponRootCtrl = cmds.listConnections(setupDataNode[0]+'.topTransform')
        if len(weaponRootCtrl) != 1:
            cmds.error('No weapons built with meta system in scene')

        selectedAttachPoint = cmds.textScrollList( self.attachList, q=True, si = True)

        #temp till I figure out a better way to not have a cycle for hands
        if 'handAttach_r' in selectedAttachPoint:
            for aap in self.availableAttachPoints:
                if 'handAttach_l' in aap:
                    self.availableAttachPoints.remove(aap)

        thePcon = cmds.parentConstraint(self.availableAttachPoints, weaponRootCtrl[0], mo=False)
        weights = cmds.parentConstraint(thePcon, q=1, wal=1)

        for wt in weights:
            cmds.addAttr(weaponRootCtrl[0], ln = wt, at = 'double' , min=0, max=1)
            cmds.setAttr(weaponRootCtrl[0]+"."+wt, e = True, keyable = True)
            cmds.connectAttr(weaponRootCtrl[0]+"."+wt, thePcon[0]+'.'+wt)

            if selectedAttachPoint:
                if selectedAttachPoint[0].split(':')[-1] in wt:
                    cmds.setAttr(weaponRootCtrl[0]+"."+wt, 1)


        onWeaponAttaches = cmds.listConnections(setupDataNode[0]+'.attachPointJoints')
        print('onWeaponAttaches: ', onWeaponAttaches)
        characterSetupDataNode = self.__meta.findMeta('character')
        attachable = cmds.listConnections(characterSetupDataNode[0]+'.attachable')

        if len(attachable) > 0:
            for attac in attachable:
                if cmds.objExists(attac+'.attachBufferMade'):
                    for owa in onWeaponAttaches:
                        attachBuffer = cmds.listConnections(attac+'.attachBufferMade')
                        print('attachBuffer[0]: ', attachBuffer[0])
                        pCon = cmds.parentConstraint(owa, attachBuffer[0])
                        weights = cmds.parentConstraint(pCon, q=1, wal=1)
                        cmds.addAttr(attac, ln = weights[-1], at = 'double' , min=0, max=1)
                        cmds.setAttr(attac+"."+weights[-1], e = True, keyable = True)
                        cmds.connectAttr(attac+"."+weights[-1], pCon[0]+'.'+weights[-1])
                        if "GRIP_02" in owa:
                            cmds.setAttr(attac+"."+weights[-1], 1)

    def closeGUI(self, *args):

        if cmds.window("attachWeaponGUI", exists = True):
            cmds.deleteUI("attachWeaponGUI")

    def closeHelpGUI(self, *args):

        if cmds.window("helpGUI", exists = True):
            cmds.deleteUI("helpGUI")
