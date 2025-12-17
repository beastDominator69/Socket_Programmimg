# tcp_echo_server.py → FINAL PERFECT VERSION (Teacher's Favorite)
import socket

HOST = "127.0.0.1"
PORT = 65432

print("TCP Echo Server Starting...")
print(f"Listening on {HOST}:{PORT}\n")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("Waiting for client...\n")

    conn, addr = s.accept()
    with conn:
        print(f"Client connected: {addr}\n")
        while True:
            data = conn.recv(1024)
            if not data:
                print("Client disconnected")
                break
            message = data.decode().strip()
            print(f"Client → {message}")
            conn.sendall(data)
            print(f"Echoed back → {message}\n")
    print("Server closed")