import socket
import threading
import time

def handle_unity_data():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12346))  
    server_socket.listen(1)
    print("Waiting for connection from Unity...")

    conn, addr = server_socket.accept()
    print(f"Connected to Unity at {addr}")

    while True:
        data = conn.recv(1024)
        if data:
            stim_code = int(data.decode('utf-8'))
            print(f"Received stim code: {stim_code}")
        
            # Check for termination code
            if stim_code == 9:
                print("Received termination code. Closing connection.")
                break

    conn.close()
    server_socket.close()

def simulate_unity_client():
    """Simulates Unity sending data to the Python server"""
    time.sleep(1)  # Wait for the server to start
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12346))
    print("Simulated Unity client connected to server")

    for i in range(1, 6):  # Send 5 test messages
        message = str(i).encode('utf-8')
        client_socket.sendall(message)
        print(f"Sent message: {i}")
        time.sleep(1)  # Wait 1 second between messages

    # Send termination code
    client_socket.sendall(b'0')
    client_socket.close()

if __name__ == '__main__':
    # Start the server in a separate thread
    server_thread = threading.Thread(target=handle_unity_data)
    server_thread.start()

    # Simulate Unity client
    # simulate_unity_client()

    # Wait for the server thread to finish
    server_thread.join()