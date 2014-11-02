import unittest

from pyeve.tests.utils import getTestFile
from pyeve.whMap import createGraphFromFile, SystemTree


class MapGraph(unittest.TestCase):
    def assertConnectedSystems(self, system, connected):
        self.assertEqual(set([x.name for x in system.getConnectedSystems()]), set(connected))

    def assertChildSystems(self, node, childSystemNames):
        self.assertEqual(set([x.system.name for x in node.children]), set(childSystemNames))

    def test_simpleMap(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map1.yaml'))

        j1 = graph.getSystem("J1")
        self.assertEqual(j1.getSystemByConnection("ABC-001").name, 'J2')
        self.assertEqual(j1.getSystemByConnection("ABC-005").name, 'J4')

        self.assertEqual(set([x.name for x in j1.getConnectedSystems()]), set(["J2", "J4"]))

        j2 = graph.getSystem("J2")
        self.assertEqual(j2.getSystemByConnection("ABC-003").name, 'J3')
        self.assertEqual(j2.getSystemByConnection("ABC-002").name, 'J1')

        self.assertEqual(set([x.name for x in j2.getConnectedSystems()]), set(["J1", "J3"]))

    def test_complexMap(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map2.yaml'))

        j1 = graph.getSystem("J151909")
        self.assertEqual(set([x.name for x in j1.getConnectedSystems()]), set(["FO8M-2", "J165205"]))

        sysOto = graph.getSystem("Oto")
        self.assertConnectedSystems(sysOto, ['GDEW', 'RRWI', 'J142055', 'J110431', 'J151538'])

        sysJ142055 = graph.getSystem('J142055')
        self.assertConnectedSystems(sysJ142055, ['Oto', 'J151035' , 'J212607', 'J215537'])

    def test_connectedSystemsWithExclusions(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map2.yaml'))

        sysOto = graph.getSystem("Oto")
        sysJ142055 = graph.getSystem('J142055')
        sysRRWI = graph.getSystem('RRWI')

        self.assertNotIn(sysRRWI, sysOto.getConnectedSystems(excluded=[sysRRWI]))
        self.assertNotIn(sysJ142055, sysOto.getConnectedSystems(excluded=[sysJ142055]))

    def test_simpleSystemTree(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map1.yaml'))

        tree = SystemTree(graph, graph.getSystem('J1'))

        self.assertEqual(tree.root.system.name, 'J1')

        self.assertChildSystems(tree.root, ['J2', 'J4'])
        self.assertChildSystems(tree.root.getChildByName('J2'), ['J3'])

    def test_complexSystemTree_childNavigating(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map2.yaml'))

        tree = SystemTree(graph, graph.getSystem('J151909'))

        self.assertChildSystems(tree.root, ['FO8M-2', 'J165205'])
        self.assertChildSystems(tree.root.getChildByName('J165205'), ['J105433', 'J113918', 'UEPO-D'])
        self.assertChildSystems(tree.root.getChildByName('FO8M-2'), ['Jita', 'Amarr'])
        self.assertChildSystems(tree.root.searchAllChildrenByName('Oto'), ['J110431', 'J142055', 'RRWI', 'GDEW'])
        self.assertChildSystems(tree.root.searchAllChildrenByName('J142055'), ['J151035', 'J212607', 'J215537'])

    def test_complexSystemTree_leafCounting(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map2.yaml'))

        tree = SystemTree(graph, graph.getSystem('J151909'))

        self.assertEqual(tree.root.getLeafNodesCount(), 11)
        self.assertEqual(tree.root.getChildByName('FO8M-2').getLeafNodesCount(), 2)
        self.assertEqual(tree.root.searchAllChildrenByName('J105433').getLeafNodesCount(), 7)
        self.assertEqual(tree.root.searchAllChildrenByName('Oto').getLeafNodesCount(), 6)
        self.assertEqual(tree.root.searchAllChildrenByName('RRWI').getLeafNodesCount(), 1)

    def test_complexSystemTree_depthCounting(self):
        graph = createGraphFromFile(getTestFile('wormholeMaps/map2.yaml'))

        tree = SystemTree(graph, graph.getSystem('J151909'))

        self.assertEqual(tree.root.getDepth(), 7)
        self.assertEqual(tree.root.searchAllChildrenByName('J105433').getDepth(), 5)
        self.assertEqual(tree.root.searchAllChildrenByName('Oto').getDepth(), 3)
        self.assertEqual(tree.root.searchAllChildrenByName('RRWI').getDepth(), 1)