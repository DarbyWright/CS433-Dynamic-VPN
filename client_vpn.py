import socket
import threading
import time
import random
import tkinter as tk


class Client:
    def __init__(self, address: str, window: tk.Tk, option: int):
        if option == 0:
            window.textbox.insert(tk.END, f"Selected Low Connection Mode - Updates every 10 seconds\n")
        elif option == 1:
            window.textbox.insert(tk.END, f"Selected Random Mode - Updates every 10 seconds\n")
        self.servers_list: dict = {}
        self.current_best: tuple = None

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((address, 10000)) # connect to rendezvous
        window.textbox.insert(tk.END, f"Bootstrap - Connected to Rendezvous Server\n")
        self.clientSocket.sendall(b'\x10') # send byte to distinguish between client and vpn server

        data = self.clientSocket.recv(1024)
        # If the first recv is a peer update, wait for the second recv
        if data[0:1] == b'\x11':
            data = self.clientSocket.recv(1024)

        self.servers_list = eval(data.decode('utf-8'))
        self.current_best = self.determine_best_server()
        window.textbox.insert(tk.END, f"Bootstrap - Received Initial Peer List. Disconnecting From Rendezvous\n")
        self.clientSocket.close()
        
        while True:
            vpn_server_addr = (self.current_best[0][0], self.current_best[1][0])
            vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vpn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            vpn_socket.connect(vpn_server_addr)
            window.textbox.insert(tk.END, f"Connected to VPN Server: {vpn_server_addr}\n")

            if option == 0:
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
                while True:
                    time.sleep(10) # request updated servers list every 10 seconds
                    vpn_socket.sendall(b'\x10')
                    data = vpn_socket.recv(1024)
                    self.servers_list = eval(data.decode('utf-8'))

                    while True:
                        key, value = random.choice(list(self.servers_list.items()))
                        self.current_best = (key, value)
                        best_server_addr = (key[0], value[0])

                        if best_server_addr != vpn_socket.getpeername():
                            # print("Randomly Selected a New Server...")
                            window.textbox.insert(tk.END, f"Selecting a Random VPN Server...\n")
                            break
                    break

    
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
    def __init__(self):
        super().__init__()
        global HALT
        self.client_thread = None

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
            text="Low Connections",
            command=self.low_connections_pressed)
        self.low_connections_button.grid(
            row=1,
            column=0,
            padx=10,
            pady=10)

        self.random_button = tk.Button(
            self,
            text="Random Server",
            command=self.random_pressed)
        self.random_button.grid(
            row=1,
            column=1,
            padx=10,
            pady=10)
        
        # self.reset_button = tk.Button(
        #     self,
        #     text="Reset",
        #     command=self.reset_pressed)
        # self.reset_button.grid(
        #     row=1,
        #     column=2,
        #     padx=10,
        #     pady=10)

    def low_connections_pressed(self):
        self.client_thread = threading.Thread(target=low_conn_client, args=(self,))
        self.client_thread.start()

    def random_pressed(self):
        client_thread = threading.Thread(target=random_client, args=(self,))
        client_thread.start()

    def reset_pressed(self):
        print("Reset Pressed")
        HALT = True


def low_conn_client(window: tk.Tk):
    client = Client('127.0.0.1', window, 0)

def random_client(window: tk.Tk):
    client = Client('127.0.0.1', window, 1)

if __name__ == "__main__":
    # main()
    app = App()
    app.mainloop()
