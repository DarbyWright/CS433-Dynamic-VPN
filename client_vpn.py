import socket
import threading
import time
import random
import tkinter as tk


class Client:
    def __init__(self, address: str, window: tk.Tk, option: int):
        self.servers_list: dict = {}
        self.current_best: tuple = None

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((address, 10000)) # connect to rendezvous
        self.clientSocket.sendall(b'\x10') # send byte to distinguish between client and vpn server

        data = self.clientSocket.recv(1024)
        # If the first recv is a peer update, wait for the second recv
        if data[0:1] == b'\x11':
            data = self.clientSocket.recv(1024)

        self.servers_list = eval(data.decode('utf-8'))
        self.current_best = self.determine_best_server()
        print(f"Received Response From Server: {self.servers_list}. Disconnecting from Rendezvous")
        window.textbox.insert(tk.END, f"Received Response From Server: {self.servers_list}. Disconnecting from Rendezvous.\n")
        self.clientSocket.close()

        
        while True:
            print(f"Best VPN Server Available: {self.current_best}")
            vpn_server_addr = (self.current_best[0][0], self.current_best[1][0])
            vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vpn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            vpn_socket.connect(vpn_server_addr)
            print(f"Connected to VPN Server: {self.current_best}")
            window.textbox.insert(tk.END, f"Connected to VPN Server: {self.current_best}\n")

            if option == 0:
                print("OPTION 0")
                while True:
                    time.sleep(10)
                    vpn_socket.sendall(b'\x10')
                    data = vpn_socket.recv(1024)
                    self.servers_list = eval(data.decode('utf-8'))
                    self.current_best = self.determine_best_server()
                    best_server_addr = (self.current_best[0][0], self.current_best[1][0])
                    if best_server_addr == vpn_socket.getpeername():
                        print("Best Server is the Current Server...")
                        window.textbox.insert(tk.END, f"Best Server is the Current Server...\n")
                    else:
                        print("Changing Servers...")
                        window.textbox.insert(tk.END, f"Changing Servers...\n")
                        break

            if option == 1:
                print("OPTION 1")
                while True:
                    time.sleep(10)
                    vpn_socket.sendall(b'\x10')
                    data = vpn_socket.recv(1024)
                    self.servers_list = eval(data.decode('utf-8'))
                    key, value = random.choice(list(self.servers_list.items()))
                    self.current_best = (key, value)
                    best_server_addr = (key[0], value[0])

                    if best_server_addr == vpn_socket.getpeername():
                        print("Randomly Selected the Current Server...")
                        window.textbox.insert(tk.END, f"Randomly Selected the Current Server\n")
                    else:
                        print("Randomly Selected a New Server...")
                        window.textbox.insert(tk.END, f"Randomly Selected a New Server\n")
                        break

    
    def handler(self):
        return
    
    def determine_best_server(self) -> tuple[str, list]:
        best_option = None
        for key, value in self.servers_list.items():
            if not best_option:
                best_option = (key, value)
            elif best_option[1][1] > value[1]:
                best_option = (key, value)
        return best_option


class Servers:
    neighbors: dict[tuple: list] = {}


class App(tk.Tk):
    client_thread = None
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("VPN Client")
        self.geometry(f"{600}x{500}")

        # Give weight to window container - allows for better window size adjustment
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = tk.Text(
            self,
            wrap="word")
        self.textbox.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="news")

        self.low_connections_button = tk.Button(
            self,
            text="Connect to Server with Lowest Number of Connections",
            command=self.low_connections_pressed)
        self.low_connections_button.grid(
            row=1,
            column=0,
            padx=10,
            pady=10)

        self.random_button = tk.Button(
            self,
            text="Connect to Random Server",
            command=self.random_pressed)
        self.random_button.grid(
            row=1,
            column=1,
            padx=10,
            pady=10)

    def low_connections_pressed(self):
        client_thread = threading.Thread(target=main, args=(self, 0))
        client_thread.start()

    def random_pressed(self):
        client_thread = threading.Thread(target=main, args=(self, 1))
        client_thread.start()


def main(window: tk.Tk, option: int):
    client = Client('127.0.0.1', window, option)

if __name__ == "__main__":
    # main()
    app = App()
    app.mainloop()
