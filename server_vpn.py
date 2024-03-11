import socket
import threading
import sys
import time
import json
from random import randint

f = open("var.json", "r")  # Get port to listen on and update var for next server instance
port = json.load(f)
myport = port["port"]
port["port"] += 1
f = open("var.json", "w")
json.dump(port, f)
f.close()


class VPN:
    def __init__(self, address: str):
        print("Starting the 'VPN' Server - Connecting to Rendezvous")
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((address, 10000))
        serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        lock = threading.Lock()
        iThread = threading.Thread(target=self.sendMsg, args=(lock, self.clientSocket))
        iThread.daemon = True
        iThread.start()

        cThread = threading.Thread(target=self.cliCon, args=(lock, serverSoc,))
        cThread.daemon = True
        cThread.start()  # daemon thread here?

        while True:
            data = self.clientSocket.recv(1024)
            if not data:
                break

            if data[0:1] == b'\x11':  # Message was a peer update
                self.updatePeers(data[1:])
            else:
                print(f"Data Received: {str(data, 'utf-8')}")

    def sendMsg(self, lock: threading.Lock, sock: socket.socket):
        while True: # TODO SYNCRONIZE SENDING AMONST SERVERS
            time.sleep(10)
            num_connections = randint(0, 20)
            message = b'\x12' + str(num_connections).encode('utf-8')
            print(f"sending message: {sock} has {num_connections} connections. Use port: {myport}")
            sock.sendall(message)

    def updatePeers(self, peerData):
        peerData = eval('{' + peerData.decode() + '}')
        #p2p.peers = str(peerData, 'utf-8').split(",")[:-1]
        p2p.peers2 = peerData
        print(f"Peers updated: {p2p.peers2}")

    def cliCon(self, lock: threading.Lock, serverSoc: socket.socket):
        serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSoc.bind(("0.0.0.0", myport))
        serverSoc.listen(1)

        self.clientSocket.sendall(b'\x09' + str(myport).encode('utf-8'))
        while True:
            print("Waiting for incoming Client connection...")
            connection, address = serverSoc.accept()
            print(f"...Client connection: {address} accepted")
            while True:
                data = connection.recv(1024)
                if not data:
                    print("Client Disconnected")
                    break
                
                print(f"Data From Client: {data.decode('utf-8')}")
            # try:
            #     data = connection.recv(1024)
            #     print(f"Received: {data.decode('utf8')}")
            # except Exception as e:
            #     print("The following error has occurred: ", e)
            # while data:
            #     print(data.decode())
            #     # do stuff with data
            #     data = connection.recv(1024)
            #     time.sleep(10)
            #     pass
                # respond and/or get more data
            # TODO
            # Need to communicate the port the client should connect to
            # What should we do with client connection
            print("Connection closed")


class p2p:
    peers = []
    peers2 = {}


def main():
    client = VPN('127.0.0.1')


if __name__ == "__main__":
    main()
