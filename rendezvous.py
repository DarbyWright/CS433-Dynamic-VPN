import socket
import threading
import json



class Server:
    connections: list[socket.socket] = []
    peers: dict[tuple: list] = {}
    best_peer: str = ""

    def __init__(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", 10000))
        server_socket.listen(1)
        print("Rendezvous Server Running...")

        while True:
            connection, address = server_socket.accept()

            lock = threading.Lock()
            handler_thread = threading.Thread(target=self.handler, args=(lock, connection, address))
            handler_thread.daemon = True
            handler_thread.start()

            self.connections.append(connection)
            self.peers[address] = []


    def handler(self, lock: threading.Lock, client_socket: socket.socket, local_addr: tuple):
        while True:
            data = client_socket.recv(1024)

            if data[0:1] == b'\x09': # VPN server listening thread
                with lock:
                    f = open("var.json", "r")  # Get port to listen on and update var for next server instance
                    port = json.load(f)
                    myport = port["port"]
                    port["port"] += 1
                    f = open("var.json", "w")
                    json.dump(port, f)
                    f.close()

                    try:
                        client_socket.sendall(b'\x12' + str(myport).encode())
                    except:
                        print("FAIL")

                    print(f"Server {local_addr} listening on port {myport}")
                    remote_addr = client_socket.getpeername()
                    self.peers[remote_addr].append(myport)
                    self.send_peers()
                    continue
                    
            elif data[0:1] == b'\x10': # VPN client
                # print("Client Connected")
                with lock:
                    del self.peers[local_addr]
                    self.connections.remove(client_socket)
                    self.send_peers()
                    self.update_best_peer()
                    client_socket.sendall(str(self.peers).encode('utf-8'))
                    continue

            elif data[0:1] == b'\x12':
                with lock:
                    num_connections = int(data[1:].decode().strip())
                    if len(self.peers[local_addr])==1:
                        self.peers[local_addr].append(num_connections)
                    else:
                        self.peers[local_addr].pop(-1)
                        self.peers[local_addr].append(num_connections)
                    self.send_peers()
                    self.update_best_peer()

            if not data:
                with lock:
                    if client_socket in self.connections:
                        self.connections.remove(client_socket)

                    if (local_addr[0], local_addr[1]) in self.peers:
                        del self.peers[local_addr]
                        
                    client_socket.close()
                    self.send_peers()
                    self.update_best_peer()
                    break

    def send_peers(self):
        peer_string = ""
        for peer1 in self.peers:
            peer_string += f"{peer1}: {self.peers[peer1]}, "

        for connection in self.connections:
            connection.sendall(b'\x11' + bytes(peer_string, 'utf-8'))

    def update_best_peer(self):
        best_option = None
        for key, value in self.peers.items():
            if len(value) < 2:
                continue

            if not best_option or value[1] < best_option:
                best_option = value[1]
                self.best_peer += f"{key}{value}"


def main():
    server = Server()


if __name__ == "__main__":
    main()