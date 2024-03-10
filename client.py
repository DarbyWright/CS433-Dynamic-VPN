import socket
import threading
import sys
import time
import json
from random import randint

class Client:
    def __init__(self, address: str):
        print("connected to client.py")
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((address, 10000))
        serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        iThread = threading.Thread(target=self.sendMsg, args=(clientSocket,))
        iThread.daemon = True
        iThread.start()

        cThread = threading.Thread(target=self.cliCon, args=(serverSoc,))
        cThread.start() # daemon thread here?

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

    def cliCon(self, serverSoc: socket.socket):
	    
        serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
        f = open("var.json", "r")
        port = json.load(f)
        myport = port["port"]
        port["port"] += 1
        f = open("var.json", "w")
        json.dump(port,f)
        f.close()
        
        serverSoc.bind(("0.0.0.0", myport))
        serverSoc.listen(1)
        print("Waiting for incoming Client connection")
        connection, address = serverSoc.accept()
        data = serverSoc.recv(1024)
        while data:
            print(data.decode())
	        # do stuff with data
            pass
            #respond and/or get more data
        # Need to communicate the port the client should connect to
        # What should we do with client connection
	    

class p2p:
    peers = ['127.0.0.1']


def main():
    while True:
        for peer in p2p.peers:
            client = Client(peer)
            print("Connected As Client")

if __name__ == "__main__":
    main()
