import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node 



"""
This program will make three nodes. one with 
- port 65000
- port 65001
- port 65004
1 sill see 65001, 2 will see 65000 and 65004, 3 will see 65001
"""


network = [Node("", 65000), Node("", 65001), Node("", 65004)]
for node in network:
    node.reconNetwork()

for node in network:
    node.nodeStatus()

for node in network:
    node.stopUDPServer()
