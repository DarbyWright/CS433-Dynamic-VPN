"""
CS433/533 - Dynamic VPN
by Darby Wright and Felix Golledge-Ostemeir

Rendezvous Server - Connect VPN Server peers

Inspired and adapted from https://github.com/AvinashAgarwal14/chatroom-p2p/blob/master/chat.py
JSON file use inspired and adapted from https://stackoverflow.com/questions/63113747/python-is-there-a-way-to-permanently-change-a-variable-from-another-python-file
"""

import socket
import threading
import json


class Server:
    """A class representing a redezvous server. Receives connections via TCP and relays VPN server IP and port information."""
    connections: list[socket.socket] = []
    peers: dict[tuple: list] = {}

    def __init__(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", 10000))
        server_socket.listen(1)
        print("Rendezvous Server Running")

        while True:
            # When a connection is received, we start a new thread and add the connection to the peer and connection lists
            connection, address = server_socket.accept()

            lock = threading.Lock()
            handler_thread = threading.Thread(target=self.handler, args=(lock, connection, address))
            handler_thread.daemon = True
            handler_thread.start()

            self.connections.append(connection)
            self.peers[address] = []


    def handler(self, lock: threading.Lock, client_socket: socket.socket, local_addr: tuple):
        """Handles incomcing vpn server or client peer connections. Is responsible for assigning port numbers
        to vpn servers and updates their peer lists when new vpn servers join. When a vpn client connects,
        it send the list of peers, then the client disconnects.
        
        Input:
            lock: lock for connections and peers lists
            client_socket: a TCP socket connected to either a vpn server or vpn client
            local_addr: the IP and port info associated with the client_socket
            """
        while True:
            data = client_socket.recv(1024)

            if data[0:1] == b'\x09': # Indicator bit \x09 means the message is a VPN server requesting a listening port.
                with lock:
                    f = open("var.json", "r")  # Get port to listen on and update var for next server instance
                    port = json.load(f)
                    myport = port["port"]
                    port["port"] += 1
                    f = open("var.json", "w")
                    json.dump(port, f)
                    f.close()

                    try:
                        # Send VPN server its listening port, adding an indicator bit '\x12' at the beginning
                        client_socket.sendall(b'\x12' + str(myport).encode())
                    except:
                        print("Failed to Send Message")

                    print(f"Server {local_addr} listening on port {myport}")
                    remote_addr = client_socket.getpeername()
                    self.peers[remote_addr].append(myport)
                    self.send_peers()
                    continue
                    
            elif data[0:1] == b'\x10': # Indicator bit \x10 means connection is a VPN client.
                # print("Client Connected")
                with lock:
                    del self.peers[local_addr] # Client is not considered a peer and no longer needs anything from rendezvous
                    self.connections.remove(client_socket)
                    self.send_peers()
                    client_socket.sendall(str(self.peers).encode('utf-8'))
                    continue

            elif data[0:1] == b'\x12': # Indicator bit \x12 means the message is a VPN server updating its current connection count.
                with lock:
                    num_connections = int(data[1:].decode().strip())
                    if len(self.peers[local_addr])==1:
                        self.peers[local_addr].append(num_connections)
                    else:
                        self.peers[local_addr].pop(-1)
                        self.peers[local_addr].append(num_connections)
                    self.send_peers()

            if not data: # If a server disconnects, update peers dict and connections list and close the socket
                with lock:
                    if client_socket in self.connections:
                        self.connections.remove(client_socket)

                    if (local_addr[0], local_addr[1]) in self.peers:
                        del self.peers[local_addr]
                        
                    client_socket.close()
                    self.send_peers()
                    break

    def send_peers(self):
        """Converts Peer dictionary to a string representation and sends to all VPN server peers."""
        peer_string = ""
        for peer1 in self.peers:
            peer_string += f"{peer1}: {self.peers[peer1]}, "

        for connection in self.connections:
            connection.sendall(b'\x11' + bytes(peer_string, 'utf-8')) # Add indicator bit '\x11 to indicate a peer update


def main():
    Server()


if __name__ == "__main__":
    main()