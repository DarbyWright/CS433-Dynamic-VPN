import socket
import threading
import sys
import time
from random import randint


class Server:
    connections: list[socket.socket] = []
    peers: list[str] = []

    def __init__(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(("0.0.0.0", 10000))
        serverSocket.listen(1)
        print("Server Running...")

        while True:
            connection, address = serverSocket.accept()
            cThread = threading.Thread(target=self.handler, args=(connection, address))
            cThread.daemon = True
            cThread.start()

            self.connections.append(connection)
            self.peers.append(address[0])
            print(f"{str(address[0])}:{str(address[1])} connected")
            self.sendPeers()

    def handler(self, clientSocket: socket.socket, addr: tuple):
        while True:
            data = clientSocket.recv(1024)
            for connection in self.connections:
                connection.send(data)

            if not data:
                print(f"{str(addr[0])}:{str(addr[1])} disconnected")
                self.connections.remove(clientSocket)
                self.peers.remove(addr[0])
                clientSocket.close()
                self.sendPeers()
                break

    def sendPeers(self):
        peerString = ""
        for peer in self.peers:
            peerString = peerString + peer + ","
        
        for connection in self.connections:
            connection.send(b'\x11' + bytes(peerString, 'utf-8'))

class p2p:
    peers = ['127.0.0.1']


def main():
    while True:
        server = Server()
        print("Connected As Server")

if __name__ == "__main__":
    main()
