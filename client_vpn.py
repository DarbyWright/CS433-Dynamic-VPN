"""
CS433/533 - Dynamic VPN
by Darby Wright and Felix Golledge-Ostemeir

VPN Client - Recieves basic config settings from user.
Connects to 'VPN Servers' based on config settings.

This is our original work
"""

import socket
import threading
import time
import random
import tkinter as tk


class Client:
    """A class representing a VPN Client. Connects to a rendezvous server via a TCP socket, receives a list of VPN servers,
    and connects to one of them. Then based on user settings, dynamically switches between servers. Currently, the two settings
    are 'random server' mode and 'low connection' mode, and the user can select a time interval to switch between servers."""
    def __init__(self, address: str, window: tk.Tk, option: int, time_interval: int):
        if option == 0:
            window.textbox.insert(tk.END, f"Selected Low Connection Mode - Updates every 10 seconds\n")
        elif option == 1:
            window.textbox.insert(tk.END, f"Selected Random Mode - Updates every 10 seconds\n")

        self.time_interval = time_interval
        self.servers_list: dict = {}
        self.current_best: tuple = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((address, 10000)) # Connect to rendezvous
        self.client_socket.sendall(b'\x10') # Send byte to alert eh rendezvous that you are a client
        window.textbox.insert(tk.END, f"Bootstrap - Connected to Rendezvous Server\n")

        data = self.client_socket.recv(1024)
        if data[0:1] == b'\x11': # If the first recv is a peer update (which will include itself), wait for the second recv
            data = self.client_socket.recv(1024)

        self.servers_list = eval(data.decode('utf-8')) # Convert the string peer data to a dictionary
        self.current_best = self.determine_best_server()
        self.client_socket.close()
        window.textbox.insert(tk.END, f"Bootstrap - Received Initial Peer List. Disconnected From Rendezvous\n")
        
        while True:
            # Create a socket and connect to VPN server
            vpn_server_addr = (self.current_best[0][0], self.current_best[1][0])
            vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vpn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            vpn_socket.connect(vpn_server_addr)
            window.textbox.insert(tk.END, f"Connected to VPN Server: {vpn_server_addr}\n")

            if option == 0: # Low connections mode
                while True:
                    time.sleep(self.time_interval)
                    vpn_socket.sendall(b'\x10') # Indicate request for updated peer list 
                    data = vpn_socket.recv(1024)
                    self.servers_list = eval(data.decode('utf-8'))
                    self.current_best = self.determine_best_server()
                    best_server_addr = (self.current_best[0][0], self.current_best[1][0])
                    # Only switch servers if they have fewer connections. If the current server is still the best option, stay connected
                    if best_server_addr == vpn_socket.getpeername():
                        window.textbox.insert(tk.END, f"Best Server is the Current Server...\n")
                    else:
                        window.textbox.insert(tk.END, f"Changing Servers...\n")
                        break

            if option == 1: # Random server mode
                while True:
                    time.sleep(self.time_interval)
                    vpn_socket.sendall(b'\x10') # Indicate request for updated peer list 
                    data = vpn_socket.recv(1024)
                    self.servers_list = eval(data.decode('utf-8'))

                    while True:
                        # Select a random server until it is different from the one currently connected
                        key, value = random.choice(list(self.servers_list.items()))
                        self.current_best = (key, value)
                        best_server_addr = (key[0], value[0])

                        if best_server_addr != vpn_socket.getpeername():
                            window.textbox.insert(tk.END, f"Selecting a Random VPN Server...\n")
                            break
                    break

    def determine_best_server(self) -> tuple[str, list]:
        """Determines the server with the lowest number of connections and returns the IP and port number for that server.
        
        Returns:
            a tuple representing the IP, port # of the best server available
        """
        best_option = None
        for key, value in self.servers_list.items():
            if not best_option or best_option[1][1] > value[1]:
                best_option = (key, value)

        return best_option


class Servers:
    neighbors: dict[tuple: list] = {}


class App(tk.Tk):
    """TKinter Main window of VPN client application"""
    def __init__(self):
        super().__init__()
        self.client_thread = None

        # Configure window
        self.title("VPN Client")
        self.geometry(f"{600}x{500}")

        # Give weight to window container - allows for better window size adjustment
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.textbox = tk.Text(
            self,
            wrap="word")

        self.config_frame = tk.Frame(self)
        self.config_frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="news")
        self.config_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.entry_frame = tk.Frame(self.config_frame)
        self.entry_frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=10)
        self.entry_frame.grid_rowconfigure((0, 1), weight=1)

        self.entry_label = tk.Label(
            self.entry_frame,
            text="Seconds")
        self.entry_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=2)

        self.time_var = tk.IntVar(self)
        self.time_var.set(10)
        self.time_entry = tk.Entry(
            self.entry_frame,
            width=10,
            textvariable=self.time_var)
        self.time_entry.grid(
            row=1,
            column=0,
            padx=10,
            pady=2)

        self.low_connections_button = tk.Button(
            self.config_frame,
            text="Low Connections",
            command=self.low_connections_pressed)
        self.low_connections_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=10)

        self.random_button = tk.Button(
            self.config_frame,
            text="Random Server",
            command=self.random_pressed)
        self.random_button.grid(
            row=0,
            column=2,
            padx=10,
            pady=10)
        

    def low_connections_pressed(self):
        """Called when low connections mode is selected."""
        try:
            switch_time = int(self.time_var.get())
        except:
            print("Invalid Time Entry")
            return
        
        self.config_frame.grid_forget() # Remove the options entry box and buttons
        self.label = tk.Label(
            self,
            text=f"Checking For Better Servers Every {switch_time} Seconds")
        self.label.grid(
            row=0,
            column=0,
            padx=10,
            pady=10)

        self.textbox.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="news")
        
        # Start a thread for the VPN Client
        self.client_thread = threading.Thread(target=low_conn_client, args=(self, switch_time))
        self.client_thread.start()

    def random_pressed(self):
        """Called when random mode is selected"""
        try:
            switch_time = int(self.time_var.get())
        except:
            print("Invalid Time Entry")
            return
        
        self.config_frame.grid_forget() # Remove the options entry box and buttons
        self.label = tk.Label(
            self,
            text=f"Switching Servers Every {switch_time} Seconds")
        self.label.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="news")

        self.textbox.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="news")
        
        # Start a thread for the VPN Client
        client_thread = threading.Thread(target=random_client, args=(self, switch_time))
        client_thread.start()


def low_conn_client(window: tk.Tk, time_interval: int):
    """Low Connections Client Thread"""
    Client('127.0.0.1', window, 0, time_interval)

def random_client(window: tk.Tk, time_interval: int):
    """Random Connection Client Thread"""
    Client('127.0.0.1', window, 1, time_interval)

if __name__ == "__main__":
    app = App()
    app.mainloop()
