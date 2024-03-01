import maya.cmds as cmds
import math

import cfx.metaSystem as rmeta
        
class ikFkSwitcher(object):
    
    def __init__(self):
        self.__generic = ['generic', 'arm', 'leg']
        self.__constraints = []
        self.__locs = []
        self.__testChannels = ['x','y','z']
        self.__keyChannels = ['tx','ty','tz','rx','ry','rz']

        #modules
        self.__meta = rmeta.metaSystem()

    def swapSelected(self):
        ctrls = cmds.ls( selection=True )

        if (len(ctrls) <1):
            cmds.error("\nPlease select one or more of the IK attr control boxes\n")

        else:
            self.swap(ctrls)

    def swap(self, ctrls):

        if not isinstance(ctrls, list):
            ctrls = [ctrls]

        for ct in ctrls:

            setupDataNode = ''
            ikSwitchCtrl = ''

            if cmds.objExists(ct+".setupData"):
                setupDataNode = cmds.listConnections(ct+".setupData",s=True,d=False)[0]

            else:
                cmds.error("\nNo setup data on ctrl selected\n")
                
            ikSwitchCtrl = cmds.listConnections(setupDataNode+".theSwitchControl",s=0,d=1)[0]
            ikTrnControl = cmds.listConnections(setupDataNode+".ikTrnControl",s=0,d=1)[0]

            if cmds.objExists(ikSwitchCtrl+".fkIk"):
                
                ikAttr = cmds.getAttr(ikSwitchCtrl+".fkIk")
                
                setupType = cmds.getAttr(setupDataNode+".setupType")

                ikPartners = cmds.listConnections(setupDataNode+".ikPartners",s=0,d=1)
                fkPartners = cmds.listConnections(setupDataNode+".fkPartners",s=0,d=1)

                if setupType in self.__generic:
                    #if in IK switch to FK
                    if ikAttr:
                        for ctrl in fkPartners:
                            
                            useRot = []
                            
                            for chn in self.__testChannels:
                                if cmds.getAttr(ctrl+'.r'+chn,l=True):
                                    useRot.append(chn)
                            if len(useRot) < 3:
                                self.__constraints.append(cmds.orientConstraint(ctrl+"_orient1",ctrl,mo=False,w=1, skip=tuple(useRot))[0])
                            
                        useTrans = []
                        
                        for chn in self.__testChannels:
                            if cmds.getAttr(ctrl+'.t'+chn,l=True):
                                useTrans.append(chn)
                        if len(useTrans) < 3:
                            self.__constraints.append(cmds.pointConstraint(ikPartners[0],ikPartners[0]+"_orient1",mo=False,w=1, skip=tuple(useTrans))[0])
                        
                        cmds.select(ikTrnControl,r=True)
                        
                        for fkctrl in fkPartners:
                            for chn in self.__keyChannels:
                                keyit = cmds.keyframe(fkctrl, attribute= chn, sl=False, q=True, tc=True)
                                
                                if keyit is not None:
                                    cmds.setKeyframe(fkctrl+'.'+chn)
                        
                    #if in FK switch to IK    
                    else:
            
                        #for theAttr in ikCopyAttrs:
                            #cmds.setAttr(ikPartners[-1]+'.'+theAttr, cmds.getAttr(ikPartners[-1]+'_orient1.'+theAttr)) 
                        for ikpv in ikPartners:
                            loc1 = cmds.spaceLocator(n=ikpv+'_loc')[0]
                            cmds.xform(loc1 ,ws=True,m=(cmds.xform(ikpv+"_orient1",q=True,ws=True,m=True)))
                            self.__locs.append(loc1)
                            self.__constraints.append(cmds.pointConstraint(loc1,ikpv,mo=False,w=1)[0])
                        #self.__constraints.append(cmds.orientConstraint(loc1,ikPartners[-1],mo=False,w=1)[0])
                        
                        loc2 = cmds.spaceLocator(n=ikTrnControl+'_loc')[0]
                        cmds.xform(loc2 ,ws=True,m=(cmds.xform(ikTrnControl+"_orient1",q=True,ws=True,m=True)))
                        self.__locs.append(loc2)
                        self.__constraints.append(cmds.parentConstraint(loc2,ikTrnControl,mo=False,w=1)[0])
            
                        cmds.select(ikTrnControl,r=True)
                        
                        #copy attrs for reverse setups
                        allUD = cmds.listAttr(setupDataNode,ud=True)
                        justCopyAttrs = [s for s in allUD if s.startswith('_')]

                        for jc in justCopyAttrs:
                            cmds.setAttr(ikTrnControl+'.'+jc[1:], cmds.getAttr(setupDataNode+'.'+jc))
                            
                        for zero in ['roll','bank']:
                            if cmds.objExists(ikTrnControl+'.'+zero):
                                cmds.setAttr(ikTrnControl+'.'+zero,0)
                
                        for chn in self.__keyChannels:
                            keyit = cmds.keyframe(ikTrnControl, attribute= chn, sl=False, q=True, tc=True)
                            
                            if keyit is not None:
                                cmds.setKeyframe(ikTrnControl+'.'+chn)
                        
                    cmds.setAttr(ikSwitchCtrl+".fkIk", not ikAttr)

                    for con in self.__constraints:
                        if cmds.objExists(con):
                            cmds.delete(con)
                    
                if len(self.__locs) >0:
                    for con in self.__locs:
                        if cmds.objExists(con):
                            cmds.delete(con)


    def bakeMetaSystem(self, metaSystemsToBake = 'ikFkSystem'):
        
        if not isinstance(metaSystemsToBake, list):
            metaSystemsToBake = [metaSystemsToBake]

        metaNodes = []
        print('Finding MetaSystems: ', metaSystemsToBake)
        for ms in metaSystemsToBake:
            metaNodesRet = self.__meta.findMeta(ms)
            print('found these: ', metaNodesRet)
            if len(metaNodesRet) > 0:
                for mnr in metaNodesRet:
                    metaNodes.append(mnr)

        if len(metaNodes) > 0:
            self.bakeRange(metaNodes)
        else:
            cmds.error('No meta systems of that type', metaSystemsToBake)


    def bakeRange(self, setupDataNodes):

        if not isinstance(setupDataNodes, list):
            setupDataNodes = [setupDataNodes]

        minTime = cmds.playbackOptions(q=True,min=True)
        maxTime = cmds.playbackOptions(q=True,max=True)

        cmds.currentTime( minTime )

        for i in range(int(minTime), int(maxTime)): 
            cmds.currentTime( i )

            for sdn in setupDataNodes:
                theIkSwitch = cmds.listConnections(sdn+'.theSwitchControl')[0]
                theIkTrn = cmds.listConnections(sdn+'.ikTrnControl')[0]
                thePvTrn = cmds.listConnections(sdn+'.ikPartners')[0]

                isIk = cmds.getAttr(theIkSwitch+'.fkIk')

                print('sending ', theIkSwitch)
                self.swap(theIkSwitch)

                if isIk:
                    cmds.setKeyframe(theIkTrn)
                    cmds.setKeyframe(thePvTrn)

                    cmds.setAttr(theIkSwitch+'.fkIk', 0)
