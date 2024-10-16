# Node.py developed by Phillip Lundin 13 sep 2024
# This is a program to simulate how a radio meshnetwork
# would work in practice. Abstractions have been made to
# justify the underlying logic on an actual implementation.
# You can read more on https://github.com/Nidocq/RadioMeshNetwork/blob/main/README.md

import abc
import socket
import random
import time
import datetime
import os
import threading
from typing import List, Tuple#, Self


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Node:
    iden : str
    position : str = "earth"

    connections : List[Tuple[str, int]] = None  
    serverIp : str
    serverPort : int

    # this will indicates the strength of a radio signal if it was
    # just a signal. If this is set to 10, this will search for other
    # nodes that are either in the range -10 ports away or +10 ports away
    portStrength : int

    # indicate that we use server threads to communicate with other nodes
    serverThread = None

    enableDiagnostics : bool

    def __init__(self, serverIp, serverPort, portStrength = 3, enableDiagnostics = True):
        self.iden = "".join([chr(random.randint(65, 90)) for _ in range(16)])
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.enableDiagnostics = enableDiagnostics
        self.portStrength = portStrength

        # https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument
        if (self.connections is None):
            self.connections = []

        self.runServerThread(serverIp, serverPort)


    def runServerThread(self, ip : str, port : int):
        """
            Will spawn a thread to start a UDP server with the specified ip and port
            POSTCONDITION: will populate the current class' server with this spawned thread (self.serverT)
            @param
                ip : str    -   the ip the server should listen on
                port : int  -   the port the server should listen on
        """
        if (self.serverThread is not None):
            print("Server already running, please run stopUDPServer() before making new connection")
            exit(1)
        else:
            serverThread = threading.Thread(group=None, target=self.startUDPServer, args=(ip, port), daemon=True)
            self.serverThread = serverThread
            self.serverThread.start()

    def reconNetwork(self, sockTimeout : int = 1, destIp = ''):
        """
            Will recon for other nodes in the vicinity for its self.portStrength self.connection
            this will mean that self.portStrength of 10, will search for every port from -10 to +10
            POSTCONDITION: will populate the self.connections with the Nodes in the vincinity.
            @param
                sockTimeout : int   -   The amount of time it should take for each port to timeout
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(sockTimeout)
        data = b'ping'

        # +1 because we skip our own port and we don't want our own port to count towards the strength
        for portScan in range(self.serverPort - self.portStrength, self.serverPort + self.portStrength+1):
            if (portScan == self.serverPort):
                # If the port is the same as the node own port, skip
                continue

            print(f'{self.diagnositcPrepend("reconNetwork()", f"Searching {portScan} for nodes")}')
            client_socket.sendto(data, (destIp, portScan))
            try:
                recData, server = client_socket.recvfrom(1024)
                if (recData == b'pong'):
                    print(f'{self.diagnositcPrepend("reconNetwork() Node found!", f"server : {server} added!")}:')
                    self.connections.append(server)
            except socket.timeout:
                #print(f'{self.diagnositcPrepend("reconNetwork()", f"No node found on {portScan}. Continuing")}')
                continue

    def nodeStatus(self):
        """
            prints the information about this node.
        """
        print(f'{self.diagnositcPrepend("NodeStatus()",f"Identification : {self.iden}\naddress : '{self.serverIp}':{self.serverPort}\nconnections : {self.connections}\nposition {self.position}, portStrength {self.portStrength}")}')

    def sendData(self, data : bytes, destIp : str, destPort : int):
        """
            Sends data in bytes to a destination ip and port
            @param
                data : bytes    -   Bytes of data that will get sent
                destIp : str    -   The destination IP
                destPort : int  -   The destination Port
        """
        for pings in range(30):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(1.0)

            start = time.time()
            client_socket.sendto(data, (destIp, destPort))
            print(f'{self.diagnositcPrepend("sendData(data, (destIp, destpPrt)))",
                  "Sending message")}:{data!r} {pings}')
            try:
                recData, server = client_socket.recvfrom(1024)
                end = time.time()
                elapsed = end - start
                # f strings produce sanitised strings if bytes are input
                # Therefore !r makes it 'bytes' spcifically
                print(f'{self.diagnositcPrepend("sendData()",
                      f"received message from {server}")}:{recData!r} {pings} {elapsed}')
            except socket.timeout:
                print('REQUEST TIMED OUT')

        pass


    def diagnositcPrepend(self, caller : str, customMessage : str):
        """
            prints diagnostic like time and current nodeto help
            the programmer debug the code
            @param
                context:str  -  the context in which this method should be run
                                could be a specific function call or an event
        """
        if self.enableDiagnostics is True or self.enableDiagnostics is not None:
            return f"\n{bcolors.BOLD}{bcolors.OKGREEN}{caller}{bcolors.WARNING} {customMessage} {bcolors.ENDC}{bcolors.BOLD}{str(datetime.datetime.now())} -c:{self.iden} '{self.serverIp}':{self.serverPort}{bcolors.ENDC}\n\t"
        else:
            return ""


    def startUDPServer(self, ip : str, port : int, listenForPing = True):
        """
            Start a UDP server that listens on the specified ip and port
            POSTCONDITION : Will populate the self.server(ip&port) of the listening ip and port
            @param
                ip : str    -   The ip the server should listen on
                port : int  -   The port the server should listen on
        """
        # https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python
        # TODO Implement some fallback behaviour, or some try catch
        print(f"{self.diagnositcPrepend("startUDPServer()", "")} starting UDP connection server {ip}:{port} as thread from id : {self.iden}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f'{self.diagnositcPrepend("startUDPServer()", "")} Binding to \'{ip}\':{port}')
        server_socket.bind((ip, port))

        self.serverIp = ip
        self.serverPort = port
        self.receiveData(server_socket)



    def receiveData(self, sock, buffer = 1024):
        """
            listens for incomming traffic forever.
            @param
                sock : socket   -   the socket which the server listens to (is bound to this node's address)
                buffer : int    -   The buffer that the receiving message can hold
        """
        while True:
            message, address = sock.recvfrom(buffer)
            print(f'{self.diagnositcPrepend("receiveData()", f"SERVER RECEIVED MESSAGE from {address}")} : {message!r}')
            self.processRequest(sock, message, address)

    def stopUDPServer(self):
        #TODO Try catch to gracefully stop the server 
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Stopping server...")
        self.serverThread.join()
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Server Stopped! ")

    def processRequest(self, sock, message, address):

        match message:
            case b'ping':
                print(f'{self.diagnositcPrepend("processRequest()", f"processing request {message!r}, responding back with pong...")}')
                sock.sendto(b'pong', address)
            case _:
                print(f'{self.diagnositcPrepend("processRequest()", f"COULD NOT PROCESS REQUEST {message!r}")} : from {address}')


#-------------------------------------------------- 


class Connection:
   source : Node
   destination : Node
   SNR : float


class IComProtocol(metaclass=abc.ABCMeta):
    nodes : list[Node]
    connections : list[Connection]

    @abc.abstractmethod
    def addNode(self, node: Node):
        pass


class Flooding(IComProtocol):
    def __init__(self, nodes : list[Node]):
        pass

    def addNode(self, node : Node):
        self.nodes.append(node)

class Routing(IComProtocol):
    pass

class MeshNetwork:
    network : IComProtocol
    def __init__(self, NetworkType):
        self.network = NetworkType


if __name__ == '__main__':
    #https://stackoverflow.com/questions/2084508/clear-the-terminal-in-python
    os.system('cls' if os.name == 'nt' else 'clear')
    network = [Node('', 65000), Node('', 65001), Node('', 65004), Node('', 65099)]

    #send_node = Node('', 65003, 2) # will send a message to 65000 through (65001 or 65004)
    #network.append(send_node)
    #send_node.sendData(b'Hello 65001 from {},format(send_node.source_port)', '', 65001)
    #network[0].connections.append(('', 650044))

    Thr = []
    # start
    for node in network:
        print("spawning thread")
        Thr.append(threading.Thread(group=None, target=node.reconNetwork, daemon=True))

    for t in Thr:
        t.start()

    for t in Thr:
        t.join()

    # end
    for node in network:
        node.nodeStatus()

    #n.sendData(b'Hello from me', '', 65001)
    time.sleep(1)



