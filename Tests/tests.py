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
        #sleep(1)
        #import threading
        #self.assertIsInstance(sut.serverThread, ) # default value


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

        self.assertTrue(all(checkList))

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


if __name__ == '__main__':
    unittest.main()

