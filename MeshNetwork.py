# MeshNetwork.py developed by Phillip Lundin 13 sep 2024

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Routing')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Flooding')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Interface')))
from Interface.IComProtocol import IComProtocol

class MeshNetwork:
    network : IComProtocol
    def __init__(self, NetworkType):
        self.network = NetworkType



