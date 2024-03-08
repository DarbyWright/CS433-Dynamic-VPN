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
        serverSocket.bind(("0.0.0.0", 55550))
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


class Client:
    def __init__(self, address: str):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((address, 55550))

        iThread = threading.Thread(target=self.sendMsg, args=(clientSocket,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            
            if data[0:1] == b'\x11': # Message was a peer update
                self.updatePeers(data[1:])
            else:
                print(str(data, 'utf-8'))


    def sendMsg(self, sock: socket.socket):
        while True:
            time.sleep(10)
            num_connections = randint(0, 20)
            message = f"{sock} has {num_connections} connections".encode('utf-8')
            sock.send(message)

            # sock.send(bytes(input(""), 'utf-8'))

    def updatePeers(self, peerData):
        p2p.peers = str(peerData, 'utf-8').split(",")[:-1]
        print(p2p.peers)


class p2p:
    peers = ['127.0.0.1']


def main():
    while True:
        try:
            print("Trying to connect...")
            time.sleep(randint(1, 5))

            for peer in p2p.peers:
                try:
                    client = Client(peer)
                    print("Connected As Client")
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    pass

                try:
                    server = Server()
                    print("Connected As Server")
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldn't start the server...")

        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()
