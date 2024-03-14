import socket
import threading
import time
from random import randint


my_port = -1
port_recieved = threading.Event()

class VPN:
    def __init__(self, address: str):
        print("'VPN Server' Started")
        self.rendezvous_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rendezvous_socket.connect((address, 10000))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        update_thread = threading.Thread(target=self.update_connections, args=(self.rendezvous_socket,))
        update_thread.daemon = True
        update_thread.start()

        client_thread = threading.Thread(target=self.client_handler, args=(self.server_socket,))
        client_thread.daemon = True
        client_thread.start()

        while True:
            data = self.rendezvous_socket.recv(1024)
            if not data:
                break

            if data[0:1] == b'\x11':  # Message was a peer update
                self.update_peers(data[1:])

            if data[0:1] == b'\x12': #
                port = int(data[1:].decode())
                global my_port
                my_port = port
                port_recieved.set()
            else:
                continue
                # print(f"Data Received: {str(data, 'utf-8')}")

    def update_connections(self, sock: socket.socket):
        while True: # TODO SYNCRONIZE SENDING AMONST SERVERS?
            time.sleep(5)
            num_connections = randint(0, 20)
            message = b'\x12' + str(num_connections).encode('utf-8')
            sock.sendall(message)

    def update_peers(self, peerData):
        peerData = eval('{' + peerData.decode() + '}')
        p2p.peers = peerData

    def client_handler(self, server_socket: socket.socket):
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rendezvous_socket.sendall(b'\x09') # request listening port

        # print(f"This is the port before waiting: {my_port}")
        port_recieved.wait(timeout=10)
        # print(f"This is the port after waiting: {my_port}")

        try:
            self.server_socket.bind(("0.0.0.0", my_port))
        except:
            print("Server failed to get a listening port")
            exit() # need cleanup?

        self.server_socket.listen(1)
        while True:
            print("Waiting for incoming Client connection...")
            connection, address = self.server_socket.accept()
            print(f"...Accepted connection from {address}")
            
            while True:
                data = connection.recv(1024)
                if not data:
                    print("Client Disconnected")
                    break
                
                print("Client requesting peer update")
                connection.sendall(str(p2p.peers).encode('utf-8'))


class p2p:
    peers = {}


def main():
    VPN('127.0.0.1')


if __name__ == "__main__":
    main()
