import abc


# Node.py developed by Phillip Lundin 13 sep 2024
class Node:
    id : str
    position : str
    connections : list
    def __init__(self):
        pass

# Connection.py developed by Phillip Lundin 13 sep 2024
class Connection:
   source : Node
   destination : Node
   SNR : float


# IComProtocol developed by Phillip Lundin 15 sep 2024
class IComProtocol(metaclass=abc.ABCMeta):
    nodes : list[Node]
    connections : list[Connection]

    @abc.abstractmethod
    def addNode(self, node: Node):
        pass


# Flooding.py developed by Phillip Lundin 15 sep 2024
class Flooding(IComProtocol):
    def __init__(self, nodes : list[Node]):
        print("hello world from flooding")

    def addNode(self, node : Node):
        self.nodes.append(node)

# MeshNetwork.py developed by Phillip Lundin 13 sep 2024
class MeshNetwork:
    network : IComProtocol
    def __init__(self, NetworkType):
        self.network = NetworkType



# Routing.py developed by Phillip Lundin 15 sep 2024
class Routing(IComProtocol):
    pass




n = Node()
m = Node()
node_list = []
node_list.append(n)
node_list.append(m)
flood = Flooding(node_list)
nw = MeshNetwork(flood)
print(nw)
