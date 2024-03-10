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

            lock = threading.Lock()
            cThread = threading.Thread(target=self.handler, args=(lock, connection, address))
            cThread.daemon = True
            cThread.start()

            self.connections.append(connection)
            self.peers.append(address)

            print(f"{str(address[0])}:{str(address[1])} connected")
            self.sendPeers()

    def handler(self, lock: threading.Lock, clientSocket: socket.socket, addr: tuple):
        while True:
            data = clientSocket.recv(1024)

            if data[0:1] == b'\x09':
                print(f"RECEIVED PORT NUMBER: {data[1:]}")

            if data[0:1] == b'\x10':
                print("Client Connected")
                self.peers.remove(addr)

                print(self.peers)
                
                for peer in self.peers:
                    clientSocket.send(str(peer).encode('utf-8'))
                #TODO Send Appropriate VPN server information
                self.connections.remove(clientSocket)
                break

            for connection in self.connections:
                connection.send(data)

            if not data:
                print(f"{str(addr[0])}:{str(addr[1])} disconnected")
                self.connections.remove(clientSocket)
                self.peers.remove(addr)
                clientSocket.close()
                self.sendPeers()
                break


    def sendPeers(self):
        peerString = ""
        for peer in self.peers:
            peerString += f"{peer},"#peerString + peer + ","
        
        for connection in self.connections:
            connection.send(b'\x11' + bytes(peerString, 'utf-8'))


def main():
    server = Server()

if __name__ == "__main__":
    main()
