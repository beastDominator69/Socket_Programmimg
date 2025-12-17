# UDP Echo Server - Connectionless, fast
import socket

HOST = "127.0.0.1"
PORT = 65431

print("UDP Echo Server started on port 65431...")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
    udp_socket.bind((HOST, PORT))
    print("Waiting for messages...")
    
    while True:
        data, client_addr = udp_socket.recvfrom(1024)
        message = data.decode()
        print(f"Received from {client_addr}: {message}")
        udp_socket.sendto(data, client_addr)  # send back same message