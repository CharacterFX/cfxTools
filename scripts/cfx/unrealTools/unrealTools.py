import cfx.getDistances as gd
import cfx.insertBufferGroup as ibg
import cfx.dynamicPOconstraint as dpo 
import cfx.addOrMakeGroup as aomg 
import cfx.returnObjectWithAttr as roa
import cfx.rigSettings as rigset
import cfx.metaSystem as rmeta
import cfx.attrUtilities as atru

import random
import maya.cmds as cmds

import importlib
modulesToReload = [atru, dpo, rigset, rmeta]
for mtr in modulesToReload:
    importlib.reload(mtr)

class unrealTools(object):

    def __init__(self):
        self.__settings = rigset.rigSettings()
        self.__meta = rmeta.metaSystem()
        self.__distance = gd.getDistances()
        self.__attrFinder = roa.returnObjectWithAttr()
        self.__attrutil = atru.attrUtilities()

    def writeUnrealAimConstraint(self, aimjoint, aimAt, nodeName, nodeUid, pinComponentPose, pinAlpha, pinPose, pos, alphaNodeGuid, alphaPinGuid, lastNode = None):

        print(lastNode)
        if lastNode is not None:

            unrealNode = 'Begin Object Class=/Script/AnimGraph.AnimGraphNode_LookAt Name=\"'+nodeName+'\"\n   Node=(BoneToModify=(BoneName=\"'+aimjoint+'\"),LookAtTarget=(BoneReference=(BoneName=\"'+aimAt+'\")),LookAtLocation=(X=0.000000,Y=0.000000,Z=0.000000),LookAt_Axis=(Axis=(X=1.000000,Y=0.000000,Z=0.000000)),LookUp_Axis=(Axis=(X=0.000000,Y=1.000000,Z=0.000000)))\n   ShowPinForProperties(0)=(PropertyName=\"BoneToModify\",PropertyFriendlyName=\"Bone to Modify\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:BoneToModify\", \"Name of bone to control. This is the main bone chain to modify from. *\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(1)=(PropertyName=\"LookAtTarget\",PropertyFriendlyName=\"Look at Target\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:LookAtTarget\", \"Target socket to look at. Used if LookAtBone is empty. - You can use  LookAtLocation if you need offset from this point. That location will be used in their local space. *\"),CategoryName=\"Target\")\n   ShowPinForProperties(2)=(PropertyName=\"LookAtLocation\",PropertyFriendlyName=\"Look at Location\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:LookAtLocation\", \"Target Offset. It\'s in world space if LookAtBone is empty or it is based on LookAtBone or LookAtSocket in their local space\"),CategoryName=\"Target\",bCanToggleVisibility=True)\n   ShowPinForProperties(3)=(PropertyName=\"LookAt_Axis\",PropertyFriendlyName=\"Look at Axis\",PropertyTooltip=NSLOCTEXT(\"\", \"29FFCC2F4BBEEA9166D94D842DB0D356\", \"Look at Axis\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(4)=(PropertyName=\"bUseLookUpAxis\",PropertyFriendlyName=\"Use Look Up Axis\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:bUseLookUpAxis\", \"Whether or not to use Look up axis\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(5)=(PropertyName=\"LookUp_Axis\",PropertyFriendlyName=\"Look Up Axis\",PropertyTooltip=NSLOCTEXT(\"\", \"145A5811443B8A3D8883C9A3112B0BE4\", \"Look Up Axis\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(6)=(PropertyName=\"LookAtClamp\",PropertyFriendlyName=\"Look at Clamp\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:LookAtClamp\", \"Look at Clamp value in degree - if you\'re look at axis is Z, only X, Y degree of clamp will be used\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(7)=(PropertyName=\"InterpolationType\",PropertyFriendlyName=\"Interpolation Type\",PropertyTooltip=NSLOCTEXT(\"\", \"4686B7B446FDFBF4C75BD897714E82D0\", \"Interpolation Type\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(8)=(PropertyName=\"InterpolationTime\",PropertyFriendlyName=\"Interpolation Time\",PropertyTooltip=NSLOCTEXT(\"\", \"AA2893FA48BBE69C90A80EA2B8C0986D\", \"Interpolation Time\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(9)=(PropertyName=\"InterpolationTriggerThreashold\",PropertyFriendlyName=\"Interpolation Trigger Threashold\",PropertyTooltip=NSLOCTEXT(\"\", \"4C29C6B94A62862DBDCFCDB3E754FC1C\", \"Interpolation Trigger Threashold\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(10)=(PropertyName=\"ComponentPose\",PropertyFriendlyName=\"Component Pose\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_SkeletalControlBase:ComponentPose\", \"Input link\"),CategoryName=\"Links\",bShowPin=True)\n   ShowPinForProperties(11)=(PropertyName=\"Alpha\",PropertyFriendlyName=\"Alpha\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_SkeletalControlBase:Alpha\", \"Current strength of the skeletal control\"),CategoryName=\"Settings\",bShowPin=True,bCanToggleVisibility=True)\n   ShowPinForProperties(12)=(PropertyName=\"AlphaScaleBias\",PropertyFriendlyName=\"Alpha Scale Bias\",PropertyTooltip=NSLOCTEXT(\"\", \"F767E3EB484C0DC7C34C96935A364FE0\", \"Alpha Scale Bias\"),CategoryName=\"Settings\")\n   ShowPinForProperties(13)=(PropertyName=\"LODThreshold\",PropertyFriendlyName=\"LOD Threshold\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_SkeletalControlBase:LODThreshold\", \"* Max LOD that this node is allowed to run\\n* For example if you have LODThreadhold to be 2, it will run until LOD 2 (based on 0 index)\\n* when the component LOD becomes 3, it will stop update/evaluate\\n* currently transition would be issue and that has to be re-visited\"),CategoryName=\"Performance\")\n   NodePosX='+str(pos[0])+'\n   NodePosY='+str(pos[1])+'\n   NodeGuid='+nodeUid+'\n   CustomProperties Pin (PinId='+pinComponentPose+',PinName=\"ComponentPose\",PinFriendlyName=NSLOCTEXT(\"\", \"6D0EA319486877FF474E8493B9A350D7\", \"Component Pose\"),PinToolTip=\"Component Pose\\nComponent Space Pose Link Structure\\n\\nInput link\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct\'\"/Script/Engine.ComponentSpacePoseLink\"\',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",AutogeneratedDefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",LinkedTo=('+lastNode[0]+' '+lastNode[4]+',),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId='+pinAlpha+',PinName=\"Alpha\",PinFriendlyName=NSLOCTEXT(\"\", \"58CD0FE248CD914C3634A2AFF19E4AA0\", \"Alpha\"),PinToolTip=\"Alpha\\nFloat\\n\\nCurrent strength of the skeletal control\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"1.000000\",AutogeneratedDefaultValue=\"1.000000\",LinkedTo=(aimConstraint_variableGet_0 '+alphaPinGuid+',),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId='+pinPose+',PinName=\"Pose\",Direction=\"EGPD_Output\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct\'\"/Script/Engine.ComponentSpacePoseLink\"\',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\nEnd Object\n'
        else:
            unrealNode = 'Begin Object Class=/Script/AnimGraph.AnimGraphNode_LookAt Name=\"'+nodeName+'\"\n   Node=(BoneToModify=(BoneName=\"'+aimjoint+'\"),LookAtTarget=(BoneReference=(BoneName=\"'+aimAt+'\")),LookAtLocation=(X=0.000000,Y=0.000000,Z=0.000000),LookAt_Axis=(Axis=(X=1.000000,Y=0.000000,Z=0.000000)),LookUp_Axis=(Axis=(X=0.000000,Y=1.000000,Z=0.000000)))\n   ShowPinForProperties(0)=(PropertyName=\"BoneToModify\",PropertyFriendlyName=\"Bone to Modify\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:BoneToModify\", \"Name of bone to control. This is the main bone chain to modify from. *\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(1)=(PropertyName=\"LookAtTarget\",PropertyFriendlyName=\"Look at Target\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:LookAtTarget\", \"Target socket to look at. Used if LookAtBone is empty. - You can use  LookAtLocation if you need offset from this point. That location will be used in their local space. *\"),CategoryName=\"Target\")\n   ShowPinForProperties(2)=(PropertyName=\"LookAtLocation\",PropertyFriendlyName=\"Look at Location\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:LookAtLocation\", \"Target Offset. It\'s in world space if LookAtBone is empty or it is based on LookAtBone or LookAtSocket in their local space\"),CategoryName=\"Target\",bCanToggleVisibility=True)\n   ShowPinForProperties(3)=(PropertyName=\"LookAt_Axis\",PropertyFriendlyName=\"Look at Axis\",PropertyTooltip=NSLOCTEXT(\"\", \"29FFCC2F4BBEEA9166D94D842DB0D356\", \"Look at Axis\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(4)=(PropertyName=\"bUseLookUpAxis\",PropertyFriendlyName=\"Use Look Up Axis\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:bUseLookUpAxis\", \"Whether or not to use Look up axis\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(5)=(PropertyName=\"LookUp_Axis\",PropertyFriendlyName=\"Look Up Axis\",PropertyTooltip=NSLOCTEXT(\"\", \"145A5811443B8A3D8883C9A3112B0BE4\", \"Look Up Axis\"),CategoryName=\"SkeletalControl\")\n   ShowPinForProperties(6)=(PropertyName=\"LookAtClamp\",PropertyFriendlyName=\"Look at Clamp\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_LookAt:LookAtClamp\", \"Look at Clamp value in degree - if you\'re look at axis is Z, only X, Y degree of clamp will be used\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(7)=(PropertyName=\"InterpolationType\",PropertyFriendlyName=\"Interpolation Type\",PropertyTooltip=NSLOCTEXT(\"\", \"4686B7B446FDFBF4C75BD897714E82D0\", \"Interpolation Type\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(8)=(PropertyName=\"InterpolationTime\",PropertyFriendlyName=\"Interpolation Time\",PropertyTooltip=NSLOCTEXT(\"\", \"AA2893FA48BBE69C90A80EA2B8C0986D\", \"Interpolation Time\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(9)=(PropertyName=\"InterpolationTriggerThreashold\",PropertyFriendlyName=\"Interpolation Trigger Threashold\",PropertyTooltip=NSLOCTEXT(\"\", \"4C29C6B94A62862DBDCFCDB3E754FC1C\", \"Interpolation Trigger Threashold\"),CategoryName=\"SkeletalControl\",bCanToggleVisibility=True)\n   ShowPinForProperties(10)=(PropertyName=\"ComponentPose\",PropertyFriendlyName=\"Component Pose\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_SkeletalControlBase:ComponentPose\", \"Input link\"),CategoryName=\"Links\",bShowPin=True)\n   ShowPinForProperties(11)=(PropertyName=\"Alpha\",PropertyFriendlyName=\"Alpha\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_SkeletalControlBase:Alpha\", \"Current strength of the skeletal control\"),CategoryName=\"Settings\",bShowPin=True,bCanToggleVisibility=True)\n   ShowPinForProperties(12)=(PropertyName=\"AlphaScaleBias\",PropertyFriendlyName=\"Alpha Scale Bias\",PropertyTooltip=NSLOCTEXT(\"\", \"F767E3EB484C0DC7C34C96935A364FE0\", \"Alpha Scale Bias\"),CategoryName=\"Settings\")\n   ShowPinForProperties(13)=(PropertyName=\"LODThreshold\",PropertyFriendlyName=\"LOD Threshold\",PropertyTooltip=NSLOCTEXT(\"UObjectToolTips\", \"AnimNode_SkeletalControlBase:LODThreshold\", \"* Max LOD that this node is allowed to run\\n* For example if you have LODThreadhold to be 2, it will run until LOD 2 (based on 0 index)\\n* when the component LOD becomes 3, it will stop update/evaluate\\n* currently transition would be issue and that has to be re-visited\"),CategoryName=\"Performance\")\n   NodePosX='+str(pos[0])+'\n   NodePosY='+str(pos[1])+'\n   NodeGuid='+nodeUid+'\n   CustomProperties Pin (PinId='+pinComponentPose+',PinName=\"ComponentPose\",PinFriendlyName=NSLOCTEXT(\"\", \"6D0EA319486877FF474E8493B9A350D7\", \"Component Pose\"),PinToolTip=\"Component Pose\\nComponent Space Pose Link Structure\\n\\nInput link\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct\'\"/Script/Engine.ComponentSpacePoseLink\"\',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",AutogeneratedDefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId='+pinAlpha+',PinName=\"Alpha\",PinFriendlyName=NSLOCTEXT(\"\", \"58CD0FE248CD914C3634A2AFF19E4AA0\", \"Alpha\"),PinToolTip=\"Alpha\\nFloat\\n\\nCurrent strength of the skeletal control\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"1.000000\",AutogeneratedDefaultValue=\"1.000000\",LinkedTo=(aimConstraint_variableGet_0 '+alphaPinGuid+',),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId='+pinPose+',PinName=\"Pose\",Direction=\"EGPD_Output\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct\'\"/Script/Engine.ComponentSpacePoseLink\"\',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\nEnd Object\n'
        
        return unrealNode

    def exportAllAimCons(self, filename):

        aimCons = cmds.ls(type='aimConstraint')
        
        posX = 0
        posY = 0

        xCount = 0
        xCountReset = 5

        file = open(filename,"w") 

        #do float variable to connect all to alpha
        alphaNodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        alphaPinGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        file.write("Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name=\"aimConstraint_variableGet_0\"\n   VariableReference=(MemberName=\"aimConstraint\",MemberGuid=7F6BE0604957E0625E6CDBADEA3F1062,bSelfContext=True)\n   NodePosX=0\n   NodePosY=-200\n   NodeGuid="+alphaNodeGuid+"\n   CustomProperties Pin (PinId="+alphaPinGuid+",PinName=\"aimConstraint\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId=71BEEF6A4633DA9C153884A57E6A68ED,PinName=\"self\",PinFriendlyName=NSLOCTEXT(\"K2Node\", \"Target\", \"Target\"),PinType.PinCategory=\"object\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\nEnd Object\n")

        pinComponentPose = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        pinAlpha = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        pinPose = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        lastNode = None

        #for ac in aimCons:
        for idx, ac in enumerate(aimCons):

            nodeId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

            theAimer = cmds.listConnections(ac+'.constraintRotateX', s=0,d=1)
            targets = cmds.listConnections(ac+'.target', s=1,d=0, type='joint')
            theTarget = list(set(targets))[0]
            file.write( self.writeUnrealAimConstraint(theAimer[0], theTarget, ac, nodeId, pinComponentPose, pinAlpha, pinPose, [posX,posY], alphaNodeGuid, alphaPinGuid, lastNode))

            posX += 300
            xCount +=1
            print('xCount is : ', xCount)
            if xCount > xCountReset:
                xCount = 0
                posX = 0
                posY += 200

            lastNode = [ac,nodeId, pinComponentPose, pinAlpha, pinPose]

        file.close() 


    #exports the list of attrs as a text file for a pose asset and a modify curve node for ABP
    def exportRigPoseData(self, filename, attrs):

        #write attrs to file for when you convert to a pose asset in Unreal
        self.__attrutil.saveAttrNamesToFile(filename, attrs)

        #write text for modify curve node

        posX = 0
        posY = 0

        mcfilename = filename+'.modifycurve'
        file = open(mcfilename,"w") 

        #do float variable to connect all to alpha
        alphaNodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        alphaPinGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        file.write("Begin Object Class=/Script/AnimGraph.AnimGraphNode_ModifyCurve Name=\"AnimGraphNode_ModifyCurve_1\"\n")   #VariableReference=(MemberName=\"aimConstraint\",MemberGuid=7F6BE0604957E0625E6CDBADEA3F1062,bSelfContext=True)\n   NodePosX=0\n   NodePosY=-200\n   NodeGuid="+alphaNodeGuid+"\n   CustomProperties Pin (PinId="+alphaPinGuid+",PinName=\"aimConstraint\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId=71BEEF6A4633DA9C153884A57E6A68ED,PinName=\"self\",PinFriendlyName=NSLOCTEXT(\"K2Node\", \"Target\", \"Target\"),PinType.PinCategory=\"object\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\nEnd Object\n")

        numString = ''
        attrString = ''
        for attr in attrs:
            numString = numString+"0.000000,"
            attrString = attrString+'\"'+attr+'\",'

        numString = numString[:-1]
        attrString = attrString[:-1]

        file.write("   Node=(CurveValues=("+numString+"),CurveNames=("+attrString+"))\n") #removed ,ApplyMode=RemapCurve

        file.write("   ShowPinForProperties(0)=(PropertyName=\"SourcePose\",PropertyFriendlyName=\"Source Pose\",PropertyTooltip=NSLOCTEXT(\"\", \"57BDD942461073D97B1037AECCA90C8C\", \"Source Pose\"),CategoryName=\"Links\",bShowPin=True)\n   ShowPinForProperties(1)=(PropertyName=\"CurveValues\",PropertyFriendlyName=\"Curve Values\",PropertyTooltip=NSLOCTEXT(\"\", \"D196777E465EF9EC5C6D6496D289DAD4\", \"Curve Values\"),CategoryName=\"ModifyCurve\",bShowPin=True,bCanToggleVisibility=True)\n   ShowPinForProperties(2)=(PropertyName=\"Alpha\",PropertyFriendlyName=\"Alpha\",PropertyTooltip=NSLOCTEXT(\"\", \"BD667E5B4051DCAE815804A27F377908\", \"Alpha\"),CategoryName=\"ModifyCurve\",bShowPin=True,bCanToggleVisibility=True)\n   ShowPinForProperties(3)=(PropertyName=\"ApplyMode\",PropertyFriendlyName=\"Apply Mode\",PropertyTooltip=NSLOCTEXT(\"\", \"041E1D0349A22F9EB11D518E9B1B15B0\", \"Apply Mode\"),CategoryName=\"ModifyCurve\")\n   NodePosX="+str(posX)+"\n   NodePosY="+str(posY)+"\n   ErrorType=4\n")
        file.write("   NodeGuid="+alphaNodeGuid+"\n")

        sourcePosePin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+sourcePosePin+",PinName=\"SourcePose\",PinFriendlyName=\"Source Pose\",PinToolTip=\"Source Pose\\nPose Link Structure\\n\\nSource Pose\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct'\"/Script/Engine.PoseLink\"',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",AutogeneratedDefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")

        curveValues = 0
        for attr in attrs:
            pinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+pinId+",PinName=\"CurveValues_"+str(curveValues)+"\",PinFriendlyName=\""+attr+"\",PinToolTip=\"Curve Values 0\\nFloat\\n\\nCurve Values\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.000000\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            curveValues = curveValues + 1

        pinAlpha = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+pinAlpha+",PinName=\"Alpha\",PinFriendlyName=\"Alpha\",PinToolTip=\"Alpha\\nFloat\\n\\nAlpha\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"1.000000\",AutogeneratedDefaultValue=\"1.000000\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        
        pinPose = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+pinPose+",PinName=\"Pose\",Direction=\"EGPD_Output\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct'\"/Script/Engine.PoseLink\"',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=(AnimGraphNode_PoseBlendNode_1 0B52322B4B1C20513E8A55BD606B741E,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        file.write("End Object")
        file.close() 


    def exportCorrectiveNodes(self, filename, attrs):

        posY = 0
        posX = 0

        mcfilename = filename
        file = open(mcfilename,"w") 

        #do float variable to connect all to alpha
        alphaNodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        alphaPinGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        modifyCurveNodeName = 'AnimGraphNode_ModifyCurve_Correctives'+''.join(random.choice('0123456789ABCDEF') for i in range(4))

        file.write("Begin Object Class=/Script/AnimGraph.AnimGraphNode_ModifyCurve Name=\""+modifyCurveNodeName+"\"\n")   #VariableReference=(MemberName=\"aimConstraint\",MemberGuid=7F6BE0604957E0625E6CDBADEA3F1062,bSelfContext=True)\n   NodePosX=0\n   NodePosY=-200\n   NodeGuid="+alphaNodeGuid+"\n   CustomProperties Pin (PinId="+alphaPinGuid+",PinName=\"aimConstraint\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId=71BEEF6A4633DA9C153884A57E6A68ED,PinName=\"self\",PinFriendlyName=NSLOCTEXT(\"K2Node\", \"Target\", \"Target\"),PinType.PinCategory=\"object\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\nEnd Object\n")

        numString = ''
        attrString = ''
        for attr in attrs:
            numString = numString+"0.000000,"
            attrString = attrString+'\"'+attr+'_cor\",'

        numString = numString[:-1]
        attrString = attrString[:-1]

        file.write("   Node=(CurveValues=("+numString+"),CurveNames=("+attrString+"))\n") #removed ,ApplyMode=RemapCurve

        file.write("   ShowPinForProperties(0)=(PropertyName=\"SourcePose\",PropertyFriendlyName=\"Source Pose\",PropertyTooltip=NSLOCTEXT(\"\", \"57BDD942461073D97B1037AECCA90C8C\", \"Source Pose\"),CategoryName=\"Links\",bShowPin=True)\n   ShowPinForProperties(1)=(PropertyName=\"CurveValues\",PropertyFriendlyName=\"Curve Values\",PropertyTooltip=NSLOCTEXT(\"\", \"D196777E465EF9EC5C6D6496D289DAD4\", \"Curve Values\"),CategoryName=\"ModifyCurve\",bShowPin=True,bCanToggleVisibility=True)\n   ShowPinForProperties(2)=(PropertyName=\"Alpha\",PropertyFriendlyName=\"Alpha\",PropertyTooltip=NSLOCTEXT(\"\", \"BD667E5B4051DCAE815804A27F377908\", \"Alpha\"),CategoryName=\"ModifyCurve\",bShowPin=True,bCanToggleVisibility=True)\n   ShowPinForProperties(3)=(PropertyName=\"ApplyMode\",PropertyFriendlyName=\"Apply Mode\",PropertyTooltip=NSLOCTEXT(\"\", \"041E1D0349A22F9EB11D518E9B1B15B0\", \"Apply Mode\"),CategoryName=\"ModifyCurve\")\n   NodePosX="+str(posX)+"\n   NodePosY="+str(posY)+"\n   ErrorType=4\n")
        file.write("   NodePosX=300\n")
        file.write("   NodePosY=0\n")
        file.write("   NodeGuid="+alphaNodeGuid+"\n")

        sourcePosePin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+sourcePosePin+",PinName=\"SourcePose\",PinFriendlyName=\"Source Pose\",PinToolTip=\"Source Pose\\nPose Link Structure\\n\\nSource Pose\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct'\"/Script/Engine.PoseLink\"',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",AutogeneratedDefaultValue=\"(LinkID=-1,SourceLinkID=-1)\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")

        pinIds = {}
        curveValues = 0
        for attr in attrs:
            pinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            recPinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            linkedTo = "K2Node_CallFunction_"+attr
            pinIds[attr] = [pinId,recPinId]
            file.write("   CustomProperties Pin (PinId="+pinId+",PinName=\"CurveValues_"+str(curveValues)+"\",PinFriendlyName=\""+attr+"_cor\",PinToolTip=\"Curve Values 0\\nFloat\\n\\nCurve Values\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.000000\",AutogeneratedDefaultValue=\"0.0\",LinkedTo=("+linkedTo+" "+recPinId+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            curveValues = curveValues + 1

        pinAlpha = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+pinAlpha+",PinName=\"Alpha\",PinFriendlyName=\"Alpha\",PinToolTip=\"Alpha\\nFloat\\n\\nAlpha\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"1.000000\",AutogeneratedDefaultValue=\"1.000000\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        
        pinPose = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        file.write("   CustomProperties Pin (PinId="+pinPose+",PinName=\"Pose\",Direction=\"EGPD_Output\",PinType.PinCategory=\"struct\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=ScriptStruct'\"/Script/Engine.PoseLink\"',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=(AnimGraphNode_PoseBlendNode_1 0B52322B4B1C20513E8A55BD606B741E,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        file.write("End Object\n")

        xCount = 0
        xCountReset = 20
        for key, value in pinIds.iteritems():
            nodeName = "K2Node_CallFunction_"+key
            NodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            pinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            pinIdTwo = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="+nodeName+"\n   bIsPureFunc=True\n   bIsConstFunc=True\n   FunctionReference=(MemberName=\"GetCurveValue\",bSelfContext=True)\n   NodePosX=-80\n   NodePosY="+str(posY)+"\n   NodeGuid="+str(NodeGuid)+"\n")
            file.write("   CustomProperties Pin (PinId="+pinId+",PinName=\"self\",PinFriendlyName=NSLOCTEXT(\"K2Node\", \"Target\", \"Target\"),PinToolTip=\"Target\n   Anim Instance Object Reference\",PinType.PinCategory=\"object\",PinType.PinSubCategory="",PinType.PinSubCategoryObject=Class\'\"/Script/Engine.AnimInstance\"\',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("   CustomProperties Pin (PinId="+pinIdTwo+",PinName=\"CurveName\",PinToolTip=\"Curve Name\\nName\",PinType.PinCategory=\"name\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\""+key+"\",AutogeneratedDefaultValue=\"None\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            pinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+value[1]+",PinName=\"ReturnValue\",PinToolTip=\"Return Value\\nFloat\\n\\nReturns the value of a named curve.\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",LinkedTo=("+modifyCurveNodeName+" "+value[0]+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("End Object\n")
            posY += 120

            xCount +=1
            if xCount > xCountReset:
                xCount = 0
                posX += 200

        file.close()


    #At this point you need to feed it the value node
    #unreal.exportLiveLinkSetShapeNodes("F:/Salif Face Scans/exportToGame/switchNodes.txt", attrs, 'K2Node_Tunnel_0 5910E8EC46BA0C987CE4BFA0BDDED287')
    def exportLiveLinkSetShapeNodes(self, filename, attrs, ValuePinId):

        posY = 0
        posX = 0

        mcfilename = filename
        file = open(mcfilename,"w") 

        #do float variable to connect all to alpha
        alphaNodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        alphaPinGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        modifyCurveNodeName = 'K2Node_SwitchString'+''.join(random.choice('0123456789ABCDEF') for i in range(4))

        file.write("Begin Object Class=/Script/BlueprintGraph.K2Node_SwitchString Name=\""+modifyCurveNodeName+"\"\n")   #VariableReference=(MemberName=\"aimConstraint\",MemberGuid=7F6BE0604957E0625E6CDBADEA3F1062,bSelfContext=True)\n   NodePosX=0\n   NodePosY=-200\n   NodeGuid="+alphaNodeGuid+"\n   CustomProperties Pin (PinId="+alphaPinGuid+",PinName=\"aimConstraint\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n   CustomProperties Pin (PinId=71BEEF6A4633DA9C153884A57E6A68ED,PinName=\"self\",PinFriendlyName=NSLOCTEXT(\"K2Node\", \"Target\", \"Target\"),PinType.PinCategory=\"object\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsArray=False,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\nEnd Object\n")

        pinCount = 0
        pinIds = {}
        for attr in attrs:
            pinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            recPinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            pinIds[attr] = [pinId,recPinId]
            file.write("   PinNames("+str(pinCount)+")=\""+attr+"\"\n")
            pinCount = pinCount + 1

        file.write("   NodePosX=0\n")
        file.write("   NodePosY=0\n")
        file.write("   NodeGuid="+alphaNodeGuid+"\n")
        CustomPropertiesPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+CustomPropertiesPin+",PinName=\"Default\",Direction=\"EGPD_Output\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        executePin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+executePin+",PinName=\"execute\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=(K2Node_Tunnel_0 9635621D465152349D7A4DBED2B6BF67,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        SelectionPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+SelectionPin+",PinName=\"Selection\",PinType.PinCategory=\"string\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=(K2Node_Tunnel_0 9313AAEE40D68A2EC9D7D182B9034418,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        NotEqualPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        file.write("   CustomProperties Pin (PinId="+NotEqualPin+",PinName=\"NotEqual_StriStri\",PinType.PinCategory=\"object\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=Class'\"/Script/Engine.KismetStringLibrary\"',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultObject=\"/Script/Engine.Default__KismetStringLibrary\",PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=True,bDefaultValueIsReadOnly=True,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
        #curveValues = 0
        for key, value in pinIds.iteritems():
            
            linkedTo = "K2Node_VariableSet_"+key
            file.write("   CustomProperties Pin (PinId="+value[0]+",PinName=\""+key+"\",Direction=\"EGPD_Output\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=("+linkedTo+" "+value[1]+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            #file.write("   CustomProperties Pin (PinId="+pinId+",PinName=\"CurveValues_"+str(curveValues)+"\",PinFriendlyName=\""+attr+"_cor\",PinToolTip=\"Curve Values 0\\nFloat\\n\\nCurve Values\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.000000\",AutogeneratedDefaultValue=\"0.0\",LinkedTo=("+linkedTo+" "+recPinId+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            #curveValues = curveValues + 1
        file.write("End Object\n")


        #this loop creates the individual set nodes
        xCount = 0
        xCountReset = 20
        for key, value in pinIds.iteritems():
            nodeName = "K2Node_VariableSet_"+key
            NodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            MemberGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("Begin Object Class=/Script/BlueprintGraph.K2Node_VariableSet Name=\""+nodeName+"\"\n")
            file.write("   VariableReference=(MemberName="+key+",MemberGuid="+MemberGuid+",bSelfContext=True)")
            file.write("   NodePosX=300\n")
            file.write("   NodePosY="+str(posY)+"\n")
            file.write("   NodeGuid="+NodeGuid+"\n")
            ExecutePin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+value[1]+",PinName=\"execute\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=("+modifyCurveNodeName+" "+value[0]+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            EpdPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+EpdPin+",PinName=\"then\",Direction=\"EGPD_Output\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("   CustomProperties Pin (PinId="+ExecutePin+",PinName=\""+key+"\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",LinkedTo=("+ValuePinId+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            OutputPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+OutputPin+",PinName=\"Output_Get\",PinToolTip=\"Retrieves the value of the variable, can use instead of a separate Get node\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("End Object\n")
            posY += 120

            xCount +=1
            if xCount > xCountReset:
                xCount = 0
                posX += 200

        file.close() 

    def exportAnimationShapeNodes(self, filename, attrs):

        posY = 0
        posX = 0

        mcfilename = filename
        file = open(mcfilename,"w") 

        #do float variable to connect all to alpha
        alphaNodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
        alphaPinGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

        pinIds = {}
        for attr in attrs:
            pinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            recPinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            egpdPinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            ValueOutPinId = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            pinIds[attr] = [pinId, recPinId, egpdPinId, ValueOutPinId]

        #this loop creates the individual set nodes
        xCount = 0
        xCountReset = 20

        yCount = 0

        previousEdp = None
        previousNode = None

        #first create set value nodes
        for key, value in pinIds.iteritems():
            nodeName = "K2Node_VariableSet_"+key
            NodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            MemberGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("Begin Object Class=/Script/BlueprintGraph.K2Node_VariableSet Name=\""+nodeName+"\"\n")
            file.write("   VariableReference=(MemberName="+key+",MemberGuid="+MemberGuid+",bSelfContext=True)\n")
            file.write("   NodePosX="+str(posX)+"\n")
            file.write("   NodePosY="+str(posY)+"\n")
            file.write("   NodeGuid="+NodeGuid+"\n")
            ExecutePin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            if previousEdp:
                file.write("   CustomProperties Pin (PinId="+value[1]+",PinName=\"execute\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,LinkedTo=("+previousNode+" "+previousEdp+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            else:
                file.write("   CustomProperties Pin (PinId="+value[1]+",PinName=\"execute\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            #EpdPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+value[2]+",PinName=\"then\",Direction=\"EGPD_Output\",PinType.PinCategory=\"exec\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("   CustomProperties Pin (PinId="+value[0]+",PinName=\""+key+"\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            OutputPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+OutputPin+",PinName=\"Output_Get\",PinToolTip=\"Retrieves the value of the variable, can use instead of a separate Get node\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("End Object\n")

            previousEdp = value[2]
            previousNode = nodeName

            posX += 250
            xCount +=1
            if xCount > xCountReset:
                xCount = 0
                posX = 0
                posY += 400

        posX = 0
        xCount = 0
        posY = 200
        #then create get curve nodes
        for key, value in pinIds.iteritems():
            nodeName = "K2Node_CallFunction_"+key
            NodeGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            MemberGuid = ''.join(random.choice('0123456789ABCDEF') for i in range(32))

            file.write("Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name=\""+nodeName+"\"\n")
            file.write("   bIsPureFunc=True\n")
            file.write("   bIsConstFunc=True\n")
            file.write("   FunctionReference=(MemberName=\"GetCurveValue\",bSelfContext=True)\n")
            file.write("   NodePosX="+str(posX)+"\n")
            file.write("   NodePosY="+str(posY)+"\n")
            file.write("   NodeGuid="+NodeGuid+"\n")
            selfPin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+selfPin+",PinName=\"self\",PinFriendlyName=NSLOCTEXT(\"K2Node\", \"Target\", \"Target\"),PinToolTip=\"Target\\nAnim Instance Object Reference\",PinType.PinCategory=\"object\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=Class\'\"/Script/Engine.AnimInstance\"\',PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            CurveNamePin = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
            file.write("   CustomProperties Pin (PinId="+CurveNamePin+",PinName=\"CurveName\",PinToolTip=\"Curve Name\\nName\",PinType.PinCategory=\"name\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\""+key+"\",AutogeneratedDefaultValue=\"None\",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            file.write("   CustomProperties Pin (PinId="+value[3]+",PinName=\"ReturnValue\",PinToolTip=\"Return Value\\nFloat\\n\\nReturns the value of a named curve.\",Direction=\"EGPD_Output\",PinType.PinCategory=\"float\",PinType.PinSubCategory=\"\",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,DefaultValue=\"0.0\",AutogeneratedDefaultValue=\"0.0\",LinkedTo=(K2Node_VariableSet_"+key+" "+value[0]+",),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)\n")
            
            file.write("End Object\n")

            previousEdp = value[2]
            previousNode = nodeName

            posX += 250
            xCount +=1
            if xCount > xCountReset:
                xCount = 0
                posX = 0
                posY += 400

        file.close() 