import socket
import threading
import time
from random import randint
import tkinter as tk


class Client:
    def __init__(self, address: str, window: tk.Tk):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((address, 10000)) # connect to rendezvous

        clientSocket.sendall(b'\x10') # send byte to distinguish between client and vpn server

        while True:
            data = clientSocket.recv(1024)
            if data[0:1] == b'\x11':
                continue
            else:
                message = eval(data.decode('utf-8'))
                print(type(message))

                window.textbox.insert(tk.END, f"Received Response From Server: {message}. Disconnecting from Rendezvous\n")
                print(f"Received Response From Server: {message}. Disconnecting from Rendezvous")
                clientSocket.close()

                parts = message.split(':')
                vpn_server_addr = (parts[0], int(parts[2]))
                vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                vpn_socket.connect(vpn_server_addr)
                window.textbox.insert(tk.END, f"Connected to VPN Server: {vpn_server_addr}\n")
                print(f"Connected to VPN Server: {vpn_server_addr}")
                while True:
                    vpn_socket.sendall(bytes("VPN Server and Client are connected", 'utf-8'))
                    time.sleep(2)
                break

            # Receive String of VPN to connect to(random or logical 1st vpn)
            # Disconnect from rendezvouz
            # Connect to VPN

            # Interface:
                # Option1: Random every short time interval - simulating per request
                
                # Option2: Button that gets the VPN with least connections and connects to it

class Servers:
    neighbors: dict[tuple: list] = {}


class App(tk.Tk):
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
        client_thread = threading.Thread(target=main, args=(self,))
        client_thread.start()

    def random_pressed(self):
        print("Random Selected")


def main(window: tk.Tk):
    client = Client('127.0.0.1', window)

if __name__ == "__main__":
    # main()
    app = App()
    app.mainloop()
