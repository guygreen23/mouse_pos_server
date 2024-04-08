import socket
import threading 
from collections import deque
import signal 
import sys


# Handle keyboard interrupt
def signal_handler(sig, frame):
    global stop_threads
    print("Ctrl+C detected. Stopping...")
    stop_threads = True
    
# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


# Define a global variable to control the thread execution
stop_threads = False

# Define a global variable to control the thread execution
HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090

# Deques to store mouse positions and cpu loads
messages = deque()
mouse_history = deque()
mouse_history_lock = threading.Lock()
cpu_load_history = deque()
cpu_load_history_lock = threading.Lock()

# Clients list to store the sender and receiver
clients = [None,None]  # 0 is the sender, 1 is the receiver

# Create a UDP socket
server = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
server.bind((HOST, PORT))
print(f"Server started at {HOST}:{PORT}")

# Function to receive data from the clients, for thread1
def receive():
    global stop_threads
    try:
        while not stop_threads:
            message, addr = server.recvfrom(1024)
            message = message.decode()
            if not message:  # If message is empty, client disconnected
                print(f"Client disconnected: {addr}")
                if addr == clients[0]:
                    clients[0] = None
                elif addr == clients[1]:
                    clients[1] = None
                continue
            print(f"Received message: {message} from {addr}")
            
            # Registering the clients
            if message.startswith("SENDER_TAG"):
                clients[0] = addr
                print(f"Sender connected: {addr}")
            elif message.startswith("RECEIVER_TAG"):
                clients[1] = addr
                print(f"Receiver connected: {addr}")
            
            # Receiving data
            elif clients[0] and addr == clients[0]: # If sender is connected
                if message.startswith("mouse:"):
                    message = message[6:] # Remove the "mouse:" prefix
                    with mouse_history_lock:
                        mouse_history.append(message)
                        print(f"Received mouse position from sender: {message}")
                elif message.startswith("cpu:"):
                    message = message[4:] # Remove the "cpu:" prefix
                    with cpu_load_history_lock:
                        cpu_load_history.append(message)
                        print(f"Received cpu load from sender: {message}")
                else:
                    print("Invalid message from sender.")
            else:
                print("Client not registered.")
                    
    except Exception as e: # Handle exceptions
        print(f"Error in receive thread: {e}")
            
# Initialize receiver thread
t = threading.Thread(target=receive)
t.start()

# Main thread loop
try:
    while not stop_threads:
        # Sending mouse positions
        if clients[1] and mouse_history:
            with mouse_history_lock:
                mouse_pos = mouse_history.popleft()
            server.sendto(mouse_pos.encode(), clients[1])
            print(f"Sent mouse position to receiver: {mouse_pos}")
        # Sending cpu_loads
        if clients[1] and cpu_load_history:
            with cpu_load_history_lock:
                cpu_load = cpu_load_history.popleft()
            server.sendto(cpu_load.encode(), clients[1])
            print(f"Sent cpu load to receiver: {cpu_load}")
            
# Handle keyboard interrupt
except KeyboardInterrupt:
    print("Client closed.")
    stop_threads = True
    t.join()
    server.close()
    sys.exit(0)




