import socket
import threading
import sys
import time
from random import randint


class Server:
    connections: list[socket.socket] = []
    peers: list[str] = []
    peers2: dict[tuple: list] = {}

    def __init__(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(("0.0.0.0", 10000))
        serverSocket.listen(1)
        print("Server Running...")

        while True:
            connection, address = serverSocket.accept()

            lock = threading.Lock()
            cThread = threading.Thread(target=self.handler, args=(lock, connection, address))
            cThread.daemon = True
            cThread.start()

            self.connections.append(connection)
            # self.peers.append(f"{address[0]}:{address[1]}")
            self.peers2[address] = []

            print(f"{str(address[0])}:{str(address[1])} connected")
            #self.sendPeers() # moved to after listening_port added ~ line 45

    def handler(self, lock: threading.Lock, clientSocket: socket.socket, local_addr: tuple):
        while True:
            data = clientSocket.recv(1024)

            if data[0:1] == b'\x09': # VPN server listening thread
                with lock:
                    listening_port = data[1:].decode('utf-8')
                    print(f"Server {local_addr} listening on port {listening_port}")
                    remote_addr = clientSocket.getpeername()
                    self.peers2[remote_addr].append(listening_port)
                    self.sendPeers()

                    #self.peers.remove(f"{remote_addr[0]}:{remote_addr[1]}")
                    #self.peers.append(f"{remote_addr[0]}:{remote_addr[1]}:{listening_port}")
                    continue
                    
            elif data[0:1] == b'\x10': # VPN client
                print("Client Connected")
                with lock:
                    del self.peers2[local_addr]

                    #self.peers.remove(f"{local_addr[0]}:{local_addr[1]}")
                    self.connections.remove(clientSocket)
                    self.sendPeers()

                    #TODO REVISE TO SEND PEERS2



                    clientSocket.sendall(self.peers[0].encode('utf-8'))

                    continue

                    #for peer in self.peers:
                    #    clientSocket.sendall(str(peer).encode('utf-8'))
                    for peer in self.peers2:
                        clientSocket.sendall(str(peer).encode('utf-8'))
                    #break

                    for connection in self.connections:
                        connection.sendall(data)

            elif data[0:1] == b'\x12':
                with lock:
                    numCon = int(data[1:].decode().strip())
                    if len(self.peers2[local_addr])==1:
                        self.peers2[local_addr].append(numCon)
                    else:
                        self.peers2[local_addr].pop(-1)
                        self.peers2[local_addr].append(numCon)
                    self.sendPeers()

            if not data:
                with lock:
                    print(f"{str(local_addr[0])}:{str(local_addr[1])} disconnected")
                    if clientSocket in self.connections:
                        self.connections.remove(clientSocket)
                    # if f"{local_addr[0]}:{local_addr[1]}" in self.peers:
                    #   self.peers.remove(f"{local_addr[0]}:{local_addr[1]}")
                    if (local_addr[0], local_addr[1]) in self.peers2:
                        del self.peers2[local_addr]
                    clientSocket.close()
                    self.sendPeers()
                    break

    def sendPeers(self):
        #print(self.peers2)
        #print(' peers\n\n')
        #peerString = ""
        peer2String = ""
        #for peer in self.peers:
        #   peerString += f"{peer},"
        for peer1 in self.peers2:
            peer2String += f"{peer1}: {self.peers2[peer1]}, "

        for connection in self.connections:
            # connection.sendall(b'\x11' + bytes(peerString, 'utf-8'))
            connection.sendall(b'\x11' + bytes(peer2String, 'utf-8'))
        #print("\n\n\npeer2String: " + peer2String)
        #print("peerString: "+ peerString)


def main():
    server = Server()


if __name__ == "__main__":
    main()