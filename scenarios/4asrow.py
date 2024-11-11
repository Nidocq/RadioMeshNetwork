
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node, RoutingProtocols



"""
This program will make three nodes. one with
- port 65000
- port 65003
- port 65006
- port 65009
1 see 65003, 2 will see 65000 and 65004, 3 will see 65001
"""


network = [Node("", 65000, RoutingProtocols.FLOODING, hopLimit=1),
           Node("", 65003, RoutingProtocols.FLOODING),
           Node("", 65006, RoutingProtocols.FLOODING),
           Node("", 65009, RoutingProtocols.FLOODING)]

for node in network:
    node.reconNetwork()

for node in network:
    node.nodeStatus()


network[0].sendData(b"ROUTE MSG hello you", '', 65009)

for node in network:
    node.serverThread.join()

#for node in network:
#    node.stopUDPServer()
