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
import threading
import re
from typing import List, Tuple#, Self

from enum import Enum

class RoutingProtocols(Enum):
    ISOLATION = 0
    CENTRALIZED = 1
    DISTRIBUTED = 2
    FLOODING  = 3
    RANDOM_WALK  = 4
    NONE  = 5

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
    stopServerThread : bool= None

    enableDiagnostics : bool
    routing : RoutingProtocols

    def __init__(self, serverIp, serverPort, RoutingProtocol = RoutingProtocols.NONE, portStrength = 3, enableDiagnostics = True):
        self.iden = "".join([chr(random.randint(65, 90)) for _ in range(16)])
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.enableDiagnostics = enableDiagnostics
        self.portStrength = portStrength
        self.routing = RoutingProtocol

        # https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument
        if (self.connections is None):
            self.connections = []

        if (self.stopServerThread is None):
            self.stopServerThread = False

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

    def reconNetwork(self, sockTimeout : int = 1, destIp = '', runAsThread=True):
        """
            Will recon for other nodes in the vicinity for its self.portStrength self.connection
            this will mean that self.portStrength of 10, will search for every port from -10 to +10
            every port from the port strength will have its own thread, to speed up the network discovery.
            POSTCONDITION: will populate the self.connections with the Nodes in the vincinity.
            @param
                sockTimeout : int   -   The amount of time it should take for each port to timeout
        """
        reconThreads : list[threading.Thread] = []
        # +1 because we skip our own port and we don't want our own port to count towards the strength
        for portScan in range(self.serverPort - self.portStrength, self.serverPort + self.portStrength+1):
            if (portScan == self.serverPort):
                # If the port is the same as the node own port, skip
                continue
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(sockTimeout)
            data = b'PING'

            print(f'{self.diagnositcPrepend("reconNetwork()", "Starting recon as a thread")}')

            t = threading.Thread(group=None, target=self.tryPing, args=(data, destIp, portScan, client_socket))
            reconThreads.append(t)

        for t in reconThreads:
            t.start()

        for t in reconThreads:
            t.join()

    def tryPing(self, data, destIp, destPort, sock):
        print(f'{self.diagnositcPrepend("reconNetwork()", f"Searching {destPort} for nodes")}')
        sock.sendto(data, (destIp, destPort))
        try:
            recData, server = sock.recvfrom(1024)
            if (recData == b'pong'):
                print(f'{self.diagnositcPrepend("reconNetwork() Node found!", f"server : {server} added!")}:')
                self.connections.append(server)
        except socket.timeout:
            pass

    def nodeStatus(self):
        """
            prints the information about this node.
        """
        print(f'{self.diagnositcPrepend("NodeStatus()",f"Identification : {self.iden}\naddress : '{self.serverIp}':{self.serverPort}\nconnections : {self.connections}\nposition {self.position}, portStrength {self.portStrength}")}')

    def sendData(self, data : bytes, destIp : str, destPort : int, requireACK=False):
        """
            Sends data in bytes to a destination ip and port
            @param
                data : bytes    -   Bytes of data that will get sent
                destIp : str    -   The destination IP
                destPort : int  -   The destination Port
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if requireACK:
            client_socket.settimeout(1.0)

        start = time.time()
        client_socket.sendto(data, (destIp, destPort))
        print(f'{self.diagnositcPrepend("sendData(data, (destIp, destpPrt)))",
              "Message sent!..")}:{data!r}')

        if requireACK:
            try:
                recData, server = client_socket.recvfrom(1024)
                end = time.time()
                elapsed = end - start
                # f strings produce sanitised strings if bytes are input
                # Therefore !r makes it 'bytes' spcifically
                print(f'{self.diagnositcPrepend("sendData()",
                      f"received ACK from {server}")}:{recData!r} {elapsed}')
                if recData == b'ACK':
                    print("LKJDLKJLKFJLKDJFJAFOMAN")
            except socket.timeout:
                print('REQUEST TIMED OUT')


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
        self.listenForRequests(server_socket)


    def listenForRequests(self, sock, buffer = 1024):
        """
            listens for incomming traffic forever.
            @param
                sock : socket   -   the socket which the server listens to (is bound to this node's address)
                buffer : int    -   The buffer that the receiving message can hold
        """
        while True:
            if self.stopServerThread:
                print(f'{self.diagnositcPrepend("listenForRequests()", "Server received stop flag ...")}')
                break
            message, address = sock.recvfrom(buffer)
            print(f'{self.diagnositcPrepend("listenForRequests()", f"SERVER RECEIVED MESSAGE from {address}")} : {message!r}')
            self.processRequest(sock, message, address)


    def stopUDPServer(self):
        #TODO Try catch to gracefully stop the server 
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Stopping server...")
        self.stopServerThread = True
        self.serverThread.join()
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Server Stopped! ")
        self.serverThread = None

    def processRequest(self, sock, message, address, errMsg=""):
        """
            processes a request from another node
            @param
                sock : socket   -   The open socket which the request came from
                message : bytes -   The bytes that were tranferred to this node and needs to be processed
                address : tuple(str, int) The address the message came from
        """
        # splitting up the message 
        cmd, rest_message = self.extractCommand(message)
        print(f"cmd : {cmd} and rmessage {rest_message}")
        match cmd:
            case 'PING':
                print(f'{self.diagnositcPrepend("processRequest()", f"processing request {message!r}, responding back with pong...")}')
                sock.sendto(b'pong', address)
            case 'ACK':
                print(f'{self.diagnositcPrepend("processRequest()", f"processing request {message!r}, responding back with ACK...")}')
                sock.sendto(b'ACK', address)
                self.processRequest(sock, rest_message, address)
            
            case 'MSG':
                print(f'{self.diagnositcPrepend("processRequest()", f"--- Message received! : {message!r}")} : from {address} ---')
            case 'ROUTE':
                print(f'{self.diagnositcPrepend("processRequest()", f"Routing message request with {self.routing.name} of message {message!r}")} : from {address}')
                adr, rest_message = self.extractCommand(rest_message)
                # Find anything in the format ('*', number<0, 65535>)
                match = re.search("^\('*', \d{0,65535}\)$", adr.trim)
                if match is None:
                    print(f'{self.diagnositcPrepend("processRequest()", f"Malformed request with {self.routing.name} of message {message!r}")} : from {address} sending errMessage back')
                    # Do request again, but without the malformed request.
                    # prepend err flag and add an error message. Send it to 
                    rest_message = self.prependCommand(rest_message, "ERR")
                    self.processRequest(sock, rest_message, address, errMsg="Malfored request")
                else:
                    # make the string into a tuple
                    requestedReceiver = tuple(cmd.split(" "))
                    # If the address match, do not do anymore routing
                    print(f'serverIp {self.serverIp} serverPort {self.serverPort}, reqRe {requestedReceiver[0]} and {requestedReceiver[1]} ')
                    if self.serverIp == requestedReceiver[0] and self.serverPort == requestedReceiver[1]:
                        # stop and process the request
                        print(f'{self.diagnositcPrepend("processRequest()", "Route Equals this adress! ")}')
                        self.processRequest(sock, rest_message, address)
                    else:
                        self.processRouteRequest(sock, message, address)

            case _:
                print(f'{self.diagnositcPrepend("processRequest()", f"COULD NOT PROCESS REQUEST {message!r}")} : from {address}')
                errMsg = "COULD NOT PROCESS REQUEST : " + errMsg
                sock.sendto(errMsg, address)


    def extractCommand(self, message : bytes):
        cmd_list = message.decode("utf-8").split(" ")
        messageCmd = cmd_list[0].upper()
        rest_message = " ".join(cmd_list[1:]).encode("utf-8")
        return messageCmd, rest_message

    def prependCommand(self, message : bytes, tag : str):
        cmd_list = message.decode("utf-8").split(" ")
        pmessage = list(reversed(cmd_list))
        pmessage.append(tag)
        pmessage = list(reversed(pmessage))
        returnMessage = " ".join(pmessage).encode("utf-8")
        return returnMessage

    def processRouteRequest(self, sock, message, address):
        print(f'{self.diagnositcPrepend("processRouteRequest()", "processing the routing algorithms...")} : from {address}')
        match self.routing:
            case RoutingProtocols.ISOLATION:
                print(RoutingProtocols.ISOLATION)
            case RoutingProtocols.CENTRALIZED:
                print(RoutingProtocols.CENTRALIZED)
            case RoutingProtocols.DISTRIBUTED:
                print(RoutingProtocols.DISTRIBUTED)
            case RoutingProtocols.FLOODING:
                print(RoutingProtocols.FLOODING)
            case RoutingProtocols.RANDOM_WALK:
                print(RoutingProtocols.RANDOM_WALK)
            case RoutingProtocols.NONE:
                print(RoutingProtocols.NONE)

if __name__ == '__main__':
    n = Node("", 65000)
    m = Node("", 65001)
    network = []
    network.append(n)
    network.append(m)

    for node in network:
        node.reconNetwork()

    time.sleep(8)
    n.sendData(b'ACK MSG Hello world', '', 65001, requireACK=True)

