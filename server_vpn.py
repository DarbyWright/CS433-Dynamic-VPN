import socket
import threading
import sys
import time
import json
from random import randint

# f = open("var.json", "r")  # Get port to listen on and update var for next server instance
# port = json.load(f)
# myport = port["port"]
# port["port"] += 1
# f = open("var.json", "w")
# json.dump(port, f)
# f.close()
myport = -1
portRecieved = threading.Event()

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
        cThread.start()

        while True:
            data = self.clientSocket.recv(1024)
            if not data:
                break

            if data[0:1] == b'\x11':  # Message was a peer update
                self.updatePeers(data[1:])
            if data[0:1] == b'\x12':
                #print(f"data: {data}")
                port = int(data[1:].decode())
                global myport
                myport = port
                portRecieved.set()
            else:
                print(f"Data Received: {str(data, 'utf-8')}")

    def sendMsg(self, lock: threading.Lock, sock: socket.socket):
        while True: # TODO SYNCRONIZE SENDING AMONST SERVERS
            time.sleep(5)
            num_connections = randint(0, 20)
            message = b'\x12' + str(num_connections).encode('utf-8')
            # print(f"sending message: {sock} has {num_connections} connections. Use port: {myport}")
            sock.sendall(message)

    def updatePeers(self, peerData):
        peerData = eval('{' + peerData.decode() + '}')
        p2p.peers2 = peerData

    def cliCon(self, lock: threading.Lock, serverSoc: socket.socket):
        serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # need to get listening port
        # serverSoc.bind(("0.0.0.0", myport))
        #serverSoc.listen(1)

        #self.clientSocket.sendall(b'\x09' + str(myport).encode('utf-8'))
        self.clientSocket.sendall(b'\x09') # request listening port
        #time.sleep(1)

        print(f"This is the port before waiting: {myport}")
        portRecieved.wait(timeout=10)
        print(f"This is the port after waiting: {myport}")
        try:
            serverSoc.bind(("0.0.0.0", myport))
        except:
            print("Server failed to get a listening port")
            exit() # need cleanup?
        serverSoc.listen(1)
        while True:
            print("Waiting for incoming Client connection...")
            connection, address = serverSoc.accept()
            print(f"...Client connection: {address} accepted")
            
            while True:
                data = connection.recv(1024)
                if not data:
                    print("Client Disconnected")
                    break
                
                print("Client Requesting Updated Peers")
                connection.sendall(str(p2p.peers2).encode('utf-8'))


class p2p:
    peers = []
    peers2 = {}


def main():
    client = VPN('127.0.0.1')


if __name__ == "__main__":
    main()
