# TCP File Receiver Server
import socket

HOST = "127.0.0.1"
PORT = 65430

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("TCP File Server started. Waiting for file...")
    conn, addr = s.accept()
    with conn:
        print(f"Client {addr} connected. Receiving file...")
        with open("received_file_from_client.txt", "wb") as file:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                file.write(data)
        print("File received successfully! Saved as 'received_file_from_client.txt'")