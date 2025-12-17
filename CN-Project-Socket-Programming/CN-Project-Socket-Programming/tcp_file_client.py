# TCP File Sender Client
import socket
import os

HOST = "127.0.0.1"
PORT = 65430
FILENAME = "sample.txt"   # This file must exist in your folder

if not os.path.isfile(FILENAME):
    print(f"Error: {FILENAME} not found! Create it first.")
    exit()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Sending {FILENAME} to server...")
    with open(FILENAME, "rb") as file:
        while True:
            bytes_read = file.read(1024)
            if not bytes_read:
                s.sendall(bytes_read)
            else:
                break
    print(f"{FILENAME} sent successfully!")