# Connection.py developed by Phillip Lundin 13 sep 2024

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Node')))
from Node import Node

class Connection:
   source : Node
   destination : Node
   SNR : float




