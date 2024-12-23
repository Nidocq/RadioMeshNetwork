import random
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node, RoutingProtocols

"""
Usage
    python3 -i scenarios/createScenario.py 2 65040 65090 6 25 7 0
    will create
    2 nodes,
    random ports between 65040 and 65090 (inclusive)
    random portStrengths between 6 and 25 (inclusive)
    7 for the hopLimit
    1/0 if nodes servers should stop after run 0 if nodes should keep running in interactive
"""


network : list[Node] = []
picked = []
for node in range(0, int(sys.argv[1])):
    random_num = random.randint(int(sys.argv[2]), int(sys.argv[3]))
    while random_num in picked:
        random_num = random.randint(int(sys.argv[2]), int(sys.argv[3]))

    picked.append(random_num)
    network.append(
        Node("", random_num, RoutingProtocols.RANDOM_WALK, portStrength=random.randint(int(sys.argv[4]) ,int(sys.argv[5])), hopLimit=sys.argv[6], persistNetworkDiscovery=int(sys.argv[8]))
    )
for node in network:
    node.reconNetwork()

for node in network:
    node.nodeStatus()

if int(sys.argv[7]) >= 1:
    for node in network:
        node.stopUDPServer()
