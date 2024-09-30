import abc
import socket
import random
import time
import datetime
import os
import threading

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

# Node.py developed by Phillip Lundin 13 sep 2024
class Node:
    iden : str
    position : str
    connections : list
    serverIp : str
    serverPort : int

    # this will indicates the strength of a radio signal if it was
    # just a signal. If this is set to 10, this will search for other
    # nodes that are either in the range -10 ports away or +10 ports away
    portStrength : int
    serverThread = None

    sourceIp : str
    sourcePort : int

    enableDiagnostics : bool

    def __init__(self, sourceIp, sourcePort, enableDiagnostics = True):
        self.iden = "".join([chr(random.randint(65, 90)) for _ in range(16)])
        self.sourceIp = sourceIp
        self.sourcePort = sourcePort
        self.enableDiagnostics = enableDiagnostics




        self.runServerThread(sourceIp, sourcePort)


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

    def sendData(self, data : bytes, destIp, destPort):
        """
            Sends data in bytes to a destination ip and port
            @param
                data : bytes    -   Bytes of data that will gets sent
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

    def recieveData(self, data : str, receiver): # : Node
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
            return f"\n{bcolors.BOLD}{bcolors.OKGREEN}{caller}{bcolors.WARNING} {customMessage} {bcolors.ENDC}{bcolors.BOLD}{str(datetime.datetime.now())} -c:{self.iden}{bcolors.ENDC}\n\t"
        else:
            return ""

    def transmitData(self, data : str):
        pass

    def connectToNetwork(self):
        pass



    def startUDPServer(self, ip : str, port : int):
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
        print(f'{self.diagnositcPrepend("startUDPServer()", "")} Binding to ip : {ip}, on port {port}')
        server_socket.bind((ip, port))

        self.serverIp = ip
        self.serverPort = port

        while True:
            message, address = server_socket.recvfrom(1024)
            message = message.upper()
            print(f'{self.diagnositcPrepend("StartUDPServer()", f"SERVER RECEIVED MESSAGE from {address}")} : {message!r}')
            server_socket.sendto(message, address)

    def stopUDPServer(self):
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Stopping server...")
        self.serverThread.join()
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Server Stopped! ")







#-------------------------------------------------- 




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
        pass

    def addNode(self, node : Node):
        self.nodes.append(node)

# Routing.py developed by Phillip Lundin 15 sep 2024
class Routing(IComProtocol):
    pass

# MeshNetwork.py developed by Phillip Lundin 13 sep 2024
class MeshNetwork:
    network : IComProtocol
    def __init__(self, NetworkType):
        self.network = NetworkType


if __name__ == '__main__':
    #https://stackoverflow.com/questions/2084508/clear-the-terminal-in-python
    os.system('cls' if os.name == 'nt' else 'clear')
    n = Node('', 65000)
    m = Node('', 65001)

    n.sendData(b'Hello from me', '', 65001)
    #time.sleep(1)
    #n.stopUDPServer()



