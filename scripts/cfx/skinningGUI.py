"""
A GUI to consolidate the various skinning tools
Author: John Riggs
"""

import cfx.autoSaveWeights as asw
import cfx.skinningTools as sts
import cfx.vertexTools as vt
import cfx.selectionTools as selt
import cfx.fileUtils as fu

import importlib
modulesToReload = [vt, asw, sts]
for mtr in modulesToReload:
    importlib.reload(mtr)

import maya.cmds as cmds
import os
import os.path
import json

class skinningGUI(object):

    def __init__(self):

        print('skinningGUI v1.0')

        self.__futil = fu.fileUtils()
        self.__weighter = asw.autoSaveWeights()
        self.__skinner = sts.skinningTools() 
        self.__verter = vt.vertexTools()
        self.__selTool = selt.selectionTools()

        self.__skinningInfluencesWindow = ''

        self.__weightsDictionary = {}
        self.__allWeightsDictionary = {}
        self.__vertsList = {}
        self.__vertsDict = {}

        #files and geo
        self.__maleSkinFile = ''
        self.__femaleSkinFile = ''
        self.__vanduulSkinFile = ''

        self.__maleSkinGeo = ''
        self.__femaleSkinGeo = ''
        self.__vanduulSkinGeo = ''

        self.__maleSRCFile = ''
        self.__femaleSRCFile = ''
        self.__vanduulSRCFile = ''

        self.__maleSkinFileVar = 'MALECOPYSKINFILE'
        self.__femaleSkinFileVar = 'FEMALECOPYSKINFILE'
        self.__vanduulSkinFileVar = 'VANDUULCOPYSKINFILE'

        self.__maleSkinGeoVar = 'MALECOPYSKINGEO'
        self.__femaleSkinGeoVar = 'FEMALECOPYSKINGEO'
        self.__vanduulSkinGeoVar = 'VANDUULCOPYSKINGEO'

        self.__maleSRCVar = 'MALESRCFILE'
        self.__femaleSRCVar = 'FEMALESRCFILE'
        self.__vanduulSRCVar = 'VANDUULSRCFILE'

        
        self.__initSettings = False

        if cmds.optionVar(exists =self.__maleSRCVar):#if it doesn't exist, make it
            self.__maleSkinFile = cmds.optionVar(q=self.__maleSRCVar)#creates a string one
        else:
            self.__initSettings = True

        if cmds.optionVar(exists =self.__femaleSRCVar):#if it doesn't exist, make it
            self.__maleSkinFile = cmds.optionVar(q=self.__femaleSRCVar)#creates a string one
        else:
            self.__initSettings = True

        if cmds.optionVar(exists =self.__maleSkinFileVar):#if it doesn't exist, make it
            self.__maleSkinFile = cmds.optionVar(q=self.__maleSkinFileVar)#creates a string one
        else:
            self.__initSettings = True

        if cmds.optionVar(exists =self.__femaleSkinFileVar):#if it doesn't exist, make it
            self.__femaleSkinFile = cmds.optionVar(q=self.__femaleSkinFileVar)#creates a string one
        else:
            self.__initSettings = True

        """
        if cmds.optionVar(exists =self.__vanduulSkinFileVar):#if it doesn't exist, make it
            self.__femaleSkinFile = cmds.optionVar(q=self.__vanduulSkinFileVar)#creates a string one
        else:
            self.__initSettings = True
        """

        if cmds.optionVar(exists =self.__maleSkinGeoVar):#if it doesn't exist, make it
            self.__maleSkinGeo = cmds.optionVar(q=self.__maleSkinGeoVar)#creates a string one
        else:
            self.__initSettings = True

        if cmds.optionVar(exists =self.__femaleSkinGeoVar):#if it doesn't exist, make it
            self.__femaleSkinGeo = cmds.optionVar(q=self.__femaleSkinGeoVar)#creates a string one
        else:
            self.__initSettings = True

        """
        if cmds.optionVar(exists =self.__vanduulSkinGeoVar):#if it doesn't exist, make it
            self.__vanduulSkinGeo = cmds.optionVar(q=self.__vanduulSkinGeoVar)#creates a string one
        else:
            self.__initSettings = True
        """

        #self.__copyWeights = []

    def UI(self):

        if cmds.window("skinningGUI", exists = True):
            cmds.deleteUI("skinningGUI")
        
        windowWidth = 400
        windowHeight = 700
        
        window = cmds.window("skinningGUI", title = "Skinning GUI", w = windowWidth, h = 300, mnb = False, mxb = False, sizeable = True)
        
        #menuLayout = cmds.columnLayout(w = windowWidth, h = 80)

        menuBarLayout = cmds.menuBarLayout()
        cmds.menu( label='File' )
        cmds.menuItem( label='Settings', c=self.settingsUI)
        #cmds.menuItem( label='Open' )
        #cmds.menuItem( label='Close' )

        cmds.menu( label='Help', helpMenu=True )
        cmds.menuItem( label='About...' )

        cmds.setParent( '..' )

        form = cmds.formLayout()
        
        imagePath = cmds.internalVar(upd = True) + "icons/riggingBanner.jpg"
        cmds.image(w=windowWidth,h=100, image = imagePath)
        


        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 100), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
        
        #--------------------------------SKINNING LAYOUT TAB
        loadSaveLayout = cmds.columnLayout("skinningLayoutTab", w = windowWidth, h = 300)
        
        textColumWidth = windowWidth * 0.70
        buttonColumWidth = windowWidth * 0.1
        bufferWidth = 5

        cmds.frameLayout( label='Auto Skinning Tools', cll = True )

        cmds.separator(h=15)
        ctrlFileColumnLayout = cmds.rowColumnLayout(nc = 3, cw = [(1, textColumWidth), (2, buttonColumWidth), (3, buttonColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth),(3, "both", bufferWidth)])
        
        
        cmds.text(label="Weights Directory: ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)
        
        weightsFile = cmds.textField("weightsFile", w = textColumWidth+buttonColumWidth)
        cmds.text(label="",vis=False)
        ctrlBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = buttonColumWidth, c = self.updateWeightsFileField) #puppetBrowseButton = cmds.symbolButton(w = 30, h = 30, image = icon)
        
        saveWeights = cmds.button(label = "Auto Save Weights", w = textColumWidth, h = buttonColumWidth, c = self.autoSaveWeights)
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        loadWeights = cmds.button(label = "Auto Load Skin Weights", w = textColumWidth, h = buttonColumWidth, c = self.autoLoadWeights)
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        loadWeights = cmds.button(label = "Auto Update to latest SRC or Mesh", w = textColumWidth, h = buttonColumWidth, c = self.autoUpdateToSRC)
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        cmds.setParent( '..' )
        
        listColumWidth = windowWidth * 0.49
        infsColumnLayout = cmds.rowColumnLayout(nc = 2, cw = [(1, listColumWidth), (2, listColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth)])

        cmds.text(label="Character Weight files : ", align = "left")
        cmds.text(label="influences in File : ", align = "right")
        
        cmds.textScrollList( "characterWeightFiles", numberOfRows=8, allowMultiSelection=True, showIndexedItem=4 , dcc = self.loadInfluencesFromFile)
        cmds.popupMenu()
        cmds.menuItem(label="Update List", c = self.populateWeightsFiles)
        cmds.menuItem(label="Load Weights from Selected", c = self.loadWeightsToSelected)
        cmds.menuItem(label="Load Weights to Selected mesh", c = self.loadWeightsToSelectedMesh)
        cmds.menuItem(label="Load Weights to Selected mesh and rename mesh", c = self.loadWeightsToSelectedMeshAndRename)
        cmds.menuItem(label="Select Mesh", c = self.selectWeightMesh)
        cmds.menuItem(label="Weighting Info", c = self.weightFileInformation)
        #cmds.menuItem(label="Update Puppet Joints From File")


        cmds.textScrollList( "infsInFile", numberOfRows=8, allowMultiSelection=True, showIndexedItem=4 )
        cmds.popupMenu()
        cmds.menuItem(label="Get All Nurbs Curves")
        cmds.menuItem(label="Get Just Marked Controls")
        
        
        cmds.button(label = "Select highlighted Influences from file", w = windowWidth, h = 50, c = self.selectHighlightedInfs)
        cmds.text(label="",vis=False)
        
        #cmds.button(label = "Reshape All", w = windowWidth, h = 50, c = self.reshapeAllControls)
        #cmds.text(label="",vis=False)
        
        cmds.setParent( '..' )
        cmds.setParent( '..' )


        cmds.setParent( '..' )

        #--------------------------------END SKINNING LAYOUT TAB

        #--------------------------------VERTEX LAYOUT TAB

        VertexToolsLayout = cmds.columnLayout("VertexToolsLayout", w = windowWidth, h = 300)
        cmds.frameLayout( label='Vertex Noodling',  cll = True )
        
        textColumWidth = windowWidth * 0.70
        buttonColumWidth = windowWidth * 0.1
        bufferWidth = 5


        
        listColumWidth = windowWidth * 0.49
        buildRowColumnLayout = cmds.rowColumnLayout(nc = 2, cw = [(1, listColumWidth), (2, listColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth)])

        cmds.text(label="Objects withe more than 4 infs ", align = "left")
        cmds.text(label="", align = "right")
        
        verts4infs = cmds.textScrollList( "objects4infs", numberOfRows=8, allowMultiSelection=False, append=['none'], showIndexedItem=4, dcc = self.updateVertListFromObj )
        cmds.popupMenu()
        cmds.menuItem(label="update list", c = self.updateObjInfList)
        #cmds.menuItem(label="Add selected Verts")


        cmds.button(label = "Update Scene Data",ann = 'Find verts with more than 4 Infs', w = listColumWidth * 0.5, h = 50, c = self.updateObjInfList)
        #cmds.popupMenu()
        #cmds.menuItem(label="update list", c = self.updateInfsListFromVerts)

        cmds.text(label="Verts withe more than 4 infs ", align = "left")
        cmds.text(label="Influences on selected verts", align = "right")
        
        verts4infs = cmds.textScrollList( "verts4infs", numberOfRows=8, allowMultiSelection=True, append=['none'], showIndexedItem=4, dcc = self.updateInfsListFromVerts )
        cmds.popupMenu()
        cmds.menuItem(label="update list", c = self.updateVertListFromObj)
        cmds.menuItem(label="from window selection", c = self.updateVertListFromSelection)


        cmds.textScrollList( "infsOnSelectedverts", numberOfRows=8, allowMultiSelection=True, append=['none'], showIndexedItem=4)#, dcc = self.updateInfsListFromVerts )
        cmds.popupMenu()
        cmds.menuItem(label="update list", c = self.updateInfsListFromVerts)
        #cmds.menuItem(label="from window selection")
        
        #cmds.button(label = "Update List",ann = 'Find verts with more than 4 Infs', w = listColumWidth * 0.5, h = 50, c = self.updateVertListFromObj)
        cmds.button(label = "Prune Small Weights", w = listColumWidth * 0.5, h = 50, c = self.doPrune)
        cmds.button(label = "Zero weights on Selected", w = listColumWidth * 0.5, h = 50, c = self.setVertsZero)
        cmds.button(label = "Select All", w = listColumWidth * 0.5, h = 50, c = lambda x:self.selectAllInList('verts4infs'))
        cmds.button(label = "All Weights on selected", w = listColumWidth * 0.5, h = 50, c = self.setVertsFull)
        #cmds.button(label = "Prune Small Weights", w = listColumWidth * 0.5, h = 50)
        cmds.setParent( '..' )
        cmds.frameLayout( label='Manual Skinning Tools', cll = True )
        cmds.separator(h=15)
        ctrlFileColumnLayout = cmds.rowColumnLayout(nc = 2, cw = [(1, textColumWidth), (2, buttonColumWidth+buttonColumWidth+buttonColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth)])

        cmds.button(label = "Smash Random Weights", w = windowWidth, h = 50, c = self.weightSmash)
        cmds.text(label="",vis=False)

        cmds.button(label = "Copy Vertex Weights", w = windowWidth, h = 50, c = self.copyVertexWeights)
        cmds.text(label="",vis=False)

        cmds.button(label = "Copy Vertex Weights, paste to Shell", w = windowWidth, h = 50, c = self.copyPasteVertWeights)
        cmds.text(label="",vis=False)

        cmds.button(label = "Paste Vertex Weights", w = windowWidth, h = 50, c = self.pasteVertexWeights)
        cmds.text(label="",vis=False)

        cmds.button(label = "Paste Vertex Weights to shell", w = windowWidth, h = 50, c = self.pasteVertexWeightsShell)
        cmds.text(label="",vis=False)
        
        
        cmds.setParent( '..' )

        cmds.setParent( '..' )
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        
        #--------------------------------END VERTEX LAYOUT TAB
        
        #--------------------------------CTRL LAYOUT TAB

        SkinningLayout = cmds.columnLayout("SkinningLayoutTab", w = windowWidth, h = 300)
        
        textColumWidth = windowWidth * 0.70
        buttonColumWidth = windowWidth * 0.1
        bufferWidth = 5

        cmds.frameLayout( label='Auto Skinning', cll = True )

        cmds.separator(h=15)
        ctrlFileColumnLayout = cmds.rowColumnLayout(nc = 3, cw = [(1, windowWidth * 0.33 ), (2, windowWidth * 0.33 ), (3, windowWidth * 0.33 )], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth),(3, "both", bufferWidth)])
 
        cmds.button(label = "Auto Skin Male", w = windowWidth * 0.33, h = buttonColumWidth, c = lambda x:self.__skinner.autoSkin(self.__maleSkinFileVar,self.__maleSkinGeoVar))
        cmds.button(label = "Auto Skin Female", w = windowWidth * 0.33, h = buttonColumWidth, c = lambda x:self.__skinner.autoSkin(self.__femaleSkinFileVar,self.__femaleSkinGeoVar))
        cmds.button(label = "Auto Skin Vanduul", w = windowWidth * 0.33, h = buttonColumWidth)#, c = lambda x:self.__skinner.autoSkin(self.__vanduulSkinFileVar,self.__vanduulSkinGeoVar))
        cmds.setParent( '..' )
        cmds.button(label = "Transsfer Maya Weights",ann =  'Transfer weights, first selection is transfer from, rest are transfer to', w = windowWidth, h = buttonColumWidth, c = self.transferMayaWeights)
        cmds.button(label = "Transfer Weights to LODs", w = windowWidth, h = buttonColumWidth, c = self.transferMayaWeightsLods)
        
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        cmds.setParent( '..' )
        
        #--------------------------------END CONTROL LAYOUT TAB

        
        cmds.tabLayout( tabs, edit=True, tabLabel=((loadSaveLayout, 'Save/Load'), (VertexToolsLayout, 'Vertex Tools'), (SkinningLayout, 'Skinning Tools')) )
        
        cmds.showWindow(window)

        if self.__initSettings:
            self.settingsUI()
        
        
    def settingsUI(self, *args):

        if cmds.window("settingGUI", exists = True):
            cmds.deleteUI("settingGUI")
        
        windowWidth = 400
        windowHeight = 700
        textColumWidth = windowWidth * 0.70
        buttonColumWidth = windowWidth * 0.2
        columnHeight = 50
        bufferWidth = 5

        settingsWindow = cmds.window("settingGUI", title = "Settings", w = windowWidth, h = windowHeight, mnb = False, mxb = False, sizeable = True)

        ctrlFileColumnLayout = cmds.rowColumnLayout(nc = 3, cw = [(1, textColumWidth), (2, buttonColumWidth), (3, buttonColumWidth)], columnOffset = [(1, "both", bufferWidth),(2, "both", bufferWidth),(3, "both", bufferWidth)])
        
        
        cmds.text(label="Male SRC File : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)
        
        maleSRCFile = cmds.textField("maleSRCFile", w = textColumWidth+buttonColumWidth, h = columnHeight, text = self.__maleSRCFile)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSrcFile('male'))
        rdBrowseButton = cmds.button(label = "Load", w = buttonColumWidth, h = columnHeight, c = lambda x:self.loadSrc('male'))

        cmds.text(label="Male Auto Skin File : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)
        
        maleAutoSkinFile = cmds.textField("maleAutoSkinFile", w = textColumWidth+buttonColumWidth, h = columnHeight, text = self.__maleSkinFile)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSkinFile('male'))
        rdBrowseButton = cmds.button(label = "Load", w = buttonColumWidth, h = columnHeight, c = lambda x:self.loadCharacter('male'))

        cmds.text(label="Male Auto Skin Geo : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        maleAutoSkinGeo = cmds.textField("maleAutoSkinGeo", w = textColumWidth+buttonColumWidth, text = self.__maleSkinGeo)
        cmds.text(label="",vis=False)
        rdBrowseButton = cmds.button(label = "Set Selected", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSkinGeo('male'))

        cmds.text(label="Female SRC File : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)
        
        maleSRCFile = cmds.textField("femaleSRCFile", w = textColumWidth+buttonColumWidth, h = columnHeight, text = self.__femaleSRCFile)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSrcFile('female'))
        rdBrowseButton = cmds.button(label = "Load", w = buttonColumWidth, h = columnHeight, c = lambda x:self.loadSrc('female'))

        cmds.text(label="Female Auto Skin File : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        femaleAutoSkinFile = cmds.textField("femaleAutoSkinFile", w = textColumWidth+buttonColumWidth, text = self.__femaleSkinFile)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSkinFile('female'))
        rdBrowseButton = cmds.button(label = "Load", w = buttonColumWidth, h = columnHeight, c = lambda x:self.loadCharacter('female'))

        cmds.text(label="Female Auto Skin Geo : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        femaleAutoSkinGeo = cmds.textField("femaleAutoSkinGeo", w = textColumWidth+buttonColumWidth, text = self.__femaleSkinGeo)
        cmds.text(label="",vis=False)
        rdBrowseButton = cmds.button(label = "Set Selected", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSkinGeo('female'))

        cmds.text(label="Vanduul SRC File : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)
        
        maleSRCFile = cmds.textField("vanduulSRCFile", w = textColumWidth+buttonColumWidth, h = columnHeight, text = self.__vanduulSRCFile)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSrcFile('vanduul'))
        rdBrowseButton = cmds.button(label = "Load", w = buttonColumWidth, h = columnHeight, c = lambda x:self.loadSrc('vanduul'))

        cmds.text(label="Vanduul Auto Skin File : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        vanduulAutoSkinFile = cmds.textField("vanduulAutoSkinFile", w = textColumWidth+buttonColumWidth, text = self.__vanduulSkinFile)
        rdBrowseButton = cmds.button(label = "...", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSkinFile('vanduul'))
        rdBrowseButton = cmds.button(label = "Load", w = buttonColumWidth, h = columnHeight, c = lambda x:self.loadCharacter('vanduul'))

        cmds.text(label="Vanduul Auto Skin Geo : ", align = "left")
        cmds.text(label="",vis=False)
        cmds.text(label="",vis=False)

        vanduulAutoSkinGeo = cmds.textField("vanduulAutoSkinGeo", w = textColumWidth+buttonColumWidth, text = self.__vanduulSkinGeo)
        cmds.text(label="",vis=False)
        rdBrowseButton = cmds.button(label = "Set Selected", w = buttonColumWidth, h = columnHeight, c = lambda x:self.setSkinGeo('vanduul'))

        cmds.showWindow(settingsWindow)


    #---------------File Browsers

    def updateWeightsFileField(self, *args):

        ctrlFileDir = cmds.fileDialog2(cap = "Select Weights Directory", fm = 2, dir = self.buildMainDir("weights"), dialogStyle=2)
        
        ctrlFile = cmds.textField("weightsFile", edit=True, text = ctrlFileDir[0])

        self.populateWeightsFiles()


    def setSkinFile(self, character):

        skinFile = cmds.fileDialog2(cap = "Select "+character+" Skin File", fm = 1, dialogStyle=2)

        characterVar = self.__maleSkinFileVar

        if character == 'female':
            characterVar = self.__femaleSkinFileVar

        if character == 'vanduul':
            characterVar = self.__vanduulSkinFileVar

        cmds.optionVar(sv=(characterVar, skinFile[0]))

        cmds.textField(character+"AutoSkinFile", e=True, text = skinFile[0])

    def setSrcFile(self, character):

        srcFile = cmds.fileDialog2(cap = "Select "+character+" SRC File", fm = 1, dialogStyle=2)

        characterVar = self.__maleSRCVar

        if character == 'female':
            characterVar = self.__femaleSRCVar

        if character == 'vanduul':
            characterVar = self.__vanduulSRCVar

        cmds.optionVar(sv=(characterVar, srcFile[0]))

        cmds.textField(character+"SRCFile", e=True, text = srcFile[0])

    def setSkinGeo(self, character):

        skinGeo = cmds.ls(sl=True)
        if len(skinGeo) != 1:
            cmds.error('Please select the main skin geo to copy weights from')

        characterVar = self.__maleSkinGeoVar

        if character == 'female':
            characterVar = self.__femaleSkinGeoVar

        if character == 'vanduul':
            characterVar = self.__vanduulSkinGeoVar
            return "No Vanduul character to skin yet.."

        cmds.optionVar(sv=(characterVar, skinGeo[0]))

        cmds.textField(character+"AutoSkinGeo", e=True, text = skinGeo[0])

    def loadCharacter(self, character):

        characterVar = self.__maleSkinFileVar

        if character == 'female':
            characterVar = self.__femaleSkinFileVar

        if character == 'vanduul':
            characterVar = self.__vanduulSkinFileVar

        cmds.file(cmds.optionVar(q=characterVar),o=True,f=True)

    def loadSrc(self, character, importIt = False):

        characterVar = self.__maleSRCVar

        if character == 'female':
            characterVar = self.__femaleSRCVar

        if character == 'vanduul':
            characterVar = self.__vanduulSRCVar

        if importIt:
            cmds.file(cmds.optionVar(q=characterVar),i=True,f=True)
        else:
            cmds.file(cmds.optionVar(q=characterVar),o=True,f=True)

        print('loaded file: '+cmds.optionVar(q=characterVar))

    def populateWeightsFiles(self, *args):
    
        weightFiles = self.__futil.returnFiles(cmds.textField("weightsFile", q=True, text=True)+'/', ['weights'])
        cmds.textScrollList("characterWeightFiles", edit = True, ra = True)

        for each in weightFiles:   
            cmds.textScrollList("characterWeightFiles",edit = True, append = each.split('.')[0])

    def loadInfluencesFromFile(self, *args):
        
        theWeightsFile = cmds.textField("weightsFile", q=True, text=True)+'/'+cmds.textScrollList("characterWeightFiles", q=True, si=True)[0]+'.weights'
        print(theWeightsFile)
        infs = self.__futil.returnInfsFromWeightsFile(theWeightsFile)
        if len(infs) != 0:
            cmds.textScrollList("infsInFile", edit = True, ra = True)
            for each in infs: 
                cmds.textScrollList("infsInFile",edit = True, append = each)


    #--------DO THINGS
   
    def selectWeightMesh(self, *args):

        cmds.select(cmds.textScrollList( "characterWeightFiles",q=True,si=True),r=True)

    def weightFileInformation(self, *args):

        print('need to get weights info')
        
    #------------------------SUPPORT PROCS

    def autoSaveWeights(self, *args):
        self.__weighter.exportWeights(cmds.textField("weightsFile", q=True, text=True))
        self.populateWeightsFiles()

    def autoLoadWeights(self, *args):
        self.__weighter.importWeights(cmds.textField("weightsFile", q=True, text=True))

    def autoUpdateToSRC(self, *args):
        
        #get original vert count per object and check
        #originalVertCount

        thisFile = cmds.file(q=True,list=True)[0]

        if '_source' not in thisFile:
            cmds.error('File should be in the _source directory')

        justMeshFile = thisFile.replace('_skinned','')
        if not os.path.isfile(justMeshFile):
            cmds.error('*_skinned file needs to be in the same directory as the base mesh and named correctly')

        splitFile = thisFile.split('/')
        del splitFile[-1]
        weightsDir = '/'.join(splitFile)+'/weights/'

        self.__futil.checkOrMakeDirectory(weightsDir)
        self.__weighter.exportWeights(weightsDir)

        print('openning file: '+justMeshFile)
        cmds.file(justMeshFile, f=True,o=True)

        toLoad = 'male'

        if 'female' in weightsDir:
            toLoad = 'female'            

        if 'vanduul' in weightsDir:
            toLoad = 'vanduul'

        self.loadSrc(toLoad,True)

        #cleanup the scene
        cmds.delete('GEO')

        self.__weighter.importWeights(weightsDir)

    def loadWeightsToSelected(self, *args):

        self.__weighter.importWeights(cmds.textField("weightsFile", q=True, text=True), cmds.textScrollList( "characterWeightFiles",q=True,si=True))

    def loadWeightsToSelectedMesh(self, *args):

        theMesh = cmds.ls(sl=True)
        meshName = cmds.textScrollList( "characterWeightFiles",q=True,si=True)

        if len(theMesh) != 1:
            cmds.error('must select 1 mesh')

        if len(theMesh) == 1:
            cmds.rename(theMesh[0], meshName)

        self.__weighter.importWeights(cmds.textField("weightsFile", q=True, text=True), meshName)

        cmds.rename(meshName, theMesh[0])

    def loadWeightsToSelectedMeshAndRename(self, *args):

        theMesh = cmds.ls(sl=True)
        meshName = cmds.textScrollList( "characterWeightFiles",q=True,si=True)

        if len(theMesh) != 1:
            cmds.error('must select 1 mesh')

        if len(theMesh) == 1:
            cmds.rename(theMesh[0], meshName)

        self.__weighter.importWeights(cmds.textField("weightsFile", q=True, text=True), meshName)

    

    def updateInfluencesForVertSkinningTools(self, *args):

        verts = cmds.ls(sl=True,fl=True)

        if len(verts) == 0 or cmds.objectType(verts[0]) != 'mesh':
            cmds.error('please select at least one vertex')

        cmds.textScrollList(self.__skinningInfluencesWindow, edit = True, ra = True)
        for each in self.__skinner.returnInfsFromVerts(verts) : 
            cmds.textScrollList(self.__skinningInfluencesWindow,edit = True, append = each)

    def copyVertexWeights(self, *args):

        #self.__vertsList = {}
        self.__weightsDictionary = {}

        verts = cmds.ls(sl=True,fl=True)

        if len(verts) == 0 or cmds.objectType(verts[0]) != 'mesh':
            cmds.error('please select at least one vertex to copy weights from')

        for vert in verts:
            for inf in self.__skinner.returnInfsFromVerts(vert) : 

                theSkin = self.__skinner.findRelatedSkinCluster(vert.rpartition('.')[0])
                self.__skinner.copyAddWeights(inf, cmds.skinPercent(theSkin, vert, t = inf, query=True, value=True), self.__weightsDictionary)

        print(self.__weightsDictionary)


    def pasteVertexWeightsShell(self, *args):

        verts = cmds.ls(sl=True)

        for vert in verts:            
            self.__selTool.selectVertexShell(vert)

            self.pasteVertexWeights()

    def pasteVertexWeights(self, *args):
        
        allData = {}

        if len(self.__weightsDictionary) == 0:
            cmds.error('no weights in buffer, please copy some')

        verts = cmds.ls(sl=True,fl=True)

        if len(verts) == 0 or cmds.objectType(verts[0]) != 'mesh':
            cmds.error('please select at least one vertex to paste weights to')

        theSkin = self.__skinner.findRelatedSkinCluster(verts[0].rpartition('.')[0])
        cmds.skinPercent( theSkin,transformValue= self.__skinner.convertWeightDictToList(self.__weightsDictionary), normalize = True)

    #this takes one verts weights and pastes them to the whole shell.
    def copyPasteVertWeights(self, *args):

        theVert = cmds.ls(sl=True)

        if len(theVert) != 1:
            cmds.error('please select one vertex to copy from')

        if cmds.objectType(theVert[0]) != 'mesh':
            cmds.error('please select one vertex to copy from')

        self.__skinner.copyVertWeightToShell(theVert[0])

    def printVertexWeights(self, *args):

        if len(self.__weightsDictionary) == 0:
            cmds.error('no weights in buffer, please copy some')

        else:
            print('number of verts '+str(len(self.__weightsDictionary)))
            print(self.__weightsDictionary)


    def transferMayaWeights(self, *args):

        selected = cmds.ls(sl=True)
        if len(selected) < 2:
            cmds.error('please select the source then the destination meshs')

        if len(selected) == 2:
            self.__skinner.transferMayaWeights(selected[0],selected[1])

        if len(selected) > 2:
            base = selected[0]
            del selected[0]
            for mesh in selected:
                self.__skinner.transferMayaWeights(base,mesh)

    def transferMayaWeightsLods(self, *args):

        autoPrune = True

        selected = cmds.ls(sl=True)

        for mesh in selected:
            for x in range(1, 5):
                if cmds.objExists(mesh+'_lod'+str(x)):
                    
                    if self.__skinner.isSkinned(mesh+'_lod'+str(x)):
                        cmds.skinCluster(mesh+'_lod'+str(x), e=True,ub=True)

                    self.__skinner.transferMayaWeights(mesh,mesh+'_lod'+str(x))

                    #prune all small weights first
                    theSkin = self.__skinner.findRelatedSkinCluster(mesh+'_lod'+str(x))
                    cmds.select(mesh+'_lod'+str(x)+'.vtx[*]', r=True)
                    allVerts=cmds.ls(sl=True)
                    cmds.skinPercent( theSkin, allVerts, pruneWeights=0.00001 )

                    if autoPrune:
                        pruneVerts = self.__verter.returnInfsWithMoreWeights(mesh+'_lod'+str(x), 9)
                        print('pruneVerts '+str(len(pruneVerts))+' on mesh'+mesh+'_lod'+str(x))
                        if len(pruneVerts) != 0:
                            print('pruning ')
                            print(theSkin)
                            print(pruneVerts)
                            cmds.skinPercent( theSkin, pruneVerts, pruneWeights=0.001 )

                if cmds.objExists(mesh+'_LOD'+str(x)):

                    if self.__skinner.isSkinned(mesh+'_LOD'+str(x)):
                        cmds.skinCluster(mesh+'_LOD'+str(x), e=True,ub=True)

                    self.__skinner.transferMayaWeights(mesh,mesh+'_LOD'+str(x))

                    theSkin = self.__skinner.findRelatedSkinCluster(mesh+'_LOD'+str(x))
                    cmds.select(mesh+'_LOD'+str(x)+'.vtx[*]', r=True)
                    allVerts=cmds.ls(sl=True)
                    cmds.skinPercent( theSkin, allVerts, pruneWeights=0.00001 )
                    
                    if autoPrune:
                        pruneVerts = self.__verter.returnInfsWithMoreWeights(mesh+'_LOD'+str(x), 9)
                        print('pruneVerts '+str(len(pruneVerts))+' on mesh'+mesh+'_LOD'+str(x))
                        if len(pruneVerts) != 0:
                            print('pruning ')
                            print(theSkin)
                            print(pruneVerts)
                            cmds.skinPercent( theSkin, pruneVerts, pruneWeights=0.001 )

  

    def weightSmash(self, *args):

        theVert = cmds.ls(sl=True,fl=True)
        if cmds.objectType(theVert) != 'mesh':
            cmds.error('please select a vertex or multuple verts to smash weights on')

        else:
            theObject = theVert[0].split('.')[0]
            cmds.skinCluster(self.__skinner.findRelatedSkinCluster(theObject),e=True,sw = 0.0 ,swi=5)

    def selectHighlightedInfs(self, *args):

        dontExist = []
        exists = []

        selectedInfs = cmds.textScrollList("infsInFile", q=True, si=True)

        for inf in selectedInfs:
            if cmds.objExists(inf):
                exists.append(inf)
            else:
                dontExist.append(inf)

        if len(exists) >0:
            cmds.select(exists,r=True)
        else:
            cmds.error('no influences exist from file')

        if len(dontExist) > 0:
            print('These influences do not exist in the scene:')
            print(dontExist)


    #old way, using a dictionary
    def updateVertInfList(self, *args):

        theObject = cmds.textScrollList('objects4infs',q=True, si = True)

        justVerts = []

        if theObject[0] == 'All':
            justVerts = self.__vertsDict.keys()

        else:
            for k in self.__vertsDict.keys():
                if k.startswith(theObject[0]):
                    justVerts.append(k)

        sortedList = sorted(justVerts)

        cmds.textScrollList('verts4infs', edit = True, ra = True)
        for each in sortedList : 
            cmds.textScrollList('verts4infs',edit = True, append = each)

    def updateVertListFromObj(self, *args):

        objects = cmds.textScrollList('objects4infs',q=True, si = True)

        vertWithMore = []
        for obj in objects:
            over = self.__skinner.returnVertsWithMaxInfs(obj, 4)
            if len(over) > 0:
                for overOne in over:
                    vertWithMore.append(overOne)

        cmds.textScrollList('verts4infs', edit = True, ra = True)
        for each in sorted(vertWithMore) : 
            cmds.textScrollList('verts4infs',edit = True, append = each)

    def updateVertListFromSelection(self, *args):

        vertWithMore = cmds.ls(sl=True,fl=True)

        if cmds.objectType(vertWithMore[0]) != 'mesh':
            cmds.error('Please selecet verts for this')

        cmds.textScrollList('verts4infs', edit = True, ra = True)
        for each in sorted(vertWithMore) : 
            cmds.textScrollList('verts4infs',edit = True, append = each)

    def updateObjInfList(self, *args):

        meshs = cmds.ls(type='mesh')

        meshWithMore = []
        for mesh in meshs:
            if self.__skinner.isSkinned(mesh):
                over = self.__skinner.returnVertsWithMaxInfs(mesh, 4)
                if len(over) > 0:
                    meshWithMore.append(mesh)

        cmds.textScrollList( 'objects4infs' , edit = True, ra = True)
        cmds.textScrollList('objects4infs',edit = True, append = 'All')     
        for each in meshWithMore : 
            cmds.textScrollList('objects4infs',edit = True, append = each)        

        cmds.textScrollList('verts4infs', edit = True, ra = True)
        cmds.textScrollList('infsOnSelectedverts', edit = True, ra = True)

    def updateInfsListFromVerts(self, *args):

        vertsFromGui = cmds.textScrollList('verts4infs',q=True, si = True)

        if vertsFromGui is None:
            #cmds.error('Please select at least one vertex from the list to the left')
            vertsFromGui = cmds.ls(sl=1,fl=1)

        allInfs = []
        for vert in vertsFromGui:
            #old way based on dictionary
            #infs = self.__vertsDict.get(vert)
            obj=vert.split('.')[0]
            skinClust = self.__skinner.findRelatedSkinCluster(obj)
            joints = cmds.skinPercent( skinClust, vert, q = 1, t = None )
            influence_value = cmds.skinPercent( skinClust, vert, q = True, v = True )

            for joint, influence  in zip( joints, influence_value ):
                if influence > 0:
                    allInfs.append(joint)

            #infs = cmds.skinPercent(skinClust, vert, query=True, value=True, ib = 0.0001)
            #for inf in infs:
                #allInfs.append(inf)

        prunedList = sorted(list(set(allInfs)))

        cmds.textScrollList('infsOnSelectedverts', edit = True, ra = True)
        for each in prunedList : 
            cmds.textScrollList('infsOnSelectedverts',edit = True, append = each)

        cmds.select(vertsFromGui,r=True)


    def setVerts(self, value, *args):

        verts = cmds.ls(sl=True,fl=True)

        if len(verts) == 0 or cmds.objectType(verts[0]) != 'mesh':
            cmds.error('please select at least one vertex')

        infs = cmds.textScrollList('infsOnSelectedverts',q=True, si = True)

        if len(infs) < 1:
            cmds.error('please select at least one influence from list')

        self.__skinner.setVertInfluenceValue(verts, infs, value)

    def setVertsZero(self, *args):

        self.setVerts(0.0)

        selectedVerts = cmds.textScrollList('verts4infs',q=True, si = True)
        selectedInfs = cmds.textScrollList('infsOnSelectedverts',q=True, si = True)

        #for vert in selectedVerts:
            #infs = self.__vertsDict[vert]
            #for inf in selectedInfs:
                #infs.remove(inf)

        #self.__vertsDict[vert] = infs

        self.updateInfsListFromVerts()

    def setVertsFull(self, *args):
        self.setVerts(1.0)
        self.updateInfsListFromVerts()
        #should manually edit them out of dict but for now just re running the proc to find them
        self.updateVertInfList()

    def selectAllInList(self, listName, *args):

        for i in range(1,cmds.textScrollList(listName ,q=True, numberOfItems = True)+1):
            cmds.textScrollList(listName ,e=True,selectIndexedItem=i)

        if listName == 'verts4infs':
            cmds.select(cmds.textScrollList(listName ,q=True,si=True), r=True)

    def doPrune(self, pruneValue = 0.01, *args):

        objects = cmds.textScrollList('verts4infs',q=True, si = True)

        allObjects = []
        for obj in objects:
            allObjects.append(obj.split('.')[0])

        prunedList = sorted(list(set(allObjects)))

        for obj in prunedList:
            skinClust = self.__skinner.findRelatedSkinCluster(obj)
            print('Prunning '+obj, skinClust)
            cmds.skinPercent(skinClust , obj, pruneWeights = pruneValue)