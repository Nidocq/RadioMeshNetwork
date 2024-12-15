import random
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node, RoutingProtocols

x = 65000
y = 65500
network : list[Node] = []
picked : list[int] = []
nodes_add = 1
hops = 3
random_num = random.randint(x, y)

while nodes_add <= 16:
    while random_num in picked:
        random_num = random.randint(x, y)
    picked.append(random_num)
    portStrength = random.randint(5 ,140)
    print(f"random_num {random_num}, portStrength {portStrength}, hops {hops}")
    network.append(Node("", random_num, RoutingProtocols.FLOODING, portStrength=portStrength, hopLimit=hops, scanIntervalSec=120))

    for node in network:
        node.reconNetwork()

    #for node in network:
    #    node.join()

    time.sleep(nodes_add/10)
    nodes_add *= 2
    hops *= 2

