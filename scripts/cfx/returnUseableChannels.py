"""
A script that return the status of an objects channels and returns whats useable
Author: John Riggs
"""

import maya.cmds as cmds

def returnUseableChannels(theObject, unlockedChannels = True):

    returnChannels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    lockedChannel = []

    isLocked = cmds.getAttr(theObject+'.tx',l=True)
    isConnected = cmds.listConnections(theObject+'.tx', s = True, d=False)

    if isConnected == None:
        isConnected = []

    if len(isConnected) > 0:
        returnChannels.remove('tx')
        lockedChannel.append('tx')

    if isLocked:
        returnChannels.remove('tx')
        lockedChannel.append('tx')

    isLocked = cmds.getAttr(theObject+'.ty',l=True)
    isConnected = cmds.listConnections(theObject+'.ty', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('ty')
        lockedChannel.append('ty')

    if isLocked:
        returnChannels.remove('ty')
        lockedChannel.append('ty')

    isLocked = cmds.getAttr(theObject+'.tz',l=True)
    isConnected = cmds.listConnections(theObject+'.tz', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('tz')
        lockedChannel.append('tz')

    if isLocked:
        returnChannels.remove('tz')
        lockedChannel.append('tz')

    isLocked = cmds.getAttr(theObject+'.rx',l=True)
    isConnected = cmds.listConnections(theObject+'.rx', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('rx')
        lockedChannel.append('rx')

    if isLocked:
        returnChannels.remove('rx')
        lockedChannel.append('rx')

    isLocked = cmds.getAttr(theObject+'.ry',l=True)
    isConnected = cmds.listConnections(theObject+'.ry', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('ry')
        lockedChannel.append('ry')

    if isLocked:
        returnChannels.remove('ry')
        lockedChannel.append('ry')

    isLocked = cmds.getAttr(theObject+'.rz',l=True)
    isConnected = cmds.listConnections(theObject+'.rz', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('rz')
        lockedChannel.append('rz')

    if isLocked:
        returnChannels.remove('rz')
        lockedChannel.append('rz')

    isLocked = cmds.getAttr(theObject+'.sx',l=True)
    isConnected = cmds.listConnections(theObject+'.sx', s = True, d=False)

    if isConnected == None:
        isConnected = []

    if len(isConnected) > 0:
        returnChannels.remove('sx')
        lockedChannel.append('sx')

    if isLocked:
        returnChannels.remove('sx')
        lockedChannel.append('sx')

    isLocked = cmds.getAttr(theObject+'.sy',l=True)
    isConnected = cmds.listConnections(theObject+'.sy', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('sy')
        lockedChannel.append('sy')

    if isLocked:
        returnChannels.remove('sy')
        lockedChannel.append('sy')

    isLocked = cmds.getAttr(theObject+'.sz',l=True)
    isConnected = cmds.listConnections(theObject+'.sz', s = True, d=False)

    if isConnected == None:
        isConnected = []
    
    if len(isConnected) > 0:
        returnChannels.remove('sz')
        lockedChannel.append('sz')

    if isLocked:
        returnChannels.remove('sz')
        lockedChannel.append('sz')

    if unlockedChannels:
        return returnChannels

    else:
        return lockedChannel