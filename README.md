Radio Mesh Network
the focus would be on the network protocol
### Prerequisites for the design
The design choices of the initial idea of the software is as follows:
- Have each node a logfile to increase the debugging of each node.
- Have each node a different communication algorithm from a interface. 
    - The communication interface makes it possible to have networks that mix
      each other
    - Extendability
- Simulate different scenarios with different files
  - nodes not reaching each other
  - Only two nodes readches each other, the rest are out of range from any one
  - Two clusters seperated from each other.



```mermaid
classDiagram 
        direction BT
    class ComProtocol {
        <<Interface>>
        +nodes: Node[]
        +connections: Connection[]

        +addNode(node: Node)
        +removeNode(node: Node)
        +addConnection(connection: Connection)
        +removeConnection(connection: Connection)
        
        +sendData(source: Node, destination: Node, data: string)
        +receiveData(node: Node, data: string)
    }
    %% %%%%%
    ComProtocol <|-- Flooding
    ComProtocol <|-- Routing
    ComProtocol <|-- Waterfall
    %% %%%%%

    class Node {
        +string : UUID
        +position : position
        +connections: Connection[]
        +MeshNetwork : network

        +sendData(data: string, Node : sender Node : receiver)
        +receiveData(data: string, Node : sender)
        +broadcastData(data: string)
    }
    %% %%%%%
    Node <-- ComProtocol
    %% %%%%%

    class MeshNetwork {
        +protocol : ComProtocol
    }
    
    class Connection {
        +source: Node
        +destination: Node
        +SNR : float?
    }
    %% %%%%%
    Connection <--  ComProtocol
    Connection <--  Node
    %% %%%%%

    class Flooding {
        ...
    }

    class Routing {
        ...
    }
    class Waterfall {
       ...
    }

    class FullyConnected {
        +protocol : ComProtocol
    }

MeshNetwork *--  Node
FullyConnected *--  Node
Flooding <-- MeshNetwork
Routing <-- MeshNetwork
Waterfall <-- FullyConnected
Logging -- Node
```
> 12 Sep 2024

The idea of the MOC is `Node`s send, receieve and broadcasts data should be
dependant on the transmission and netowrk protocol used in the network.

The network is dependant on the communication protocol which implements how the
nodes talk together and exchange data. The network also takes care of which
nodes are currently present and which nodes can see which nodes.

Communication Protocol as the main idea of the project as it carries the
emphasis of the project. This is where how the communication should be carried
out. There is a "general" way of sending data which is why we have the interface
of the protocol

MeshNetowrk can either use the Flooding or the routing communication algorithm.
