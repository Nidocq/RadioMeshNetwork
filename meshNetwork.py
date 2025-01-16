# Node.py developed by Phillip Lundin 13 sep 2024
# This is a program to simulate radio mesh networks
# Abstractions have been made to justify the underlying logic on an actual implementation.
# You can read more on https://github.com/Nidocq/RadioMeshNetwork/blob/main/README.md

import socket
import random
import time
import datetime
from threading import Thread, Lock, active_count
import re
from typing import List, Tuple
from enum import Enum

fruitsvegs = [
    "Apple", "Apricot", "Avocado", "Banana", "Blueberry",
    "Cherry", "Date", "Durian", "Elderberry", "Fig",
    "Gooseberry", "Grape", "Guava", "Jackfruit", "Kiwi",
    "Lemon", "Lychee", "Mango", "Melon", "Orange",
    "Papaya", "Pear", "Persimmon", "Pineapple", "Plum",
    "Pomegranate", "Quince", "Raspberry", "Strawberry", "Tangerine",
    "Artichoke", "Arugula", "Asparagus", "Beet", "Bok Choy",
    "Broccoli", "Brussels Sprouts", "Cabbage", "Cauliflower",
    "Celery", "Chard", "Collard Greens", "Corn", "Cucumber",
    "Eggplant", "Endive", "Escarole", "Fennel", "Garlic",
    "Ginger", "Horseradish", "Kale", "Leek", "Lettuce",
    "Mushroom", "Okra", "Onion", "Parsnip", "Pea",
    "Pumpkin", "Radish", "Rapini", "Rhutabaga", "Spinach",
    "Swiss Chard", "Turnip", "Watercress", "Zucchini"
]

# Global variables for measuring network
mutex = Lock()
recv_network_requests = 0
sent_network_requests = 0
err_network_requests = 0
route_recv_network_requests = 0
hops_reached_network_requests = 0
avg_time_network_requests = 0.0
time_network_list_requests : list[float] = []
time_network_times_dic : dict[str,float] = {}
withDaemon = True

class DiagnosticStats(Enum):
    """
        When performing network audit, different cases need to be categorized
        This is the categories which a request can be categorized as.
        NB this is not mutually exclusive.
            RECV_REQ - Request received
            SENT_REQ - Request sent
            ERR_REQ  - Error in request
            TIME_LIST_REQ - time request reach destination
            AVG_TIME_REQ_RECV - Average time for requests reaching destination
            ROUTE_RECV - Route requests received
            HOPS_REACHED - Hop reached
    """
    RECV_REQ = 0
    SENT_REQ = 1
    ERR_REQ = 2
    TIME_LIST_REQ = 3
    AVG_TIME_REQ_RECV = 4
    ROUTE_RECV = 5
    HOPS_REACHED = 6

class RoutingProtocols(Enum):
    """
        Routing protocols used by all Nodes. Refer to section 3.5 in thesis.
    """
    ISOLATION = 0
    CENTRALIZED = 1
    DISTRIBUTED = 2
    FLOODING  = 3
    RANDOM_WALK  = 4
    NONE  = 5

