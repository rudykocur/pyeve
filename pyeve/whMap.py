import yaml


def createGraphFromFile(filename):

    graph = SystemGraph()

    with open(filename, 'r') as f:
        data = list(yaml.load_all(f))[1]

        for systemData in data['systems']:
            graph.addSystem(System(**systemData))

        for connectionData in data['connections']:
            connectionData['left'] = graph.getSystem(connectionData['left'])
            connectionData['right'] = graph.getSystem(connectionData['right'])

            Connection(**connectionData)

    return graph


class SystemGraph(object):
    def __init__(self):
        self.systems = {}

    def addSystem(self, system):
        self.systems[system.name] = system

    def getSystem(self, systemName):
        """
        :rtype: pyeve.whMap.System
        """
        return self.systems[systemName]


class System(object):
    def __init__(self, name):
        self.name = name

        #: :type: list of pyeve.whMap.Connection
        self.connections = []

    def getSystemByConnection(self, connectionName):
        for c in self.connections:
            if c.leftName == connectionName:
                return c.right

            if c.rightName == connectionName:
                return c.left

        raise KeyError('No connection named: %s' % connectionName)

    def getConnectedSystems(self, excluded=None):
        for c in self.connections:
            if excluded:
                if c.left in excluded or c.right in excluded:
                    continue

            if c.left == self:
                yield c.right
            else:
                yield c.left


class Connection(object):
    def __init__(self, left, right, leftName, rightName):
        """

        :type left: pyeve.whMap.System
        :type right: pyeve.whMap.System
        """
        self.left = left
        self.right = right
        self.leftName = leftName
        self.rightName = rightName

        self.left.connections.append(self)
        self.right.connections.append(self)


class SystemTree(object):
    def __init__(self, graph, topSystem):
        #: :type: pyeve.whMap.TreeNode
        self.root = None

        #: :type: pyeve.whMap.System
        self.topSystem = topSystem
        self.graph = graph

        self.initTree()

    def initTree(self):
        children = list(self.topSystem.getConnectedSystems())
        self.root = TreeNode(self.topSystem, None, [])

        self.root.children = self.createNodes(self.root, children)

    def createNodes(self, parent, childSystems):
        """

        :type childSystems: list of pyeve.whMap.System
        :type parent: pyeve.whMap.TreeNode
        """
        result = []
        for child in childSystems:
            nodeSubSystems = list(child.getConnectedSystems([parent.system]))
            node = TreeNode(child, parent, [])
            node.children = self.createNodes(node, nodeSubSystems)

            result.append(node)

        return result


class TreeNode(object):
    def __init__(self, node, parent, children):
        self.system = node
        self.parent = parent

        #: :type: list of pyeve.whMap.TreeNode
        self.children = children

    def getChildByName(self, systemName):
        for child in self.children:
            if child.system.name == systemName:
                return child

        raise KeyError('No child by system name: %s' % systemName)

    def searchAllChildrenByName(self, systemName):
        if self.system.name == systemName:
            return self

        for child in self.children:
            hit = child.searchAllChildrenByName(systemName)
            if hit:
                return hit

    def getLeafNodesCount(self):
        return max(1, sum([c.getLeafNodesCount() for c in self.children]))

    def getDepth(self):
        if len(self.children):
            return max([c.getDepth() for c in self.children]) + 1

        return 1