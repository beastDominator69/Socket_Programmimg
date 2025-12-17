# tcp_echo_client.py → BEST CHAT CLIENT FOR PROJECT
import socket

HOST = "127.0.0.1"
PORT = 65432

print("Connecting to server...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected! Start chatting. Type 'bye' to quit.\n")

    while True:
        msg = input("You → ").strip()
        if msg.lower() == "bye":
            print("Goodbye!")
            break
        if not msg:
            continue  # skip empty messages

        s.sendall(msg.encode())
        reply = s.recv(1024).decode().strip()
        print(f"Server → {reply}\n")