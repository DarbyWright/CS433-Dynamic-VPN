import socket
import threading
import sys
import time
from random import randint


class Client:
    def __init__(self, address: str):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((address, 10000)) # connect to rendezvous

        current_vpn_list = []

        clientSocket.sendall(b'\x10') # send byte to distinguish between client and vpn server

        while True:
            data = clientSocket.recv(1024)
            # Receive String of VPN to connect to(random or logical 1st vpn)
            # Disconnect from rendezvouz
            # Connect to VPN

            # Interface:
                # Option1: Random every short time interval - simulating per request
                
                # Option2: Button that gets the VPN with least connections and connects to it

            print(f"Received Response From Server: {data.decode('utf-8')}")


def main():
    client = Client('127.0.0.1')

if __name__ == "__main__":
    main()
