import pymel.core as pm


def getPerspectiveCameras():
    pcamlist = pm.listCameras(perspective=True)
    return pcamlist


def pmList2Objects(mylist):
    selection = pm.ls(selection=True)
    pm.select(cl=True)
    for o in mylist:
        pm.select(o, add=True)
    objects = pm.ls(sl=True)
    pm.select(selection)
    return objects


class bobj(object):
    def __init__(self, sourceObj):
        self.sourceObj = sourceObj
        self.parents = self.findParents()
        self.hierarchy = list(self.parents)
        self.hierarchy.insert(0, sourceObj)
        self.animationData = self.getAnimationData()

    def findParents(self):
        startingNode = self.sourceObj
        parents = []
        # check if the current item has a parent. If so then add it to the parents list and set the parent as current item and start over
        while (True):
            myParent = startingNode.listRelatives(parent=True)
            if not myParent:
                break;
            startingNode = myParent[0]
            parents.append(startingNode)

        return parents

    def getAnimationData(self):
        keyframes = []
        objs = self.hierarchy
        for obj in objs:
            animAttributes = pm.listAnimatable(obj);
            for attribute in animAttributes:
                numKeyframes = pm.keyframe(attribute, q=True, keyframeCount=True)
                if (numKeyframes > 0):
                    times = (pm.keyframe(attribute, q=True, index=(0, numKeyframes), timeChange=True))
                    for t in times:
                        keyframes.append(t)
                        keyframes.sort()
        return keyframes


def main(selection=False):
    copies = []
    if selection == False:
        objs = pmList2Objects(getPerspectiveCameras())
    else:
        objs = pm.ls(sl=True)
        if len(objs)<1:
            print ("Please select an object to bake")

    for obj in objs:
        source = bobj(obj)
        if source.animationData != []:
            print "Baking {0}".format(obj)
            copy = pm.duplicate(source.sourceObj, n=(str(source.sourceObj) + "_baked"))
            print "Result = {0}".format(copy)
            pm.parent(copy[0], world=True)
            pm.parentConstraint(source.sourceObj, copy)
            pm.bakeResults(copy, t=(source.animationData[0], source.animationData[-1]), simulation=True)
            pm.delete(pm.listRelatives(copy, c=True)[1])


if __name__ == "__main__":
    main(True)
