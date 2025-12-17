from flask import Flask, render_template, request, jsonify, send_file
import threading
import socket
import time
import os
from datetime import datetime

app = Flask(__name__)
server_log = []
client_log = []
tcp_conn = None
browser_tcp_client = None
udp_socket = None

# Set your specific directory path
PROJECT_DIR = r"C:\Users\HP\OneDrive\Desktop\3rd semester\Computer Network\CN-Project-Socket-Programming"
FILE_SAVE_PATH = os.path.join(PROJECT_DIR, "received_files")

# Create directory if it doesn't exist
os.makedirs(FILE_SAVE_PATH, exist_ok=True)

print(f"Project Directory: {PROJECT_DIR}")
print(f"Files will be saved to: {FILE_SAVE_PATH}")

# TCP SERVER
def tcp_server():
    global tcp_conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 65432))
    s.listen(1)
    server_log.append("[TCP] Server started on port 65432")
    server_log.append("[TCP] Waiting for connection...")
    tcp_conn, addr = s.accept()
    server_log.append(f"[TCP] Client connected: {addr}")
    while True:
        try:
            data = tcp_conn.recv(1024)
            if not data: 
                server_log.append("[TCP] Client disconnected")
                break
            msg = data.decode().strip()
            server_log.append(f"[TCP] Received: {msg}")
            tcp_conn.sendall(data)
            server_log.append(f"[TCP] Echoed back: {msg}")
        except Exception as e:
            server_log.append(f"[TCP] Error: {e}")
            break
    tcp_conn.close()

# UDP SERVER
def udp_server():
    global udp_socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 65433))
    server_log.append("[UDP] Server started on port 65433")
    server_log.append("[UDP] Ready to receive packets...")
    
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            msg = data.decode().strip()
            server_log.append(f"[UDP] From {addr[0]}:{addr[1]}: {msg}")
            udp_socket.sendto(data, addr)
            server_log.append(f"[UDP] Echoed back to {addr[0]}:{addr[1]}")
            
        except Exception as e:
            # Ignore specific Windows UDP errors
            error_msg = str(e)
            if "10054" in error_msg or "forcibly closed" in error_msg:
                # This is normal UDP behavior, just continue
                continue
            elif "10040" in error_msg:
                # Message too long, ignore
                continue
            else:
                # Log other errors
                server_log.append(f"[UDP] Error: {e}")
                break

# FILE SERVER - Updated with your specific directory
def file_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 65434))
    s.listen(1)
    
    server_log.append("[FILE] Server started on port 65434")
    server_log.append(f"[FILE] Files will be saved to: {FILE_SAVE_PATH}")
    
    conn, addr = s.accept()
    server_log.append(f"[FILE] Client connected: {addr}")
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_file_{timestamp}.txt"
    file_path = os.path.join(FILE_SAVE_PATH, filename)
    
    total_bytes = 0
    with open(file_path, "wb") as f:
        while True:
            data = conn.recv(1024)
            if not data: 
                break
            f.write(data)
            total_bytes += len(data)
    
    conn.close()
    
    # Verify file was saved
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        server_log.append(f"[FILE] ✓ Successfully saved: {filename}")
        server_log.append(f"[FILE] ✓ File size: {file_size} bytes")
        server_log.append(f"[FILE] ✓ Location: {file_path}")
        print(f"\n[FILE SERVER] File saved: {file_path}")
        print(f"[FILE SERVER] Size: {file_size} bytes")
    else:
        server_log.append("[FILE] ✗ ERROR: File was not saved!")
        print("[FILE SERVER] ERROR: File was not saved!")

# AUTO CONNECT FOR TCP
def auto_tcp_connect():
    global browser_tcp_client
    time.sleep(2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(10):
        try:
            s.connect(("127.0.0.1", 65432))
            browser_tcp_client = s
            client_log.append("[TCP] Connected to server!")
            return
        except Exception as e:
            if i == 9:
                client_log.append(f"[TCP] Connection failed: {e}")
            time.sleep(0.5)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global server_log, client_log
    choice = request.json["choice"]
    
    # Clear logs
    server_log = []
    client_log = []
    
    server_log.append(f"[SYSTEM] Starting {choice.upper()} protocol...")
    client_log.append("[SYSTEM] Initializing...")

    if choice == "tcp":
        threading.Thread(target=tcp_server, daemon=True).start()
        threading.Thread(target=auto_tcp_connect, daemon=True).start()
        client_log.append("[TCP] Connecting to server...")
    elif choice == "udp":
        threading.Thread(target=udp_server, daemon=True).start()
        client_log.append("[UDP] Ready! Type messages below...")
    elif choice == "file":
        threading.Thread(target=file_server, daemon=True).start()
        client_log.append("[FILE] Ready! Select a file to upload...")
        client_log.append(f"[FILE] Files will be saved to: {FILE_SAVE_PATH}")

    return jsonify({"status": "ok"})

@app.route("/send", methods=["POST"])
def send():
    msg = request.json["msg"].strip()
    type_ = request.json["type"]
    client_log.append(f"[YOU] {msg}")

    if type_ == "tcp" and browser_tcp_client:
        try:
            browser_tcp_client.sendall((msg + "\n").encode())
            client_log.append(f"[TCP] Sent: {msg}")
        except Exception as e:
            client_log.append(f"[TCP] Error: {e}")
    elif type_ == "udp":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg.encode(), ("127.0.0.1", 65433))
            client_log.append(f"[UDP] Sent: {msg}")
            sock.close()
        except Exception as e:
            client_log.append(f"[UDP] Error: {e}")

    return jsonify({"status": "sent"})

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    client_log.append(f"[FILE] Preparing: {file.filename}")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("127.0.0.1", 65434))
        
        # Send file in chunks
        file.stream.seek(0)
        total_sent = 0
        while True:
            data = file.stream.read(1024)
            if not data: 
                break
            s.sendall(data)
            total_sent += len(data)
        
        s.close()
        client_log.append(f"[FILE] ✓ Successfully sent: {file.filename}")
        client_log.append(f"[FILE] ✓ Transferred: {total_sent} bytes")
        
    except Exception as e:
        client_log.append(f"[FILE] ✗ Error: {e}")
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"status": "uploaded", "bytes": total_sent})

@app.route("/list-files")
def list_files():
    """List all received files"""
    files = []
    if os.path.exists(FILE_SAVE_PATH):
        for filename in os.listdir(FILE_SAVE_PATH):
            filepath = os.path.join(FILE_SAVE_PATH, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                files.append({
                    "name": filename,
                    "size": size,
                    "modified": modified.strftime("%Y-%m-%d %H:%M:%S"),
                    "path": filepath
                })
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x["modified"], reverse=True)
    return jsonify({"files": files})

@app.route("/download/<filename>")
def download_file(filename):
    """Download a specific file"""
    file_path = os.path.join(FILE_SAVE_PATH, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_file(file_path, as_attachment=True)

@app.route("/logs")
def logs():
    return jsonify({
        "server": server_log[-50:], 
        "client": client_log[-50:],
        "file_dir": FILE_SAVE_PATH
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CYBER LAB - NETWORK PROTOCOL TESTER")
    print("="*60)
    print(f"Project Directory: {PROJECT_DIR}")
    print(f"File Save Path: {FILE_SAVE_PATH}")
    print("\nAccess the web interface at: http://127.0.0.1:5000")
    print("\nAvailable Servers:")
    print("  • TCP Server:   127.0.0.1:65432")
    print("  • UDP Server:   127.0.0.1:65433")
    print("  • File Server:  127.0.0.1:65434")
    print("="*60 + "\n")
    
    app.run(port=5000, debug=False)