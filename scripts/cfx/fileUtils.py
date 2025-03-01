"""
A Class to make dealing with files easier, aimed at our tools
Autho: John Riggs
"""

import cfx.systemSettings as sysSet

import os
import glob
import fnmatch
from os import path
import maya.cmds as cmds

import logging

import importlib
importlib.reload(sysSet)

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class fileUtils(object):
    
    def __init__(self):
        self.__settings = sysSet.sysSettings()
        self.__controlLocation = self.__settings.controlLocation
        self.__ikScriptsLocation = self.__settings.ikSystems #path.join(path.dirname(__file__), 'ikSystem')
        self.__ikAutoSetupsLocation = self.__settings.autoSetupsDir #path.join(path.dirname(__file__), 'autoSetup')
        self.__rootLocation =  self.__settings.installLocation #path.join(path.dirname(__file__))
        self.__riggingLocation =  self.__settings.rigBuildScriptsLocation #path.join(path.dirname(__file__))

        self.__weaponFiles = {}

    def checkOrMakeDirectory(self, theDir):

        d=os.path.dirname(theDir)
        if not os.path.exists(d):
            os.makedirs(d)

        return d


    def returnNewestDir(self, basePath):
    
        result = []
        for d in os.listdir(basePath):
            bd = os.path.join(basePath, d)
            if os.path.isdir(bd): result.append(bd)
        return max(result,key=os.path.getmtime)

    
    def returnFiles(self, directory, extension = []):

        #test for string and make array if it is
        if type(extension) is str:
            extension = [extension]

        allFiles = []

        try:
            for file in os.listdir(directory):
                for ext in extension:
                    if file.endswith("."+ext):
                        allFiles.append(file)
        except:
            pass

        return allFiles

    def returnAllFiles(self, directory, extension = []):
        '''
        :param directory: The directory to search
        :param extension: The File Extension
        :return:
        '''
        allFiles = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, extension):
                allFiles.append(os.path.join(root, filename))

        return allFiles

    def returnNewestVersion(self, directory, extension = []):
        '''
        returns the file with the newest version number
        @param directory: the directory
        @param extension: the file extension to be checked
        '''
        print(directory)
        if os.path.isdir(directory):
            if os.listdir(directory) == []:
                return None
            else:
                return max(self.returnFiles(directory, extension))
        else:
            cmds.warning('No directory ', directory)

    def returnNewestDate(self, directory, extension):
        '''
        returns the file with the newest date
        @param directory: the directory
        @param extension: the file extension to be checked
        '''
        theDir = directory+'/*.'+extension
        if not os.path.isdir(directory):
            os.makedirs(directory)

        if os.listdir(directory) == []:
            return None
        else:
            return max(glob.iglob(theDir), key=os.path.getctime)


    def bumpFileVersion(self, directory, extension):
        
        newestFile = self.returnNewestDate(directory, extension)
        if newestFile is None:
            newName = directory+'/'+directory.split('/')[:-3][-1]+'_'+directory.split('/')[-1]+'.01.ma'
            cmds.warning('No files in that directory returning a new name: ', newName)

            return newName

        else:
            splited = newestFile.split('.')
            if len(splited) == 2:
                return splited[0]+'.01.'+splited[1]
            splited[-2] = str(int(splited[-2])+1)
            return '.'.join(splited)

    def returnCtrlShapes(self):

        shapes = self.returnFiles(self.__controlLocation, ['ctrlShape'])
        return [x.partition('.')[0] for x in shapes]

    def returnSystem(self, theType):

        returnSystems = []
        theSystems = []
        print(self.__riggingLocation+'/'+theType)
        if theType != 'controlShape':
            if theType == 'ikAddOns':
                theSystems = self.returnFiles(self.__riggingLocation+'/ikSystems/'+theType, ['py'])
            else:
                theSystems = self.returnFiles(self.__riggingLocation+'/'+theType, ['py'])
        else:
            theSystems = self.returnFiles(self.__riggingLocation+'/'+theType, ['ctrlShape'])

        for ts in theSystems:
            if ts.startswith('__') is not True:
                #add methods search here
                returnSystems.append(ts.partition('.')[0])

        return returnSystems

    def returnSubdirectories(self, dir):
        if os.path.exists(dir):
            return [name for name in os.listdir(dir)
                    if os.path.isdir(os.path.join(dir, name))]

    def returnInfsFromWeightsFile(self, filename):

        try:
            fRead = open(filename,'rb')
        except IOError:
           #raise statusError('file '+ `filename` +'does not exist')
           cmds.error('file does not exist: ', filename)

        jntFound = 0
        for line in fRead:
            if line.find('# Joint list') != -1: jntFound = 1; break;
        if jntFound == 0: cmds.error("No file or Invalid format")
        # make a list of joint chain
        jntList = fRead.next().split()
        for line in fRead:
            if line.find('# Joint list ends') != -1:  break

        return jntList

    def returnVertCountFromWeightsFile(self, filename):

        try:
            fRead = open(filename,'rb')
        except IOError:
           #raise statusError('file '+ `filename` +'does not exist')
           cmds.error('file does not exist: ', filename)

        vertsFound = 0
        for line in fRead:
            if line.startswith('['):
                vertsFound += 1
                
        return vertsFound
        
    def replaceInFile(self, fileIn, old, replaceWith):

        f = open(fileIn,'r')
        filedata = f.read()
        f.close()

        newdata = filedata.replace(old, replaceWith)

        f = open(fileIn,'w')
        f.write(newdata)
        f.close()

    def returnWeapons(self,rootDir):

        files = self.returnAllFiles(rootDir,'attach*.png')
        return files

    def exportHeirarchyAsText(self, exportFile):

        obs = cmds.ls(sl=1)
        if len(obs) != 1:
            cmds.error('Pleases select 1 object to export heirarchy')
        theStart = obs[0]

        heirFile = open(exportFile,"w")

        def print_heir(ob, levels=10):
            def recurse(ob, theParent, depth):
                if depth > levels: 
                    return
                print("  " * depth, ob)
                filePrint= ("  " * depth)+ob
                heirFile.write(filePrint) 
                heirFile.write('\n')

                children = cmds.listRelatives(ob,c=1)
                if children:
                    for child in children:
                        recurse(child, ob,  depth + 1)
            recurse(ob, cmds.listRelatives(ob,p=1)[0], 0)

        print_heir(theStart)

        heirFile.close()