import socket
import threading
import sys
import time
from random import randint


class Client:
    def __init__(self, address: str):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((address, 10000))

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
        for peer in p2p.peers:
            client = Client(peer)
            print("Connected As Client")

if __name__ == "__main__":
    main()
