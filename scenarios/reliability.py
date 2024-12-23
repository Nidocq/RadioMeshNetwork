
import random
import time
import sys
import os
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node, RoutingProtocols

"""
Usage
    python3 -i scenarios/createScenario.py 2 65040 65090 6 25 7 0 1 50
    will create
    2 nodes,
    random ports between 65040 and 65090 (inclusive)
    random portStrengths between 6 and 25 (inclusive)
    7 for the hopLimit
    1/0 if nodes servers should stop after run 0 if nodes should keep running in interactive
    1/0 : 1 if nodes should persist their network discovery phase for a set interval
    50 : secs of interval
"""



network : list[Node] = []
picked = []
for node in range(0, int(sys.argv[1])):
    random_num = random.randint(int(sys.argv[2]), int(sys.argv[3]))
    while random_num in picked:
        random_num = random.randint(int(sys.argv[2]), int(sys.argv[3]))

    picked.append(random_num)
    network.append(
        Node("",
             random_num,
             RoutingProtocols.FLOODING,
             portStrength=random.randint(int(sys.argv[4]) ,int(sys.argv[5])),
             hopLimit=sys.argv[6],
             persistNetworkDiscovery=int(sys.argv[8]),
             scanIntervalSec=int(sys.argv[9])
        )
    )
for node in network:
    node.reconNetwork()
    # node.printNetworkStats()

time.sleep(0.2)
for node in network:
    node.nodeStatus()
time.sleep(0.2)
network[0].PopNetworkStats()

for msg in range(len(network)*2):
    randomIntNode = random.randint(0, len(network)-1)
    anotherRandomIntNode = random.randint(0, len(network)-1)
    while len(network[randomIntNode].connections) == 0:
        randomIntNode = random.randint(0, len(network)-1)

    network[randomIntNode].sendData(b'ROUTE MSG sending lots of love',
                                    network[anotherRandomIntNode].serverIp,
                                    network[anotherRandomIntNode].serverPort
                                   )
    print("waiting for messages to finish")


time.sleep(30)

a, b, c, d, e, ff, g = network[0].PopNetworkStats()
with open("reliability_2212_FLOODING.txt", "a") as f:
    print(f"{sys.argv[1]}, {int(sys.argv[1])*2}, {sys.argv[6]}, {a}, {b}, {c}, {d}, {e}, {ff}, {g}", file=f)
    print(f"{sys.argv[1]}, {int(sys.argv[1])*2}, {sys.argv[6]}, {a}, {b}, {c}, {d}, {e}, {ff}, {g}")
print("Saved!")

time.sleep(1)


if int(sys.argv[7]) >= 1:
    for node in network:
        node.stopUDPServer(waitForJoin=True)