class bcolors:
    """
        Helper class to color output. Used for debugging.
    """
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
    """
        iden            : str                   - Identification of the Node. formatted
        connection      : List[Tuple[str, int]] - The connection list every node possesses
            to identify which other Node this Node can see. This is done through the Network
            discovery covered in section 4.2.1.
        ServerIp        : str                   - The Node's server IP.
        serverPort      : str                   - The Node's server Port
        hopLimit        : int                   - The Node's hop Limit Port. Used to limit
            the amount of routes a message can travel. refer to section 4.2.2 in thesis
        portStrength    : int                   - This will indicates the strength of a radio signal if it was
            just a signal. If this is set to 10, this will search for other nodes that are either in
            the range -10 ports away or +10 ports away. Default value 3.
        serverThread    : Thread                - Indicate that we use server threads to communicate with other nodes
            Set to None for it to be distinct from all the other Nodes
        networkDiscoveryThread : Thread         - Thread that keep track of the reoccurring network discovery. Refer
            to chapter 4.3.2 in thesis. This is set to None for it to be distinct from all the other Nodes
        stopServerThread : bool                 - This signals the Node to stop the server listening for requests
            This is set to None for it to be distinct from all the other Nodes
        enableDiagnostics : bool                - Enables diagnostics in the terminal. Default True
        routing         : RoutingProtocols      - Determines which routing protocol should be used. Refer to the section
            3.5 in thesis.
        scanIntervalSec : int                   - Interval time in seconds the Nodes should scan for local netowrk again.
        persistNetworkDiscovery : bool          - Enables the reoccurring network discovery. Default True,
    """
    iden : str
    connections : List[Tuple[str, int]] = None
    serverIp : str
    serverPort : int
    hopLimit : int
    portStrength : int
    serverThread = None
    networkDiscoveryThread = None
    stopServerThread : bool = None
    enableDiagnostics : bool
    routing : RoutingProtocols
    scanIntervalSec : int

    def __init__(self, serverIp,
                 serverPort,
                 RoutingProtocol = RoutingProtocols.NONE,
                 portStrength = 3,
                 enableDiagnostics = True,
                 hopLimit = 3,
                 persistNetworkDiscovery = True,
                 scanIntervalSec = 20,
                ):

        if not len(fruitsvegs) == 0:
            random_fruit = random.choice(fruitsvegs)
            # prevents duplicates of fruit
            fruitsvegs.remove(random_fruit)
        else:
            random_fruit = "".join([chr(random.randint(65, 90)) for _ in range(4)])
        self.iden = random_fruit + "_" + "".join([chr(random.randint(65, 90)) for _ in range(8)]) # Create unique ID for node

        self.serverIp = serverIp
        self.serverPort = serverPort
        self.enableDiagnostics = enableDiagnostics
        self.portStrength = portStrength
        self.routing = RoutingProtocol
        self.hopLimit = hopLimit
        self.persistNetworkDiscovery = persistNetworkDiscovery
        if self.persistNetworkDiscovery:
            self.scanIntervalSec = scanIntervalSec

        # https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument
        # Contains connections in the form of tuples e.g. ('127.0.0.1', 60123) as a tuple<(str, int)>
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
            serverThread = Thread(group=None, target=self.startUDPServer, args=(ip, port), daemon=withDaemon)
            self.serverThread = serverThread
            self.serverThread.start()

    def reconNetwork(self, sockTimeout : int = 1, destIp = '', runAsThread=True, isRunningAsThread=False):
        """
            Will recon for other nodes in the vicinity for its self.portStrength self.connection
            this will mean that self.portStrength of 10, will search for every port from -10 to +10 (except itself)
            every port from the port strength will have its own thread, to speed up the network discovery.
            POSTCONDITION:
                - Will populate the self.connections with the Nodes in the vincinity.
                - Will populate the self.networkDiscoveryThread with the thread for the reoccurring network discovery
                - Will derive everything what tryPing function does as POSTCONDITION
            @param
                sockTimeout : int   -   The amount of time it should take for each port to timeout
                destIp      : str  (optional)  -   Destination IP for the tryPing function
                runAsThread : bool (optional)  -   If the recon should run as a thread.
                isRunningAsThread : bool (optional)  - implementation based parameter. If the function is already running
        """
        while True:

            # here because if the netowrking should persist, then we want to spawn a thread of this function
            # with a wait time, this will enable this function running continuasly, in fixed intervals
            reconThreads : list[Thread] = []
            # +1 because we skip our own port and we don't want our own port to count towards the strength
            for portScan in range(self.serverPort - self.portStrength, self.serverPort + self.portStrength+1):
                if (portScan == self.serverPort):
                    # If the port is the same as the node own port, skip
                    continue
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                client_socket.settimeout(sockTimeout)

                print(f'{self.diagnositcPrepend("reconNetwork()", "Starting recon as a thread")}')

                t = Thread(group=None, target=self.tryPing, args=(destIp, portScan, client_socket))
                reconThreads.append(t)


            for t in reconThreads:
                # Limit the amount of threads before starting new ones to prevent too many threads
                if int(active_count()) > 3500:
                    time.sleep(0.05)
                else:
                    t.start()


            if runAsThread and not isRunningAsThread and self.persistNetworkDiscovery:
                initTh = Thread(group=None, target=self.reconNetwork, kwargs={'isRunningAsThread' : True}, daemon=withDaemon)
                self.networkDiscoveryThread = initTh
                self.networkDiscoveryThread.start()
                return

            if self.persistNetworkDiscovery:
                time.sleep(self.scanIntervalSec)
            else:
                break

    def tryPing(self, destIp, destPort, sock):
        """
            Pings a specific destination ip & port on a specific socket. If a pong response is received
            the messeger will be added to this node's connections
            POSTCONDITIONS:
                - Will populate the self.connections with connections this Node can see
            @param
                destIp : str    - The destination Ip to ping
                destPort  : str - The destination port  to ping
                sock  : socket  - The given socket to send the message over
        """
        print(f'{self.diagnositcPrepend("reconNetwork()", f"Searching {destPort} for nodes")}')
        self.connections = []
        sock.sendto(b'ping', (destIp, destPort))
        self.increaseNetworkStats([DiagnosticStats.SENT_REQ, DiagnosticStats.TIME_LIST_REQ], diagnostic=True)

        server = None
        try:
            recData, server = sock.recvfrom(1024)
            self.increaseNetworkStats([DiagnosticStats.RECV_REQ], diagnostic=True)

            if (recData == b'pong'):
                with mutex:
                    print(self.diagnositcPrepend("reconNetwork() Node found!", f"server : {server} added!"))
                    if server not in self.connections:
                        self.connections.append(server)

        except socket.timeout:
            pass
        except ConnectionRefusedError:
            print(f'{self.diagnositcPrepend("tryPing() [EXCEPTION]", "CONNECTION REFUSED")}')
            self.increaseNetworkStats([DiagnosticStats.ERR_REQ], diagnostic=True)
        except RuntimeError:
            print(f'{self.diagnositcPrepend("tryPing() [EXCEPTION]", "CANNOT START NEW THREAD")}')
            self.increaseNetworkStats([DiagnosticStats.ERR_REQ], diagnostic=True)
        #except:
        #    print(f'{self.diagnositcPrepend("tryPing() [EXCEPTION]", "COULD NOT PROCESS REQUEST")}')
        #    self.increaseNetworkStats([DiagnosticStats.ERR_REQ], diagnostic=True)

    def nodeStatus(self):
        """
            prints the information about this node.
        """
        print(f'{self.diagnositcPrepend("NodeStatus()",f"Identification : {self.iden}\naddress : '{self.serverIp}':{self.serverPort}\nconnections : {self.connections}\nportStrength : {self.portStrength}")}')

    def sendData(self, data : bytes, destIp : str, destPort : int, requireACK=False, timeout=1.0):
        """
            Sends data in bytes to a destination ip and port
            @param
                data : bytes    -   Bytes of data that will get sent
                destIp : str    -   The destination IP
                destPort : int  -   The destination Port
                requireACK: bool-   when sending out a message, listen for an ACK
                timeout: int    -   The time it should take for the ACK to respond
        """
        print(f'{self.diagnositcPrepend("sendData()", f"Init message, sending to {destIp}, {destPort}")} with data : {self.bytesToStr(data)}')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if re.search(r"^ROUTE", data.decode("utf-8")):
            strData = data.decode("utf-8")
            _, rest_message = self.extractCommand(data)

            strData = strData.replace("ROUTE", f"ROUTE {self.hopLimit} ('{destIp}',{destPort})")
            data = strData.encode("utf-8")
            self.processRouteRequest(client_socket, data, (self.serverIp, self.serverPort))
        else:
            client_socket.sendto(data, (destIp, destPort)) ; self.increaseNetworkStats([DiagnosticStats.SENT_REQ, DiagnosticStats.TIME_LIST_REQ], diagnostic=True, time=time.time())
            print(f'{self.diagnositcPrepend("sendData(data, (destIp, destpPrt)))",
                  "Message sent!..")}:{self.bytesToStr(data)}')

            start = time.time()
            if requireACK:
                client_socket.settimeout(timeout)
                try:
                    recData, server = client_socket.recvfrom(1024)
                    self.increaseNetworkStats([DiagnosticStats.RECV_REQ], diagnostic=True)
                    end = time.time()
                    elapsed = end - start
                    print(f'{self.diagnositcPrepend("sendData()",
                          f"received ACK from {server}")}:{self.bytesToStr(recData)} {elapsed}')
                    if recData == b'ACK':
                        print("ACK Acknowlegded")
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
        print(f'{self.diagnositcPrepend("startUDPServer()", "")} Binding to \'{ip}\':{port}')
        server_socket.bind((ip, port))

        self.serverIp = ip
        self.serverPort = port
        self.listenForRequests(server_socket)

    def listenForRequests(self, sock, buffer = 1024):
        """
            listens for incomming traffic until self.stopServerThread is True
            @param
                sock : socket   -   the socket which the server listens to (is bound to this node's address)
                buffer : int    -   The buffer that the receiving message can hold
        """
        sock.settimeout(0.2)
        while True:
            try:
                if self.stopServerThread:
                    print(f'{self.diagnositcPrepend("listenForRequests()", "Server stopped from flag...")}')
                    break
                message, sender = sock.recvfrom(buffer) ; self.increaseNetworkStats([DiagnosticStats.RECV_REQ], diagnostic=True)
                print(f'{self.diagnositcPrepend("listenForRequests()", f"SERVER RECEIVED MESSAGE from {sender}")} : {self.bytesToStr(message)}')
                self.processRequest(sock, message, sender)
            except socket.timeout:
                pass

    def stopUDPServer(self, waitForJoin=True):
        """
            Stops the listenForRequests and cleans up the Threads.
            POSTCONDITION:
                - self.serverThread & self.networkDiscoveryThread = False
                - self.stopServerThread =  True
                - self.persistNetworkDiscovery = False
            @param
                waitForJoin : bool      -   Use the .join() function to wait for threads to finish
        """
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Stopping server...")
        self.stopServerThread = True
        self.persistNetworkDiscovery = False

        if waitForJoin and self.serverThread:
            self.serverThread.join()

        if waitForJoin and self.networkDiscoveryThread:
            self.networkDiscoveryThread.join()

        self.serverThread = None
        self.networkDiscoveryThread  = None
        print(f"{self.diagnositcPrepend("StopUDPServer()", "")} Server Stopped! ")

    def processRequest(self, sock, message : bytes, sender : Tuple[str, int], errMsg=""):
        """
            processes a request from another node
            @param
                sock : socket   -   The open socket which the request came from
                message : bytes -   The bytes that were tranferred to this node and needs to be processed
                sender : tuple(str, int) The sender the message came from
                errMsg  : str   -   OPTIONAL If any error message should be reported they are appended here.
        """
        # splitting up the message 
        cmd, rest_message = self.extractCommand(message)
        match cmd:
            case 'MSG':
                print(f'{self.diagnositcPrepend("processRequest() [MSG]", f"Message received! : {self.bytesToStr(message)}")} : from {sender}')
            case 'PING':
                print(f'{self.diagnositcPrepend("processRequest() [PING]", f"processing request {self.bytesToStr(message)}, responding back with pong...")}')
                sock.sendto(b'pong', sender)
            case 'ACK':
                print(f'{self.diagnositcPrepend("processRequest() [ACK]", f"processing request {self.bytesToStr(message)}, responding back with ACK...")}')
                sock.sendto(b'ACK', sender)
                self.processRequest(sock, rest_message, sender)
            case 'ERR':
                self.increaseNetworkStats([DiagnosticStats.ERR_REQ], diagnostic=True)
                print(f'{self.diagnositcPrepend("processRequest() [ERR]", f"COULD NOT PROCESS REQUEST {self.bytesToStr(message)} because {errMsg}")}')
            case 'ROUTE':
                hops, rest_message = self.extractCommand(rest_message)
                adr, rest_message = self.extractCommand(rest_message)
                print(f'{self.diagnositcPrepend("processRequest() [ROUTE]", f"Routing message request as {self.routing.name} of message {self.bytesToStr(message)}")}\n from {sender}, \n cmd : {cmd} \n hops : {hops} \n adr : {adr} \n network_hops total : {self.printNetworkStats()}')
                # Find anything in the format ('*',number<0, 65535>)
                match = re.search(r"^\('*',\d{0,65535}\)$", adr.strip())
                if match is None:
                    print(f'{self.diagnositcPrepend("processRequest()", f"Malformed request with {self.routing.name} of message {self.bytesToStr(message)}")} : from {sender} sending errMessage back')
                    # Do request again, but without the malformed request.
                    # prepend err flag and add an error message. Send it to 
                    rest_message = self.prependCommand(rest_message, "ERR")
                    self.processRequest(sock, rest_message, sender, errMsg="Malfored request")
                else:
                    # make the string into a tuple
                    requestedReceiver = tuple(adr.split(","))
                    requestedIp = requestedReceiver[0].replace('(', '').replace("'", '')
                    requestedPort = requestedReceiver[1].replace(')', '')

                    print(f'serverIp {self.serverIp} serverPort {self.serverPort}, reqRe {requestedIp} and {requestedPort}')
                    # If the receiver match, do not do anymore routing
                    if str(self.serverIp) == str(requestedIp) and str(self.serverPort) == str(requestedPort):
                        # stop and process the request
                        print(f'{self.diagnositcPrepend("processRequest()", "MESSAGE RECEIVED TO RIGHTFUL OWNER")} : req for {sender} with message {self.bytesToStr(message)}')
                        self.increaseNetworkStats([DiagnosticStats.ROUTE_RECV], diagnostic=True)
                        self.processRequest(sock, rest_message, sender)
                    else:
                        self.processRouteRequest(sock, message, sender)
            case _:
                pass


    def extractCommand(self, message : bytes) -> Tuple[str, bytes]:
        """
            Extract one header command from a bytes message
            @param
                message : bytes   -   the bytes message to be processed

            returns typle with (command, rest of the message)
        """
        cmd_list = message.decode("utf-8").split(" ")
        messageCmd = cmd_list[0].upper()
        rest_message = " ".join(cmd_list[1:]).encode("utf-8")
        return messageCmd, rest_message

    def prependCommand(self, message : bytes, tag : str) -> bytes:
        """
            prepend one header command to a bytes message
            @param
                message : bytes   -   the bytes message to be processed
                tag : str         -   the string to be prepended as a command

            returns command as bytes
        """
        cmd_list = message.decode("utf-8").split(" ")
        pmessage = list(reversed(cmd_list))
        pmessage.append(tag)
        pmessage = list(reversed(pmessage))
        returnMessage = " ".join(pmessage).encode("utf-8")
        return returnMessage

    def processRouteRequest(self, sock, message : bytes, sender : Tuple[str, int]):
        """
            processes a request that has to be routed/relayed.
            @param
                sock : socket   -   socket given from where request came from (in case of sending information back
                message : bytes -   the bytes (payload) of the requets
                sender : tuple(str,itn) -   sender (ip, port)
        """
        strMessage = message.decode("utf-8")
        err = None
        cmd, rest_message = self.extractCommand(message)
        hops, rest_message = self.extractCommand(rest_message)
        adr, rest_message = self.extractCommand(rest_message)
        print(f'{self.diagnositcPrepend("processRouteRequest()", f"Parsing request as {self.routing.name} of message {self.bytesToStr(message)}")} : from {sender}, \n cmd : {cmd} \n hops : {hops} \n adr : {adr}')
        # Look for the number of hops
        if not cmd == "ROUTE":
            print(f'{self.diagnositcPrepend("processRouteRequest()", "ROUTE does not exists in the query...")} : req for {sender} with message {self.bytesToStr(message)}')
            err = "ROUTE request could not be processed as it does not contain 'ROUTE'"
        elif not int(hops) > 0:
            print(f'{self.diagnositcPrepend("processRouteRequest()", "Hops limit reached!...")} : req for {sender} with message {self.bytesToStr(message)}')
            self.increaseNetworkStats([DiagnosticStats.HOPS_REACHED], diagnostic=True)
            err = "Hops limit reached"
        if err:
            errMessage = self.prependCommand(message, "ERR")
            self.processRequest(sock, errMessage, sender, err)
            return

        # After the hop subtract one from the total hopcount
        strHops = int(hops) - 1
        message = self.strToBytes(re.sub(r"^ROUTE [0-9]+", f"ROUTE {strHops}", strMessage))

        print(f'{self.diagnositcPrepend("processRouteRequest()", "processing the routing algorithms...")} : req for {sender} with message {self.bytesToStr(message)}')
        # NB: If the function sendData is used here instead of sendto, an infinite recursion will happen
        match self.routing:
            case RoutingProtocols.ISOLATION:
                print(RoutingProtocols.ISOLATION)
            case RoutingProtocols.CENTRALIZED:
                # Find central node
                # Send the request to the node
                print(RoutingProtocols.CENTRALIZED)
            case RoutingProtocols.DISTRIBUTED:
                # Make a calculation of the whole self.graph network
                # based on the self.graph and MST then make a decision on where to go
                print(RoutingProtocols.DISTRIBUTED)
            case RoutingProtocols.FLOODING:
                print(RoutingProtocols.FLOODING)
                for con in self.connections:
                    if not con[0] == sender[0] or not con[1] == sender[1]:
                        sock.sendto(message, (con[0], con[1])) ; self.increaseNetworkStats([DiagnosticStats.SENT_REQ], diagnostic=True)
                    else:
                        pass
            case RoutingProtocols.RANDOM_WALK:
                print(RoutingProtocols.RANDOM_WALK)
                if len(self.connections) != 0:
                    random_path = random.randint(0, len(self.connections)-1)
                    sock.sendto(message, (self.connections[random_path])) ; self.increaseNetworkStats([DiagnosticStats.SENT_REQ], diagnostic=True)
                else:
                    print(f'{self.diagnositcPrepend("processRouteRequest()", "self.connections contains no path to Random walk")}')
                    #errMessage = self.prependCommand(message, "ERR")
                    #errMessage = self.processRequest(sock, errMessage, sender, "self.connections contains no path to Random walk")

            case RoutingProtocols.NONE:
                print(RoutingProtocols.NONE)
            case _:
                print(RoutingProtocols.NONE)

    def strToBytes(self, s : str) -> bytes:
        return s.encode("utf-8")
    def bytesToStr(self, b : bytes) -> str:
        return b.decode("utf-8")

    def increaseNetworkStats(self, stats : List[DiagnosticStats], diagnostic=False):
        """
            Increase global counter of network information by a list of Network diagnostic stats.
            @param
                stats : List[DiagnosticStats]   -   Given list of DiagnosticStats enums to increase to the respective counter of stats
                (optional) diagnostic : bool    -   will print information about the network when a change has happened
        """
        global recv_network_requests
        global sent_network_requests
        global err_network_requests
        global time_network_list_requests
        global time_network_times_dic
        global route_recv_network_requests
        global hops_reached_network_requests
        with mutex:
            for stat in stats:
                match stat:
                    case DiagnosticStats.RECV_REQ:
                        recv_network_requests += 1
                    case DiagnosticStats.SENT_REQ:
                        sent_network_requests += 1
                    case DiagnosticStats.ERR_REQ:
                        err_network_requests += 1
                    case DiagnosticStats.ROUTE_RECV:
                        route_recv_network_requests += 1
                    case DiagnosticStats.HOPS_REACHED:
                        hops_reached_network_requests += 1
                    case DiagnosticStats.TIME_LIST_REQ:
                        pass
                    case DiagnosticStats.AVG_TIME_REQ_RECV:
                        pass
                    case _:
                        print("Unknown network stat! (don't) PANIC")


    def printNetworkStats(self):
        """
            Will print the Network status
        """
        global recv_network_requests
        global sent_network_requests
        global err_network_requests
        global hops_reached_network_requests
        global avg_time_network_requests
        global time_network_list_requests
        global route_recv_network_requests
        with mutex:
            print(f'''{self.diagnositcPrepend("printNetworkStats()", "")}
            {DiagnosticStats.RECV_REQ.name} : {recv_network_requests}
            {DiagnosticStats.SENT_REQ.name} : {sent_network_requests}
            {DiagnosticStats.ERR_REQ.name} : {err_network_requests}
            {DiagnosticStats.AVG_TIME_REQ_RECV.name} : {avg_time_network_requests}
            {DiagnosticStats.ROUTE_RECV.name} : {route_recv_network_requests}
            {DiagnosticStats.HOPS_REACHED.name} : {hops_reached_network_requests}
            {DiagnosticStats.TIME_LIST_REQ.name} : (len) {len(time_network_list_requests)}
            Threads count : {active_count()}
                   ''')

    def PopNetworkStats(self):
        """
            POSTCONDITION 
                - will return the current network status and delete the existing network data
            returns
                recv_network_requests,
                sent_network_requests,
                err_network_requests,
                avg_time_network_requests,
                time_network_list_requests,
                hops_reached_network_requests,
                route_recv_network_requests

        """
        global recv_network_requests
        global route_recv_network_requests
        global sent_network_requests
        global hops_reached_network_requests
        global err_network_requests
        global avg_time_network_requests
        global time_network_list_requests

        ret_pack = recv_network_requests, sent_network_requests, err_network_requests, avg_time_network_requests, time_network_list_requests, hops_reached_network_requests, route_recv_network_requests

        recv_network_requests = 0
        sent_network_requests = 0
        err_network_requests = 0
        avg_time_network_requests = 0
        time_network_list_requests = []
        route_recv_network_requests = 0
        hops_reached_network_requests = 0

        return ret_pack


if __name__ == '__main__':
    n = Node("", 65000, RoutingProtocols.RANDOM_WALK)
    m = Node("", 65003, RoutingProtocols.RANDOM_WALK)
    s = Node("", 65006, RoutingProtocols.RANDOM_WALK)
    network = []
    network.append(n)
    network.append(m)
    network.append(s)

    for node in network:
        node.reconNetwork()

    time.sleep(2)
    for node in network:
        node.nodeStatus()

    time.sleep(1)
    print(n) 
    print(s.serverPort)
    n.sendData(b'ROUTE MSG Hello world', '', s.serverPort)

else:
    print("Node library imported!")
    pass
