import socket
import threading
import sys
import time
from random import randint


class Server:
    connections: list[socket.socket] = []
    peers: list[str] = []
    peers2: dict[tuple: list] = {}
    bestPeer: str = ""

    def __init__(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(("0.0.0.0", 10000))
        serverSocket.listen(1)
        print("Rendezvous Server Running...")

        while True:
            connection, address = serverSocket.accept()

            lock = threading.Lock()
            cThread = threading.Thread(target=self.handler, args=(lock, connection, address))
            cThread.daemon = True
            cThread.start()

            self.connections.append(connection)
            self.peers2[address] = []

            # print(f"{str(address[0])}:{str(address[1])} connected")
            #self.sendPeers() # moved to after listening_port added ~ line 45

    def handler(self, lock: threading.Lock, clientSocket: socket.socket, local_addr: tuple):
        while True:
            data = clientSocket.recv(1024)

            if data[0:1] == b'\x09': # VPN server listening thread
                with lock:
                    listening_port = int(data[1:].decode('utf-8'))
                    print(f"VPN Server ({local_addr[0]}, {listening_port} is accepting connections")
                    remote_addr = clientSocket.getpeername()
                    self.peers2[remote_addr].append(listening_port)
                    self.sendPeers()
                    continue
                    
            elif data[0:1] == b'\x10': # VPN client
                print("Client Connected")
                with lock:
                    del self.peers2[local_addr]
                    self.connections.remove(clientSocket)
                    self.sendPeers()
                    self.updateBestpeer()
                    clientSocket.sendall(str(self.peers2).encode('utf-8'))
                    continue

            elif data[0:1] == b'\x12':
                with lock:
                    numCon = int(data[1:].decode().strip())
                    if len(self.peers2[local_addr])==1:
                        self.peers2[local_addr].append(numCon)
                    else:
                        self.peers2[local_addr].pop(-1)
                        self.peers2[local_addr].append(numCon)
                    self.sendPeers()
                    self.updateBestpeer()

            if not data:
                with lock:
                    # print(f"{str(local_addr[0])}:{str(local_addr[1])} disconnected")
                    if clientSocket in self.connections:
                        self.connections.remove(clientSocket)
                    # if f"{local_addr[0]}:{local_addr[1]}" in self.peers:
                    #   self.peers.remove(f"{local_addr[0]}:{local_addr[1]}")
                    if (local_addr[0], local_addr[1]) in self.peers2:
                        del self.peers2[local_addr]
                    clientSocket.close()
                    self.sendPeers()
                    self.updateBestpeer()
                    break

    def sendPeers(self):
        peer2String = ""
        for peer1 in self.peers2:
            peer2String += f"{peer1}: {self.peers2[peer1]}, "

        for connection in self.connections:
            connection.sendall(b'\x11' + bytes(peer2String, 'utf-8'))

    def updateBestpeer(self):
        best = 100000000
        for peer in self.peers2:
            if len(self.peers2[peer]) > 1:
                if (((self.peers2[peer])[1]) < best):
                    best = (self.peers2[peer])[1]
                    self.bestPeer = ""
                    self.bestPeer += str(peer)
                    self.bestPeer += str(self.peers2[peer])

        # print(f"Best peer: {self.bestPeer}")

def main():
    server = Server()


if __name__ == "__main__":
    main()