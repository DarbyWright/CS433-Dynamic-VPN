import socket
import threading
import sys
import time
from random import randint


class Client:
    def __init__(self, address: str):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((address, 10000)) # connect to rendezvous

        clientSocket.send(b'\x10') # send byte to distinguish between client and vpn server

        while True:
            data = clientSocket.recv(1024)
            print(f"Received Response From Server: {data.decode('utf-8')}")


def main():
    client = Client('127.0.0.1')

if __name__ == "__main__":
    main()
