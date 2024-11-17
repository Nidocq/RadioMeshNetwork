import random
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node, RoutingProtocols




network : list[Node] = []
for node in range(0, 30):
    network.append(Node("", random.randint(65000, 65090), RoutingProtocols.FLOODING, portStrength=random.randint(5,33), hopLimit=7))

for node in network:
    node.reconNetwork()

for node in network:
    node.nodeStatus()



time.sleep(2)
#print(f" Request count : {network[0].printNetworkCongestion()}")
for node in network:
    node.serverThread.join()

#for node in network:
#    node.stopUDPServer()
