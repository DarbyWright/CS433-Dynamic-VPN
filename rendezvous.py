import socket
import threading
import sys
import time
from random import randint


class Server:
    connections: list[socket.socket] = []
    cCon: list[tuple] = []
    peers2: dict[tuple: list] = {}
    peers: list[str] = []

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

            print(f"{str(address)} connected")
            self.sendPeers()

    def handler(self, lock: threading.Lock, clientSocket: socket.socket, local_addr: tuple):
        while True:
            data = clientSocket.recv(1024)

            if data[0:1] == b'\x09':
                with lock:
                    listening_port = data[1:].decode('utf-8')
                    print(f"Server {local_addr} listening on port {listening_port}")
                    remote_addr = clientSocket.getpeername()
                    # self.peers.remove(f"{remote_addr[0]}:{remote_addr[1]}")
                    # del self.peers2[remote_addr]
                    # self.peers.append(f"{remote_addr[0]}:{remote_addr[1]}:{listening_port}")
                    self.peers2[remote_addr].append(listening_port)

            if data[0:1] == b'\x10':
                print("Client Connected")
                with lock:
                    del self.peers2[local_addr]
                    self.connections.remove(clientSocket)

            if data[0:1] == b'\x12':
                numCon = int(data[1:].decode())

                remote_addr = clientSocket.getpeername()
                # self.peers.remove(f"{remote_addr[0]}:{remote_addr[1]}:{listening_port}")
                self.peers2[remote_addr].append(numCon)

                #print(data[1:].decode())
                #print(numCon)
                #TODO HOW DO WE STORE CLIENT DATA 

                for peer in self.peers2:
                    clientSocket.send(str(peer).encode('utf-8'))

                #TODO Send Appropriate VPN server information
                self.connections.remove(clientSocket)
                break

            
            for connection in self.connections:
                connection.sendall(data)

            if not data:
                with lock:
                    print(f"{str(local_addr[0])}:{str(local_addr[1])} disconnected")
                    self.connections.remove(clientSocket)
                    self.peers.remove(f"{local_addr[0]}:{local_addr[1]}")
                    clientSocket.close()
                    self.sendPeers()
                    break

    def sendPeers(self):
        print("SEND")
        peerString = ""
        for peer in self.peers:
            print("1111111")
            print(peer)
            peerString += f"{peer},"
        
        for connection in self.connections:
            connection.sendall(b'\x11' + bytes(peerString, 'utf-8'))


def main():
    server = Server()

if __name__ == "__main__":
    main()
