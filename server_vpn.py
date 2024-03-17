"""
CS433/533 - Dynamic VPN
by Darby Wright and Felix Golledge-Ostemeir

VPN Server - A peer in a p2p network.
Receives client connections, acts as a pseudo VPN server.
Further adaptions will include full VPN integration.

Inspired and adapted from https://github.com/AvinashAgarwal14/chatroom-p2p/blob/master/chat.py
"""

import socket
import threading
import time
from random import randint


my_port = -1
port_recieved = threading.Event()

class VPN:
    """A class representing a VPN Server.
    A peer in a p2p network. The VPN server communicates with other peers via a rendezvous server,
    and connects to VPN clients simulating a VPN server-client connection."""
    def __init__(self, address: str):
        print("'VPN Server' Started")
        self.rendezvous_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rendezvous_socket.connect((address, 10000))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Create a thread for updating peers about current connection conditions
        update_thread = threading.Thread(target=self.update_connections, args=(self.rendezvous_socket,))
        update_thread.daemon = True
        update_thread.start()

        # Thread for incomming client connections
        client_thread = threading.Thread(target=self.client_handler, args=(self.server_socket,))
        client_thread.daemon = True
        client_thread.start()

        while True:
            data = self.rendezvous_socket.recv(1024)
            if not data:
                break

            if data[0:1] == b'\x11':  # Indicator bit \x11 means the message is a peer update.
                self.update_peers(data[1:])

            if data[0:1] == b'\x12': # Indicator bit \x12 means the message is a listening port
                port = int(data[1:].decode())
                global my_port
                my_port = port
                port_recieved.set()
            else:
                continue
                # print(f"Data Received: {str(data, 'utf-8')}")

    def update_connections(self, sock: socket.socket):
        """Sends updates about current VPN server conditions. Currently, only simulates this through random number generation."""
        while True:
            # Every 5 seconds, randomly send a value representing current connection count to neighbors.
            # This is where in future work we will get information from VPN server process running on the
            # same machine about the number of client connections currently on the server.
            time.sleep(5)
            num_connections = randint(0, 20)
            message = b'\x12' + str(num_connections).encode('utf-8')
            sock.sendall(message)

    def update_peers(self, peerData: bytes):
        """Turns the byte peer data into dictionary format"""
        peerData = eval('{' + peerData.decode() + '}')
        p2p.peers = peerData

    def client_handler(self, server_socket: socket.socket):
        """Thread for receiving incoming client connections. Receives a listening port number from the rendezvous server,
        then waits for incoming client connections. When a client connection is received, it currently just waits and recvs data,
        then sends the client its peer list so the client can decide what to do next. In future implementations we plan to use
        this thread to validate clients"""
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rendezvous_socket.sendall(b'\x09') # Send byte '\x09' to rendezvous to request port number

        port_recieved.wait(timeout=10) # Wait until recieve listening port

        try:
            self.server_socket.bind(("0.0.0.0", my_port))
        except:
            print("Server failed to get a listening port")
            exit()

        self.server_socket.listen(1)
        while True:
            print("Waiting for incoming Client connection...")
            connection, address = self.server_socket.accept()
            print(f"...Accepted connection from {address}")
            
            while True:
                # constantly loop until no data is recieved, indicating the client disconnected
                data = connection.recv(1024)
                if not data:
                    print("Client Disconnected")
                    break
                
                connection.sendall(str(p2p.peers).encode('utf-8'))


class p2p:
    peers = {}


def main():
    VPN('127.0.0.1')


if __name__ == "__main__":
    main()
