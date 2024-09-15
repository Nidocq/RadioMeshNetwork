# ComProtocol.py developed by Phillip Lundin 15 sep 2024
import abc
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Node')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Connection')))
from Node import Node
from Connection import Connection

class IComProtocol(metaclass=abc.ABCMeta):
    nodes : list[Node]
    connections : list[Connection]

    @abc.abstractmethod
    def addNode(self, node: Node):
        pass

