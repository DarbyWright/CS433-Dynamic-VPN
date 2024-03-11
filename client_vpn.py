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
                message = data.decode('utf-8')
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


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("VPN Client")
        self.geometry(f"{600}x{500}")

        # Give weight to window container - allows for better window size adjustment
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = tk.Text(
            self,
            wrap="word")
        self.textbox.pack()

        self.start_button = tk.Button(
            self,
            text="Start",
            command=self.start_pressed)
        self.start_button.pack()
        
    def start_pressed(self):
        client_thread = threading.Thread(target=main, args=(self,))
        client_thread.start()


def main(window: tk.Tk):
    client = Client('127.0.0.1', window)

if __name__ == "__main__":
    # main()
    app = App()
    app.mainloop()
