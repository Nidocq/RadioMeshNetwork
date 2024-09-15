# Node.py developed by Phillip Lundin 15 sep 2024

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'MeshNetwork')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Node')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Flooding')))

from MeshNetwork import MeshNetwork
from Flooding import Flooding
from Node import Node


n = Node()
m = Node()
node_list = []
node_list.append(n)
node_list.append(m)
flood = Flooding(node_list)
nw = MeshNetwork(flood)
print(nw)
