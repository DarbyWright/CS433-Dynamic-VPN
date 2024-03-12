import socket
import threading
import time
from random import randint
import tkinter as tk


class Client:
    def __init__(self, address: str, window: tk.Tk, option: int):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((address, 10000)) # connect to rendezvous

        self.clientSocket.sendall(b'\x10') # send byte to distinguish between client and vpn server

        data = self.clientSocket.recv(1024)
        if data[0:1] == b'\x11':
            data = self.clientSocket.recv(1024)

        message: dict = eval(data.decode('utf-8'))
        window.textbox.insert(tk.END, f"Received Response From Server: {message}. Disconnecting from Rendezvous\n")
        print(f"Received Response From Server: {message}. Disconnecting from Rendezvous")
        self.clientSocket.close()

        if option == 0:
            while True:
                # data = self.clientSocket.recv(1024)
                # if data[0:1] == b'\x11':
                #     continue
                # else:
                #     message: dict = eval(data.decode('utf-8'))

                #     window.textbox.insert(tk.END, f"Received Response From Server: {message}. Disconnecting from Rendezvous\n")
                #     print(f"Received Response From Server: {message}. Disconnecting from Rendezvous")
                #     self.clientSocket.close()

                best_option = None
                for key, value in message.items():
                    if not best_option:
                        best_option = (key, value)
                    elif best_option[1][1] > value[1]:
                        best_option = (key, value)
                print(f"Best VPN Server Available: {best_option}")
                vpn_server_addr = (best_option[0][0], best_option[1][0])
                vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                vpn_socket.connect(vpn_server_addr)
                window.textbox.insert(tk.END, f"Connected to VPN Server: {best_option}\n")
                print(f"Connected to VPN Server: {best_option}")

                while True:
                    vpn_socket.sendall(bytes("VPN Server and Client are connected", 'utf-8'))
                    time.sleep(2)
        if option == 1:
            pass#TODO
    
    def handler(self):
        return

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
