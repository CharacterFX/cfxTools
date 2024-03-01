"""
A script that return the status of an objects channels and returns whats useable
Author: John Riggs
"""

import maya.cmds as cmds

def returnUseableChannels(theObject, unlockedChannels = True):

    returnChannels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    lockedChannel = []

    isLocked = cmds.getAttr(theObject+'.tx',l=True)
    #print 'tx isLocked '+str(isLocked)
    isConnected = cmds.listConnections(theObject+'.tx', s = True, d=False)

    if isConnected == None:
        isConnected = []

    if len(isConnected) > 0:
        returnChannels.remove('tx')
        lockedChannel.append('tx')

    #elif cmds.transformLimits(theObject, q=True,etx=True)[0] and cmds.transformLimits(theObject, q=True,etx=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,tx=True)
    if isLocked:#lowLimit[0] == lowLimit[1] or isLocked:
        #print 'adding tx'
        returnChannels.remove('tx')
        lockedChannel.append('tx')

    isLocked = cmds.getAttr(theObject+'.ty',l=True)
    isConnected = cmds.listConnections(theObject+'.ty', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('ty')
        lockedChannel.append('ty')
    #elif cmds.transformLimits(theObject, q=True,ety=True)[0] and cmds.transformLimits(theObject, q=True,ety=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,ty=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('ty')
        lockedChannel.append('ty')

    isLocked = cmds.getAttr(theObject+'.tz',l=True)
    isConnected = cmds.listConnections(theObject+'.tz', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('tz')
        lockedChannel.append('tz')
    #elif cmds.transformLimits(theObject, q=True,etz=True)[0] and cmds.transformLimits(theObject, q=True,etz=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,tz=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('tz')
        lockedChannel.append('tz')

    isLocked = cmds.getAttr(theObject+'.rx',l=True)
    isConnected = cmds.listConnections(theObject+'.rx', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('rx')
        lockedChannel.append('rx')
    #elif cmds.transformLimits(theObject, q=True,erx=True)[0] and cmds.transformLimits(theObject, q=True,erx=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,rx=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('rx')
        lockedChannel.append('rx')

    isLocked = cmds.getAttr(theObject+'.ry',l=True)
    isConnected = cmds.listConnections(theObject+'.ry', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('ry')
        lockedChannel.append('ry')
    #elif cmds.transformLimits(theObject, q=True,ery=True)[0] and cmds.transformLimits(theObject, q=True,ery=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,ry=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('ry')
        lockedChannel.append('ry')

    isLocked = cmds.getAttr(theObject+'.rz',l=True)
    isConnected = cmds.listConnections(theObject+'.rz', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('rz')
        lockedChannel.append('rz')
    #elif cmds.transformLimits(theObject, q=True,erz=True)[0] and cmds.transformLimits(theObject, q=True,erz=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,rz=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('rz')
        lockedChannel.append('rz')

    isLocked = cmds.getAttr(theObject+'.sx',l=True)
    isConnected = cmds.listConnections(theObject+'.sx', s = True, d=False)

    if isConnected == None:
        isConnected = []
    #print 'isConnected', isConnected, len(isConnected)
    if len(isConnected) > 0:
        returnChannels.remove('sx')
        lockedChannel.append('sx')
    #elif cmds.transformLimits(theObject, q=True,esx=True)[0] and cmds.transformLimits(theObject, q=True,esx=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,sx=True)
        #print 'ScaleX ', isLocked
    if isLocked: #lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('sx')
        lockedChannel.append('sx')

    isLocked = cmds.getAttr(theObject+'.sy',l=True)
    isConnected = cmds.listConnections(theObject+'.sy', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('sy')
        lockedChannel.append('sy')
    #elif cmds.transformLimits(theObject, q=True,esy=True)[0] and cmds.transformLimits(theObject, q=True,esy=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,sy=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('sy')
        lockedChannel.append('sy')

    isLocked = cmds.getAttr(theObject+'.sz',l=True)
    isConnected = cmds.listConnections(theObject+'.sz', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('sz')
        lockedChannel.append('sz')
    #elif cmds.transformLimits(theObject, q=True,esz=True)[0] and cmds.transformLimits(theObject, q=True,esz=True)[1] is True:
        #lowLimit = cmds.transformLimits(theObject, q=True,sz=True)
    if isLocked:# lowLimit[0] == lowLimit[1] or isLocked:
        returnChannels.remove('sz')
        lockedChannel.append('sz')

    if unlockedChannels:
        return returnChannels

    else:
        return lockedChannel