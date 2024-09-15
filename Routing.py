# Routing.py developed by Phillip Lundin 15 sep 2024
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Interface')))
from Interface.IComProtocol import IComProtocol

class Routing(IComProtocol):
    pass
