import unittest
import sys
import os
from time import sleep
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node

# // Naming structure: test_UnitOfWork_StateUnderTest_ExpectedBehavious
class TestSuite(unittest.TestCase):
    #@classmethod
    #def setUpClass(cls):
    #    pass

    def test_NetworkManager_GetResponse(self):
        sut = Node('', 65001)
        self.assertEqual(sut.serverIp, '')
        self.assertEqual(sut.serverPort, 65001)
        self.assertEqual(sut.portStrength, 3) # default value
        sut.stopUDPServer()
        self.assertTrue(sut.serverThread is None)
        exit(0)


    def test_proj_EveryNodeSeeEachOther(self):
        network = [Node('', 65000, portStrength=3),
                   Node('', 65003, portStrength=3),
                   Node('', 65005, portStrength=3)]

        for node in network:
            node.reconNetwork()

        checkList = []
        for node in network:
            node.nodeStatus()
            # we anticipate all the nodes at least seeing > 1 node
            checkList.append(len(node.connections) != 0)
            #node.serverThread.join()

        self.assertEqual(network[0].connections[0], ('127.0.0.1', 65003))
        self.assertEqual(network[1].connections[0], ('127.0.0.1', 65000))
        self.assertEqual(network[1].connections[1], ('127.0.0.1', 65005))
        self.assertEqual(network[2].connections[0], ('127.0.0.1', 65003))
        self.assertTrue(all(checkList))

        for node in network:
            node.stopUDPServer()

    def test_proj_OneNodeDoesNotSeeNetwork(self):
        #Which is the port 65099
        network = [Node('', 65000, portStrength=3),
                   Node('', 65001, portStrength=3),
                   Node('', 65004, portStrength=3),
                   Node('', 65099, portStrength=3)]
        for node in network:
            node.reconNetwork()

        checkList = []
        for node in network:
            # Here == because we anticipate one node not being able to see anyone
            checkList.append(len(node.connections) == 0)

        self.assertTrue(any(checkList))

        #for node in network:
        #    node.stopUDPServer()


if __name__ == '__main__':
    unittest.main()

