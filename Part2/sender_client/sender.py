import socket
import threading
import pyautogui as py #Import pyautogui
import sys
import time
from collections import deque
import signal
import psutil

# Handle keyboard interrupt
def signal_handler(sig, frame):
    global stop_threads
    print("Ctrl+C detected. Stopping...")
    stop_threads = True
    
# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Define a global variable to control the thread execution
stop_threads = False

# Create a UDP socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
HOST = socket.gethostbyname(socket.gethostname())  # The ip of the server
PORT = 9092
SERVER_PORT = 9090
# Bind the socket to the client's IP and port
client.bind((HOST, PORT))
print(f"Client started at {HOST}:{PORT}")

# Check if the number of arguments is correct
if len(sys.argv) != 5:
    print("Not correct amount of args.\nUsage: python sender.py <generate_period_mouse> <send_period_mouse> <generate_period_cpu> <send_period_cpu>")
    sys.exit(1)

# Params for mouse positions
generate_period_mouse = float(sys.argv[1])
send_period_mouse = float(sys.argv[2])  

# Params for cpu load
generate_period_cpu = float(sys.argv[3])
send_period_cpu = float(sys.argv[4])  

# Get initial time
start_time_mouse = time.time()
last_send_time_mouse = start_time_mouse
start_time_cpu = time.time()
last_send_time_cpu = start_time_cpu

# Deques to store mouse positions and cpu loads
mouse_positions = deque(maxlen=100)
mouse_positions_lock = threading.Lock()
cpu_loads = deque(maxlen=100)
cpu_load_lock = threading.Lock()



# Generate mouse positions and cpu load
def generate_data():
    global start_time_mouse, start_time_cpu  # Declare global variables
    while not stop_threads:
        # Generate mouse positions
        if time.time() - start_time_mouse >= generate_period_mouse:
            x, y = py.position()
            print(f"Generating mouse position: ({x}, {y})")
            with mouse_positions_lock: 
                mouse_positions.append((x, y))
            start_time_mouse = time.time()
        
        # Generate cpu loads
        if time.time() - start_time_cpu >= generate_period_cpu:
            cpu_load = psutil.cpu_percent()
            print(f"Generating CPU load: {cpu_load}")
            with cpu_load_lock:
                cpu_loads.append(cpu_load)
            start_time_cpu = time.time()

# Start the thread to generate data
t = threading.Thread(target=generate_data)
t.start()

# Send a message to the server to identify as a sender client
client.sendto(f"SENDER_TAG".encode(), (HOST,SERVER_PORT))

# Send mouse positions and cpu loads to the server
try:
    while not stop_threads:
        # Send mouse positions
        if time.time() - last_send_time_mouse >= send_period_mouse:
            if mouse_positions:
                with mouse_positions_lock:
                    client.sendto(f"mouse:{list(mouse_positions)}".encode(), (HOST, SERVER_PORT))
                    mouse_positions.clear()
                last_send_time_mouse = time.time()
        # Send cpu loads
        if time.time() - last_send_time_cpu >= send_period_cpu:
            if cpu_loads:
                with cpu_load_lock:
                    client.sendto(f"cpu:{list(cpu_loads)}".encode(), (HOST, SERVER_PORT))
                    cpu_loads.clear()
            last_send_time_cpu = time.time()

# Handle keyboard interrupt
except KeyboardInterrupt:
    print("Client closed.")
    stop_threads = True
    t.join()
    client.close()
    sys.exit(0)