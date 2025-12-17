# UDP Echo Client
import socket

HOST = "127.0.0.1"
PORT = 65431

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
    print("UDP Client ready. Type 'bye' to exit.\n")
    while True:
        message = input("You → ")
        if message.lower() == "bye":
            break
        client_socket.sendto(message.encode(), (HOST, PORT))
        data, _ = client_socket.recvfrom(1024)
        print(f"Server → {data.decode()}\n")
print("UDP Client stopped")