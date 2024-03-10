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
                # print(str(data, 'utf-8'))
                print("Received Data")

    def sendMsg(self, lock: threading.Lock, sock: socket.socket):
        while True: # TODO SYNCRONIZE SENDING AMONST SERVERS
            time.sleep(10)
            num_connections = randint(0, 20)
            message = b'\x12'+ f"{sock} has {num_connections} connections. Use port: {myport}".encode('utf-8')
            sock.send(message)

    def updatePeers(self, peerData):
        p2p.peers = str(peerData, 'utf-8').split(",")[:-1]
        print(p2p.peers)

    def cliCon(self, lock: threading.Lock, serverSoc: socket.socket):
        serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSoc.bind(("0.0.0.0", myport))
        self.clientSocket.send(b'\x09' + str(myport).encode('utf-8'))

        serverSoc.listen(1)
        print("Waiting for incoming Client connection")
        connection, address = serverSoc.accept()
        try:
            data = connection.recv(1024)
        except Exception as e:
            print("The following error has occurred: ", e)
        while data:
            print(data.decode())
            # do stuff with data
            data = connection.recv(1024)
            time.sleep(10)
            pass
            # respond and/or get more data
        # TODO
        # Need to communicate the port the client should connect to
        # What should we do with client connection
        print("Connection closed")


class p2p:
    peers = []


def main():
    client = VPN('127.0.0.1')


if __name__ == "__main__":
    main()





