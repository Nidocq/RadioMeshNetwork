# Routing.py developed by Phillip Lundin 15 sep 2024
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Interface')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Node')))
from Interface.IComProtocol import IComProtocol
from Node import Node

class Flooding(IComProtocol):
    def __init__(self, nodes : list[Node]):
        print("hello world from flooding")

    def addNode(self, node : Node):
        self.nodes.append(node)

