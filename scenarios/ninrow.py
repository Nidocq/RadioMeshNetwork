import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './..')))
from proj import Node, RoutingProtocols


start = 20000
n = int(sys.argv[1])
network = []
scanInterval = 10
ran = 3
# (ran*2-1)*nodes
# where ran is the range of the node's portStrength
#       nodes is the amount of nodes
# f(5) = (3*2-1)*5 = 5*5 = 25




tim = 0
res = False
for i in range(start, start+(n*ran), ran):
    network.append(Node("", i, RoutingProtocols.FLOODING, persistNetworkDiscovery=False, scanIntervalSec=scanInterval, portStrength=3))

time.sleep(1)
timenow = time.time()
for node in network:
    node.reconNetwork()

timediff = time.time() - timenow
time.sleep(4)
res = False


st = len(network[0].connections) == 1
mid = True
for i in range(1, len(network)-1):
    mid = mid & (len(network[i].connections) == 2)
    if mid is False:
        break
end = len(network[-1].connections) == 1
res = st & mid & end
a, b, c, d, e, ff, g = network[0].PopNetworkStats()
with open("stringStatsTest.txt", "a") as f:
    print(f"{n}, {tim}, {res}, {timediff}, {a}, {b}, {c}, {d}, {e}, {ff}, {g}", file=f)
    print(f"{n}, {tim}, {res}, {timediff}, {a}, {b}, {c}, {d}, {e} {ff}, {g}")
print("Saved!")
n += 1

for node in network:
    node.stopUDPServer()
time.sleep(2)
